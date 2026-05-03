from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import check_workbook_integrity, resolve_static_pool_paths


DEFAULT_M36 = "deliveries/archive/milestones/milestone36r_manual_field_review/milestone36r_manual_field_review_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone37r_final_field_confirmation"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 37R-最终字段确认包-v1.md"

DECISION_OPTIONS = [
    "sync_main_to_profile",
    "keep_profile",
    "merge_values",
    "record_alias_only",
    "hold_pending_more_evidence",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M37R final human field confirmation package without mutating workbooks.")
    parser.add_argument("--m36-package", default=DEFAULT_M36)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: object) -> str:
    return str(value or "").strip()


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def _suggest_default_decision(item: dict[str, Any]) -> str:
    field = _clean(item.get("field"))
    action = _clean(item.get("recommended_action"))
    main_value = _clean(item.get("main_value"))
    profile_value = _clean(item.get("profile_value"))
    if field == "account_canonical_name":
        return "record_alias_only"
    if action in {"likely_sync_main_to_profile_after_human_confirm", "review_main_more_specific_then_sync_if_accepted"} and len(main_value) >= len(profile_value):
        return "sync_main_to_profile"
    return "hold_pending_more_evidence"


def _build_confirmation_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        suggested = _suggest_default_decision(item)
        rows.append(
            {
                "review_item_id": item.get("review_item_id"),
                "account_id": item.get("account_id"),
                "account_name": item.get("account_name"),
                "field": item.get("field"),
                "main_value": item.get("main_value"),
                "profile_value": item.get("profile_value"),
                "review_rule": item.get("review_rule"),
                "recommended_action": item.get("recommended_action"),
                "suggested_decision": suggested,
                "human_decision": "",
                "human_note": "",
                "allowed_decisions": " | ".join(DECISION_OPTIONS),
                "writeback_status": "not_executed",
            }
        )
    return rows


def _build_account_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_clean(row.get("account_id"))].append(row)
    summaries: list[dict[str, Any]] = []
    for account_id, items in sorted(grouped.items()):
        decisions = Counter(_clean(item.get("suggested_decision")) for item in items)
        summaries.append(
            {
                "account_id": account_id,
                "account_name": items[0].get("account_name"),
                "review_item_count": len(items),
                "fields": "、".join(_clean(item.get("field")) for item in items),
                "suggested_decision_distribution": dict(decisions),
                "requires_human_confirmation": True,
            }
        )
    return summaries


