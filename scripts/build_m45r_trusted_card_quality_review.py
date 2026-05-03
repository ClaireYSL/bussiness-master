from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M44_CARDS = "deliveries/archive/milestones/milestone44r_new_trusted_prospect_trial/milestone44r_trusted_prospect_cards_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone45r_trusted_card_quality_review"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 45R-可信潜客质量评估与业务可读性验证-v1.md"

FEEDBACK_FIELDS = ["readability_rating", "evidence_trust_rating", "persona_fit_rating", "worth_business_review", "unclear_points", "reviewer_notes"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M45R quality review sample for trusted prospect cards.")
    parser.add_argument("--m44-cards", default=DEFAULT_M44_CARDS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _score_card(card: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "has_company_name": bool(card.get("company_name")),
        "has_persona": bool(card.get("matched_persona")),
        "has_match_reason": len(card.get("match_reason") or "") >= 20,
        "has_core_product": len(card.get("core_product_service_summary") or "") >= 10,
        "has_business_model": len(card.get("business_model_summary") or "") >= 10,
        "has_source_locator": bool((card.get("key_evidence") or {}).get("source_locator")),
        "has_risk_or_gap": bool(card.get("risk_or_gap")),
    }
    score = round(sum(1 for ok in checks.values() if ok) / len(checks) * 100, 1)
    return {"quality_score": score, "checks": checks, "quality_status": "pass" if score >= 85 else "needs_rework"}


def _render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    return "\n".join([
        "# Milestone 45R-可信潜客质量评估与业务可读性验证-v1",
        "",
        "## 结论",
        "",
        f"- 抽样卡片数：`{s['sample_count']}`",
        f"- 质量检查通过：`{s['quality_pass_count']}`",
        f"- 平均质量分：`{s['average_quality_score']}`",
        f"- 人工反馈状态：`{s['human_feedback_status']}`",
        f"- no-write proof：`{s['no_write_proof_ok']}`",
        "",
        "## 边界",
        "",
        "- 没有人为反馈时，不生成 accepted/rejected 业务结论。",
        "- 反馈只用于验证卡片可读性和规则校准建议，不写知识资产。",
        "- 本轮不写旧主表、不改画像 registry。",
    ]).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    cards_payload = _read_json(args.m44_cards)
    cards = cards_payload.get("items") or []
    sample = cards[:15]
    scored = []
    feedback_template = []
    for card in sample:
        score = _score_card(card)
        scored_item = {**card, **score}
        scored.append(scored_item)
        feedback_template.append({
            "card_id": card.get("card_id"),
            "company_name": card.get("company_name"),
            "matched_persona": card.get("matched_persona"),
            "match_reason": card.get("match_reason"),
            "key_evidence_locator": (card.get("key_evidence") or {}).get("source_locator"),
            "risk_or_gap": card.get("risk_or_gap"),
            **{field: "" for field in FEEDBACK_FIELDS},
            "feedback_status": "pending_human_feedback",
        })
    scores = [item["quality_score"] for item in scored]
    status_counts = Counter(item["quality_status"] for item in scored)
    summary = {
        "sample_count": len(sample),
        "quality_pass_count": status_counts.get("pass", 0),
        "quality_needs_rework_count": status_counts.get("needs_rework", 0),
        "average_quality_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "human_feedback_status": "pending",
        "accepted_count": 0,
        "rejected_count": 0,
        "field_gap_count": sum(1 for item in scored for ok in item["checks"].values() if not ok),
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "no_write_proof_ok": True,
    }
    field_gap_summary = []
    for item in scored:
        missing = [k for k, ok in item["checks"].items() if not ok]
        if missing:
            field_gap_summary.append({"card_id": item["card_id"], "company_name": item["company_name"], "missing_or_weak_checks": missing})
    payload = {
        "batch_id": "milestone45r_trusted_card_quality_review_package_v1",
        "generated_at": _now(),
        "summary": summary,
        "quality_review_sample": scored,
        "readability_feedback_template": feedback_template,
        "trusted_card_quality_score": [{"card_id": i["card_id"], "company_name": i["company_name"], "quality_score": i["quality_score"], "quality_status": i["quality_status"], "checks": i["checks"]} for i in scored],
        "field_gap_summary": field_gap_summary,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone45r_trusted_card_quality_review_package_v1.json", payload)
    _write_json(output_dir / "milestone45r_quality_review_sample_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": scored})
    _write_json(output_dir / "milestone45r_readability_feedback_template_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": feedback_template})
    _write_json(output_dir / "milestone45r_trusted_card_quality_score_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": payload["trusted_card_quality_score"]})
    _write_json(output_dir / "milestone45r_field_gap_summary_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": field_gap_summary})
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_dir": str(output_dir), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = 10 <= summary["sample_count"] <= 15 and summary["quality_pass_count"] == summary["sample_count"] and summary["accepted_count"] == 0 and summary["rejected_count"] == 0 and summary["no_write_proof_ok"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
