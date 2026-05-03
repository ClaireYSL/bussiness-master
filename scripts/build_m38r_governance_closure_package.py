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
DEFAULT_M37 = "deliveries/archive/milestones/milestone37r_final_field_confirmation/milestone37r_final_field_confirmation_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone38r_governance_closure"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 38R-三表治理闭环收口-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Close workbook governance loop without forcing low-value manual confirmations.")
    parser.add_argument("--m33-package", default=DEFAULT_M33)
    parser.add_argument("--m37-package", default=DEFAULT_M37)
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


def _closure_item(row: dict[str, Any]) -> dict[str, Any]:
    field = _clean(row.get("field"))
    suggested = _clean(row.get("suggested_decision"))
    if field == "account_canonical_name":
        closure_type = "accepted_alias_variance"
        rationale = "公司主体以主表为准；档案中的简称/旧称作为别名观察，不阻塞潜客池使用。"
    elif suggested == "sync_main_to_profile":
        closure_type = "accepted_profile_description_variance"
        rationale = "主表和档案均有可读信息，差异属于描述粒度或旧新口径差异；不影响画像匹配和核心可靠信息消费。"
    else:
        closure_type = "pending_evidence_non_blocking"
        rationale = "该字段保留待补证，但不影响三表行级一致性、画像匹配结论和当前共享消费。"
    return {
        "review_item_id": row.get("review_item_id"),
        "account_id": row.get("account_id"),
        "account_name": row.get("account_name"),
        "field": field,
        "main_value": row.get("main_value"),
        "profile_value": row.get("profile_value"),
        "suggested_decision": suggested,
        "closure_type": closure_type,
        "blocking_project_progress": False,
        "requires_immediate_writeback": False,
        "rationale": rationale,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 38R-三表治理闭环收口-v1",
        "",
        "## 摘要",
        "",
        f"- 三表行级治理状态：`{summary['row_level_governance_status']}`",
        f"- 剩余 profile 差异：`{summary['residual_profile_variance_item_count']}` 个字段 / `{summary['residual_profile_variance_account_count']}` 家",
        f"- 非阻塞差异：`{summary['non_blocking_variance_count']}`",
        f"- 治理阻塞项：`{summary['governance_blocker_count']}`",
        f"- 共享版占位解释：`{summary['shared_placeholder_diff_count']}` 个 diff，状态 `{summary['shared_placeholder_status']}`",
        f"- 工作簿完整性：`{summary['workbook_integrity_ok']}`",
        "",
        "## 产品判断",
        "",
        "- 不再要求用户逐字段确认剩余 5 家差异。",
        "- 剩余差异不影响核心目标：基于知识库和 ICP 找到匹配潜客，并提供核心可靠信息。",
        "- 三表治理主线从阻塞态转为常规维护态；下一步应回到潜客池质量、反馈和扩容。",
        "- 本包不写工作簿、不写知识资产、不改画像注册表。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    m33 = _load_json(args.m33_package)
    m37 = _load_json(args.m37_package)
    rows = ((m37.get("confirmation_template") or {}).get("rows") or [])
    closure_items = [_closure_item(row) for row in rows]
    closure_counts = Counter(item["closure_type"] for item in closure_items)
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["main_shared"], pool["governance"]], deep_scan=True)
    m33_summary = m33.get("summary") or {}
    m37_summary = m37.get("summary") or {}
    row_level_ok = (
        m33_summary.get("main_duplicate_account_id_count") == 0
        and m33_summary.get("main_not_in_profile_count") == 0
        and m33_summary.get("main_not_in_shared_count") == 0
        and m33_summary.get("shared_not_in_main_count") == 0
    )
    summary = {
        "row_level_governance_status": "closed" if row_level_ok else "needs_attention",
        "main_row_count": int(m33_summary.get("main_row_count") or 0),
        "profile_row_count": int(m33_summary.get("profile_row_count") or 0),
        "shared_row_count": int(m33_summary.get("shared_row_count") or 0),
        "residual_profile_variance_account_count": len({_clean(item.get("account_id")) for item in closure_items if _clean(item.get("account_id"))}),
        "residual_profile_variance_item_count": len(closure_items),
        "non_blocking_variance_count": sum(1 for item in closure_items if not item["blocking_project_progress"]),
        "governance_blocker_count": sum(1 for item in closure_items if item["blocking_project_progress"]),
        "closure_type_distribution": dict(closure_counts),
        "shared_placeholder_diff_count": int(m37_summary.get("shared_placeholder_diff_count") or 0),
        "shared_placeholder_status": "accepted_generated_view_placeholder",
        "project_can_continue_to_core_pipeline": row_level_ok,
        "workbook_integrity_ok": bool(integrity.get("ok")),
        "true_writeback_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone38r_governance_closure_package_v1",
        "generated_at": _now(),
        "static_pool_root": str(pool["root"]),
        "policy": {
            "do_not_force_low_value_manual_confirmation": True,
            "residual_profile_variance_is_non_blocking": True,
            "shared_placeholder_is_accepted_generated_view_behavior": True,
            "return_to_core_pipeline_after_closure": True,
            "true_writeback_enabled": False,
        },
        "summary": summary,
        "non_blocking_profile_variance_register": {
            "batch_id": "milestone38r_non_blocking_profile_variance_register_v1",
            "items": closure_items,
        },
        "recommended_next_stage": {
            "stage": "M39R_core_pipeline_resume",
            "goal": "回到可信画像匹配潜客池主线：复核当前 L3/L5 可消费状态、业务反馈输入和下一批扩容阈值。",
            "default_actions": [
                "不继续清理低价值字段差异。",
                "使用 M32R 反馈模板或当前 568 家底座重新生成项目级质量面板。",
                "确定下一批扩容或共享消费增强的质量阈值。",
            ],
        },
        "workbook_integrity": integrity,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone38r_governance_closure_package_v1.json", payload)
    _write_json(output_dir / "milestone38r_non_blocking_profile_variance_register_v1.json", payload["non_blocking_profile_variance_register"])
    _write_json(output_dir / "milestone38r_core_pipeline_resume_plan_v1.json", payload["recommended_next_stage"])
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone38r_governance_closure_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = (
        summary["row_level_governance_status"] == "closed"
        and summary["governance_blocker_count"] == 0
        and summary["project_can_continue_to_core_pipeline"]
        and summary["workbook_integrity_ok"]
        and not summary["true_writeback_enabled"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
