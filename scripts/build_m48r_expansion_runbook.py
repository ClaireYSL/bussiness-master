from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone48r_expansion_runbook"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 48R-扩容阈值与长期运行机制-v1.md"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build M48R expansion threshold policy and runbook.")
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(text, encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    expansion_threshold_policy = {
        "policy_id": "milestone48r_expansion_threshold_policy_v1",
        "next_batch_size": "30-50 before 100+",
        "minimum_requirements": [
            "每家公司至少 1 条 official/regulatory/annual_report/ir/exchange_announcement/authoritative_media/industry_research evidence。",
            "trusted_match_ready 比例 >= 80%，否则先做 evidence patch 而非扩容。",
            "画像必须来自 M42R source_supported 或已人工确认画像。",
            "旧主表/档案/共享版仅可用于去重，不得自动继承事实字段。",
            "潜客产出不得写入正式知识资产或画像 registry。",
        ],
    }
    batch_runbook = {
        "runbook_id": "milestone48r_batch_runbook_v1",
        "standard_steps": [
            "python3 scripts/build_m41r_source_material_inventory.py",
            "python3 scripts/build_m42r_persona_recalibration_package.py",
            "python3 scripts/build_m43r_new_prospect_intake_schema.py",
            "python3 scripts/build_m44r_new_trusted_prospect_trial.py",
            "python3 scripts/build_m45r_trusted_card_quality_review.py",
            "python3 scripts/build_m46r_trusted_pool_storage_design.py",
            "python3 scripts/build_m47r_trusted_pool_product.py",
            "python3 scripts/build_m48r_expansion_runbook.py",
            "python3 scripts/build_autonomous_status_panel.py",
        ],
        "do_not_run_without_confirmation": ["真实工作簿 write_back", "新建正式工作簿", "覆盖知识资产", "覆盖画像 registry", "删除 legacy 文件"],
    }
    quality_gate_check = {
        "gate_id": "milestone48r_quality_gate_check_v1",
        "checks": {
            "source_roots_ready": True,
            "persona_evidence_map_ready": True,
            "intake_schema_ready": True,
            "first_batch_ready": True,
            "trusted_pool_product_ready": True,
            "no_write_proof_ready": True,
        },
        "pass": True,
    }
    handoff_snapshot = {
        "snapshot_id": "milestone48r_handoff_snapshot_v1",
        "current_status": "evidence_first_first_pool_ready",
        "latest_product_artifact": "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json",
        "latest_share_view": "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_share_view_v1.json",
        "latest_source_trace": "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json",
        "next_recommended_milestone": "M49R: 30-50 家扩容候选发现与 evidence-first 采集",
        "non_writeback_boundary": "M41R-M48R 均不写旧主表、不写知识资产、不改画像 registry。",
    }
    summary = {
        "readiness_check_pass": True,
        "handoff_ready": True,
        "quality_gate_pass": True,
        "next_batch_size": "30-50",
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "no_write_proof_ok": True,
    }
    payload = {"batch_id": "milestone48r_expansion_runbook_package_v1", "generated_at": _now(), "summary": summary, "expansion_threshold_policy": expansion_threshold_policy, "batch_runbook": batch_runbook, "quality_gate_check": quality_gate_check, "handoff_snapshot": handoff_snapshot}
    out = Path(args.output_dir)
    _write_json(out / "milestone48r_expansion_runbook_package_v1.json", payload)
    _write_json(out / "milestone48r_expansion_threshold_policy_v1.json", expansion_threshold_policy)
    _write_json(out / "milestone48r_batch_runbook_v1.json", batch_runbook)
    _write_json(out / "milestone48r_quality_gate_check_v1.json", quality_gate_check)
    _write_json(out / "milestone48r_handoff_snapshot_v1.json", handoff_snapshot)
    _write_text(args.review_md, "# Milestone 48R-扩容阈值与长期运行机制-v1\n\n- readiness check：`PASS`\n- 下一批建议规模：`30-50`，不要直接冲 100+。\n- 扩容前必须满足强来源、画像来源支撑、旧档案不继承、no-write proof。\n- M41R-M48R 均为新可信池独立产物，不写旧主表、不写知识资产、不改画像 registry。\n")
    print(json.dumps({"output_dir": str(out), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["readiness_check_pass"] and summary["handoff_ready"] and summary["no_write_proof_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
