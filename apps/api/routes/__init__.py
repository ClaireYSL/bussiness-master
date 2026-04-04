from apps.api.routes.admin import router as admin_router
from apps.api.routes.auth import router as auth_router
from apps.api.routes.pages import router as pages_router
from apps.api.routes.query_jobs import router as query_jobs_router
from apps.api.routes.research import router as research_router
from apps.api.routes.tungee import router as tungee_router

__all__ = [
    "admin_router",
    "auth_router",
    "pages_router",
    "query_jobs_router",
    "research_router",
    "tungee_router",
]
