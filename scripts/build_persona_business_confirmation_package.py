from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M20_SUMMARY = "deliveries/archive/milestones/milestone20_batch_intake_patch/milestone20_batch_intake_summary_v1.json"
DEFAULT_M20_PROMOTE = "deliveries/archive/milestones/milestone20_batch_intake_patch/milestone20_batch_intake_promote_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone21_persona_business_confirmation/milestone21_persona_business_confirmation_package_v1.json"
DEFAULT_TEMPLATE_JSON = "configs/execution_batches/milestone21_persona_business_confirmation_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 21-画像确认与业务价值准入包复盘-v1.md"

CONFIRMATION_OPTIONS = [
    "confirm_active_high_value",
    "confirm_active_low_priority",
    "keep_pending_need_business_context",
    "persona_adjust",
    "hold_not_icp",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M21 persona + business value confirmation package from M20 warn batch.")
    parser.add_argument("--m20-summary", default=DEFAULT_M20_SUMMARY)
    parser.add_argument("--m20-promote", default=DEFAULT_M20_PROMOTE)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--template-json", default=DEFAULT_TEMPLATE_JSON)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _issue_codes(rows: object) -> list[str]:
    if not isinstance(rows, list):
        return []
    return [_clean(row.get("code")) for row in rows if isinstance(row, dict) and _clean(row.get("code"))]


def _promote_index(promote: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in promote.get("results") or []:
        if isinstance(item, dict):
            account_id = _clean(item.get("account_id"))
            if account_id:
                out[account_id] = item
    return out


def _suggest_default_confirmation(item: dict[str, Any]) -> str:
    if item["blocking_codes"]:
        return "hold_not_icp"
    if "persona_boundary_unstable" in item["warning_codes"]:
        return "keep_pending_need_business_context"
    if item["decision"] == "allow":
        return "confirm_active_low_priority"
    return "keep_pending_need_business_context"


def _business_value_prompt(item: dict[str, Any]) -> str:
    return (
        f"请判断 `{item['account_name']}` 是否值得围绕 `{item['track']}/{item['persona']}` "
        "进入下一步业务动作；如果值得，请给出场景和动作，如果不值得，请给出淘汰原因。"
    )


def _confirmation_item(summary_item: dict[str, Any], promote_item: dict[str, Any] | None) -> dict[str, Any]:
    gate = promote_item.get("promotion_gate") if isinstance(promote_item, dict) and isinstance(promote_item.get("promotion_gate"), dict) else {}
    warning_issues = summary_item.get("warning_issues") or gate.get("warning_issues") or []
    blocking_issues = summary_item.get("blocking_issues") or gate.get("blocking_issues") or []
    item = {
        "account_id": _clean(summary_item.get("account_id")),
        "account_name": _clean(summary_item.get("account_name")),
        "track": _clean(summary_item.get("track") or (promote_item or {}).get("primary_track")),
        "persona": _clean(summary_item.get("persona_tag") or (promote_item or {}).get("persona_tag")),
        "from_level": _clean(summary_item.get("from_level")),
        "target_level": _clean(summary_item.get("target_level")),
        "current_level": _clean(summary_item.get("current_level")),
        "decision": _clean(summary_item.get("decision") or gate.get("decision")),
        "profile_status": _clean(summary_item.get("profile_status")),
        "validation_gap": _clean(summary_item.get("validation_gap")),
        "promote_summary": _clean(summary_item.get("promote_summary") or gate.get("summary")),
        "blocking_codes": _issue_codes(blocking_issues),
        "warning_codes": _issue_codes(warning_issues),
        "remaining_gaps": summary_item.get("remaining_gaps") or [],
        "open_queue_types": summary_item.get("open_queue_types") or [],
        "knowledge_asset_refs": _clean((promote_item or {}).get("knowledge_asset_refs")),
        "talk_track_refs": _clean((promote_item or {}).get("talk_track_refs")),
    }
    item["default_confirmation_status"] = _suggest_default_confirmation(item)
    item["business_value_prompt"] = _business_value_prompt(item)
    item["business_confirmation_fields"] = {
        "business_fit_rating": "",
        "worth_following": "",
        "target_scenario": "",
        "recommended_next_action": "",
        "business_priority": "",
        "disqualify_reason": "",
        "reviewer": "",
        "review_date": "",
        "review_note": "",
    }
    item["allowed_confirmation_statuses"] = CONFIRMATION_OPTIONS
    item["writeback_admission_hint"] = (
        "Only confirm_active_high_value may enter M22 writeback admission, and only after gate/baseline checks plus explicit user confirmation."
    )
    return item


def _template_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": item["account_id"],
        "account_name": item["account_name"],
        "confirmation_status": "pending_business_persona_review",
        "allowed_confirmation_statuses": CONFIRMATION_OPTIONS,
        "business_fit_rating": "",
        "worth_following": "",
        "target_scenario": "",
        "recommended_next_action": "",
        "business_priority": "",
        "disqualify_reason": "",
        "reviewer": "",
        "review_date": "",
        "review_note": "",
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 21-画像确认与业务价值准入包复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 输入对象：`{summary['account_count']}`",
        f"- M20 决策分布：`{summary['m20_decision_counts']}`",
        f"- 默认确认状态分布：`{summary['default_confirmation_status_counts']}`",
        f"- `confirm_active_high_value_count`：`{summary['confirm_active_high_value_count']}`",
        "",
        "本包不写回工作簿。M21 的目的不是直接转 active，而是把画像确认和业务价值判断绑定起来。",
        "",
        "## 准入规则",
        "",
        "- 只有 `confirm_active_high_value` 可进入 M22 写回准入。",
        "- 如果 `confirm_active_high_value_rate < 30%`，暂停 M22 写回，回到画像定义和候选选择策略。",
        "- 真实写回仍需 baseline、gate、workbook integrity 和用户单独确认。",
        "",
        "## 明细",
        "",
    ]
    for item in payload["confirmation_items"]:
        lines.extend(
            [
                f"### {item['account_name']}（{item['account_id']}）",
                "",
                f"- 主线/画像：`{item['track']}` / `{item['persona']}`",
                f"- M20 决策：`{item['decision']}`",
                f"- warning codes：`{item['warning_codes']}`",
                f"- 默认确认状态：`{item['default_confirmation_status']}`",
                f"- 业务问题：{item['business_value_prompt']}",
                f"- 待补/风险：{item['validation_gap'] or item['remaining_gaps']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 下一步",
            "",
            "1. 等 M23A 业务反馈回来后，更新本包 template。",
            "2. 对 M21 的 30 家填写 `confirmation_status` 和业务价值字段。",
            "3. 只有出现 `confirm_active_high_value` 时，生成 M22 写回准入包。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    summary = _load_json(args.m20_summary)
    promote = _load_json(args.m20_promote)
    promote_by_id = _promote_index(promote)
    items = [
        _confirmation_item(item, promote_by_id.get(_clean(item.get("account_id"))))
        for item in summary.get("items") or []
        if isinstance(item, dict)
    ]
    decision_counts = Counter(item["decision"] for item in items)
    default_counts = Counter(item["default_confirmation_status"] for item in items)
    high_value_count = default_counts.get("confirm_active_high_value", 0)
    payload = {
        "batch_id": "milestone21_persona_business_confirmation_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {"m20_summary": args.m20_summary, "m20_promote": args.m20_promote},
        "policy": {
            "default_writeback": False,
            "writeback_requires": [
                "confirmation_status == confirm_active_high_value",
                "report_only allow",
                "gate_check PASS",
                "baseline signature match",
                "explicit user confirmation",
            ],
            "stop_condition": "If confirm_active_high_value_rate < 30%, pause M22 and revisit persona/candidate strategy.",
        },
        "summary": {
            "account_count": len(items),
            "m20_decision_counts": dict(decision_counts),
            "default_confirmation_status_counts": dict(default_counts),
            "confirm_active_high_value_count": high_value_count,
            "confirm_active_high_value_rate": round(high_value_count / len(items), 4) if items else 0,
            "business_reviewed_count": 0,
            "next_action_defined_count": 0,
        },
        "confirmation_items": items,
    }
    template = {
        "batch_id": "milestone21_persona_business_confirmation_template_v1",
        "source_file": args.output_json,
        "policy": payload["policy"],
        "confirmation_items": [_template_item(item) for item in items],
    }
    _write_json(args.output_json, payload)
    _write_json(args.template_json, template)
    _write_text(args.review_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "template_json": args.template_json, "review_md": args.review_md, "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
