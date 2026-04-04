from __future__ import annotations

import logging
import os
import shutil
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_current_user
from deliveries.exporter import export_query_job
from shared.db import get_db
from shared.models import QueryItem, ResearchEventResult, ResearchFieldResult, TungeeSession, User
from shared.services.tungee_auth import TungeeAuthService
from shared.services.query_executor import enqueue_query_job
from shared.services.query_orchestrator import (
    create_query_job,
    get_query_item_detail,
    get_query_job,
    list_query_jobs_page,
    reset_query_item_for_retry,
    serialize_query_item,
    serialize_query_job,
)

router = APIRouter(prefix="/api/query-jobs", tags=["query-jobs"])
logger = logging.getLogger("bussiness.api.query_jobs")


class CreateQueryJobRequest(BaseModel):
    company_names: list[str] = Field(default_factory=list)
    recruiting_keyword: Optional[str] = None
    resolved_matches: list[dict[str, str]] = Field(default_factory=list)
    prefetched_results: list[dict[str, object]] = Field(default_factory=list)


DELETABLE_ITEM_STATUSES = {"completed", "failed", "not_found", "session_expired"}


def _current_tungee_identity(db: Session, *, user_id: int) -> tuple[str, str | None] | None:
    session_record = db.execute(select(TungeeSession).where(TungeeSession.user_id == user_id)).scalar_one_or_none()
    if session_record is None:
        return None
    payload = TungeeAuthService().load_session_payload(session_record)
    profile = payload.profile or {}
    mobile = str(
        profile.get("_login_mobile")
        or profile.get("phone")
        or profile.get("mobile")
        or profile.get("login_phone")
        or ""
    ).strip()
    name = str(
        profile.get("name")
        or profile.get("nickname")
        or profile.get("nick_name")
        or profile.get("user_name")
        or ""
    ).strip() or None
    if not mobile:
        return None
    return mobile, name


def _delete_query_item_record(db: Session, *, item: QueryItem) -> bool:
    job = item.job
    if item.research_report is not None:
        db.query(ResearchFieldResult).filter(ResearchFieldResult.report_id == item.research_report.id).delete()
        db.query(ResearchEventResult).filter(ResearchEventResult.report_id == item.research_report.id).delete()
        db.delete(item.research_report)
    if item.result is not None:
        db.delete(item.result)
    db.delete(item)
    db.flush()
    if job is None:
        return False
    remaining = db.execute(select(QueryItem).where(QueryItem.job_id == job.id)).scalars().all()
    if remaining:
        job.submitted_count = len(remaining)
        summary_statuses = [record.status for record in remaining]
        if all(status_name == "completed" for status_name in summary_statuses):
            job.status = "completed"
        elif any(status_name == "completed" for status_name in summary_statuses):
            job.status = "partial_success"
        elif any(status_name == "session_expired" for status_name in summary_statuses):
            job.status = "session_expired"
        elif any(status_name == "failed" for status_name in summary_statuses):
            job.status = "failed"
        elif any(status_name == "not_found" for status_name in summary_statuses):
            job.status = "completed"
        else:
            job.status = "pending"
        return False
    db.delete(job)
    return True


