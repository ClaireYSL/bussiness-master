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
DEFAULT_M35 = "deliveries/archive/milestones/milestone35r_field_governance/milestone35r_field_governance_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone36r_manual_field_review"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 36R-人工字段复核与共享占位口径-v1.md"

CANONICAL_FIELD_REVIEW_RULES = {
    "account_canonical_name": "公司主体名称差异。默认主表为 source of truth，但需人工确认是否为简称、曾用名或误配。",
    "信息扎实度": "质量等级差异。不得自动覆盖，应确认新旧证据口径和最近写回来源。",
    "admission_reason_summary": "入池理由差异。主表通常更新，但需要确认是否丢失档案中的有效判断。",
    "公司产品与服务概述": "产品服务描述差异。需要确认主表是否更具体、档案是否保留补充细节。",
    "商业模式概述": "商业模式描述差异。需要确认是否存在画像或经营模式口径变化。",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M36R manual field review and shared placeholder policy package.")
    parser.add_argument("--m33-package", default=DEFAULT_M33)
    parser.add_argument("--m35-package", default=DEFAULT_M35)
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


def _recommend_action(field: str, main_value: str, profile_value: str) -> str:
    if field == "account_canonical_name":
        return "confirm_main_canonical_name_then_sync_profile_or_record_alias"
    if len(main_value) > len(profile_value) and profile_value and profile_value in main_value:
        return "likely_sync_main_to_profile_after_human_confirm"
    if field in {"admission_reason_summary", "公司产品与服务概述", "商业模式概述"} and len(main_value) > len(profile_value):
        return "review_main_more_specific_then_sync_if_accepted"
    return "manual_compare_before_sync"


def _build_manual_review_items(profile_mismatches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for account in profile_mismatches:
        for diff in account.get("diffs") or []:
            field = _clean(diff.get("field"))
            main_value = _clean(diff.get("main_value"))
            profile_value = _clean(diff.get("profile_value"))
            items.append(
                {
                    "review_item_id": f"m36r_{_clean(account.get('account_id'))}_{field}",
                    "account_id": _clean(account.get("account_id")),
                    "account_name": _clean(account.get("account_name")),
                    "field": field,
                    "main_value": main_value,
                    "profile_value": profile_value,
                    "review_rule": CANONICAL_FIELD_REVIEW_RULES.get(field, "字段口径差异，需人工确认。"),
                    "recommended_action": _recommend_action(field, main_value, profile_value),
                    "allowed_decisions": [
                        "sync_main_to_profile",
                        "keep_profile",
                        "merge_values",
                        "record_alias_only",
                        "hold_pending_more_evidence",
                    ],
                    "default_decision": "hold_pending_more_evidence",
                    "writeback_status": "not_executed",
                }
            )
    return items


def _build_candidate_patch(review_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in review_items:
        action = item["recommended_action"]
        if action not in {"likely_sync_main_to_profile_after_human_confirm", "review_main_more_specific_then_sync_if_accepted", "confirm_main_canonical_name_then_sync_profile_or_record_alias"}:
            continue
        account_id = item["account_id"]
        entry = grouped.setdefault(
            account_id,
            {
                "account_id": account_id,
                "account_name": item["account_name"],
                "mode": "requires_human_confirmation_no_write",
                "proposed_updates": {},
                "proposed_alias_note": "",
            },
        )
        if item["field"] == "account_canonical_name":
            entry["proposed_updates"][item["field"]] = item["main_value"]
            entry["proposed_alias_note"] = f"原档案名称 `{item['profile_value']}` 可作为简称/别名候选，需人工确认是否保留。"
        else:
            entry["proposed_updates"][item["field"]] = item["main_value"]
    return list(grouped.values())


def _build_shared_placeholder_policy(shared_items: list[dict[str, Any]]) -> dict[str, Any]:
    field_distribution = dict(Counter(_clean(item.get("shared_field")) for item in shared_items if _clean(item.get("shared_field"))))
    account_count = len({_clean(item.get("account_id")) for item in shared_items if _clean(item.get("account_id"))})
    return {
        "policy_id": "milestone36r_shared_placeholder_policy_v1",
        "status": "active_for_audit_interpretation",
        "shared_is_generated_view": True,
        "main_should_not_be_overwritten_by_shared_placeholder": True,
        "placeholder_values": ["待补充", "待验证", "pending", "PENDING"],
        "applies_to_fields": sorted(field_distribution),
        "account_count": account_count,
        "diff_count": len(shared_items),
        "field_distribution": field_distribution,
        "interpretation": [
            "共享版中的 `待补充` 表示消费视图对缺口的显式占位，不表示主表字段错误。",
            "共享版可以从 profile 或投影规则补充消费字段，但不得反向覆盖主表。",
            "若需要消除审计噪声，应调整审计规则识别 generated_view_placeholder，而不是把主表空字段批量写成待补充。",
        ],
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 36R-人工字段复核与共享占位口径-v1",
        "",
        "## 摘要",
        "",
        f"- 待人工复核账户数：`{summary['manual_review_account_count']}`",
        f"- 待人工复核字段数：`{summary['manual_review_item_count']}`",
        f"- 候选人工确认后 patch 账户数：`{summary['candidate_patch_account_count']}`",
        f"- 共享占位解释 diff：`{summary['shared_placeholder_diff_count']}`",
        f"- 共享占位涉及账户数：`{summary['shared_placeholder_account_count']}`",
        f"- 工作簿完整性：`{summary['workbook_integrity_ok']}`",
        "",
        "## 结论",
        "",
        "- 剩余 profile 差异不再属于空字段补齐，必须人工确认后才能写回。",
        "- 共享版 `待补充` 是生成视图占位，不应反向覆盖主表。",
        "- 本包不真实写入工作簿、知识资产或画像注册表。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    m33 = _load_json(args.m33_package)
    m35 = _load_json(args.m35_package)
    profile_mismatches = (m33.get("level_mismatch_report") or {}).get("profile_mismatches") or []
    shared_placeholder_items = (m35.get("shared_generated_view_explanations") or {}).get("items") or []
    review_items = _build_manual_review_items(profile_mismatches)
    candidate_patch = _build_candidate_patch(review_items)
    shared_policy = _build_shared_placeholder_policy(shared_placeholder_items)
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["main_shared"], pool["governance"]], deep_scan=True)
    summary = {
        "manual_review_account_count": len({_clean(item.get("account_id")) for item in review_items if _clean(item.get("account_id"))}),
        "manual_review_item_count": len(review_items),
        "candidate_patch_account_count": len(candidate_patch),
        "candidate_patch_field_count": sum(len(item.get("proposed_updates") or {}) for item in candidate_patch),
        "manual_review_field_distribution": dict(Counter(item["field"] for item in review_items)),
        "shared_placeholder_account_count": shared_policy["account_count"],
        "shared_placeholder_diff_count": shared_policy["diff_count"],
        "shared_placeholder_field_distribution": shared_policy["field_distribution"],
        "workbook_integrity_ok": bool(integrity.get("ok")),
        "true_writeback_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone36r_manual_field_review_package_v1",
        "generated_at": _now(),
        "static_pool_root": str(pool["root"]),
        "policy": {
            "manual_confirmation_required_for_profile_differences": True,
            "shared_placeholder_is_not_main_error": True,
            "no_true_writeback": True,
            "no_knowledge_asset_write": True,
            "no_persona_registry_write": True,
        },
        "summary": summary,
        "manual_review_queue": {
            "batch_id": "milestone36r_manual_field_review_queue_v1",
            "items": review_items,
        },
        "candidate_patch_after_manual_confirmation": {
            "batch_id": "milestone36r_candidate_patch_after_manual_confirmation_v1",
            "mode": "requires_human_confirmation_no_write",
            "accounts": candidate_patch,
        },
        "shared_placeholder_policy": shared_policy,
        "workbook_integrity": integrity,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone36r_manual_field_review_package_v1.json", payload)
    _write_json(output_dir / "milestone36r_manual_field_review_queue_v1.json", payload["manual_review_queue"])
    _write_json(output_dir / "milestone36r_candidate_patch_after_manual_confirmation_v1.json", payload["candidate_patch_after_manual_confirmation"])
    _write_json(output_dir / "milestone36r_shared_placeholder_policy_v1.json", shared_policy)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone36r_manual_field_review_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = (
        summary["manual_review_account_count"] == 5
        and summary["manual_review_item_count"] == 15
        and summary["shared_placeholder_diff_count"] == 131
        and summary["workbook_integrity_ok"]
        and not summary["true_writeback_enabled"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
