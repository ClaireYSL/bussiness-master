from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_current_user
from shared.db import get_db
from shared.models import QueryItem, User
from shared.services.kimi_research import KimiResearchService
from shared.services.query_orchestrator import serialize_query_item, serialize_research_report
from shared.services.research_runner import enqueue_research_report, ensure_research_report

router = APIRouter(prefix="/api/research", tags=["research"])


class RunResearchRequest(BaseModel):
    query_item_public_id: str
@router.post("/run")
async def run_research(
    payload: RunResearchRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    item = db.query(QueryItem).filter(QueryItem.public_id == payload.query_item_public_id).one_or_none()
    if item is None or item.job is None or item.job.user_id != current_user.id:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}

    if item.research_report is not None and item.research_report.status in {"queued", "running"}:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "ok": False,
            "message": "AI详研进行中，暂不支持重跑",
            "item": serialize_query_item(item),
            "research": serialize_research_report(item.research_report),
        }

    report, should_enqueue = ensure_research_report(db, item=item, force=True)
    db.commit()
    if should_enqueue:
        enqueue_research_report(report.id)
    db.refresh(item)
    return {"ok": True, "item": serialize_query_item(item), "research": serialize_research_report(report)}


@router.get("/item/{query_item_public_id}")
async def get_research_by_item(
    query_item_public_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    item = db.query(QueryItem).filter(QueryItem.public_id == query_item_public_id).one_or_none()
    if item is None or item.job is None or item.job.user_id != current_user.id:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "查询项不存在"}
    return {"ok": True, "research": serialize_research_report(item.research_report)}


@router.get("/knowledge-document")
async def get_knowledge_document(
    response: Response,
    path: str = Query(..., description="知识库相对路径"),
    chunk_id: Optional[str] = Query(None, description="命中的 chunk_id"),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    del current_user
    service = KimiResearchService()
    document = service.get_local_knowledge_document(path=path, chunk_id=chunk_id)
    if document is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "知识库文档不存在"}
    return {"ok": True, "document": document}
