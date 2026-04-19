from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
ROOT = Path.home()
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import (
    attach_account_ids,
    build_promote_summary_payload,
    evaluate_promotion_batch,
    load_main_rows,
    load_sheet_rows,
    render_promote_review_markdown,
    WorkbookLockError,
)
from shared.static_pool import write_back_promotion_results

VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"
MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
MAIN_SHARED_XLSX = VAULT / "内部运营-静态潜客池-共享版.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
GOV_XLSX = VAULT / "治理与证据.xlsx"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generic promote evaluation entry for the static pool.")
    parser.add_argument("--config-file", help="Optional JSON batch config file.")
    parser.add_argument("--enrich-result-file", help="Optional enrich result JSON to consume before promotion evaluation.")
    parser.add_argument("--account-id", action="append", default=[], help="Specific account IDs to evaluate.")
    parser.add_argument("--from-level", help="Current level to filter, for example L5.")
    parser.add_argument("--target-level", help="Target level for this batch, for example L3.")
    parser.add_argument("--track", help="Track filter, for example 零售消费.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of accounts to include.")
    parser.add_argument("--output-file", help="Where to write the promotion evaluation report.")
    parser.add_argument("--report-only", action="store_true", help="Only build the promotion report, do not write back.")
    parser.add_argument("--write-back", action="store_true", help="Write allow results back to the shared fact layer.")
    return parser


def load_primary_main_rows() -> list[dict[str, object]]:
    return load_main_rows(MAIN_XLSX, "accounts_main")


def _clean(value: object) -> str:
    return str(value or "").strip()


def load_enrich_payload(path: str | None) -> dict[str, object]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _resolve_optional_path(path: str | None) -> Path | None:
    if not path:
        return None
    raw = Path(path)
    if raw.is_absolute():
        return raw
    return (WORKSPACE / raw).resolve()


def _load_optional_patch(path: str | None) -> dict[str, object]:
    resolved = _resolve_optional_path(path)
    if not resolved or not resolved.exists():
        return {}
    return json.loads(resolved.read_text(encoding="utf-8"))


def _normalize_shared_main_row(shared_row: dict[str, object], *, account_id: str) -> dict[str, object]:
    return {
        "account_id": account_id,
        "account_canonical_name": shared_row.get("公司主体"),
        "primary_track": shared_row.get("主线"),
        "persona_tag": shared_row.get("业务形态画像"),
        "secondary_persona_tags": shared_row.get("辅助画像标签") or shared_row.get("次级画像") or "",
        "公司产品与服务概述": shared_row.get("公司产品与服务概述"),
        "商业模式概述": shared_row.get("商业模式概述"),
        "admission_reason_summary": shared_row.get("一话入池理由"),
        "validation_gap": shared_row.get("待验证项"),
        "信息扎实度": shared_row.get("信息扎实度"),
        "ICP匹配概率": shared_row.get("ICP匹配概率"),
        "静态潜客记录成熟度": shared_row.get("静态潜客记录成熟度"),
        "review_status": "pending_review",
        "knowledge_asset_refs": shared_row.get("主要知识资产引用"),
        "talk_track_refs": shared_row.get("主要切入话术引用"),
    }


