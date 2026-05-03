from __future__ import annotations

import os


LEGACY_WORKBOOK_WRITE_ENV = "STATIC_POOL_ALLOW_LEGACY_WORKBOOK_WRITE"
LEGACY_WORKBOOK_WRITE_TOKEN = "I_UNDERSTAND_LEGACY_WRITE"


def legacy_write_enabled(cli_override: bool) -> bool:
    return bool(cli_override) and os.getenv(LEGACY_WORKBOOK_WRITE_ENV, "").strip() == LEGACY_WORKBOOK_WRITE_TOKEN


def assert_legacy_workbook_write_allowed(*, cli_override: bool, context: str) -> None:
    if legacy_write_enabled(cli_override):
        return
    raise PermissionError(
        f"{context} blocked: old workbook write is legacy-only. "
        f"Pass --allow-legacy-workbook-write and set "
        f"{LEGACY_WORKBOOK_WRITE_ENV}={LEGACY_WORKBOOK_WRITE_TOKEN} to proceed."
    )
