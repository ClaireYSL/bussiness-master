from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M18_PACKAGE = "deliveries/archive/milestones/milestone18_l3_operationalization/milestone18_l3_operational_package_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone23a_l3_business_feedback/milestone23a_l3_business_feedback_package_v1.json"
DEFAULT_TEMPLATE_JSON = "configs/execution_batches/milestone23a_l3_business_feedback_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 23A-首批15家L3业务反馈快跑复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M23A L3 business feedback fast-run package.")
    parser.add_argument("--m18-package", default=DEFAULT_M18_PACKAGE)
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


def _business_question(item: dict[str, Any]) -> str:
    track = _clean(item.get("track"))
    persona = _clean(item.get("persona"))
    return f"这家公司是否值得围绕 `{track}/{persona}` 进入下一步业务动作？"


def _action_card(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "why_worth_review": _clean(item.get("why_worth_review")),
        "target_scenario": _clean(item.get("business_model_summary")),
        "evidence_enough_for_first_review": bool(int(item.get("evidence_count") or 0) >= 3),
        "largest_risk": _clean(item.get("validation_gap")) or "待业务侧确认真实场景、优先级和触达价值。",
        "suggested_next_action": "请业务/研究负责人判断是否 worth_following，并给出 recommended_next_action。",
    }


def _feedback_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": _clean(item.get("account_id")),
        "account_name": _clean(item.get("account_name")),
        "track": _clean(item.get("track")),
        "persona": _clean(item.get("persona")),
        "main_level": _clean(item.get("main_level")),
        "profile_status": _clean(item.get("profile_status")),
        "share_status": _clean(item.get("share_status")),
        "evidence_count": int(item.get("evidence_count") or 0),
        "open_queue_count": int(item.get("open_queue_count") or 0),
        "business_question": _business_question(item),
        "action_card": _action_card(item),
        "evidence_brief": {
            "product_summary": _clean(item.get("product_summary")),
            "business_model_summary": _clean(item.get("business_model_summary")),
            "why_worth_review": _clean(item.get("why_worth_review")),
            "validation_gap": _clean(item.get("validation_gap")),
        },
        "feedback_status": "pending_business_feedback",
        "business_feedback_fields": {
            "business_fit_rating": "",
            "worth_following": "",
            "recommended_next_action": "",
            "target_scenario": "",
            "disqualify_reason": "",
            "priority_rank": "",
            "feedback_owner": "",
            "feedback_date": "",
            "feedback_notes": "",
        },
        "allowed_worth_following_values": ["yes", "no", "unclear"],
        "allowed_recommended_next_actions": [
            "advance_to_l2_research",
            "sales_review",
            "keep_l3_monitoring",
            "disqualify",
            "needs_more_context",
        ],
    }


def _template_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": item["account_id"],
        "account_name": item["account_name"],
        "business_fit_rating": "",
        "worth_following": "",
        "recommended_next_action": "",
        "target_scenario": "",
        "disqualify_reason": "",
        "priority_rank": "",
        "feedback_owner": "",
        "feedback_date": "",
        "feedback_notes": "",
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 23A-首批15家L3业务反馈快跑复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 输入对象：`{summary['account_count']}`",
        f"- share ready：`{summary['share_ready_count']}`",
        f"- 当前业务反馈：`business_reviewed_count={summary['business_reviewed_count']}`",
        f"- 北极星口径：`可行动静态潜客数`，本包生成后仍需业务填写反馈才能统计。",
        "",
        "## 使用方式",
        "",
        "本包不写回工作簿。请在模板 JSON 中填写业务反馈字段，或将字段映射到后续表格/协作工具。",
        "",
        "关键判断不是“这家公司像不像画像”，而是“业务是否愿意基于这张行动卡继续推进”。",
        "",
        "## 反馈字段",
        "",
        "- `business_fit_rating`：1-5 分",
        "- `worth_following`：yes/no/unclear",
        "- `recommended_next_action`：advance_to_l2_research/sales_review/keep_l3_monitoring/disqualify/needs_more_context",
        "- `target_scenario`：业务认为最可能切入的场景",
        "- `disqualify_reason`：淘汰原因，worth_following=no 时必填",
        "- `priority_rank`：本批内部优先级",
        "- `feedback_owner / feedback_date / feedback_notes`：反馈人、日期、备注",
        "",
        "## 明细",
        "",
    ]
    for item in payload["feedback_items"]:
        card = item["action_card"]
        lines.extend(
            [
                f"### {item['account_name']}（{item['account_id']}）",
                "",
                f"- 主线/画像：`{item['track']}` / `{item['persona']}`",
                f"- 问题：{item['business_question']}",
                f"- 为什么值得看：{card['why_worth_review']}",
                f"- 适合什么场景：{card['target_scenario']}",
                f"- 当前证据是否够首轮判断：`{card['evidence_enough_for_first_review']}`",
                f"- 最大风险：{card['largest_risk']}",
                f"- 建议下一步：{card['suggested_next_action']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 验收标准",
            "",
            "- `business_reviewed_count >= 15`，或明确记录未完成原因。",
            "- `accepted_by_business_count / rejected_by_business_count` 可统计。",
            "- `next_action_defined_count` 可统计。",
            "- rejected 对象必须有 `disqualify_reason`。",
            "- 至少形成一版画像/候选选择修正建议。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    m18 = _load_json(args.m18_package)
    feedback_items = [_feedback_item(item) for item in m18.get("items") or [] if isinstance(item, dict)]
    share_ready_count = sum(1 for item in feedback_items if item.get("share_status") == "l3_share_ready")
    payload = {
        "batch_id": "milestone23a_l3_business_feedback_fast_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {"m18_package": args.m18_package},
        "north_star_metric": {
            "name": "可行动静态潜客数",
            "definition": "同时满足证据可信、画像明确、业务场景清楚、下一步动作明确、可被业务侧接收或继续判断的公司数量。",
        },
        "summary": {
            "account_count": len(feedback_items),
            "share_ready_count": share_ready_count,
            "business_reviewed_count": 0,
            "accepted_by_business_count": 0,
            "rejected_by_business_count": 0,
            "next_action_defined_count": 0,
            "positive_fit_rate": None,
            "feedback_status_counts": dict(Counter(item["feedback_status"] for item in feedback_items)),
        },
        "feedback_items": feedback_items,
    }
    template = {
        "batch_id": "milestone23a_l3_business_feedback_template_v1",
        "source_file": args.output_json,
        "policy": "Fill this template manually or via a business feedback workflow. Do not use blank feedback to promote accounts.",
        "allowed_worth_following_values": ["yes", "no", "unclear"],
        "allowed_recommended_next_actions": [
            "advance_to_l2_research",
            "sales_review",
            "keep_l3_monitoring",
            "disqualify",
            "needs_more_context",
        ],
        "feedback_items": [_template_item(item) for item in feedback_items],
    }
    _write_json(args.output_json, payload)
    _write_json(args.template_json, template)
    _write_text(args.review_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "template_json": args.template_json, "review_md": args.review_md, "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
