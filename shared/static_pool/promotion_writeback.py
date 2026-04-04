from __future__ import annotations

from typing import Any


def append_semicolon_note(existing: object, addition: str) -> str:
    current = str(existing or "").strip().strip("；")
    extra = str(addition or "").strip().strip("；")
    if not extra:
        return current
    if not current:
        return extra
    if extra in current:
        return current
    return f"{current}；{extra}"


def prepend_gap_once(existing: object, prefix: str) -> str:
    current = str(existing or "").strip()
    marker = str(prefix or "").strip()
    if not marker:
        return current
    if marker in current:
        return current
    return f"{marker}{current}" if current else marker


def ensure_evidence_row(
    ws: Any,
    header_index: dict[str, int],
    evidence_id: str,
    values: dict[str, object],
) -> bool:
    evidence_col = header_index["evidence_id"]
    for row in range(2, ws.max_row + 1):
        if str(ws.cell(row, evidence_col).value or "") == evidence_id:
            return False

    row_values = [values.get(header) for header in header_index]
    ws.append(row_values)
    return True


def apply_row_updates(
    ws: Any,
    header_index: dict[str, int],
    row_num: int,
    updates: dict[str, object],
) -> None:
    for key, value in updates.items():
        if key not in header_index:
            continue
        ws.cell(row_num, header_index[key]).value = value


def update_main_promotion_core(
    ws: Any,
    header_index: dict[str, int],
    row_num: int,
    *,
    maturity_level: str,
    source_note_suffix: str | None = None,
    validation_gap: str | None = None,
    extra_updates: dict[str, object] | None = None,
) -> None:
    updates = dict(extra_updates or {})
    updates["静态潜客记录成熟度"] = maturity_level
    if source_note_suffix and "source_note" in header_index:
        updates["source_note"] = append_semicolon_note(
            ws.cell(row_num, header_index["source_note"]).value,
            source_note_suffix,
        )
    if validation_gap is not None and "validation_gap" in header_index:
        updates["validation_gap"] = validation_gap
    apply_row_updates(ws, header_index, row_num, updates)


def update_profile_promotion_core(
    ws: Any,
    header_index: dict[str, int],
    row_num: int,
    *,
    maturity_level: str,
    profile_status: str | None = None,
    validation_gap: str | None = None,
    last_profiled_at: str | None = None,
    extra_updates: dict[str, object] | None = None,
) -> None:
    updates = dict(extra_updates or {})
    updates["静态潜客记录成熟度"] = maturity_level
    if "static_maturity_level" in header_index:
        updates["static_maturity_level"] = maturity_level
    if profile_status is not None and "profile_status" in header_index:
        updates["profile_status"] = profile_status
    if validation_gap is not None and "validation_gap" in header_index:
        updates["validation_gap"] = validation_gap
    if last_profiled_at is not None and "last_profiled_at" in header_index:
        updates["last_profiled_at"] = last_profiled_at
    apply_row_updates(ws, header_index, row_num, updates)


def resolve_open_queue_rows(
    ws: Any,
    header_index: dict[str, int],
    *,
    account_id: str,
    queue_type: str = "promotion_review",
    resolved_at: str | None = None,
    note_suffix: str | None = None,
) -> int:
    resolved = 0
    for row in range(2, ws.max_row + 1):
        row_account_id = str(ws.cell(row, header_index["account_id"]).value or "")
        row_queue_type = str(ws.cell(row, header_index["queue_type"]).value or "")
        row_status = str(ws.cell(row, header_index["status"]).value or "")
        if row_account_id != account_id or row_queue_type != queue_type or row_status != "open":
            continue
        ws.cell(row, header_index["status"]).value = "resolved"
        if resolved_at and "resolved_at" in header_index:
            ws.cell(row, header_index["resolved_at"]).value = resolved_at
        if note_suffix and "note" in header_index:
            note_cell = ws.cell(row, header_index["note"])
            note_cell.value = append_semicolon_note(note_cell.value, note_suffix)
        resolved += 1
    return resolved
