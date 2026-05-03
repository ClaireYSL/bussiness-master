from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONSUMPTION = "deliveries/archive/milestones/milestone26r_m25r_trusted_consumption/milestone26r_m25r_trusted_consumption_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone27r_m25r_persona_confirmation"
DEFAULT_TEMPLATE_JSON = "configs/execution_batches/milestone27r_m25r_persona_confirmation_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 27R-M25R画像稳定性确认包复盘-v1.md"


CONFIRMATION_ACTIONS = [
    "confirm_active_candidate",
    "keep_pending",
    "persona_adjust",
    "hold",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M27R persona confirmation package for M25R cards.")
    parser.add_argument("--consumption-file", default=DEFAULT_CONSUMPTION)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--template-json", default=DEFAULT_TEMPLATE_JSON)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _has_only_persona_boundary_warn(card: dict[str, Any]) -> bool:
    warnings = card.get("warning_codes") if isinstance(card.get("warning_codes"), list) else []
    blocks = card.get("blocking_codes") if isinstance(card.get("blocking_codes"), list) else []
    return not blocks and set(_clean(code) for code in warnings) <= {"persona_boundary_unstable"}


def _recommended_action(card: dict[str, Any]) -> str:
    if card.get("blocking_codes"):
        return "hold"
    if not card.get("strong_evidence"):
        return "keep_pending"
    if _clean(card.get("trusted_status")) != "trusted_match_ready":
        return "keep_pending"
    if not _clean(card.get("matched_persona")):
        return "persona_adjust"
    if _has_only_persona_boundary_warn(card):
        return "confirm_active_candidate"
    return "keep_pending"


def _confidence(card: dict[str, Any], action: str) -> str:
    if action != "confirm_active_candidate":
        return "medium"
    if card.get("strong_evidence") and _clean(card.get("core_product_or_service")) and _clean(card.get("business_model")):
        return "high"
    return "medium"


def _confirmation_item(card: dict[str, Any]) -> dict[str, Any]:
    action = _recommended_action(card)
    return {
        "account_id": card["account_id"],
        "company_name": card["company_name"],
        "matched_track": card["matched_track"],
        "matched_persona": card["matched_persona"],
        "from_level": card.get("from_level", ""),
        "target_level": card.get("target_level", "L3"),
        "system_recommendation": action,
        "recommendation_confidence": _confidence(card, action),
        "manual_confirmation_required": True,
        "allowed_manual_actions": CONFIRMATION_ACTIONS,
        "manual_action": "",
        "manual_reviewer": "",
        "manual_review_date": "",
        "manual_review_note": "",
        "confirm_basis": {
            "trusted_status": card.get("trusted_status"),
            "strong_evidence_count": len(card.get("strong_evidence") or []),
            "warning_codes": card.get("warning_codes") or [],
            "blocking_codes": card.get("blocking_codes") or [],
            "match_reason": card.get("match_reason"),
            "core_product_or_service": card.get("core_product_or_service"),
            "business_model": card.get("business_model"),
        },
        "boundary_question": (
            f"{card['company_name']} 是否应按 `{card['matched_persona']}` 进入 L3 可消费池？"
            "如果不是，应调整画像、继续 pending，还是 hold？"
        ),
        "knowledge_asset_boundary_note": "该确认项只用于潜客画像复核，不能作为客户案例、画像正例/反例或正式知识资产来源。",
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 27R-M25R画像稳定性确认包复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 输入对象：`{summary['account_count']}`",
        f"- 系统建议分布：`{summary['system_recommendation_counts']}`",
        f"- 待人工确认：`{summary['manual_confirmation_required_count']}`",
        f"- 知识资产写入：`{summary['formal_knowledge_write_enabled']}`",
        "",
        "## 解释",
        "",
        "- `confirm_active_candidate` 不是自动写回，也不是自动转 active。",
        "- 它表示该对象已具备强来源、核心信息和可信画像匹配基础，可进入人工确认或 M28R report-only 准入。",
        "- 本包不写入工作簿，不写入正式知识资产，不修改画像注册表。",
        "",
        "## 明细",
        "",
    ]
    for item in payload["confirmation_items"]:
        lines.extend(
            [
                f"### {item['company_name']}（{item['account_id']}）",
                "",
                f"- 主线/画像：`{item['matched_track']}` / `{item['matched_persona']}`",
                f"- 系统建议：`{item['system_recommendation']}`，置信度：`{item['recommendation_confidence']}`",
                f"- 边界问题：{item['boundary_question']}",
                f"- 匹配理由：{item['confirm_basis']['match_reason']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    consumption = _load_json(args.consumption_file)
    cards = consumption.get("trusted_prospect_cards") if isinstance(consumption.get("trusted_prospect_cards"), list) else []
    items = [_confirmation_item(card) for card in cards if isinstance(card, dict)]
    action_counts = Counter(item["system_recommendation"] for item in items)
    confirm_active = [item for item in items if item["system_recommendation"] == "confirm_active_candidate"]
    keep_pending = [item for item in items if item["system_recommendation"] == "keep_pending"]
    persona_adjust = [item for item in items if item["system_recommendation"] == "persona_adjust"]
    hold = [item for item in items if item["system_recommendation"] == "hold"]
    boundary_questions = [
        {
            "account_id": item["account_id"],
            "company_name": item["company_name"],
            "matched_persona": item["matched_persona"],
            "boundary_question": item["boundary_question"],
            "system_recommendation": item["system_recommendation"],
        }
        for item in items
    ]
    summary = {
        "account_count": len(items),
        "system_recommendation_counts": dict(action_counts),
        "confirm_active_candidate_count": len(confirm_active),
        "keep_pending_count": len(keep_pending),
        "persona_adjust_count": len(persona_adjust),
        "hold_count": len(hold),
        "manual_confirmation_required_count": len([item for item in items if item["manual_confirmation_required"]]),
        "formal_knowledge_write_enabled": False,
        "true_writeback_enabled": False,
    }
    payload = {
        "batch_id": "milestone27r_m25r_persona_confirmation_package_v1",
        "generated_at": _now(),
        "source_files": {"consumption_file": args.consumption_file},
        "policy": {
            "true_writeback_enabled": False,
            "formal_knowledge_write_enabled": False,
            "not_customer_case": True,
            "not_persona_registry_update": True,
            "requires_manual_confirmation_before_writeback": True,
        },
        "summary": summary,
        "confirmation_items": items,
        "persona_boundary_questions": boundary_questions,
        "confirm_active_candidates": confirm_active,
        "keep_pending_candidates": keep_pending,
        "persona_adjust_candidates": persona_adjust,
        "hold_candidates": hold,
    }
    template = {
        "batch_id": "milestone27r_m25r_persona_confirmation_template_v1",
        "generated_at": _now(),
        "allowed_manual_actions": CONFIRMATION_ACTIONS,
        "items": [
            {
                "account_id": item["account_id"],
                "company_name": item["company_name"],
                "system_recommendation": item["system_recommendation"],
                "manual_action": "",
                "manual_reviewer": "",
                "manual_review_date": "",
                "manual_review_note": "",
            }
            for item in items
        ],
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone27r_m25r_persona_confirmation_package_v1.json", payload)
    _write_json(output_dir / "milestone27r_m25r_persona_boundary_questions_v1.json", {"batch_id": "milestone27r_m25r_persona_boundary_questions_v1", "items": boundary_questions})
    _write_json(output_dir / "milestone27r_m25r_confirm_active_candidates_v1.json", {"batch_id": "milestone27r_m25r_confirm_active_candidates_v1", "items": confirm_active})
    _write_json(args.template_json, template)
    _write_text(args.review_md, _render_markdown(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone27r_m25r_persona_confirmation_package_v1.json"), "template_json": args.template_json, "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["account_count"] == 50 and not summary["formal_knowledge_write_enabled"] and not summary["true_writeback_enabled"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