def _build_writeback_readiness(rows: list[dict[str, Any]], candidate_patch_accounts: list[dict[str, Any]]) -> dict[str, Any]:
    suggested_sync_items = [row for row in rows if row.get("suggested_decision") == "sync_main_to_profile"]
    alias_items = [row for row in rows if row.get("suggested_decision") == "record_alias_only"]
    hold_items = [row for row in rows if row.get("suggested_decision") == "hold_pending_more_evidence"]
    return {
        "batch_id": "milestone37r_writeback_readiness_after_human_confirmation_v1",
        "mode": "not_ready_until_human_decision_filled",
        "candidate_patch_account_count_from_m36": len(candidate_patch_accounts),
        "suggested_sync_item_count": len(suggested_sync_items),
        "suggested_alias_item_count": len(alias_items),
        "suggested_hold_item_count": len(hold_items),
        "required_before_true_writeback": [
            "human_decision 必须填写，且只能使用 allowed_decisions 中的值。",
            "account_canonical_name 不直接覆盖；默认作为 alias 记录候选处理。",
            "只有 human_decision=sync_main_to_profile 或 merge_values 的字段才能进入最终写回 patch。",
            "真实写回前必须重新读取当前 profile，确认目标字段未发生漂移。",
        ],
        "true_writeback_enabled": False,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 37R-最终字段确认包-v1",
        "",
        "## 摘要",
        "",
        f"- 待确认账户数：`{summary['confirmation_account_count']}`",
        f"- 待确认字段数：`{summary['confirmation_item_count']}`",
        f"- 建议同步主表到 profile：`{summary['suggested_sync_item_count']}`",
        f"- 建议记录别名：`{summary['suggested_alias_item_count']}`",
        f"- 建议暂挂补证：`{summary['suggested_hold_item_count']}`",
        f"- 共享版占位规则：`{summary['shared_placeholder_policy_status']}`",
        f"- 工作簿完整性：`{summary['workbook_integrity_ok']}`",
        "",
        "## 结论",
        "",
        "- 本包是最终人工确认入口，不真实写入工作簿。",
        "- 没有人工确认时，不生成 accepted/rejected，也不执行字段写回。",
        "- 公司主体名称差异默认不覆盖，先作为别名候选处理。",
        "- 共享版 `待补充` 是消费视图占位，不反向覆盖主表。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    m36 = _load_json(args.m36_package)
    review_items = ((m36.get("manual_review_queue") or {}).get("items") or [])
    candidate_patch_accounts = ((m36.get("candidate_patch_after_manual_confirmation") or {}).get("accounts") or [])
    shared_policy = m36.get("shared_placeholder_policy") or {}

    confirmation_rows = _build_confirmation_rows(review_items)
    account_summary = _build_account_summary(confirmation_rows)
    readiness = _build_writeback_readiness(confirmation_rows, candidate_patch_accounts)
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["main_shared"], pool["governance"]], deep_scan=True)

    output_dir = Path(args.output_dir)
    confirmation_csv = output_dir / "milestone37r_final_field_confirmation_template_v1.csv"
    csv_headers = [
        "review_item_id",
        "account_id",
        "account_name",
        "field",
        "main_value",
        "profile_value",
        "review_rule",
        "recommended_action",
        "suggested_decision",
        "human_decision",
        "human_note",
        "allowed_decisions",
        "writeback_status",
    ]
    _write_csv(confirmation_csv, confirmation_rows, csv_headers)

    suggested_counts = Counter(row["suggested_decision"] for row in confirmation_rows)
    summary = {
        "confirmation_account_count": len(account_summary),
        "confirmation_item_count": len(confirmation_rows),
        "candidate_patch_account_count_from_m36": len(candidate_patch_accounts),
        "suggested_sync_item_count": int(suggested_counts.get("sync_main_to_profile", 0)),
        "suggested_alias_item_count": int(suggested_counts.get("record_alias_only", 0)),
        "suggested_hold_item_count": int(suggested_counts.get("hold_pending_more_evidence", 0)),
        "shared_placeholder_policy_status": shared_policy.get("status", ""),
        "shared_placeholder_diff_count": int(shared_policy.get("diff_count") or 0),
        "confirmation_csv": str(confirmation_csv),
        "workbook_integrity_ok": bool(integrity.get("ok")),
        "true_writeback_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone37r_final_field_confirmation_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "static_pool_root": str(pool["root"]),
        "policy": {
            "requires_human_confirmation": True,
            "no_auto_accept_reject": True,
            "account_name_diff_defaults_to_alias_review": True,
            "shared_placeholder_not_main_error": True,
            "true_writeback_enabled": False,
        },
        "summary": summary,
        "account_summary": account_summary,
        "confirmation_template": {
            "csv_path": str(confirmation_csv),
            "rows": confirmation_rows,
        },
        "writeback_readiness_after_human_confirmation": readiness,
        "shared_placeholder_policy": shared_policy,
        "workbook_integrity": integrity,
    }
    _write_json(output_dir / "milestone37r_final_field_confirmation_package_v1.json", payload)
    _write_json(output_dir / "milestone37r_account_confirmation_summary_v1.json", {"batch_id": "milestone37r_account_confirmation_summary_v1", "items": account_summary})
    _write_json(output_dir / "milestone37r_writeback_readiness_after_human_confirmation_v1.json", readiness)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone37r_final_field_confirmation_package_v1.json"), "review_md": args.review_md, "confirmation_csv": str(confirmation_csv), "summary": summary}, ensure_ascii=False, indent=2))

    ok = (
        summary["confirmation_account_count"] == 5
        and summary["confirmation_item_count"] == 15
        and summary["shared_placeholder_diff_count"] == 131
        and summary["workbook_integrity_ok"]
        and not summary["true_writeback_enabled"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
