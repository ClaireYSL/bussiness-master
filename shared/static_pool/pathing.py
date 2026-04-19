from __future__ import annotations

import os
from pathlib import Path


def _env_path(key: str) -> Path | None:
    value = os.getenv(key, "").strip()
    if not value:
        return None
    return Path(value).expanduser().resolve()


def get_static_pool_root() -> Path:
    return _env_path("STATIC_POOL_ROOT") or (Path.home() / "Documents/Obsidian-Codex/潜客池")


def resolve_static_pool_paths() -> dict[str, Path]:
    root = get_static_pool_root()
    return {
        "root": root,
        "main": _env_path("STATIC_POOL_MAIN_FILE") or (root / "静态潜客主表.xlsx"),
        "main_shared": _env_path("STATIC_POOL_MAIN_SHARED_FILE") or (root / "内部运营-静态潜客池-共享版.xlsx"),
        "profile": _env_path("STATIC_POOL_PROFILE_FILE") or (root / "潜客档案库.xlsx"),
        "governance": _env_path("STATIC_POOL_GOVERNANCE_FILE") or (root / "治理与证据.xlsx"),
        "track_persona": _env_path("STATIC_POOL_TRACK_PERSONA_FILE") or (root / "主线与画像注册表.xlsx"),
        "knowledge_registry": _env_path("STATIC_POOL_KNOWLEDGE_REGISTRY_FILE") or (root / "知识资产注册表.xlsx"),
    }

