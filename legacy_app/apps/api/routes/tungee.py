from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_current_user
from shared.config import Settings, get_settings
from shared.db import get_db
from shared.models import TungeeSession, User
from shared.services.tungee_auth import SessionPayload, TungeeAuthError, TungeeAuthService, TungeeSessionExpiredError

router = APIRouter(prefix="/api/tungee/session", tags=["tungee"])
logger = logging.getLogger("bussiness.api.tungee")


class TungeeBrowserImportRequest(BaseModel):
    user_agent: Optional[str] = Field(default=None, max_length=1024)
    sales_cookie_header: str = Field(min_length=1, max_length=65535)
    sales_search_cookie_header: Optional[str] = Field(default=None, max_length=65535)
    user_cookie_header: Optional[str] = Field(default=None, max_length=65535)
    sales_request_headers: Dict[str, str] = Field(default_factory=dict)
    sales_search_request_headers: Dict[str, str] = Field(default_factory=dict)
    source_url: Optional[str] = Field(default=None, max_length=4096)


def _ensure_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _serialize_session(record: TungeeSession) -> dict[str, object]:
    expires_at = _ensure_utc(record.expires_at)
    last_verified_at = _ensure_utc(record.last_verified_at)
    return {
        "status": record.status,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "last_verified_at": last_verified_at.isoformat() if last_verified_at else None,
    }


def _sales_headers_ready(session_payload: Any) -> bool:
    headers = getattr(session_payload, "sales_request_headers", None)
    if headers is None and isinstance(session_payload, dict):
        headers = session_payload.get("sales_request_headers")
    if not isinstance(headers, dict):
        return False
    return all(str(headers.get(key) or "").strip() for key in ("x-tonxis-pid", "x-tonxis-sid", "x-tonxis-signature"))


def _specific_headers_ready(headers: Any) -> bool:
    if not isinstance(headers, dict):
        return False
    return all(str(headers.get(key) or "").strip() for key in ("x-tonxis-pid", "x-tonxis-sid", "x-tonxis-signature"))


def _cookie_present(payload: SessionPayload, cookie_name: str) -> bool:
    if str((payload.cookies or {}).get(cookie_name) or "").strip():
        return True
    raw_headers = [payload.sales_cookie_header, payload.user_cookie_header]
    for raw_header in raw_headers:
        text = str(raw_header or "")
        if f"{cookie_name}=" in text:
            return True
    return False


def _build_context_summary(payload: SessionPayload) -> dict[str, object]:
    cookie_names = [
        "accountCenterSessionId",
        "remember_token",
        "CGISessionId",
        "doncusSessionId",
        "_tx_pid",
        "_tx_sid",
        "_tx_cid",
        "_tx_uid",
        "SecurityCenterDuId",
    ]
    cookie_flags = {name: _cookie_present(payload, name) for name in cookie_names}
    current_headers = payload.sales_request_headers or {}
    search_headers = payload.sales_search_request_headers or {}
    return {
        "source": "browser_sync" if payload.sales_cookie_header or payload.user_cookie_header else "manual_login",
        "sales_headers_ready": _specific_headers_ready(current_headers),
        "sales_search_headers_ready": _specific_headers_ready(search_headers),
        "headers": {
            "current": {key: bool(str(current_headers.get(key) or "").strip()) for key in ("x-tonxis-pid", "x-tonxis-sid", "x-tonxis-signature")},
            "search": {key: bool(str(search_headers.get(key) or "").strip()) for key in ("x-tonxis-pid", "x-tonxis-sid", "x-tonxis-signature")},
        },
        "cookies": cookie_flags,
        "sales_cookie_header_present": bool(payload.sales_cookie_header),
        "sales_search_cookie_header_present": bool(payload.sales_search_cookie_header),
        "user_cookie_header_present": bool(payload.user_cookie_header),
    }


def _merged_cookie_map(
    service: TungeeAuthService,
    *,
    sales_cookie_header: Optional[str],
    user_cookie_header: Optional[str],
) -> dict[str, str]:
    cookies: dict[str, str] = {}
    if user_cookie_header:
        cookies.update(service._parse_cookie_header(user_cookie_header))
    if sales_cookie_header:
        cookies.update(service._parse_cookie_header(sales_cookie_header))
    return cookies