def supplement_missing_main_rows_from_shared(
    main_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    *,
    account_ids: list[str],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    wanted_ids = {_clean(value) for value in account_ids if _clean(value)}
    if not wanted_ids:
        return main_rows, {"requested": 0, "existing": 0, "added_from_shared": 0, "still_missing": 0}
    existing_ids = {_clean(row.get("account_id")) for row in main_rows if _clean(row.get("account_id"))}
    missing_ids = wanted_ids - existing_ids
    if not missing_ids:
        return main_rows, {"requested": len(wanted_ids), "existing": len(existing_ids & wanted_ids), "added_from_shared": 0, "still_missing": 0}

    profile_name_to_id = {
        _clean(row.get("account_canonical_name")): _clean(row.get("account_id"))
        for row in profile_rows
        if _clean(row.get("account_canonical_name")) and _clean(row.get("account_id"))
    }
    _shared_headers, shared_rows = load_sheet_rows(MAIN_SHARED_XLSX, "全量主表")
    for shared_row in shared_rows:
        account_name = _clean(shared_row.get("公司主体"))
        if not account_name:
            continue
        account_id = profile_name_to_id.get(account_name, "")
        if not account_id or account_id not in missing_ids:
            continue
        main_rows.append(_normalize_shared_main_row(shared_row, account_id=account_id))
        missing_ids.discard(account_id)
        if not missing_ids:
            break

    return main_rows, {
        "requested": len(wanted_ids),
        "existing": len((wanted_ids - missing_ids)),
        "added_from_shared": len((wanted_ids - existing_ids) - missing_ids),
        "still_missing": len(missing_ids),
    }


def resolve_output_file(path: str | None, batch_hint: str) -> Path:
    if path:
        return Path(path)
    base = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{batch_hint}.json"


def optional_output_path(path: str | None) -> Path | None:
    if not path:
        return None
    return Path(path)


def apply_fact_patch(
    main_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    evidence_rows: list[dict[str, object]],
    patch: dict[str, object],
) -> tuple[int, int]:
    accounts = patch.get("accounts")
    if not isinstance(accounts, list):
        return 0, 0
    main_by_id = {_clean(row.get("account_id")): row for row in main_rows if _clean(row.get("account_id"))}
    profile_by_id = {_clean(row.get("account_id")): row for row in profile_rows if _clean(row.get("account_id"))}
    main_by_name = {_clean(row.get("account_canonical_name")): row for row in main_rows if _clean(row.get("account_canonical_name"))}
    profile_by_name = {_clean(row.get("account_canonical_name")): row for row in profile_rows if _clean(row.get("account_canonical_name"))}
    profile_updated = 0
    evidence_added = 0
    for item in accounts:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        account_name = _clean(item.get("account_name"))
        main_row = main_by_id.get(account_id) or main_by_name.get(account_name)
        profile_row = profile_by_id.get(account_id) or profile_by_name.get(account_name)
        profile_fields = item.get("profile_fields")
        if isinstance(profile_fields, dict) and profile_row is not None:
            for key, value in profile_fields.items():
                profile_row[key] = value
            profile_updated += 1
        main_fields = item.get("main_fields")
        if isinstance(main_fields, dict) and main_row is not None:
            for key, value in main_fields.items():
                main_row[key] = value
        for field in ("official_source_count", "high_confidence_source_count", "primary_source_types", "primary_source_refs"):
            if field in item and profile_row is not None:
                profile_row[field] = item.get(field)
        rows = item.get("evidence_rows")
        if not isinstance(rows, list):
            continue
        for ev in rows:
            if not isinstance(ev, dict):
                continue
            copied = dict(ev)
            copied.setdefault("account_id", account_id)
            evidence_rows.append(copied)
            evidence_added += 1
    return profile_updated, evidence_added


def apply_queue_patch(queue_rows: list[dict[str, object]], patch: dict[str, object]) -> int:
    accounts = patch.get("accounts")
    if not isinstance(accounts, list):
        return 0
    created = 0
    for item in accounts:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        queue_type = _clean(item.get("queue_type"))
        if not account_id or not queue_type:
            continue
        exists = False
        for row in queue_rows:
            if _clean(row.get("account_id")) != account_id:
                continue
            if _clean(row.get("queue_type")) != queue_type:
                continue
            if _clean(row.get("status")) in {"", "open", "in_progress"}:
                exists = True
                break
        if exists:
            continue
        queue_rows.append(
            {
                "queue_item_id": _clean(item.get("queue_item_id")) or f"patch_{account_id}_{queue_type}",
                "queue_type": queue_type,
                "account_id": account_id,
                "priority": _clean(item.get("priority")) or "P1",
                "status": _clean(item.get("status")) or "open",
                "owner": _clean(item.get("owner")) or "codex",
                "note": _clean(item.get("note")),
                "created_at": _clean(item.get("created_at")),
                "resolved_at": "",
            }
        )
        created += 1
    return created


def apply_auto_promotion_review_queue(queue_rows: list[dict[str, object]], account_ids: list[str]) -> int:
    created = 0
    today = ""
    for account_id in account_ids:
        account_id = _clean(account_id)
        if not account_id:
            continue
        exists = False
        for row in queue_rows:
            if _clean(row.get("account_id")) != account_id:
                continue
            if _clean(row.get("queue_type")) != "promotion_review":
                continue
            if _clean(row.get("status")) in {"", "open", "in_progress"}:
                exists = True
                break
        if exists:
            continue
        queue_rows.append(
            {
                "queue_item_id": f"auto_{account_id}_promotion_review",
                "queue_type": "promotion_review",
                "account_id": account_id,
                "priority": "P1",
                "status": "open",
                "owner": "codex",
                "note": "auto_opened_by_execution_batch",
                "created_at": today,
                "resolved_at": "",
            }
        )
        created += 1
    return created


def overlay_enrich_results(
    main_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    enrich_results: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    main_by_id = {str(row.get("account_id") or "").strip(): dict(row) for row in main_rows if row.get("account_id")}
    profile_by_id = {str(row.get("account_id") or "").strip(): dict(row) for row in profile_rows if row.get("account_id")}
    for item in enrich_results:
        account_id = _clean(item.get("account_id"))
        if not account_id:
            continue
        main_row = dict(main_by_id.get(account_id) or {})
        profile_row = dict(profile_by_id.get(account_id) or {})
        for row in (main_row, profile_row):
            if not row:
                continue
            row["primary_track"] = item.get("primary_track") or row.get("primary_track")
            row["persona_tag"] = item.get("persona_tag") or row.get("persona_tag")
            row["secondary_persona_tags"] = ",".join(item.get("secondary_persona_tags") or [])
            row["knowledge_asset_refs"] = ",".join(item.get("knowledge_asset_refs") or [])
            row["talk_track_refs"] = ",".join(item.get("talk_track_refs") or [])
            row["validation_gap"] = item.get("validation_gap") or row.get("validation_gap")
            row["review_status"] = row.get("review_status") or item.get("review_status")
            row["静态潜客记录成熟度"] = item.get("suggested_maturity") or row.get("静态潜客记录成熟度")
            rewrite = item.get("rewrite_suggestion") if isinstance(item.get("rewrite_suggestion"), dict) else {}
            if rewrite.get("公司产品与服务概述") and not _clean(row.get("公司产品与服务概述")):
                row["公司产品与服务概述"] = rewrite.get("公司产品与服务概述")
            if rewrite.get("商业模式概述") and not _clean(row.get("商业模式概述")):
                row["商业模式概述"] = rewrite.get("商业模式概述")
            if rewrite.get("admission_reason_summary") and not _clean(row.get("admission_reason_summary")):
                row["admission_reason_summary"] = rewrite.get("admission_reason_summary")
        if main_row:
            main_by_id[account_id] = main_row
        if profile_row:
            profile_by_id[account_id] = profile_row
    return list(main_by_id.values()), list(profile_by_id.values())


def apply_enrich_guardrails(payload: dict[str, object], enrich_results: list[dict[str, object]]) -> None:
    enrich_by_id = {_clean(item.get("account_id")): item for item in enrich_results}
    batch_summary = payload.get("batch_summary") or {}
    for key in ("allow", "warn", "block"):
        batch_summary.setdefault(key, 0)
    recalculated = {"allow": 0, "warn": 0, "block": 0}
    for item in payload.get("results") or []:
        account_id = _clean(item.get("account_id"))
        enrich = enrich_by_id.get(account_id, {})
        gate = item.get("promotion_gate") or {}
        decision = _clean(gate.get("decision"))
        if enrich:
            gate["enrich_candidate_type"] = enrich.get("candidate_type")
            gate["enrich_ready_for_promote"] = enrich.get("enrich_ready_for_promote")
            gate["enrich_minimum_fact_status"] = enrich.get("minimum_fact_status")
            if (
                enrich.get("candidate_type") == "observation"
                or enrich.get("minimum_fact_status") == "fail"
                or not enrich.get("enrich_ready_for_promote")
            ) and decision == "allow":
                gate["decision"] = "block"
                gate["summary"] = "enrich 结果显示该对象仍未准备好进入 promote，程序已将 allow 降为 block。"
                gate.setdefault("blocking_issues", []).append(
                    {
                        "code": "enrich_not_ready",
                        "severity": "block",
                        "field_name": "enrich_ready_for_promote",
                        "message": "enrich 未通过，不能直接进入 allow。",
                    }
                )
                decision = "block"
        recalculated[decision] = recalculated.get(decision, 0) + 1
    payload["batch_summary"] = recalculated


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config: dict[str, object] = {}
    if args.config_file:
        config = json.loads(Path(args.config_file).read_text(encoding="utf-8"))
    config_output = config.get("output") or {}
    enrich_result_file = args.enrich_result_file or str(config.get("enrich_result_file") or "")
    enrich_payload = load_enrich_payload(enrich_result_file or None)
    enrich_results = list(enrich_payload.get("results") or [])
    fact_patch_payload = _load_optional_patch(str(config.get("fact_patch_file") or ""))
    queue_patch_payload = _load_optional_patch(str(config.get("queue_patch_file") or ""))

    main_rows = load_primary_main_rows()
    _profile_headers, profile_rows = load_sheet_rows(PROFILE_XLSX, "account_profiles")
    _queue_headers, queue_rows = load_sheet_rows(GOV_XLSX, "review_queue")
    _evidence_headers, evidence_rows = load_sheet_rows(GOV_XLSX, "evidence_log")
    main_rows = attach_account_ids(main_rows, profile_rows)
    patch_profile_updates = 0
    patch_evidence_added = 0
    patch_queue_created = 0
    if fact_patch_payload:
        patch_profile_updates, patch_evidence_added = apply_fact_patch(main_rows, profile_rows, evidence_rows, fact_patch_payload)
    if queue_patch_payload:
        patch_queue_created = apply_queue_patch(queue_rows, queue_patch_payload)
    if enrich_results:
        main_rows, profile_rows = overlay_enrich_results(main_rows, profile_rows, enrich_results)

    account_ids = args.account_id or list(config.get("account_ids") or []) or [
        _clean(item.get("account_id")) for item in enrich_results if _clean(item.get("account_id"))
    ]
    main_rows, main_coverage = supplement_missing_main_rows_from_shared(
        main_rows,
        profile_rows,
        account_ids=account_ids,
    )
    if bool(config.get("auto_open_promotion_review_for_selected")) and account_ids:
        patch_queue_created += apply_auto_promotion_review_queue(queue_rows, account_ids)
    from_level = args.from_level or str(config.get("from_level") or "")
    target_level = args.target_level or str(config.get("promote_target_level") or config.get("target_level") or "")
    track = args.track or str(config.get("track") or "")
    limit = args.limit if args.limit != 20 or not config.get("limit") else int(config.get("limit") or 20)
    output_file = args.output_file or str(config_output.get("promote_file") or config.get("output_file") or "")
    summary_file = str(config_output.get("summary_file") or config.get("summary_file") or "")
    review_file = str(config_output.get("review_file") or config.get("review_file") or "")
    output_path = resolve_output_file(output_file or None, str(config.get("batch_id") or "promote_static_pool_run"))

    payload = {
        "batch_id": str(config.get("batch_id") or output_path.stem),
        "goal": str(config.get("goal") or ""),
        "from_level": from_level,
        "target_level": target_level,
        "track": track,
        "write_back": {"enabled": False},
        "enrich_result_file": enrich_result_file,
        "selection": {
            "account_ids": account_ids,
            "limit": limit,
        },
    }
    payload.update(
        evaluate_promotion_batch(
            main_rows,
            profile_rows,
            evidence_rows,
            queue_rows,
            account_ids=account_ids,
            from_level=from_level,
            target_level=target_level,
            track=track,
            limit=limit,
        )
    )
    apply_guardrails = bool(config.get("apply_enrich_guardrails", True))
    if enrich_results and apply_guardrails:
        apply_enrich_guardrails(payload, enrich_results)
        payload["enrich_summary"] = {
            "result_count": len(enrich_results),
            "ready_for_promote": sum(1 for item in enrich_results if item.get("enrich_ready_for_promote")),
            "observation": sum(1 for item in enrich_results if item.get("candidate_type") == "observation"),
        }
    elif enrich_results:
        payload["enrich_summary"] = {
            "result_count": len(enrich_results),
            "ready_for_promote": sum(1 for item in enrich_results if item.get("enrich_ready_for_promote")),
            "observation": sum(1 for item in enrich_results if item.get("candidate_type") == "observation"),
            "guardrails_applied": False,
        }
    payload["patch_summary"] = {
        "fact_patch_file": str(config.get("fact_patch_file") or ""),
        "queue_patch_file": str(config.get("queue_patch_file") or ""),
        "profile_updates": patch_profile_updates,
        "evidence_rows_added": patch_evidence_added,
        "queue_rows_added": patch_queue_created,
        "main_coverage": main_coverage,
    }
    if (args.write_back or bool(config.get("write_back"))) and not args.report_only:
        lock_timeout = float(config.get("workbook_lock_timeout_seconds") or 0.0)
        try:
            payload["write_back"] = write_back_promotion_results(
                payload["results"],
                batch_id=payload["batch_id"],
                profile_xlsx=PROFILE_XLSX,
                main_xlsx=MAIN_XLSX,
                main_shared_xlsx=MAIN_SHARED_XLSX,
                gov_xlsx=GOV_XLSX,
                lock_timeout_seconds=lock_timeout,
            )
        except WorkbookLockError as exc:
            raise SystemExit(str(exc)) from exc
    else:
        payload["write_back"] = {
            "enabled": False,
            "workbook_lock_acquired": False,
            "workbook_lock_wait_seconds": 0.0,
            "workbook_integrity_check": {},
        }

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path = optional_output_path(summary_file)
    if summary_path:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_payload = build_promote_summary_payload(
            config,
            payload,
            config_path=str(args.config_file or ""),
            promote_result_path=str(output_path),
        )
        summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path = optional_output_path(review_file)
    if review_path:
        review_path.parent.mkdir(parents=True, exist_ok=True)
        if not summary_path:
            summary_payload = build_promote_summary_payload(
                config,
                payload,
                config_path=str(args.config_file or ""),
                promote_result_path=str(output_path),
            )
        review_path.write_text(render_promote_review_markdown(summary_payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_file": str(output_path),
                "result_count": len(payload["results"]),
                "batch_summary": payload["batch_summary"],
                "write_back": payload.get("write_back") or {},
                "summary_file": str(summary_path) if summary_path else "",
                "review_file": str(review_path) if review_path else "",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
