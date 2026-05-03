from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M21R = "deliveries/archive/milestones/milestone21r_trusted_match_review/milestone21r_trusted_match_review_package_v1.json"
DEFAULT_M22R = "deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_admission_package_v1.json"
DEFAULT_GATE = "deliveries/archive/repairs/milestone22r_trusted_writeback_admission_gate_check_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone23r_trusted_prospect_summary"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 23R-可信潜客摘要层复盘-v1.md"

STRONG_SOURCE_TYPES = {"cninfo", "official_website", "annual_report", "ir", "announcement"}
SALES_ACTION_TERMS = {"跟进", "触达", "销售行动", "商机", "报价", "拜访", "成交", "线索推进"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M23R trusted prospect summary cards without write-back.")
    parser.add_argument("--trusted-review-file", default=DEFAULT_M21R)
    parser.add_argument("--admission-file", default=DEFAULT_M22R)
    parser.add_argument("--gate-file", default=DEFAULT_GATE)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    return {_clean(row.get("account_id")): row for row in rows if isinstance(row, dict) and _clean(row.get("account_id"))}


def _strong_evidence(rows: list[Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        source_type = _clean(row.get("source_type"))
        locator = _clean(row.get("source_locator"))
        if source_type not in STRONG_SOURCE_TYPES or not locator:
            continue
        out.append(
            {
                "source_type": source_type,
                "source_locator": locator,
                "evidence_strength": _clean(row.get("evidence_strength")) or "A",
                "summary": _clean(row.get("summary")),
            }
        )
    return out


def _contains_sales_action(payload: Any) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return any(term in text for term in SALES_ACTION_TERMS)


def _card(review: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    trusted_card = review.get("trusted_prospect_card") if isinstance(review.get("trusted_prospect_card"), dict) else {}
    evidence = trusted_card.get("key_evidence") if isinstance(trusted_card.get("key_evidence"), list) else []
    strong = _strong_evidence(evidence)
    return {
        "account_id": _clean(review.get("account_id")),
        "company_name": _clean(review.get("account_name")),
        "matched_track": _clean(review.get("track")),
        "matched_persona": _clean(review.get("persona")),
        "trusted_status": _clean(review.get("trusted_status")),
        "target_level": _clean(admission.get("target_level") or review.get("target_level")),
        "match_reason": _clean(trusted_card.get("match_reason")),
        "core_product_or_service": _clean(trusted_card.get("core_product_or_service")),
        "business_model": _clean(trusted_card.get("business_model")),
        "key_evidence": evidence,
        "strong_evidence": strong,
        "risk_or_gap": trusted_card.get("risk_or_gap") or [],
        "writeback_admission": _clean(admission.get("writeback_admission")),
        "not_knowledge_asset_source": True,
        "knowledge_asset_boundary_note": "该卡片只说明潜客可信信息，不是客户案例、画像正例或正式知识资产来源。",
    }


def _share_item(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": card["account_id"],
        "company_name": card["company_name"],
        "display_status": "trusted_match_ready",
        "matched_persona": card["matched_persona"],
        "one_line_reason": card["match_reason"],
        "core_info": card["core_product_or_service"],
        "evidence_locator": (card.get("strong_evidence") or [{}])[0].get("source_locator", ""),
        "risk_or_gap": "；".join(card.get("risk_or_gap") or []),
        "knowledge_asset_boundary_note": card["knowledge_asset_boundary_note"],
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 23R-可信潜客摘要层复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 摘要卡数量：`{summary['card_count']}`",
        f"- 强来源覆盖：`{summary['strong_evidence_card_count']}/{summary['card_count']}`",
        f"- 画像分布：`{summary['persona_counts']}`",
        f"- 主线分布：`{summary['track_counts']}`",
        f"- 知识资产写入：`{summary['formal_knowledge_write_enabled']}`",
        "",
        "## 边界",
        "",
        "- 本包不执行真实 write_back。",
        "- 本包不写入正式知识资产。",
        "- 摘要卡只用于可信潜客阅读和复核，不作为客户案例或画像正例。",
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
                f"- 画像：`{card['matched_track']}` / `{card['matched_persona']}`",
                f"- 匹配理由：{card['match_reason']}",
                f"- 核心产品/服务：{card['core_product_or_service']}",
                f"- 经营结构：{card['business_model']}",
                f"- 关键来源：`{evidence.get('source_type', '')}` {evidence.get('source_locator', '')}",
                f"- 风险/待补点：{'；'.join(card.get('risk_or_gap') or [])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    trusted = _load_json(args.trusted_review_file)
    admission = _load_json(args.admission_file)
    gate = _load_json(args.gate_file)
    output_dir = Path(args.output_dir)

    admission_by_id = _by_id(admission.get("admission_items") or [])
    cards = []
    for review in trusted.get("review_items") or []:
        if not isinstance(review, dict) or _clean(review.get("trusted_status")) != "trusted_match_ready":
            continue
        account_id = _clean(review.get("account_id"))
        cards.append(_card(review, admission_by_id.get(account_id, {})))

    share_view = [_share_item(card) for card in cards]
    missing_strong = [card["account_id"] for card in cards if not card.get("strong_evidence")]
    summary = {
        "card_count": len(cards),
        "strong_evidence_card_count": len(cards) - len(missing_strong),
        "missing_strong_evidence_count": len(missing_strong),
        "missing_strong_evidence_account_ids": missing_strong,
        "trusted_status_counts": dict(Counter(card["trusted_status"] for card in cards)),
        "persona_counts": dict(Counter(card["matched_persona"] for card in cards)),
        "track_counts": dict(Counter(card["matched_track"] for card in cards)),
        "sales_action_terms_detected": _contains_sales_action(cards),
        "formal_knowledge_write_enabled": False,
        "gate_ok": bool(gate.get("ok")),
    }
    payload = {
        "batch_id": "milestone23r_trusted_prospect_summary_package_v1",
        "generated_at": _now(),
        "source_files": {
            "trusted_review_file": args.trusted_review_file,
            "admission_file": args.admission_file,
            "gate_file": args.gate_file,
        },
        "policy": {
            "true_writeback_executed": False,
            "formal_knowledge_write_enabled": False,
            "not_customer_case": True,
            "not_persona_positive_example": True,
        },
        "summary": summary,
        "trusted_prospect_cards": cards,
        "trusted_prospect_share_view": share_view,
    }
    _write_json(output_dir / "milestone23r_trusted_prospect_summary_package_v1.json", payload)
    _write_json(output_dir / "milestone23r_trusted_prospect_cards_v1.json", {"batch_id": "milestone23r_trusted_prospect_cards_v1", "cards": cards})
    _write_json(output_dir / "milestone23r_trusted_prospect_share_view_v1.json", {"batch_id": "milestone23r_trusted_prospect_share_view_v1", "items": share_view})
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone23r_trusted_prospect_summary_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["card_count"] == 30 and summary["missing_strong_evidence_count"] == 0 and not summary["sales_action_terms_detected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
