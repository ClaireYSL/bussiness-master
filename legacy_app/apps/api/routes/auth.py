from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_current_user
from shared.config import Settings, get_settings
from shared.db import get_db
from shared.models import User
from shared.security import issue_session_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=255)


class UserPayload(BaseModel):
    id: int
    username: str
    is_admin: bool


@router.post("/login")
async def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    settings = get_settings()
    user = db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"ok": False, "message": "用户名或密码错误"}

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
    return {"ok": True, "user": UserPayload.model_validate(user, from_attributes=True).model_dump()}


@router.post("/logout")
async def logout(
    response: Response,
) -> dict[str, bool]:
    settings = get_settings()
    response.delete_cookie(settings.auth_cookie_name)
    return {"ok": True}


@router.get("/me")
async def me(current_user: User = Depends(require_current_user)) -> dict[str, object]:
    return {"ok": True, "user": UserPayload.model_validate(current_user, from_attributes=True).model_dump()}
