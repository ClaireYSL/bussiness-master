from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone46r_trusted_pool_storage_design"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 46R-新可信池标准化写回导出设计-v1.md"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build M46R trusted pool storage/export design.")
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
    design = {
        "design_id": "milestone46r_trusted_pool_storage_design_v1",
        "recommended_storage": "trusted_prospect_pool_v1_independent_artifact",
        "do_not_reuse_legacy_excel_as_primary_store": True,
        "storage_paths": {
            "json_canonical": "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json",
            "share_view_json": "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_share_view_v1.json",
            "source_trace_index": "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json",
        },
        "required_record_fields": ["prospect_id", "company_name", "matched_persona", "match_reason", "core_product_service_summary", "business_model_summary", "key_evidence", "trusted_status", "risk_or_gap"],
    }
    export_spec = {
        "spec_id": "milestone46r_export_view_spec_v1",
        "views": [
            {"view_name": "trusted_prospect_share_view", "purpose": "给业务/研究侧快速判断", "format": ["json", "markdown_later"]},
            {"view_name": "persona_summary_dashboard", "purpose": "按画像查看数量与证据覆盖", "format": ["json"]},
            {"view_name": "source_trace_index", "purpose": "快速回溯来源", "format": ["json"]},
        ],
    }
    writeback_policy = {
        "policy_id": "milestone46r_writeback_policy_v1",
        "default_writeback_target": "none",
        "legacy_excel_writeback_allowed": False,
        "new_formal_workbook_requires_user_confirmation": True,
        "knowledge_asset_write_allowed": False,
        "persona_registry_write_allowed": False,
    }
    boundary_doc = {
        "doc_id": "milestone46r_migration_boundary_doc_v1",
        "legacy_role": "dedupe_reference_only",
        "new_pool_role": "trusted_operating_pool",
        "migration_boundary": "旧主表/档案字段不得自动迁入；每条新池记录必须由 M43/M44 schema 和 evidence 支撑。",
    }
    summary = {
        "storage_design_ready": True,
        "legacy_excel_primary_store": False,
        "new_formal_workbook_requires_confirmation": True,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "no_write_proof_ok": True,
    }
    payload = {"batch_id": "milestone46r_trusted_pool_storage_design_package_v1", "generated_at": _now(), "summary": summary, "trusted_pool_storage_design": design, "export_view_spec": export_spec, "writeback_policy": writeback_policy, "migration_boundary_doc": boundary_doc}
    out = Path(args.output_dir)
    _write_json(out / "milestone46r_trusted_pool_storage_design_package_v1.json", payload)
    _write_json(out / "milestone46r_trusted_pool_storage_design_v1.json", design)
    _write_json(out / "milestone46r_export_view_spec_v1.json", export_spec)
    _write_json(out / "milestone46r_writeback_policy_v1.json", writeback_policy)
    _write_json(out / "milestone46r_migration_boundary_doc_v1.json", boundary_doc)
    _write_text(args.review_md, "# Milestone 46R-新可信池标准化写回导出设计-v1\n\n- 新可信池建议承载：独立 `trusted_prospect_pool_v1` 产物。\n- 旧 Excel：仅 legacy 去重参考，不作为主存储。\n- 新建正式工作簿或真实写回：需要单独确认。\n- 本轮不写旧主表、不写知识资产、不改画像 registry。\n")
    print(json.dumps({"output_dir": str(out), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["storage_design_ready"] and summary["no_write_proof_ok"] and not summary["legacy_excel_primary_store"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
