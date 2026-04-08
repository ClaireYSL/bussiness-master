from __future__ import annotations

from typing import Optional

from datetime import timedelta
import hmac

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import issue_admin_gate_cookie, require_admin_gate
from shared.config import Settings, get_settings
from shared.db import get_db
from shared.services.app_settings import get_secret_setting, set_secret_setting
from shared.services.kimi_research import KimiResearchError, KimiResearchService
from shared.services.query_orchestrator import (
    get_query_item_detail,
    get_query_job,
    list_query_jobs_page,
    list_tungee_sessions,
    serialize_query_item,
    serialize_query_job,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_GATE_PASSWORD = "Wl87654321@"


class AdminGateRequest(BaseModel):
    password: str


class AdminMoonshotKeyRequest(BaseModel):
    api_key: str


@router.post("/gate/login")
async def admin_gate_login(
    payload: AdminGateRequest,
    response: Response,
) -> dict[str, object]:
    settings = get_settings()
    if not hmac.compare_digest(payload.password, ADMIN_GATE_PASSWORD):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"ok": False, "message": "后台密码错误"}

    token = issue_admin_gate_cookie(settings=settings)
    response.set_cookie(
        key=settings.admin_gate_cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=int(timedelta(days=settings.auth_session_days).total_seconds()),
    )
    return {"ok": True}


@router.get("/query-jobs")
async def admin_query_jobs(
    user_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 6,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    jobs, total = list_query_jobs_page(db, user_id=user_id, status=status_filter, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "ok": True,
        "jobs": [serialize_query_job(job, include_items=True, item_summary_only=True) for job in jobs],
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    }


@router.get("/query-jobs/{job_public_id}")
async def admin_query_job_detail(
    job_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    job = get_query_job(db, public_id=job_public_id)
    if job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询批次不存在"}
    return {"ok": True, "job": serialize_query_job(job, include_items=True)}


@router.get("/query-jobs/items/{item_public_id}/detail")
async def admin_query_item_detail(
    item_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    item = get_query_item_detail(db, public_id=item_public_id)
    if item is None or item.job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    return {
        "ok": True,
        "job": serialize_query_job(item.job, include_items=False),
        "item": serialize_query_item(item),
    }


@router.get("/tungee-sessions")
async def admin_tungee_sessions(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    return {"ok": True, "sessions": list_tungee_sessions(db, user_id=user_id)}


@router.get("/settings/moonshot")
async def get_moonshot_setting(
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    settings = get_settings()
    configured = bool(get_secret_setting(db, key="MOONSHOT_API_KEY", secret_key=settings.app_secret_key))
    return {"ok": True, "configured": configured}


@router.post("/settings/moonshot")
async def save_moonshot_setting(
    payload: AdminMoonshotKeyRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    settings = get_settings()
    api_key = payload.api_key.strip()
    if not api_key:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ok": False, "message": "请输入有效的 MOONSHOT_API_KEY"}

    set_secret_setting(db, key="MOONSHOT_API_KEY", value=api_key, secret_key=settings.app_secret_key)
    db.commit()
    return {"ok": True, "configured": True}


@router.post("/settings/moonshot/test")
async def test_moonshot_setting(
    payload: AdminMoonshotKeyRequest,
    response: Response,
    _: bool = Depends(require_admin_gate),
) -> dict[str, object]:
    service = KimiResearchService()
    try:
        result = service.test_api_key(payload.api_key)
    except KimiResearchError as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"ok": False, "message": str(exc)}
    return {"ok": True, "result": result}
