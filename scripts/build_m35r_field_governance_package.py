from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import check_workbook_integrity, resolve_static_pool_paths


DEFAULT_M33 = "deliveries/archive/milestones/milestone33r_workbook_governance_audit/milestone33r_workbook_governance_audit_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone35r_field_governance"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 35R-字段级差异治理准入包-v1.md"

PROFILE_SAFE_FROM_MAIN_FIELDS = {
    "信息扎实度",
    "ICP匹配概率",
    "admission_reason_summary",
    "公司产品与服务概述",
    "商业模式概述",
}
PROFILE_REVIEW_FIELDS = {"account_canonical_name", "primary_track", "persona_tag", "静态潜客记录成熟度"}
SHARED_PLACEHOLDER_VALUES = {"待补充", "待验证", "pending", "PENDING"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M35R field-level governance package without mutating workbooks.")
    parser.add_argument("--m33-package", default=DEFAULT_M33)
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


def _classify_profile_mismatch(item: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    safe_updates: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []
    for diff in item.get("diffs") or []:
        field = _clean(diff.get("field"))
        main_value = _clean(diff.get("main_value"))
        profile_value = _clean(diff.get("profile_value"))
        base = {
            "account_id": _clean(item.get("account_id")),
            "account_name": _clean(item.get("account_name")),
            "field": field,
            "main_value": main_value,
            "profile_value": profile_value,
        }
        if field in PROFILE_SAFE_FROM_MAIN_FIELDS and main_value and not profile_value:
            safe_updates.append({**base, "recommended_action": "sync_main_to_profile"})
        elif field in PROFILE_REVIEW_FIELDS:
            review_items.append({**base, "recommended_action": "manual_review_identity_or_core_status"})
        else:
            review_items.append({**base, "recommended_action": "manual_review_before_sync"})
    return safe_updates, review_items


def _classify_shared_mismatch(item: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    expected_generated: list[dict[str, Any]] = []
    safe_regenerate: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []
    for diff in item.get("diffs") or []:
        main_field = _clean(diff.get("main_field"))
        shared_field = _clean(diff.get("shared_field"))
        main_value = _clean(diff.get("main_value"))
        shared_value = _clean(diff.get("shared_value"))
        base = {
            "account_id": _clean(item.get("account_id")),
            "account_name": _clean(item.get("account_name")),
            "main_field": main_field,
            "shared_field": shared_field,
            "main_value": main_value,
            "shared_value": shared_value,
        }
        if not main_value and shared_value in SHARED_PLACEHOLDER_VALUES:
            expected_generated.append({**base, "classification": "generated_view_placeholder_not_main_error"})
        elif main_value and not shared_value:
            safe_regenerate.append({**base, "recommended_action": "regenerate_shared_from_main"})
        elif not main_value and shared_value:
            expected_generated.append({**base, "classification": "generated_view_profile_or_placeholder_enrichment"})
        else:
            review_items.append({**base, "recommended_action": "manual_review_shared_projection_rule"})
    return expected_generated, safe_regenerate, review_items


def _build_profile_patch(profile_mismatches: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    updates_by_account: dict[str, dict[str, Any]] = {}
    review_items: list[dict[str, Any]] = []
    for item in profile_mismatches:
        safe_updates, reviews = _classify_profile_mismatch(item)
        review_items.extend(reviews)
        for update in safe_updates:
            account_id = update["account_id"]
            account = updates_by_account.setdefault(
                account_id,
                {
                    "account_id": account_id,
                    "account_name": update["account_name"],
                    "updates": {},
                    "source": "main_to_profile_safe_blank_fill",
                    "writeback_status": "not_executed",
                },
            )
            account["updates"][update["field"]] = update["main_value"]
    return list(updates_by_account.values()), review_items


def _build_shared_plan(shared_mismatches: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    expected: list[dict[str, Any]] = []
    safe_regenerate: list[dict[str, Any]] = []
    review_items: list[dict[str, Any]] = []
    for item in shared_mismatches:
        item_expected, item_safe, item_review = _classify_shared_mismatch(item)
        expected.extend(item_expected)
        safe_regenerate.extend(item_safe)
        review_items.extend(item_review)
    return expected, safe_regenerate, review_items


def _counter_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(Counter(_clean(item.get(key)) for item in items if _clean(item.get(key))))


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 35R-字段级差异治理准入包-v1",
        "",
        "## 摘要",
        "",
        f"- profile mismatch 对象：`{summary['source_profile_mismatch_account_count']}`，diff：`{summary['source_profile_diff_count']}`",
        f"- 可安全从主表补 profile 的对象：`{summary['safe_profile_patch_account_count']}`，字段更新：`{summary['safe_profile_patch_field_count']}`",
        f"- 需人工复核 profile 字段差异：`{summary['profile_manual_review_item_count']}`",
        f"- shared mismatch 对象：`{summary['source_shared_mismatch_account_count']}`，diff：`{summary['source_shared_diff_count']}`",
        f"- 共享版可解释占位/补充差异：`{summary['shared_expected_generated_diff_count']}`",
        f"- 共享版需人工复核差异：`{summary['shared_manual_review_item_count']}`",
        f"- 工作簿完整性：`{summary['workbook_integrity_ok']}`",
        "",
        "## 判断",
        "",
        "- M34R 已解决三表行级覆盖；M35R 只处理字段级口径。",
        "- profile 中主表已有、档案为空的核心摘要字段，可作为安全补齐候选。",
        "- 共享版是投影视图，`待补充` 或来自档案的补充值不应反向覆盖主表。",
        "- 本包不真实写入工作簿；真实字段修复需单独确认。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    m33 = _load_json(args.m33_package)
    report = m33.get("level_mismatch_report") or {}
    profile_mismatches = report.get("profile_mismatches") or []
    shared_mismatches = report.get("shared_mismatches") or []

    profile_patch, profile_review = _build_profile_patch(profile_mismatches)
    shared_expected, shared_safe_regenerate, shared_review = _build_shared_plan(shared_mismatches)
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["main_shared"], pool["governance"]], deep_scan=True)

    profile_diff_count = sum(len(item.get("diffs") or []) for item in profile_mismatches)
    shared_diff_count = sum(len(item.get("diffs") or []) for item in shared_mismatches)
    safe_profile_field_count = sum(len(item.get("updates") or {}) for item in profile_patch)
    summary = {
        "source_profile_mismatch_account_count": len(profile_mismatches),
        "source_profile_diff_count": profile_diff_count,
        "safe_profile_patch_account_count": len(profile_patch),
        "safe_profile_patch_field_count": safe_profile_field_count,
        "profile_manual_review_item_count": len(profile_review),
        "source_shared_mismatch_account_count": len(shared_mismatches),
        "source_shared_diff_count": shared_diff_count,
        "shared_expected_generated_diff_count": len(shared_expected),
        "shared_safe_regenerate_diff_count": len(shared_safe_regenerate),
        "shared_manual_review_item_count": len(shared_review),
        "profile_patch_field_distribution": dict(Counter(field for item in profile_patch for field in (item.get("updates") or {}))),
        "profile_manual_review_field_distribution": _counter_by(profile_review, "field"),
        "shared_expected_field_distribution": _counter_by(shared_expected, "shared_field"),
        "shared_manual_review_field_distribution": _counter_by(shared_review, "shared_field"),
        "workbook_integrity_ok": bool(integrity.get("ok")),
        "true_writeback_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone35r_field_governance_package_v1",
        "generated_at": _now(),
        "static_pool_root": str(pool["root"]),
        "policy": {
            "main_remains_source_of_truth_for_account_identity": True,
            "profile_safe_fill_only_when_profile_blank_and_main_nonempty": True,
            "shared_is_generated_view_no_reverse_overwrite": True,
            "true_writeback_enabled": False,
            "requires_user_confirmation_for_real_field_sync": True,
        },
        "summary": summary,
        "safe_profile_patch": {
            "batch_id": "milestone35r_safe_profile_patch_v1",
            "mode": "candidate_only_no_write",
            "accounts": profile_patch,
        },
        "profile_manual_review_queue": {
            "batch_id": "milestone35r_profile_manual_review_queue_v1",
            "items": profile_review,
        },
        "shared_generated_view_explanations": {
            "batch_id": "milestone35r_shared_generated_view_explanations_v1",
            "items": shared_expected,
        },
        "shared_safe_regenerate_candidates": {
            "batch_id": "milestone35r_shared_safe_regenerate_candidates_v1",
            "items": shared_safe_regenerate,
        },
        "shared_manual_review_queue": {
            "batch_id": "milestone35r_shared_manual_review_queue_v1",
            "items": shared_review,
        },
        "workbook_integrity": integrity,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone35r_field_governance_package_v1.json", payload)
    _write_json(output_dir / "milestone35r_safe_profile_patch_v1.json", payload["safe_profile_patch"])
    _write_json(output_dir / "milestone35r_profile_manual_review_queue_v1.json", payload["profile_manual_review_queue"])
    _write_json(output_dir / "milestone35r_shared_generated_view_explanations_v1.json", payload["shared_generated_view_explanations"])
    _write_json(output_dir / "milestone35r_shared_safe_regenerate_candidates_v1.json", payload["shared_safe_regenerate_candidates"])
    _write_json(output_dir / "milestone35r_shared_manual_review_queue_v1.json", payload["shared_manual_review_queue"])
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone35r_field_governance_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))

    ok = (
        summary["workbook_integrity_ok"]
        and summary["source_shared_mismatch_account_count"] == 68
        and summary["shared_manual_review_item_count"] == 0
        and not summary["true_writeback_enabled"]
        and not summary["knowledge_asset_write_enabled"]
        and not summary["persona_registry_write_enabled"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