@router.post("")
async def create_job(
    payload: CreateQueryJobRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ok": False, "message": "请先登录探迹账号后再创建查询批次"}

    tungee_mobile, tungee_name = identity
    try:
        job = create_query_job(
            db,
            user_id=current_user.id,
            company_names=payload.company_names,
            tungee_mobile=tungee_mobile,
            tungee_name=tungee_name,
            recruiting_keyword=(payload.recruiting_keyword or "").strip() or None,
            resolved_matches=payload.resolved_matches,
            prefetched_results=payload.prefetched_results,
        )
        db.commit()
    except ValueError as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ok": False, "message": str(exc)}
    except Exception:
        db.rollback()
        raise

    enqueue_query_job(job_id=job.id, user_id=current_user.id)

    hydrated = get_query_job(db, job_id=job.id, user_id=current_user.id, tungee_mobile=tungee_mobile)
    logger.info(
        "Created query job. user_id=%s username=%s tungee_mobile=%s job_public_id=%s company_count=%s",
        current_user.id,
        current_user.username,
        tungee_mobile,
        job.public_id,
        len(payload.company_names),
    )
    return {"ok": True, "job": serialize_query_job(hydrated or job, include_items=True)}


@router.get("")
async def get_jobs(
    status_filter: Optional[str] = None,
    search: Optional[str] = Query(default=None),
    item_status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        logger.info(
            "Listed query jobs without tungee identity. user_id=%s username=%s status_filter=%s jobs_count=0",
            current_user.id,
            current_user.username,
            status_filter,
        )
        return {
            "ok": True,
            "jobs": [],
            "pagination": {"page": page, "page_size": page_size, "total": 0, "total_pages": 0},
        }
    tungee_mobile, _ = identity
    jobs, total = list_query_jobs_page(
        db,
        user_id=current_user.id,
        status=status_filter,
        tungee_mobile=tungee_mobile,
        search=search,
        item_status=item_status,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    logger.info(
        "Listed query jobs. user_id=%s username=%s tungee_mobile=%s status_filter=%s item_status=%s search=%s page=%s page_size=%s jobs_count=%s total=%s",
        current_user.id,
        current_user.username,
        tungee_mobile,
        status_filter,
        item_status,
        search,
        page,
        page_size,
        len(jobs),
        total,
    )
    return {
        "ok": True,
        "jobs": [serialize_query_job(job, include_items=True, item_summary_only=True) for job in jobs],
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    }


@router.get("/{job_public_id}")
async def get_job_detail(
    job_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        logger.info(
            "Query job detail missed due to missing tungee identity. user_id=%s username=%s job_public_id=%s",
            current_user.id,
            current_user.username,
            job_public_id,
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询批次不存在"}
    tungee_mobile, _ = identity
    job = get_query_job(db, public_id=job_public_id, user_id=current_user.id, tungee_mobile=tungee_mobile)
    if job is None:
        logger.info(
            "Query job detail miss. user_id=%s username=%s tungee_mobile=%s job_public_id=%s",
            current_user.id,
            current_user.username,
            tungee_mobile,
            job_public_id,
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询批次不存在"}
    logger.info(
        "Query job detail hit. user_id=%s username=%s tungee_mobile=%s job_public_id=%s",
        current_user.id,
        current_user.username,
        tungee_mobile,
        job_public_id,
    )
    return {"ok": True, "job": serialize_query_job(job, include_items=True)}


@router.get("/items/{item_public_id}/detail")
async def get_item_detail(
    item_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    tungee_mobile, _ = identity
    item = get_query_item_detail(
        db,
        public_id=item_public_id,
        user_id=current_user.id,
        tungee_mobile=tungee_mobile,
    )
    if item is None or item.job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    return {
        "ok": True,
        "job": serialize_query_job(item.job, include_items=False),
        "item": serialize_query_item(item),
    }


@router.post("/items/{item_public_id}/retry")
async def retry_query_item(
    item_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    tungee_mobile, _ = identity
    item = db.execute(select(QueryItem).where(QueryItem.public_id == item_public_id)).scalar_one_or_none()
    if item is None or item.job is None or item.job.user_id != current_user.id or item.job.tungee_mobile != tungee_mobile:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}

    reset_query_item_for_retry(item)
    item.job.status = "pending"
    db.commit()
    enqueue_query_job(job_id=item.job_id, user_id=current_user.id)
    db.refresh(item)
    return {"ok": True, "item": serialize_query_item(item)}


@router.delete("/items/{item_public_id}")
async def delete_query_item(
    item_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    tungee_mobile, _ = identity
    item = db.execute(select(QueryItem).where(QueryItem.public_id == item_public_id)).scalar_one_or_none()
    if item is None or item.job is None or item.job.user_id != current_user.id or item.job.tungee_mobile != tungee_mobile:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    if item.status not in DELETABLE_ITEM_STATUSES:
        response.status_code = status.HTTP_409_CONFLICT
        return {"ok": False, "message": "正在执行中的记录暂不支持删除"}

    deleted_job = _delete_query_item_record(db, item=item)
    db.commit()
    return {"ok": True, "deleted_item_public_id": item_public_id, "deleted_job": deleted_job}


@router.get("/{job_public_id}/export")
async def export_job_result(
    job_public_id: str,
    format: str = Query(default="csv"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    identity = _current_tungee_identity(db, user_id=current_user.id)
    if identity is None:
        if response is not None:
            response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询批次不存在"}
    tungee_mobile, _ = identity
    job = get_query_job(db, public_id=job_public_id, user_id=current_user.id, tungee_mobile=tungee_mobile)
    if job is None:
        if response is not None:
            response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询批次不存在"}

    tmp_dir = tempfile.mkdtemp(prefix="query_job_export_")
    try:
        export_path = export_query_job(job.id, file_format=format, output_dir=tmp_dir)
    except ValueError as exc:
        if response is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ok": False, "message": str(exc)}

    filename = os.path.basename(export_path)
    media_type = "text/csv; charset=utf-8" if format.lower() == "csv" else (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return FileResponse(
        export_path,
        filename=filename,
        media_type=media_type,
        background=BackgroundTask(lambda: shutil.rmtree(tmp_dir, ignore_errors=True)),
    )
