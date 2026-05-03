from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_JSON = "deliveries/archive/handoffs/milestone16_2_autonomous_status_panel_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 16.2-自治运行状态面板-v1.md"

SOURCE_FILES = {
    "M12": "deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_promote_v1.json",
    "M13": "deliveries/archive/milestones/milestone13_persona_boundary_rules/milestone13_persona_boundary_promote_v1.json",
    "M14": "deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_promote_v1.json",
    "M14.2": "deliveries/archive/milestones/milestone14_2_intake_quality_unblock/milestone14_2_intake_quality_promote_v1.json",
    "M14.3": "deliveries/archive/milestones/milestone14_3_candidate_preflight/milestone14_3_candidate_preflight_package_v1.json",
    "M15.2": "deliveries/archive/milestones/milestone15_2_share_consumption/milestone15_2_share_consumption_package_v1.json",
    "M17": "deliveries/archive/milestones/milestone17_writeback_admission/milestone17_writeback_admission_package_v1.json",
    "M18": "deliveries/archive/milestones/milestone18_l3_operationalization/milestone18_l3_operational_package_v1.json",
    "M19": "deliveries/archive/milestones/milestone19_expansion_feedback/milestone19_expansion_feedback_package_v1.json",
    "M20": "deliveries/archive/milestones/milestone20_batch_intake_patch/milestone20_batch_intake_promote_v1.json",
    "M20_gate": "deliveries/archive/repairs/milestone20_batch_intake_gate_check_v1.json",
    "M23A": "deliveries/archive/milestones/milestone23a_l3_business_feedback/milestone23a_l3_business_feedback_package_v1.json",
    "M21": "deliveries/archive/milestones/milestone21_persona_business_confirmation/milestone21_persona_business_confirmation_package_v1.json",
    "M21R": "deliveries/archive/milestones/milestone21r_trusted_match_review/milestone21r_trusted_match_review_package_v1.json",
    "M22R": "deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_admission_package_v1.json",
    "M22R_gate": "deliveries/archive/repairs/milestone22r_trusted_writeback_admission_gate_check_v1.json",
    "M23R": "deliveries/archive/milestones/milestone23r_trusted_prospect_summary/milestone23r_trusted_prospect_summary_package_v1.json",
    "M24R": "deliveries/archive/milestones/milestone24r_knowledge_source_governance/milestone24r_knowledge_source_governance_package_v1.json",
    "M25R": "deliveries/archive/milestones/milestone25r_trusted_expansion_preflight/milestone25r_trusted_expansion_preflight_package_v1.json",
    "M25R_patch": "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_intake_patch_v1.json",
    "M25R_run": "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_run_summary_v1.json",
    "M25R_gate": "deliveries/archive/repairs/milestone25r_trusted_expansion_gate_check_v1.json",
    "M25R_post_integrity": "deliveries/archive/repairs/milestone25r_workbook_integrity_report_post_writeback_v1.json",
    "M25R_review": "deliveries/archive/milestones/milestone25r_trusted_expansion_review/milestone25r_trusted_expansion_review_package_v1.json",
    "M26R": "deliveries/archive/milestones/milestone26r_m25r_trusted_consumption/milestone26r_m25r_trusted_consumption_package_v1.json",
    "M27R": "deliveries/archive/milestones/milestone27r_m25r_persona_confirmation/milestone27r_m25r_persona_confirmation_package_v1.json",
    "M28R": "deliveries/archive/milestones/milestone28r_m25r_promote_admission/milestone28r_m25r_promote_admission_package_v1.json",
    "M28R_run": "deliveries/archive/milestones/milestone28r_m25r_promote_admission/milestone28r_m25r_promote_admission_run_summary_v1.json",
    "M28R_gate": "deliveries/archive/repairs/milestone28r_m25r_promote_admission_gate_check_v1.json",
    "M28R_post_integrity": "deliveries/archive/repairs/milestone28r_workbook_integrity_report_post_writeback_v1.json",
    "M30R": "deliveries/archive/milestones/milestone30r_post_writeback_consumption_review/milestone30r_post_writeback_consumption_review_package_v1.json",
    "M31R": "deliveries/archive/milestones/milestone31r_business_feedback_loop/milestone31r_business_feedback_loop_package_v1.json",
    "M32R": "deliveries/archive/milestones/milestone32r_feedback_quality_validation/milestone32r_feedback_quality_validation_package_v1.json",
    "M33R": "deliveries/archive/milestones/milestone33r_workbook_governance_audit/milestone33r_workbook_governance_audit_package_v1.json",
    "M34R": "deliveries/archive/milestones/milestone34r_workbook_governance_repair_admission/milestone34r_workbook_governance_repair_admission_package_v1.json",
    "M34R_true_repair": "deliveries/archive/milestones/milestone34r_workbook_governance_true_repair/milestone34r_workbook_governance_true_repair_summary_v1.json",
    "M35R": "deliveries/archive/milestones/milestone35r_field_governance/milestone35r_field_governance_package_v1.json",
    "M35R_true_repair": "deliveries/archive/milestones/milestone35r_field_governance_true_repair/milestone35r_safe_profile_field_true_repair_summary_v1.json",
    "M36R": "deliveries/archive/milestones/milestone36r_manual_field_review/milestone36r_manual_field_review_package_v1.json",
    "M37R": "deliveries/archive/milestones/milestone37r_final_field_confirmation/milestone37r_final_field_confirmation_package_v1.json",
    "M38R": "deliveries/archive/milestones/milestone38r_governance_closure/milestone38r_governance_closure_package_v1.json",
    "M40R": "deliveries/archive/milestones/milestone40r_trusted_pool_restart/milestone40r_trusted_pool_restart_package_v1.json",
    "M41R": "deliveries/archive/milestones/milestone41r_source_material_inventory/milestone41r_source_coverage_summary_v1.json",
    "M42R": "deliveries/archive/milestones/milestone42r_persona_recalibration/milestone42r_persona_recalibration_package_v1.json",
    "M43R": "deliveries/archive/milestones/milestone43r_new_prospect_intake_schema/milestone43r_new_prospect_intake_schema_package_v1.json",
    "M44R": "deliveries/archive/milestones/milestone44r_new_trusted_prospect_trial/milestone44r_new_trusted_prospect_trial_package_v1.json",
    "M45R": "deliveries/archive/milestones/milestone45r_trusted_card_quality_review/milestone45r_trusted_card_quality_review_package_v1.json",
    "M46R": "deliveries/archive/milestones/milestone46r_trusted_pool_storage_design/milestone46r_trusted_pool_storage_design_package_v1.json",
    "M47R": "deliveries/archive/milestones/milestone47r_trusted_pool_product/milestone47r_trusted_pool_product_package_v1.json",
    "M48R": "deliveries/archive/milestones/milestone48r_expansion_runbook/milestone48r_expansion_runbook_package_v1.json",
    "M16": "deliveries/archive/handoffs/milestone16_project_readiness_check_v1.json",
    "M14.2_gate": "deliveries/archive/repairs/milestone14_2_intake_quality_gate_check_v1.json",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build autonomous milestone status panel.")
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    return parser


def _load_json(path: str) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _promote_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("batch_summary") if isinstance(payload.get("batch_summary"), dict) else {}
    return {
        "result_count": len(payload.get("results") or []),
        "allow": int(summary.get("allow") or 0),
        "warn": int(summary.get("warn") or 0),
        "block": int(summary.get("block") or 0),
        "write_back_enabled": bool((payload.get("write_back") or {}).get("enabled")),
    }


def _writeback_summary(payload: dict[str, Any], post_integrity: dict[str, Any]) -> dict[str, Any]:
    enrich_writeback = ((payload.get("enrich") or {}).get("write_back") or {})
    promote_writeback = ((payload.get("promote") or {}).get("write_back") or {})
    return {
        "mode": payload.get("mode") or "",
        "status": payload.get("status") or "",
        "enrich_writeback_enabled": bool(enrich_writeback.get("enabled")),
        "enrich_profile_updates": int(enrich_writeback.get("profile_updates") or 0),
        "enrich_main_updates": int(enrich_writeback.get("main_updates") or 0),
        "enrich_main_shared_updates": int(enrich_writeback.get("main_shared_updates") or 0),
        "enrich_queue_items_created": int(enrich_writeback.get("queue_items_created") or 0),
        "enrich_evidence_items_created": int(enrich_writeback.get("evidence_items_created") or 0),
        "promote_writeback_enabled": bool(promote_writeback.get("enabled")),
        "promoted": int(promote_writeback.get("promoted") or 0),
        "skipped": int(promote_writeback.get("skipped") or 0),
        "post_workbook_integrity_ok": bool((post_integrity.get("report") or {}).get("ok")),
        "lock_acquired": bool(enrich_writeback.get("workbook_lock_acquired") or promote_writeback.get("workbook_lock_acquired")),
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Milestone 16.2-自治运行状态面板-v1",
        "",
        f"- 生成时间：`{payload['generated_at']}`",
        f"- 总结论：`{payload['overall_status']}`",
        f"- 当前建议：{payload['recommended_next_action']}",
        "",
        "## 里程碑状态",
        "",
    ]
    for key, item in payload["milestones"].items():
        lines.append(f"- {key}：`{item}`")
    lines.extend(["", "## 写回边界", ""])
    for item in payload["writeback_boundaries"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 下一步命令", ""])
    for command in payload["next_commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    loaded = {key: _load_json(path) for key, path in SOURCE_FILES.items()}
    milestones = {
        "M12": _promote_summary(loaded["M12"]),
        "M13": _promote_summary(loaded["M13"]),
        "M14_before_patch": _promote_summary(loaded["M14"]),
        "M14_2_after_patch": _promote_summary(loaded["M14.2"]),
        "M14_3_preflight": (loaded["M14.3"].get("summary") or {}),
        "M15_2_share": (loaded["M15.2"].get("summary") or {}),
        "M17": (loaded.get("M17") or {}).get("summary") or {},
        "M18": (loaded.get("M18") or {}).get("summary") or {},
        "M19": (loaded.get("M19") or {}).get("summary") or {},
        "M20": _promote_summary(loaded.get("M20") or {}),
        "M20_gate_ok": bool((loaded.get("M20_gate") or {}).get("ok")),
        "M23A": (loaded.get("M23A") or {}).get("summary") or {},
        "M21": (loaded.get("M21") or {}).get("summary") or {},
        "M21R": (loaded.get("M21R") or {}).get("summary") or {},
        "M22R": (loaded.get("M22R") or {}).get("summary") or {},
        "M22R_gate_ok": bool((loaded.get("M22R_gate") or {}).get("ok")),
        "M23R": (loaded.get("M23R") or {}).get("summary") or {},
        "M24R": (loaded.get("M24R") or {}).get("summary") or {},
        "M25R": (loaded.get("M25R") or {}).get("summary") or {},
        "M25R_patch": (loaded.get("M25R_patch") or {}).get("summary") or {},
        "M25R_writeback": _writeback_summary(loaded.get("M25R_run") or {}, loaded.get("M25R_post_integrity") or {}),
        "M25R_gate_ok": bool((loaded.get("M25R_gate") or {}).get("ok")),
        "M25R_review": (loaded.get("M25R_review") or {}).get("summary") or {},
        "M26R": (loaded.get("M26R") or {}).get("summary") or {},
        "M27R": (loaded.get("M27R") or {}).get("summary") or {},
        "M28R": (loaded.get("M28R") or {}).get("summary") or {},
        "M28R_writeback": _writeback_summary(loaded.get("M28R_run") or {}, loaded.get("M28R_post_integrity") or {}),
        "M28R_gate_ok": bool((loaded.get("M28R_gate") or {}).get("ok")),
        "M30R": (loaded.get("M30R") or {}).get("summary") or {},
        "M31R": (loaded.get("M31R") or {}).get("summary") or {},
        "M32R": (loaded.get("M32R") or {}).get("summary") or {},
        "M33R": (loaded.get("M33R") or {}).get("summary") or {},
        "M34R": (loaded.get("M34R") or {}).get("summary") or {},
        "M34R_true_repair": (loaded.get("M34R_true_repair") or {}).get("summary") or {},
        "M35R": (loaded.get("M35R") or {}).get("summary") or {},
        "M35R_true_repair": (loaded.get("M35R_true_repair") or {}).get("summary") or {},
        "M36R": (loaded.get("M36R") or {}).get("summary") or {},
        "M37R": (loaded.get("M37R") or {}).get("summary") or {},
        "M38R": (loaded.get("M38R") or {}).get("summary") or {},
        "M40R": (loaded.get("M40R") or {}).get("summary") or {},
        "M41R": (loaded.get("M41R") or {}).get("summary") or {},
        "M42R": (loaded.get("M42R") or {}).get("summary") or {},
        "M43R": (loaded.get("M43R") or {}).get("summary") or {},
        "M44R": (loaded.get("M44R") or {}).get("summary") or {},
        "M45R": (loaded.get("M45R") or {}).get("summary") or {},
        "M46R": (loaded.get("M46R") or {}).get("summary") or {},
        "M47R": (loaded.get("M47R") or {}).get("summary") or {},
        "M48R": (loaded.get("M48R") or {}).get("summary") or {},
        "M16_readiness_ok": bool(loaded["M16"].get("ok")),
        "M14_2_gate_ok": bool(loaded["M14.2_gate"].get("ok")),
    }
    m142 = milestones["M14_2_after_patch"]
    has_allow = int(m142.get("allow") or 0) > 0
    m17_done = bool((milestones.get("M17") or {}).get("writeback_executed"))
    m18_ready = int((milestones.get("M18") or {}).get("share_ready_count") or 0) == 15
    m19_ready = int((milestones.get("M19") or {}).get("feedback_item_count") or 0) == 15
    m20_ready = int((milestones.get("M20") or {}).get("result_count") or 0) == 30 and int((milestones.get("M20") or {}).get("block") or 0) == 0
    m23a_ready = int((milestones.get("M23A") or {}).get("account_count") or 0) == 15
    m21_ready = int((milestones.get("M21") or {}).get("account_count") or 0) == 30
    m21r_ready = int((milestones.get("M21R") or {}).get("trusted_match_ready_count") or 0) == 30
    m22r_ready = (
        int((milestones.get("M22R") or {}).get("admission_candidate_count") or 0) == 30
        and int((milestones.get("M22R") or {}).get("report_only_allow") or 0) == 30
        and bool(milestones.get("M22R_gate_ok"))
    )
    m23r_ready = (
        int((milestones.get("M23R") or {}).get("card_count") or 0) == 30
        and int((milestones.get("M23R") or {}).get("missing_strong_evidence_count") or 0) == 0
        and not bool((milestones.get("M23R") or {}).get("sales_action_terms_detected"))
    )
    m24r_ready = bool((milestones.get("M24R") or {}).get("no_write_proof_ok"))
    m25r_ready = (
        int((milestones.get("M25R") or {}).get("candidate_count") or 0) == 50
        and (milestones.get("M25R") or {}).get("report_only_status") == "not_run_pre_patch_required"
    )
    m25r_patch_ready = (
        int((milestones.get("M25R_patch") or {}).get("account_count") or 0) == 50
        and int((milestones.get("M25R_patch") or {}).get("official_source_ready_count") or 0) == 50
        and int((milestones.get("M25R_patch") or {}).get("report_only_block") or 0) == 0
        and bool(milestones.get("M25R_gate_ok"))
        and int((milestones.get("M25R_review") or {}).get("trusted_match_ready_count") or 0) == 50
    )
    m25r_writeback_executed = (
        (milestones.get("M25R_writeback") or {}).get("mode") == "write_back"
        and (milestones.get("M25R_writeback") or {}).get("status") == "success"
        and bool((milestones.get("M25R_writeback") or {}).get("enrich_writeback_enabled"))
        and bool((milestones.get("M25R_writeback") or {}).get("post_workbook_integrity_ok"))
    )
    m26r_ready = (
        int((milestones.get("M26R") or {}).get("card_count") or 0) == 50
        and int((milestones.get("M26R") or {}).get("missing_strong_evidence_count") or 0) == 0
        and not bool((milestones.get("M26R") or {}).get("formal_knowledge_write_enabled"))
    )
    m27r_ready = (
        int((milestones.get("M27R") or {}).get("account_count") or 0) == 50
        and int((milestones.get("M27R") or {}).get("confirm_active_candidate_count") or 0) == 50
        and not bool((milestones.get("M27R") or {}).get("true_writeback_enabled"))
    )
    m28r_ready = (
        int((milestones.get("M28R") or {}).get("admission_candidate_count") or 0) == 50
        and int((milestones.get("M28R") or {}).get("report_only_allow") or 0) == 50
        and int((milestones.get("M28R") or {}).get("report_only_block") or 0) == 0
        and bool(milestones.get("M28R_gate_ok"))
        and not bool((milestones.get("M28R") or {}).get("true_writeback_enabled"))
    )
    m28r_writeback_done = (
        (milestones.get("M28R_writeback") or {}).get("mode") == "write_back"
        and (milestones.get("M28R_writeback") or {}).get("status") == "success"
        and int((milestones.get("M28R_writeback") or {}).get("promoted") or 0) == 50
        and int((milestones.get("M28R_writeback") or {}).get("skipped") or 0) == 0
        and bool((milestones.get("M28R_writeback") or {}).get("post_workbook_integrity_ok"))
    )
    m30r_ready = (
        int((milestones.get("M30R") or {}).get("account_count") or 0) == 50
        and int((milestones.get("M30R") or {}).get("l3_share_ready_count") or 0) == 50
        and int((milestones.get("M30R") or {}).get("sample_count") or 0) == 15
        and bool((milestones.get("M30R") or {}).get("workbook_integrity_ok"))
    )
    m31r_ready = (
        int((milestones.get("M31R") or {}).get("sample_count") or 0) == 15
        and int((milestones.get("M31R") or {}).get("pending_business_feedback_count") or 0) == 15
        and bool((milestones.get("M31R") or {}).get("no_write_proof_ok"))
        and not bool((milestones.get("M31R") or {}).get("true_writeback_enabled"))
    )
    m32r_ready = (
        int((milestones.get("M32R") or {}).get("sample_count") or 0) == 15
        and bool((milestones.get("M32R") or {}).get("no_write_proof_ok"))
        and int((milestones.get("M32R") or {}).get("validation_error_count") or 0) == 0
        and not bool((milestones.get("M32R") or {}).get("true_writeback_enabled"))
    )
    m32r_analyzed = m32r_ready and int((milestones.get("M32R") or {}).get("business_reviewed_count") or 0) > 0
    m33r_ready = (
        int((milestones.get("M33R") or {}).get("main_row_count") or 0) > 0
        and bool((milestones.get("M33R") or {}).get("workbook_integrity_ok"))
        and not bool((milestones.get("M33R") or {}).get("true_writeback_enabled"))
        and not bool((milestones.get("M33R") or {}).get("destructive_action_enabled"))
    )
    m34r_ready = (
        int((milestones.get("M34R") or {}).get("duplicate_group_count") or 0) == 7
        and int((milestones.get("M34R") or {}).get("duplicate_rows_to_remove_count") or 0) == 7
        and int((milestones.get("M34R") or {}).get("missing_profile_patch_count") or 0) == 78
        and int((milestones.get("M34R") or {}).get("shared_projection_row_count") or 0)
        == int((milestones.get("M34R") or {}).get("deduped_main_row_count") or 0)
        and bool((milestones.get("M34R") or {}).get("workbook_integrity_ok"))
        and not bool((milestones.get("M34R") or {}).get("true_writeback_enabled"))
        and not bool((milestones.get("M34R") or {}).get("destructive_action_enabled"))
        and not bool((milestones.get("M34R") or {}).get("shared_overwrite_enabled"))
    )
    m34r_true_repair_done = (
        bool((milestones.get("M34R_true_repair") or {}).get("true_repair_executed"))
        and int((milestones.get("M34R_true_repair") or {}).get("duplicate_rows_deleted") or 0) == 7
        and int((milestones.get("M34R_true_repair") or {}).get("profile_rows_appended") or 0) == 78
        and (milestones.get("M34R_true_repair") or {}).get("post_main_duplicate_group_count") == 0
        and (milestones.get("M34R_true_repair") or {}).get("post_main_not_in_profile_count") == 0
        and int((milestones.get("M34R_true_repair") or {}).get("post_shared_row_count") or 0) == 568
        and bool((milestones.get("M34R_true_repair") or {}).get("post_workbook_integrity_ok"))
    )
    m35r_ready = (
        bool((milestones.get("M35R") or {}).get("workbook_integrity_ok"))
        and int((milestones.get("M35R") or {}).get("source_shared_mismatch_account_count") or 0) == 68
        and (milestones.get("M35R") or {}).get("shared_manual_review_item_count") == 0
        and not bool((milestones.get("M35R") or {}).get("true_writeback_enabled"))
        and not bool((milestones.get("M35R") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M35R") or {}).get("persona_registry_write_enabled"))
    )
    m35r_true_repair_done = (
        bool((milestones.get("M35R_true_repair") or {}).get("true_field_repair_executed"))
        and int((milestones.get("M35R_true_repair") or {}).get("updated_account_count") or 0) == 64
        and int((milestones.get("M35R_true_repair") or {}).get("updated_field_count") or 0) == 320
        and bool((milestones.get("M35R") or {}).get("workbook_integrity_ok"))
        and int((milestones.get("M35R") or {}).get("source_profile_mismatch_account_count") or -1) == 5
        and (milestones.get("M35R") or {}).get("safe_profile_patch_field_count") == 0
        and not bool((milestones.get("M35R_true_repair") or {}).get("shared_reverse_overwrite_enabled"))
        and not bool((milestones.get("M35R_true_repair") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M35R_true_repair") or {}).get("persona_registry_write_enabled"))
    )
    m36r_ready = (
        int((milestones.get("M36R") or {}).get("manual_review_account_count") or 0) == 5
        and int((milestones.get("M36R") or {}).get("manual_review_item_count") or 0) == 15
        and int((milestones.get("M36R") or {}).get("shared_placeholder_diff_count") or 0) == 131
        and bool((milestones.get("M36R") or {}).get("workbook_integrity_ok"))
        and not bool((milestones.get("M36R") or {}).get("true_writeback_enabled"))
        and not bool((milestones.get("M36R") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M36R") or {}).get("persona_registry_write_enabled"))
    )
    m37r_ready = (
        int((milestones.get("M37R") or {}).get("confirmation_account_count") or 0) == 5
        and int((milestones.get("M37R") or {}).get("confirmation_item_count") or 0) == 15
        and int((milestones.get("M37R") or {}).get("suggested_sync_item_count") or 0) == 8
        and int((milestones.get("M37R") or {}).get("suggested_alias_item_count") or 0) == 2
        and int((milestones.get("M37R") or {}).get("suggested_hold_item_count") or 0) == 5
        and bool((milestones.get("M37R") or {}).get("workbook_integrity_ok"))
        and not bool((milestones.get("M37R") or {}).get("true_writeback_enabled"))
        and not bool((milestones.get("M37R") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M37R") or {}).get("persona_registry_write_enabled"))
    )
    m38r_closed = (
        (milestones.get("M38R") or {}).get("row_level_governance_status") == "closed"
        and (milestones.get("M38R") or {}).get("governance_blocker_count") == 0
        and int((milestones.get("M38R") or {}).get("non_blocking_variance_count") or 0) == 15
        and bool((milestones.get("M38R") or {}).get("project_can_continue_to_core_pipeline"))
        and bool((milestones.get("M38R") or {}).get("workbook_integrity_ok"))
        and not bool((milestones.get("M38R") or {}).get("true_writeback_enabled"))
    )
    m40r_restart_ready = (
        (milestones.get("M40R") or {}).get("legacy_isolation_status") == "active"
        and (milestones.get("M40R") or {}).get("new_pool_entry_mode") == "evidence_first"
        and not bool((milestones.get("M40R") or {}).get("shared_view_in_core_pipeline"))
        and not bool((milestones.get("M40R") or {}).get("legacy_profile_in_trusted_decision"))
        and not bool((milestones.get("M40R") or {}).get("legacy_main_in_trusted_decision"))
        and bool((milestones.get("M40R") or {}).get("workbook_integrity_ok"))
        and not bool((milestones.get("M40R") or {}).get("true_writeback_enabled"))
    )
    m41r_source_inventory_ready = (
        int((milestones.get("M41R") or {}).get("source_root_count") or 0) == 3
        and int((milestones.get("M41R") or {}).get("total_material_count") or 0) >= 700
        and int((milestones.get("M41R") or {}).get("learnable_queue_count") or 0) > 0
        and bool((milestones.get("M41R") or {}).get("registry_available"))
        and not any(((milestones.get("M41R") or {}).get("no_write_proof") or {}).values())
    )
    m42r_persona_recalibration_ready = (
        int((milestones.get("M42R") or {}).get("persona_count") or 0) > 0
        and int((milestones.get("M42R") or {}).get("source_supported_count") or 0) > 0
        and bool((milestones.get("M42R") or {}).get("no_write_proof_ok"))
        and not bool((milestones.get("M42R") or {}).get("registry_write_enabled"))
        and not bool((milestones.get("M42R") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M42R") or {}).get("prospect_generation_enabled"))
    )
    m43r_intake_schema_ready = (
        int((milestones.get("M43R") or {}).get("intake_required_field_count") or 0) > 0
        and int((milestones.get("M43R") or {}).get("evidence_required_field_count") or 0) > 0
        and bool((milestones.get("M43R") or {}).get("guard_detected_missing_evidence"))
        and bool((milestones.get("M43R") or {}).get("guard_detected_legacy_field"))
        and bool((milestones.get("M43R") or {}).get("no_write_proof_ok"))
        and not bool((milestones.get("M43R") or {}).get("old_workbook_write_enabled"))
        and not bool((milestones.get("M43R") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M43R") or {}).get("persona_registry_write_enabled"))
    )
    m44r_new_trusted_trial_ready = (
        20 <= int((milestones.get("M44R") or {}).get("candidate_count") or 0) <= 30
        and int((milestones.get("M44R") or {}).get("trusted_match_ready_count") or 0) >= 20
        and int((milestones.get("M44R") or {}).get("official_or_strong_evidence_count") or 0) >= 20
        and int((milestones.get("M44R") or {}).get("validation_error_count") or 0) == 0
        and bool((milestones.get("M44R") or {}).get("no_write_proof_ok"))
        and not bool((milestones.get("M44R") or {}).get("old_workbook_write_enabled"))
        and not bool((milestones.get("M44R") or {}).get("knowledge_asset_write_enabled"))
        and not bool((milestones.get("M44R") or {}).get("persona_registry_write_enabled"))
    )
    m45r_quality_review_ready = (
        10 <= int((milestones.get("M45R") or {}).get("sample_count") or 0) <= 15
        and int((milestones.get("M45R") or {}).get("quality_pass_count") or 0) == int((milestones.get("M45R") or {}).get("sample_count") or -1)
        and (milestones.get("M45R") or {}).get("human_feedback_status") == "pending"
        and bool((milestones.get("M45R") or {}).get("no_write_proof_ok"))
    )
    m46r_storage_design_ready = (
        bool((milestones.get("M46R") or {}).get("storage_design_ready"))
        and not bool((milestones.get("M46R") or {}).get("legacy_excel_primary_store"))
        and bool((milestones.get("M46R") or {}).get("new_formal_workbook_requires_confirmation"))
        and bool((milestones.get("M46R") or {}).get("no_write_proof_ok"))
    )
    m47r_product_ready = (
        int((milestones.get("M47R") or {}).get("trusted_pool_count") or 0) == 20
        and int((milestones.get("M47R") or {}).get("share_view_count") or 0) == 20
        and int((milestones.get("M47R") or {}).get("source_trace_count") or 0) == 20
        and bool((milestones.get("M47R") or {}).get("no_write_proof_ok"))
    )
    m48r_runbook_ready = (
        bool((milestones.get("M48R") or {}).get("readiness_check_pass"))
        and bool((milestones.get("M48R") or {}).get("handoff_ready"))
        and bool((milestones.get("M48R") or {}).get("quality_gate_pass"))
        and bool((milestones.get("M48R") or {}).get("no_write_proof_ok"))
    )
    payload = {
        "batch_id": "milestone16_2_autonomous_status_panel_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": SOURCE_FILES,
        "overall_status": (
            "PASS_M48R_EVIDENCE_FIRST_RUNBOOK_READY"
            if milestones["M16_readiness_ok"] and m40r_restart_ready and m41r_source_inventory_ready and m42r_persona_recalibration_ready and m43r_intake_schema_ready and m44r_new_trusted_trial_ready and m45r_quality_review_ready and m46r_storage_design_ready and m47r_product_ready and m48r_runbook_ready
            else
            "PASS_M47R_TRUSTED_POOL_PRODUCT_READY"
            if milestones["M16_readiness_ok"] and m44r_new_trusted_trial_ready and m45r_quality_review_ready and m46r_storage_design_ready and m47r_product_ready
            else
            "PASS_M46R_TRUSTED_POOL_STORAGE_DESIGNED"
            if milestones["M16_readiness_ok"] and m44r_new_trusted_trial_ready and m45r_quality_review_ready and m46r_storage_design_ready
            else
            "PASS_M45R_TRUSTED_CARD_QUALITY_READY"
            if milestones["M16_readiness_ok"] and m44r_new_trusted_trial_ready and m45r_quality_review_ready
            else
            "PASS_M44R_NEW_TRUSTED_PROSPECT_TRIAL_READY"
            if milestones["M16_readiness_ok"] and m40r_restart_ready and m41r_source_inventory_ready and m42r_persona_recalibration_ready and m43r_intake_schema_ready and m44r_new_trusted_trial_ready
            else
            "PASS_M43R_NEW_INTAKE_SCHEMA_READY"
            if milestones["M16_readiness_ok"] and m40r_restart_ready and m41r_source_inventory_ready and m42r_persona_recalibration_ready and m43r_intake_schema_ready
            else
            "PASS_M42R_PERSONA_RECALIBRATION_READY"
            if milestones["M16_readiness_ok"] and m40r_restart_ready and m41r_source_inventory_ready and m42r_persona_recalibration_ready
            else
            "PASS_M41R_SOURCE_MATERIAL_INVENTORY_READY"
            if milestones["M16_readiness_ok"] and m40r_restart_ready and m41r_source_inventory_ready
            else
            "PASS_M40R_TRUSTED_POOL_RESTART_READY"
            if milestones["M16_readiness_ok"] and m40r_restart_ready
            else
            "PASS_M38R_GOVERNANCE_CLOSED_CORE_PIPELINE_READY"
            if milestones["M16_readiness_ok"] and m38r_closed
            else
            "PASS_M37R_FINAL_FIELD_CONFIRMATION_READY"
            if milestones["M16_readiness_ok"] and m37r_ready
            else
            "PASS_M36R_MANUAL_FIELD_REVIEW_READY"
            if milestones["M16_readiness_ok"] and m36r_ready
            else
            "PASS_M35R_SAFE_PROFILE_FIELD_REPAIR_COMPLETED"
            if milestones["M16_readiness_ok"] and m35r_true_repair_done
            else
            "PASS_M35R_FIELD_GOVERNANCE_ADMISSION_READY"
            if milestones["M16_readiness_ok"] and m35r_ready
            else
            "PASS_M34R_GOVERNANCE_TRUE_REPAIR_COMPLETED"
            if milestones["M16_readiness_ok"] and m34r_true_repair_done
            else
            "PASS_M34R_GOVERNANCE_REPAIR_ADMISSION_READY"
            if milestones["M16_readiness_ok"] and m34r_ready
            else
            "PASS_M33R_WORKBOOK_GOVERNANCE_AUDIT_READY"
            if milestones["M16_readiness_ok"] and m33r_ready
            else
            "PASS_M32R_FEEDBACK_ANALYZED"
            if milestones["M16_readiness_ok"] and m32r_analyzed
            else
            "PASS_M32R_FEEDBACK_COLLECTION_READY"
            if milestones["M16_readiness_ok"] and m32r_ready
            else
            "PASS_M31R_FEEDBACK_LOOP_READY"
            if milestones["M16_readiness_ok"] and m30r_ready and m31r_ready
            else
            "PASS_M30R_POST_WRITEBACK_REVIEW_READY"
            if milestones["M16_readiness_ok"] and m28r_writeback_done and m30r_ready
            else
            "PASS_M28R_PROMOTE_WRITEBACK_COMPLETED"
            if milestones["M16_readiness_ok"] and m28r_writeback_done
            else
            "PASS_M25R_PROMOTE_WRITEBACK_ADMISSION_READY"
            if milestones["M16_readiness_ok"] and m25r_writeback_executed and m26r_ready and m27r_ready and m28r_ready
            else
            "PASS_EXPANSION_ENRICH_WRITEBACK_COMPLETED_PROMOTE_PENDING"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready and m22r_ready and m23r_ready and m24r_ready and m25r_patch_ready and m25r_writeback_executed
            else
            "PASS_WRITEBACK_COMPLETED"
            if milestones["M16_readiness_ok"] and milestones["M14_2_gate_ok"] and m17_done and not m18_ready
            else "PASS_L3_OPERATIONALIZED"
            if milestones["M16_readiness_ok"] and milestones["M14_2_gate_ok"] and m17_done and m18_ready and not m19_ready
            else "PASS_FEEDBACK_LOOP_READY"
            if milestones["M16_readiness_ok"] and milestones["M14_2_gate_ok"] and m17_done and m18_ready and m19_ready and not m20_ready
            else "PASS_EXPANSION_TRUSTED_REVIEW_READY"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready and m22r_ready and m23r_ready and m24r_ready and m25r_patch_ready
            else "PASS_EXPANSION_PREFLIGHT_READY"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready and m22r_ready and m23r_ready and m24r_ready and m25r_ready
            else "PASS_TRUSTED_PRODUCTIZED_AND_GOVERNED"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready and m22r_ready and m23r_ready and m24r_ready
            else "PASS_TRUSTED_SUMMARY_READY"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready and m22r_ready and m23r_ready
            else "PASS_TRUSTED_WRITEBACK_ADMISSION_READY"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready and m22r_ready
            else "PASS_TRUSTED_MATCH_READY"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m21r_ready
            else "PASS_TRUSTED_MATCH_PLANNED"
            if milestones["M16_readiness_ok"] and m17_done and m18_ready and m20_ready and m23a_ready and m21_ready
            else "PASS_BATCH_INTAKE_READY"
            if milestones["M16_readiness_ok"] and milestones["M14_2_gate_ok"] and m17_done and m18_ready and m19_ready and m20_ready and milestones["M20_gate_ok"]
            else ("PASS_NON_WRITEBACK" if milestones["M16_readiness_ok"] and milestones["M14_2_gate_ok"] else "CHECK_REQUIRED")
        ),
        "recommended_next_action": "M48R 已完成 evidence-first 首批可信池与长期运行机制：下一步建议进入 M49R，按阈值扩容 30-50 家，仍先 report/product 化，不默认写回正式工作簿。"
        if m48r_runbook_ready
        else "M47R 已形成独立 trusted_prospect_pool_v1、共享视图和来源索引；下一步进入 M48R 扩容阈值与长期运行机制。"
        if m47r_product_ready
        else "M46R 已明确新可信池承载方式：下一步进入 M47R，形成可给人使用的 trusted_prospect_pool_v1 与 share view。"
        if m46r_storage_design_ready
        else "M45R 已完成 15 张摘要卡可读性质量验证：下一步进入 M46R，确定新可信池独立承载/导出方案。"
        if m45r_quality_review_ready
        else "M44R 已完成首批 20 家新可信潜客试运行：下一步进入 M45R，抽样验证摘要卡是否可读、可信、可判断；仍不写旧主表。"
        if m44r_new_trusted_trial_ready
        else "M43R 已完成新可信潜客 intake schema 和门禁校验：下一步进入 M44R，首批 20-30 家只按 evidence-first 生成候选、证据包和摘要卡，不写旧主表。"
        if m43r_intake_schema_ready
        else "M42R 已完成画像证据映射和刷新 proposal：下一步进入 M43R，落地新可信潜客 intake schema/校验器；M44R 只优先使用 source_supported 画像做首批试运行。"
        if m42r_persona_recalibration_ready
        else "M41R 已完成原素材盘点与可学习素材分层：下一步进入 M42R，用真实客户案例/解决方案校准画像证据映射，只生成 proposal，不覆盖正式知识资产。"
        if m41r_source_inventory_ready
        else "M40R 已完成 legacy 隔离和 evidence-first 重启：下一步进入 M41R，先盘点原始学习素材并生成可执行学习清单，不直接产出潜客。"
        if m40r_restart_ready
        else "M38R 已将三表治理收口为非阻塞：下一步回到核心主线，做当前可信潜客池质量面板、业务反馈输入和下一批扩容阈值，而不是继续抠低价值字段差异。"
        if m38r_closed
        else "M37R 已生成最终字段确认表：5 家/15 字段待人工填写；填写后才能进入最终 profile 修复，未填写前不继续扩容也不写回。"
        if m37r_ready
        else "M36R 已完成人工字段复核包和共享占位口径固化：剩余 5 家/15 字段需人工确认；默认不继续扩容，先做人工确认或接受共享版占位审计解释。"
        if m36r_ready
        else "M35R 安全 profile 字段修复已完成：64 家/320 字段已补齐，profile mismatch 降至 5 家且均为人工复核项；下一步建议进入 M36R 人工复核队列或共享版占位口径说明固化。"
        if m35r_true_repair_done
        else "M35R 已完成字段级差异治理准入包：64 家 profile 可安全补齐，15 个字段需人工复核，共享版差异已解释为生成视图占位；真实字段写回仍需用户单独确认。"
        if m35r_ready
        else "M34R 真实三表治理修复已完成：重复和缺档案已清零，共享版已重建；下一步建议进入 M35R 字段级差异治理与共享版字段口径收敛。"
        if m34r_true_repair_done
        else "M34R 已完成三表治理安全修复准入包：去重、补档案、共享版重建均已形成可复核方案；真实修表仍需用户单独确认。"
        if m34r_ready
        else "M33R 已完成三表口径治理审计；下一步应先处理 account_id 重复、缺档案和共享版重建计划，再继续规模化扩容。"
        if m33r_ready
        else "M32R 已完成反馈采集与质量验证闭环，已有业务反馈可分析；下一步进入 M33R 扩容质量阈值定义。"
        if m32r_analyzed
        else "M32R 已完成反馈采集模板与空反馈校验：15 家均 pending，no-write proof PASS；下一步等待业务填写反馈，或进入 M33R 先定义扩容质量阈值。"
        if m32r_ready
        else "M31R 已完成业务反馈闭环准备：15 家抽样均待业务反馈，no-write proof PASS；下一步应收集反馈，或进入 M32R 规模化扩容前的质量阈值定义。"
        if m31r_ready
        else "M30R 已完成写回后 50 家可消费池复核和 15 家业务抽样评估模板；下一步应收集业务反馈，形成 M31R 反馈闭环与规则校准建议。"
        if m30r_ready
        else "M28R 真实 promote 写回已完成：promoted=50、skipped=0、workbook integrity PASS；下一步进入 M30R 写回后可消费池复核与业务抽样评估。"
        if m28r_writeback_done
        else "M28R 已形成 M25R 二次 promote 写回准入材料：report-only allow=50、gate PASS；如要真实 promote 写回，必须再次由用户单独确认。"
        if m28r_ready
        else "M25R 已执行真实 write_back：enrich 补证/核心信息写入成功，promote 因 warn=50 安全跳过；下一步应生成 M25R 可信潜客摘要/share view，并决定是否做画像确认解 warn。"
        if m25r_writeback_executed
        else "M17 已完成真实写回；下一步进入写回后复核和 M18 运营化。"
        if m17_done and not m18_ready
        else "M18 已形成首批 L3 可消费池；下一步进入 M19 扩容节奏与业务使用反馈闭环。"
        if m18_ready and not m19_ready
        else "M19 已形成反馈模板和下一轮 30 家补证试运行计划；下一步进入 M20 批量补证自动化。"
        if m19_ready and not m20_ready
        else "M20 已完成 30 家补证 report-only/gate；下一步进入 M21 人工确认或写回准入试点。"
        if m20_ready and not (m23a_ready and m21_ready)
        else "M25R 已完成 50 家补证、report-only/gate 和可信画像复核：block=0，trusted_match_ready=50；真实 write_back 仍需用户单独确认。"
        if m25r_patch_ready
        else "M25R 已完成 50 家扩容预检，全部 needs_patch；下一步应补官方来源与核心字段后再 report-only。"
        if m25r_ready
        else "M24R 已完成来源治理与 no-write proof；下一步进入 M25R 扩容预检或补源任务。"
        if m24r_ready
        else "M23R 已形成 30 张可信潜客摘要卡；下一步进入 M24R 来源治理，避免潜客观察污染知识资产。"
        if m23r_ready
        else "M22R 已形成 30 家可信潜客写回准入材料，report-only/gate 均 PASS；下一步进入 M23R 摘要层或 M24R 来源治理；真实 write_back 仍需用户单独确认。"
        if m22r_ready
        else "M21R 已确认 30 家 trusted_match_ready；下一步进入 M22R 写回准入材料与非写回 gate。"
        if m21r_ready
        else "M23A/M21 已生成但已降级为可读性参考；下一步进入 M21R 可信画像匹配复核，只有 trusted_match_ready 才进入 M22R 写回准入。"
        if m23a_ready and m21_ready
        else ("进入 M17 写回候选准入材料，但不执行真实 write_back。" if has_allow else "继续候选质量治理；暂不进入写回。"),
        "milestones": milestones,
        "writeback_boundaries": [
            "M25R 已在用户确认后执行真实 write_back：enrich 写入补证与核心信息；promote 未上移，skipped=50。",
            "M28R 已在用户确认后执行真实 promote write_back：promoted=50，skipped=0。",
            "本轮未批量将 pending_review 转 active。",
            "M23A/M21 只作为可读性参考；主写回准入应以 M21R 的 trusted_match_ready 为准。",
            "M22R 已生成 active fact patch 仅用于 report-only/gate 验证；不等于已写回。",
            "潜客批次产物只能形成 candidate_observation/source_gap/rule_calibration_proposal，不能直接写入正式知识资产或画像正例。",
            "M34R 仅生成三表治理安全修复准入包和共享版预览，不删除主表重复行、不补写档案库、不覆盖共享版。",
            "M34R true repair 已在用户确认后执行：主表去重、档案库补 stub、共享版重建；未写入知识资产注册表或画像注册表。",
            "M35R 仅生成字段级差异治理准入包；profile 字段真实补齐仍需用户单独确认，共享版差异不得反向覆盖主表。",
            "M35R true repair 已在用户确认后执行：仅补齐 profile 安全空字段，未处理人工复核项，未让共享版反向覆盖主表。",
            "M36R 仅生成人工复核队列和共享版占位口径说明；不自动处理仍需人工确认的 profile 差异。",
            "M37R 仅生成最终确认表；human_decision 未填写前，不生成最终写回 patch。",
            "M38R 已将剩余 5 家/15 字段登记为非阻塞差异；不再要求用户逐字段确认，主线可继续。",
            "M40R 已将旧主表/档案/共享版降级为 legacy/reference/export；新可信池必须走 evidence-first。",
            "M41R 只盘点原素材和学习队列，不生成潜客、不写知识资产、不改画像 registry。",
            "M42R 只生成画像证据映射和刷新 proposal，不覆盖正式画像 registry。",
            "M43R 只生成新可信潜客 intake/schema/validator，不继承旧档案字段。",
            "M44R 只生成新可信潜客候选、证据包和摘要卡；不写旧主表、不写知识资产。",
            "M45R 只做卡片质量抽样和反馈模板；无人工反馈时不生成 accepted/rejected。",
            "M46R-M47R 采用独立 trusted_prospect_pool_v1 产物，不复用旧 Excel 作为主存储。",
            "M48R 只固化扩容阈值和 runbook，不触发真实写回。",
            "任何真实工作簿 write_back 仍需用户单独确认。",
        ],
        "next_commands": [
            "python3 scripts/build_m48r_expansion_runbook.py",
            "python3 scripts/build_m47r_trusted_pool_product.py",
            "python3 scripts/build_m46r_trusted_pool_storage_design.py",
            "python3 scripts/build_m45r_trusted_card_quality_review.py",
            "python3 scripts/build_m44r_new_trusted_prospect_trial.py",
            "python3 scripts/build_m43r_new_prospect_intake_schema.py",
            "python3 scripts/build_m42r_persona_recalibration_package.py",
            "python3 scripts/build_m41r_source_material_inventory.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/build_m40r_trusted_pool_restart_package.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/build_m38r_governance_closure_package.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/build_m37r_final_field_confirmation_package.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/build_m36r_manual_field_review_package.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/build_m35r_field_governance_package.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/build_m34r_workbook_governance_repair_admission.py",
            "python3 scripts/build_trusted_match_review_package.py",
            "python3 scripts/build_trusted_writeback_admission_package.py",
            "python3 scripts/run_execution_batch.py --config-file configs/execution_batches/milestone22r_trusted_writeback_admission_registry_v1.json --report-only",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/pre_writeback_gate_check.py --candidate-file deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_candidates_v1.json --baseline-file deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_admission_report_baseline_v1.json --run-summary-file deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_admission_run_summary_v1.json --promote-file deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_admission_promote_v1.json --output-json deliveries/archive/repairs/milestone22r_trusted_writeback_admission_gate_check_v1.json --output-md 'docs/03-执行与校验/Milestone 22R-可信潜客写回前闸门检查-v1.md'",
            "python3 scripts/build_trusted_prospect_summary_package.py",
            "python3 scripts/build_knowledge_source_governance_package.py",
            "python3 scripts/build_trusted_expansion_preflight_package.py",
            "python3 scripts/build_trusted_expansion_intake_patch.py",
            "STATIC_POOL_ROOT='/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池' python3 scripts/run_execution_batch.py --config-file configs/execution_batches/milestone25r_trusted_expansion_registry_v1.json --report-only",
            "python3 scripts/build_trusted_expansion_review_package.py",
            "python3 scripts/run_project_readiness_check.py",
        ],
    }
    _write_json(args.output_json, payload)
    _write_text(args.output_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "overall_status": payload["overall_status"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
