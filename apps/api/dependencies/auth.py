from __future__ import annotations

import logging
import secrets
from typing import Optional

from datetime import timedelta

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from shared.config import Settings, get_settings
from shared.db import get_db
from shared.models import User
from shared.security import (
    InvalidSessionTokenError,
    hash_password,
    issue_session_token,
    issue_signed_value,
    read_session_token,
    read_signed_value,
)


ANONYMOUS_USERNAME = "anonymous"
ANONYMOUS_PASSWORD_PLACEHOLDER = "anonymous-local-only"
ADMIN_GATE_COOKIE_VALUE = "admin:granted"
logger = logging.getLogger("bussiness.api.auth")


def _issue_auth_cookie(*, response: Response, settings: Settings, user: User) -> None:
    token = issue_session_token(
        {"sub": user.id, "username": user.username},
        secret_key=settings.app_secret_key,
        expires_in=timedelta(days=settings.auth_session_days),
    )
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.auth_session_days * 24 * 60 * 60,
    )


def _create_browser_local_user(db: Session) -> User:
    while True:
        browser_local_user = User(
            username=f"{ANONYMOUS_USERNAME}_{secrets.token_hex(8)}",
            password_hash=hash_password(ANONYMOUS_PASSWORD_PLACEHOLDER),
            is_admin=True,
        )
        db.add(browser_local_user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(browser_local_user)
        return browser_local_user


async def get_current_user_optional(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Optional[User]:
    settings = get_settings()
    raw_token = request.cookies.get(settings.auth_cookie_name)
    if raw_token:
        try:
            payload = read_session_token(raw_token, secret_key=settings.app_secret_key)
            user_id = payload.get("sub")
            if user_id is not None:
                user = db.get(User, int(user_id))
                if user is not None:
                    return user
        except InvalidSessionTokenError:
            logger.warning("Invalid auth cookie received; issuing browser-local user. client_host=%s", getattr(request.client, "host", None))

    browser_local_user = _create_browser_local_user(db)
    _issue_auth_cookie(response=response, settings=settings, user=browser_local_user)
    logger.info(
        "Issued browser-local user session. user_id=%s username=%s client_host=%s had_cookie=%s",
        browser_local_user.id,
        browser_local_user.username,
        getattr(request.client, "host", None),
        bool(raw_token),
    )
    return browser_local_user


async def require_current_user(
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录系统")
    return current_user


async def require_admin_user(
    current_user: User = Depends(require_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


def issue_admin_gate_cookie(*, settings: Settings) -> str:
    return issue_signed_value(
        ADMIN_GATE_COOKIE_VALUE,
        secret_key=settings.app_secret_key,
        expires_in=timedelta(days=settings.auth_session_days),
    )


async def require_admin_gate(
    request: Request,
) -> bool:
    settings = get_settings()
    raw_token = request.cookies.get(settings.admin_gate_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="需要后台访问密码")

    try:
        value = read_signed_value(raw_token, secret_key=settings.app_secret_key)
    except InvalidSessionTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="后台访问凭证已失效") from exc

    if value != ADMIN_GATE_COOKIE_VALUE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="后台访问凭证无效")
    return True
