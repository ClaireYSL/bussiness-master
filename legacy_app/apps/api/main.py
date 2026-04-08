from pathlib import Path

from fastapi import FastAPI, Response

from apps.api.routes import admin_router, auth_router, pages_router, query_jobs_router, research_router, tungee_router
from shared.config import get_settings

settings = get_settings()
STATIC_DIR = Path("apps/api/static")
APP_CSS = (STATIC_DIR / "app.css").read_text(encoding="utf-8")
APP_JS = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

app = FastAPI(title=settings.app_name)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(query_jobs_router)
app.include_router(research_router)
app.include_router(tungee_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/static/app.css")
async def static_app_css() -> Response:
    return Response(content=APP_CSS, media_type="text/css; charset=utf-8")


@app.get("/static/app.js")
async def static_app_js() -> Response:
    return Response(content=APP_JS, media_type="application/javascript; charset=utf-8")
