from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REVIEW = "deliveries/archive/milestones/milestone25r_trusted_expansion_review/milestone25r_trusted_expansion_review_package_v1.json"
DEFAULT_ENRICH = "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_enrich_v1.json"
DEFAULT_PROMOTE = "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_promote_v1.json"
DEFAULT_RUN = "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_run_summary_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone26r_m25r_trusted_consumption"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 26R-M25R可信潜客消费层复盘-v1.md"

STRONG_SOURCE_TYPES = {"cninfo", "official_website", "annual_report", "ir", "announcement"}
FORBIDDEN_KNOWLEDGE_WRITE_KEYS = {
    "knowledge_assets",
    "knowledge_assets_write",
    "customer_case",
    "customer_case_write",
    "persona_registry",
    "persona_registry_write",
    "persona_positive_example",
    "persona_negative_example",
}
SALES_ACTION_TERMS = {"跟进", "触达", "销售行动", "商机", "报价", "拜访", "成交", "线索推进"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M26R trusted prospect consumption cards for M25R.")
    parser.add_argument("--review-file", default=DEFAULT_REVIEW)
    parser.add_argument("--enrich-file", default=DEFAULT_ENRICH)
    parser.add_argument("--promote-file", default=DEFAULT_PROMOTE)
    parser.add_argument("--run-summary-file", default=DEFAULT_RUN)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
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


def _by_id(rows: list[Any]) -> dict[str, dict[str, Any]]:
    return {
        _clean(row.get("account_id")): row
        for row in rows
        if isinstance(row, dict) and _clean(row.get("account_id"))
    }


def _strong_evidence(rows: list[Any]) -> list[dict[str, str]]:
    strong: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        source_type = _clean(row.get("source_type"))
        locator = _clean(row.get("source_locator"))
        if source_type not in STRONG_SOURCE_TYPES or not locator:
            continue
        strong.append(
            {
                "source_type": source_type,
                "source_locator": locator,
                "evidence_strength": _clean(row.get("evidence_strength")) or "A",
                "summary": _clean(row.get("summary")),
            }
        )
    return strong


def _warning_codes(promote: dict[str, Any]) -> list[str]:
    gate = promote.get("promotion_gate") if isinstance(promote.get("promotion_gate"), dict) else {}
    warnings = gate.get("warning_issues") if isinstance(gate.get("warning_issues"), list) else []
    return [_clean(item.get("code")) for item in warnings if isinstance(item, dict) and _clean(item.get("code"))]


def _blocking_codes(promote: dict[str, Any]) -> list[str]:
    gate = promote.get("promotion_gate") if isinstance(promote.get("promotion_gate"), dict) else {}
    blocks = gate.get("blocking_issues") if isinstance(gate.get("blocking_issues"), list) else []
    return [_clean(item.get("code")) for item in blocks if isinstance(item, dict) and _clean(item.get("code"))]


def _consumer_status(card: dict[str, Any]) -> str:
    if card["blocking_codes"]:
        return "hold"
    if "persona_boundary_unstable" in card["warning_codes"]:
        return "needs_persona_confirmation"
    if card["trusted_status"] == "trusted_match_ready" and card["strong_evidence"]:
        return "ready_for_review"
    return "needs_intake_patch"


def _card(review: dict[str, Any], enrich: dict[str, Any], promote: dict[str, Any]) -> dict[str, Any]:
    trusted_card = review.get("trusted_prospect_card") if isinstance(review.get("trusted_prospect_card"), dict) else {}
    rewrite = enrich.get("rewrite_suggestion") if isinstance(enrich.get("rewrite_suggestion"), dict) else {}
    evidence = trusted_card.get("key_evidence") if isinstance(trusted_card.get("key_evidence"), list) else []
    strong = _strong_evidence(evidence)
    warnings = _warning_codes(promote)
    blocks = _blocking_codes(promote)
    card = {
        "account_id": _clean(review.get("account_id") or enrich.get("account_id") or promote.get("account_id")),
        "company_name": _clean(review.get("account_name") or enrich.get("account_canonical_name") or promote.get("account_canonical_name")),
        "matched_track": _clean(review.get("track") or enrich.get("primary_track") or promote.get("primary_track")),
        "matched_persona": _clean(review.get("persona") or enrich.get("persona_tag") or promote.get("persona_tag")),
        "from_level": _clean(review.get("from_level") or promote.get("from_level") or enrich.get("current_level")),
        "target_level": _clean(review.get("target_level") or promote.get("target_level")),
        "trusted_status": _clean(review.get("trusted_status")),
        "match_reason": _clean(trusted_card.get("match_reason") or rewrite.get("admission_reason_summary")),
        "core_product_or_service": _clean(trusted_card.get("core_product_or_service") or rewrite.get("公司产品与服务概述")),
        "business_model": _clean(trusted_card.get("business_model") or rewrite.get("商业模式概述")),
        "key_evidence": evidence,
        "strong_evidence": strong,
        "warning_codes": warnings,
        "blocking_codes": blocks,
        "current_risk_or_gap": trusted_card.get("risk_or_gap") or ["仍需画像稳定性确认。"],
        "suggested_review_question": "该公司是否应按当前画像进入 L3 可消费池，还是保留 pending 并等待更多画像边界确认？",
        "suggested_consumer_status": "",
        "not_knowledge_asset_source": True,
        "knowledge_asset_boundary_note": "该卡片只用于潜客消费和人工复核，不能作为客户案例、画像正例/反例或正式知识资产来源。",
    }
    card["suggested_consumer_status"] = _consumer_status(card)
    return card


def _share_item(card: dict[str, Any]) -> dict[str, Any]:
    evidence = (card.get("strong_evidence") or [{}])[0]
    return {
        "account_id": card["account_id"],
        "company_name": card["company_name"],
        "share_status": card["suggested_consumer_status"],
        "matched_track": card["matched_track"],
        "matched_persona": card["matched_persona"],
        "why_it_matches": card["match_reason"],
        "core_product_or_service": card["core_product_or_service"],
        "business_model": card["business_model"],
        "primary_evidence_type": evidence.get("source_type", ""),
        "primary_evidence_locator": evidence.get("source_locator", ""),
        "risk_or_gap": "；".join(card.get("current_risk_or_gap") or []),
        "next_review_question": card["suggested_review_question"],
        "knowledge_asset_boundary_note": card["knowledge_asset_boundary_note"],
    }


def _index(cards: list[dict[str, Any]]) -> dict[str, Any]:
    by_track: dict[str, list[str]] = defaultdict(list)
    by_persona: dict[str, list[str]] = defaultdict(list)
    by_status: dict[str, list[str]] = defaultdict(list)
    by_warning: dict[str, list[str]] = defaultdict(list)
    for card in cards:
        by_track[card["matched_track"]].append(card["account_id"])
        by_persona[card["matched_persona"]].append(card["account_id"])
        by_status[card["suggested_consumer_status"]].append(card["account_id"])
        for code in card["warning_codes"]:
            by_warning[code].append(card["account_id"])
    return {
        "by_track": dict(sorted(by_track.items())),
        "by_persona": dict(sorted(by_persona.items())),
        "by_consumer_status": dict(sorted(by_status.items())),
        "by_warning_code": dict(sorted(by_warning.items())),
    }


def _contains_forbidden_write_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(key in FORBIDDEN_KNOWLEDGE_WRITE_KEYS for key in payload) or any(
            _contains_forbidden_write_key(value) for value in payload.values()
        )
    if isinstance(payload, list):
        return any(_contains_forbidden_write_key(item) for item in payload)
    return False


def _contains_sales_action(payload: Any) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return any(term in text for term in SALES_ACTION_TERMS)


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 26R-M25R可信潜客消费层复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 摘要卡数量：`{summary['card_count']}`",
        f"- 强来源覆盖：`{summary['strong_evidence_card_count']}/{summary['card_count']}`",
        f"- 共享状态分布：`{summary['consumer_status_counts']}`",
        f"- warn 分布：`{summary['warning_code_counts']}`",
        f"- 知识资产写入：`{summary['formal_knowledge_write_enabled']}`",
        "",
        "## 结论",
        "",
        "- M26R 将 M25R 已补证的 50 家转成可阅读、可复核、可交接的消费层材料。",
        "- 本包不改变层级、不转 active、不写入正式知识资产。",
        "- 当前主要下一步是 M27R：围绕 `persona_boundary_unstable` 做画像稳定性确认。",
        "",
        "## 摘要卡",
        "",
    ]
    for card in payload["trusted_prospect_cards"]:
        evidence = (card.get("strong_evidence") or [{}])[0]
        lines.extend(
            [
                f"### {card['company_name']}（{card['account_id']}）",
                "",
                f"- 共享状态：`{card['suggested_consumer_status']}`",
                f"- 画像：`{card['matched_track']}` / `{card['matched_persona']}`",
                f"- 匹配理由：{card['match_reason']}",
                f"- 核心产品/服务：{card['core_product_or_service']}",
                f"- 经营结构：{card['business_model']}",
                f"- 关键来源：`{evidence.get('source_type', '')}` {evidence.get('source_locator', '')}",
                f"- 风险/待确认：{'；'.join(card.get('current_risk_or_gap') or [])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    review = _load_json(args.review_file)
    enrich = _load_json(args.enrich_file)
    promote = _load_json(args.promote_file)
    run = _load_json(args.run_summary_file)

    enrich_by_id = _by_id(enrich.get("results") or [])
    promote_by_id = _by_id(promote.get("results") or [])
    cards: list[dict[str, Any]] = []
    for item in review.get("review_items") or []:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        if not account_id:
            continue
        cards.append(_card(item, enrich_by_id.get(account_id, {}), promote_by_id.get(account_id, {})))

    share_view = [_share_item(card) for card in cards]
    missing_strong = [card["account_id"] for card in cards if not card.get("strong_evidence")]
    warning_counts = Counter(code for card in cards for code in card["warning_codes"])
    summary = {
        "card_count": len(cards),
        "strong_evidence_card_count": len(cards) - len(missing_strong),
        "missing_strong_evidence_count": len(missing_strong),
        "missing_strong_evidence_account_ids": missing_strong,
        "consumer_status_counts": dict(Counter(card["suggested_consumer_status"] for card in cards)),
        "trusted_status_counts": dict(Counter(card["trusted_status"] for card in cards)),
        "persona_counts": dict(Counter(card["matched_persona"] for card in cards)),
        "track_counts": dict(Counter(card["matched_track"] for card in cards)),
        "warning_code_counts": dict(warning_counts),
        "promote_mode": _clean(run.get("mode")),
        "enrich_writeback_executed": bool(((run.get("enrich") or {}).get("write_back") or {}).get("enabled")),
        "promote_promoted": int((((run.get("promote") or {}).get("write_back") or {}).get("promoted")) or 0),
        "promote_skipped": int((((run.get("promote") or {}).get("write_back") or {}).get("skipped")) or 0),
        "sales_action_terms_detected": _contains_sales_action(cards),
        "forbidden_knowledge_write_keys_detected": _contains_forbidden_write_key(cards),
        "formal_knowledge_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone26r_m25r_trusted_consumption_package_v1",
        "generated_at": _now(),
        "source_files": {
            "review_file": args.review_file,
            "enrich_file": args.enrich_file,
            "promote_file": args.promote_file,
            "run_summary_file": args.run_summary_file,
        },
        "policy": {
            "true_writeback_scope": "M25R enrich 已写入补证/核心信息；M26R 本身不写回。",
            "formal_knowledge_write_enabled": False,
            "not_customer_case": True,
            "not_persona_positive_or_negative_example": True,
            "not_persona_registry_update": True,
        },
        "summary": summary,
        "trusted_prospect_cards": cards,
        "trusted_prospect_share_view": share_view,
        "review_index": _index(cards),
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone26r_m25r_trusted_consumption_package_v1.json", payload)
    _write_json(output_dir / "milestone26r_m25r_trusted_prospect_cards_v1.json", {"batch_id": "milestone26r_m25r_trusted_prospect_cards_v1", "cards": cards})
    _write_json(output_dir / "milestone26r_m25r_trusted_share_view_v1.json", {"batch_id": "milestone26r_m25r_trusted_share_view_v1", "items": share_view})
    _write_json(output_dir / "milestone26r_m25r_review_index_v1.json", {"batch_id": "milestone26r_m25r_review_index_v1", "review_index": payload["review_index"]})
    _write_text(args.review_md, _render_md(payload))

    print(json.dumps({"output_json": str(output_dir / "milestone26r_m25r_trusted_consumption_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = (
        summary["card_count"] == 50
        and summary["missing_strong_evidence_count"] == 0
        and not summary["sales_action_terms_detected"]
        and not summary["forbidden_knowledge_write_keys_detected"]
        and not summary["formal_knowledge_write_enabled"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
