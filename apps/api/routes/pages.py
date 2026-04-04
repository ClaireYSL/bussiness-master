from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.api.dependencies.auth import get_current_user_optional, require_current_user
from shared.config import Settings, get_settings
from shared.security import InvalidSessionTokenError, read_signed_value
from shared.models import User


templates = Jinja2Templates(directory="apps/api/templates")
router = APIRouter(tags=["pages"])


def _base_context(request: Request, current_user: Optional[User]) -> dict[str, object]:
    settings = get_settings()
    user_label = "匿名模式"
    if current_user is not None and not current_user.username.startswith("anonymous"):
        user_label = current_user.username
    return {
        "request": request,
        "current_user": current_user,
        "user_label": user_label,
        "app_name": settings.app_name,
        "tungee_sales_base_url": settings.tungee_sales_base_url,
    }


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> HTMLResponse:
    return RedirectResponse(url="/console", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> HTMLResponse:
    return RedirectResponse(url="/console", status_code=302)


@router.get("/console", response_class=HTMLResponse)
async def console_page(
    request: Request,
    current_user: User = Depends(require_current_user),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="query_console.html",
        context=_base_context(request, current_user),
    )


@router.get("/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    current_user: User = Depends(require_current_user),
) -> HTMLResponse:
    return RedirectResponse(url="/console", status_code=302)


@router.get("/tungee/connect", response_class=HTMLResponse)
async def tungee_connect_page(
    request: Request,
    current_user: User = Depends(require_current_user),
) -> HTMLResponse:
    return RedirectResponse(url="/console", status_code=302)


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    current_user: User = Depends(require_current_user),
) -> HTMLResponse:
    settings = get_settings()
    raw_token = request.cookies.get(settings.admin_gate_cookie_name)
    if not raw_token:
        return RedirectResponse(url="/admin/login", status_code=302)
    try:
        read_signed_value(raw_token, secret_key=settings.app_secret_key)
    except InvalidSessionTokenError:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin_query_jobs.html",
        context=_base_context(request, current_user),
    )


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_gate_page(
    request: Request,
    current_user: User = Depends(require_current_user),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin_gate.html",
        context=_base_context(request, current_user),
    )
