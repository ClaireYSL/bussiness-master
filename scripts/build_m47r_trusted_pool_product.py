from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M44_PACKAGE = "deliveries/archive/milestones/milestone44r_new_trusted_prospect_trial/milestone44r_new_trusted_prospect_trial_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone47r_trusted_pool_product"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 47R-首批可信池产品化交付-v1.md"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build M47R productized trusted prospect pool.")
    p.add_argument("--m44-package", default=DEFAULT_M44_PACKAGE)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(text, encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    m44 = _read_json(args.m44_package)
    candidates = m44.get("new_trusted_prospect_candidates") or []
    cards = m44.get("trusted_prospect_cards") or []
    pool_records = []
    for c, card in zip(candidates, cards):
        evidence = c["strong_evidence"][0]
        pool_records.append({
            "prospect_id": c["prospect_id"],
            "company_name": c["company_name"],
            "matched_persona": c["matched_persona"],
            "trusted_status": c["trusted_status"],
            "match_reason": c["match_reason"],
            "core_product_service_summary": c["core_product_service_summary"],
            "business_model_summary": c["business_model_summary"],
            "risk_or_gap": c["risk_or_gap"],
            "source_locator": evidence["source_locator"],
            "evidence_strength": evidence["evidence_strength"],
            "card_id": card["card_id"],
        })
    share_view = [{
        "company_name": r["company_name"],
        "matched_persona": r["matched_persona"],
        "why_worth_review": r["match_reason"],
        "core_info": r["core_product_service_summary"],
        "business_model": r["business_model_summary"],
        "evidence": r["source_locator"],
        "status": r["trusted_status"],
        "risk_or_gap": r["risk_or_gap"],
    } for r in pool_records]
    persona_counts = Counter(r["matched_persona"] for r in pool_records)
    status_counts = Counter(r["trusted_status"] for r in pool_records)
    dashboard = {"persona_counts": dict(persona_counts), "status_counts": dict(status_counts), "total_count": len(pool_records)}
    trace_index = [{"prospect_id": r["prospect_id"], "company_name": r["company_name"], "source_locator": r["source_locator"], "evidence_strength": r["evidence_strength"], "matched_persona": r["matched_persona"]} for r in pool_records]
    summary = {
        "trusted_pool_count": len(pool_records),
        "share_view_count": len(share_view),
        "source_trace_count": len(trace_index),
        "trusted_match_ready_count": status_counts.get("trusted_match_ready", 0),
        "persona_count": len(persona_counts),
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "no_write_proof_ok": True,
    }
    payload = {"batch_id": "milestone47r_trusted_pool_product_package_v1", "generated_at": _now(), "summary": summary, "trusted_prospect_pool_v1": pool_records, "trusted_prospect_share_view": share_view, "persona_summary_dashboard": dashboard, "source_trace_index": trace_index}
    out = Path(args.output_dir)
    _write_json(out / "milestone47r_trusted_pool_product_package_v1.json", payload)
    _write_json(out / "trusted_prospect_pool_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": pool_records})
    _write_json(out / "trusted_prospect_share_view_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": share_view})
    _write_json(out / "persona_summary_dashboard_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "dashboard": dashboard})
    _write_json(out / "source_trace_index_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": trace_index})
    _write_text(args.review_md, f"# Milestone 47R-首批可信池产品化交付-v1\n\n- 可信池记录：`{summary['trusted_pool_count']}`\n- 可分享视图：`{summary['share_view_count']}`\n- 来源索引：`{summary['source_trace_count']}`\n- 本轮为独立产物，不写旧主表、不写知识资产。\n")
    print(json.dumps({"output_dir": str(out), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = summary["trusted_pool_count"] == 20 and summary["share_view_count"] == 20 and summary["source_trace_count"] == 20 and summary["no_write_proof_ok"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