@router.post("/import")
async def import_tungee_session(
    payload: TungeeBrowserImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    user_agent = (payload.user_agent or "").strip() or TungeeAuthService().user_agent
    service = TungeeAuthService(user_agent=user_agent)
    merged_cookies = _merged_cookie_map(
        service,
        sales_cookie_header=payload.sales_cookie_header,
        user_cookie_header=payload.user_cookie_header,
    )
    normalized_headers = service._normalize_sales_request_headers(
        merged_cookies,
        sales_request_headers=payload.sales_request_headers,
    )
    normalized_search_headers = service._normalize_sales_request_headers(
        merged_cookies,
        sales_request_headers=payload.sales_search_request_headers,
    )

    imported = SessionPayload(
        cookies=merged_cookies,
        user_agent=user_agent,
        sales_request_headers=normalized_headers,
        sales_search_request_headers=normalized_search_headers,
        sales_cookie_header=(payload.sales_cookie_header or "").strip() or None,
        sales_search_cookie_header=(payload.sales_search_cookie_header or "").strip() or None,
        user_cookie_header=(payload.user_cookie_header or "").strip() or None,
    )

    try:
        profile = service.verify(imported)
    except TungeeAuthError as exc:
        return {"ok": False, "message": f"探迹浏览器上下文导入失败：{exc}"}

    final_payload = SessionPayload(
        cookies=merged_cookies,
        user_agent=user_agent,
        profile=profile,
        sales_request_headers=normalized_headers,
        sales_search_request_headers=normalized_search_headers,
        sales_cookie_header=(payload.sales_cookie_header or "").strip() or None,
        sales_search_cookie_header=(payload.sales_search_cookie_header or "").strip() or None,
        user_cookie_header=(payload.user_cookie_header or "").strip() or None,
    )

    try:
        record = service.save_session(db, user_id=current_user.id, session_payload=final_payload)
        db.commit()
    except Exception:
        db.rollback()
        raise

    logger.info(
        "Imported tungee session. user_id=%s username=%s tungee_mobile=%s source_url=%s",
        current_user.id,
        current_user.username,
        profile.get("_login_mobile") or profile.get("phone") or profile.get("mobile") or profile.get("login_phone"),
        payload.source_url,
    )

    return {
        "ok": True,
        "message": "已从浏览器导入探迹会话",
        "session": _serialize_session(record),
        "profile": profile,
        "sales_headers_ready": _sales_headers_ready(final_payload),
        "context_summary": _build_context_summary(final_payload),
        "source_url": payload.source_url,
    }


@router.get("/status")
async def tungee_session_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    settings = get_settings()
    record = db.execute(select(TungeeSession).where(TungeeSession.user_id == current_user.id)).scalar_one_or_none()
    if record is None:
        return {"ok": True, "connected": False, "session": None}

    now = datetime.now(timezone.utc)
    expires_at = _ensure_utc(record.expires_at)
    if expires_at is not None and expires_at <= now:
        try:
            record.status = "expired"
            record.last_verified_at = now
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {"ok": True, "connected": False, "session": _serialize_session(record)}

    service = TungeeAuthService(settings=settings)
    payload = service.load_session_payload(record)
    try:
        profile = service.verify(payload)
    except TungeeSessionExpiredError:
        try:
            record.status = "invalid"
            record.last_verified_at = now
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {"ok": True, "connected": False, "session": _serialize_session(record)}
    except TungeeAuthError as exc:
        return {
            "ok": False,
            "connected": True,
            "message": str(exc),
            "session": _serialize_session(record),
        }

    try:
        record.status = "active"
        record.last_verified_at = now
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "ok": True,
        "connected": True,
        "session": _serialize_session(record),
        "profile": profile,
        "tungee_mobile": profile.get("_login_mobile") or profile.get("phone"),
        "sales_headers_ready": _sales_headers_ready(payload),
        "context_summary": _build_context_summary(payload),
    }


@router.post("/refresh")
async def refresh_tungee_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    settings = get_settings()
    record = db.execute(select(TungeeSession).where(TungeeSession.user_id == current_user.id)).scalar_one_or_none()
    if record is None:
        return {"ok": False, "message": "当前用户还没有探迹会话"}

    service = TungeeAuthService(settings=settings)
    payload = service.load_session_payload(record)
    now = datetime.now(timezone.utc)
    try:
        profile = service.verify(payload)
    except TungeeSessionExpiredError:
        try:
            record.status = "invalid"
            record.last_verified_at = now
            db.commit()
        except Exception:
            db.rollback()
            raise
        return {"ok": False, "message": "探迹会话已失效，请重新登录", "session": _serialize_session(record)}

    try:
        record.status = "active"
        record.last_verified_at = now
        record.expires_at = now + timedelta(hours=settings.tungee_session_ttl_hours)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "ok": True,
        "session": _serialize_session(record),
        "profile": profile,
        "tungee_mobile": profile.get("_login_mobile") or profile.get("phone"),
        "sales_headers_ready": _sales_headers_ready(payload),
        "context_summary": _build_context_summary(payload),
    }


@router.delete("")
async def delete_tungee_session(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> dict[str, object]:
    record = db.execute(select(TungeeSession).where(TungeeSession.user_id == current_user.id)).scalar_one_or_none()
    if record is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"ok": False, "message": "当前用户还没有探迹会话"}

    try:
        db.delete(record)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"ok": True}
