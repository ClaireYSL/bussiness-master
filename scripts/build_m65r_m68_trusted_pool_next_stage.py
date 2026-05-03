from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M65 = MILESTONES / "milestone65r_trusted_pool_runner_v3"
M66 = MILESTONES / "milestone66r_trusted_pool_storage_layer"
M67 = MILESTONES / "milestone67r_vault_output_closure"
M68 = MILESTONES / "milestone68r_evidence_first_expansion"
C6 = MILESTONES / "workspace_cleanup_c6_long_term_governance"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
TRUSTED_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
SOURCE_TRACE = MILESTONES / "milestone52r_second_evidence_patch/source_trace_index_v2.json"
M25_PATCH = MILESTONES / "milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_intake_patch_v1.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> list[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout.splitlines()


def account_to_pool_item(account: dict[str, Any]) -> dict[str, Any]:
    fields = account.get("main_fields") or {}
    evidence_rows = account.get("evidence_rows") or account.get("rectification", {}).get("evidence_rows") or []
    first_source = next((row for row in evidence_rows if str(row.get("source_locator") or "").startswith("http")), {})
    return {
        "prospect_id": f"m68r_{account.get('account_id')}",
        "source_account_id": account.get("account_id"),
        "company_name": account.get("account_name"),
        "matched_persona": fields.get("persona_tag") or account.get("persona"),
        "trusted_status": "candidate_seed",
        "level": "L5",
        "match_reason": fields.get("admission_reason_summary"),
        "core_product_service_summary": fields.get("公司产品与服务概述"),
        "business_model_summary": fields.get("商业模式概述"),
        "risk_or_gap": fields.get("validation_gap"),
        "source_locator": first_source.get("source_locator"),
        "evidence_strength": first_source.get("source_type") or first_source.get("evidence_strength"),
    }


def account_to_source_trace_item(account: dict[str, Any]) -> dict[str, Any]:
    evidence_rows = account.get("evidence_rows") or account.get("rectification", {}).get("evidence_rows") or []
    sources = []
    for row in evidence_rows:
        sources.append(
            {
                "source_type": row.get("source_type"),
                "source_locator": row.get("source_locator"),
                "evidence_strength": row.get("source_type") or row.get("evidence_strength"),
                "supports_dimension": row.get("supports_dimension"),
                "summary": row.get("summary"),
            }
        )
    return {
        "prospect_id": f"m68r_{account.get('account_id')}",
        "company_name": account.get("account_name"),
        "source_count": len(sources),
        "sources": sources,
    }


def build_m68_inputs() -> tuple[Path, Path]:
    patch = read_json(M25_PATCH, {})
    accounts = (patch.get("accounts") or [])[:30]
    pool_items = [account_to_pool_item(account) for account in accounts]
    source_items = [account_to_source_trace_item(account) for account in accounts]
    pool_path = M68 / "m68r_expansion_trusted_pool_input_v1.json"
    source_path = M68 / "m68r_expansion_source_trace_v1.json"
    write_json(
        pool_path,
        {
            "generated_at": now(),
            "source_file": str(M25_PATCH.relative_to(WORKSPACE)),
            "summary": {"candidate_count": len(pool_items), "old_workbook_write_enabled": False},
            "items": pool_items,
        },
    )
    write_json(source_path, {"generated_at": now(), "items": source_items})
    return pool_path, source_path


def update_status_panel(m65: dict[str, Any], m66: dict[str, Any], m67: dict[str, Any], m68: dict[str, Any], c6: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel["generated_at"] = now()
    panel["overall_status"] = "PASS_M68R_EVIDENCE_FIRST_EXPANSION_READY"
    panel["latest_milestone"] = "M68R"
    panel["m65r_trusted_pool_runner_v3"] = m65.get("summary", {})
    panel["m66r_storage_layer"] = m66.get("summary", {})
    panel["m67r_vault_output_closure"] = m67.get("summary", {})
    panel["m68r_expansion"] = m68.get("summary", {})
    panel["c6_workspace_governance"] = c6.get("summary", {})
    panel["canonical_next_action"] = "下一步：对 M68R 的 L3 扩容样本补第二强来源，进入 L3->L2 持续升层。"
    panel["next_recommended_action"] = panel["canonical_next_action"]
    write_json(STATUS_PANEL, panel)


def main() -> int:
    for directory in (M65, M66, M67, M68, C6):
        directory.mkdir(parents=True, exist_ok=True)

    pool_path, source_path = build_m68_inputs()

    m65_report = M65 / "trusted_pool_runner_v3_report_v1.json"
    subprocess.run(
        [
            "python3",
            "scripts/trusted_pool_runner.py",
            "--mode",
            "report_only",
            "--output-file",
            str(m65_report.relative_to(WORKSPACE)),
            "--gap-queue-file",
            str((M65 / "static_gap_queue_v1.json").relative_to(WORKSPACE)),
            "--baseline-file",
            str((M65 / "trusted_pool_runner_baseline_v1.json").relative_to(WORKSPACE)),
            "--source-trace-output",
            str((M65 / "source_trace_normalized_v1.json").relative_to(WORKSPACE)),
            "--no-write-proof-file",
            str((M65 / "no_write_proof_v1.json").relative_to(WORKSPACE)),
            "--pool-diff-file",
            str((M65 / "pool_diff_report_v1.json").relative_to(WORKSPACE)),
            "--validation-report-file",
            str((M65 / "validation_report_v1.json").relative_to(WORKSPACE)),
            "--write-baseline",
        ],
        cwd=WORKSPACE,
        check=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/trusted_pool_runner.py",
            "--mode",
            "validate_only",
            "--output-file",
            str((M65 / "trusted_pool_runner_v3_validate_only_v1.json").relative_to(WORKSPACE)),
            "--gap-queue-file",
            str((M65 / "validate_only_gap_queue_v1.json").relative_to(WORKSPACE)),
            "--baseline-file",
            str((M65 / "trusted_pool_runner_baseline_v1.json").relative_to(WORKSPACE)),
            "--source-trace-output",
            str((M65 / "validate_only_source_trace_normalized_v1.json").relative_to(WORKSPACE)),
            "--no-write-proof-file",
            str((M65 / "validate_only_no_write_proof_v1.json").relative_to(WORKSPACE)),
            "--pool-diff-file",
            str((M65 / "validate_only_pool_diff_report_v1.json").relative_to(WORKSPACE)),
            "--validation-report-file",
            str((M65 / "validate_only_validation_report_v1.json").relative_to(WORKSPACE)),
            "--require-baseline",
        ],
        cwd=WORKSPACE,
        check=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/trusted_pool_runner.py",
            "--mode",
            "generate_vault_preview",
            "--output-file",
            str((M67 / "trusted_pool_runner_vault_preview_report_v1.json").relative_to(WORKSPACE)),
            "--gap-queue-file",
            str((M67 / "vault_preview_gap_queue_v1.json").relative_to(WORKSPACE)),
            "--source-trace-output",
            str((M67 / "vault_preview_source_trace_normalized_v1.json").relative_to(WORKSPACE)),
            "--no-write-proof-file",
            str((M67 / "vault_preview_no_write_proof_v1.json").relative_to(WORKSPACE)),
            "--pool-diff-file",
            str((M67 / "vault_preview_pool_diff_report_v1.json").relative_to(WORKSPACE)),
            "--validation-report-file",
            str((M67 / "vault_preview_validation_report_v1.json").relative_to(WORKSPACE)),
            "--vault-preview-dir",
            str((M67 / "vault_output_preview").relative_to(WORKSPACE)),
        ],
        cwd=WORKSPACE,
        check=True,
    )
    subprocess.run(
        [
            "python3",
            "scripts/trusted_pool_runner.py",
            "--mode",
            "report_only",
            "--trusted-pool",
            str(pool_path.relative_to(WORKSPACE)),
            "--source-trace",
            str(source_path.relative_to(WORKSPACE)),
            "--output-file",
            str((M68 / "m68r_expansion_static_promote_report_v1.json").relative_to(WORKSPACE)),
            "--gap-queue-file",
            str((M68 / "m68r_expansion_gap_queue_v1.json").relative_to(WORKSPACE)),
            "--source-trace-output",
            str((M68 / "m68r_expansion_source_trace_normalized_v1.json").relative_to(WORKSPACE)),
            "--no-write-proof-file",
            str((M68 / "m68r_expansion_no_write_proof_v1.json").relative_to(WORKSPACE)),
            "--pool-diff-file",
            str((M68 / "m68r_expansion_pool_diff_v1.json").relative_to(WORKSPACE)),
            "--validation-report-file",
            str((M68 / "m68r_expansion_validation_v1.json").relative_to(WORKSPACE)),
            "--write-baseline",
            "--baseline-file",
            str((M68 / "m68r_expansion_baseline_v1.json").relative_to(WORKSPACE)),
        ],
        cwd=WORKSPACE,
        check=True,
    )

    m65_data = read_json(m65_report, {})
    m66_diff = read_json(M65 / "pool_diff_report_v1.json", {})
    m67_data = read_json(M67 / "trusted_pool_runner_vault_preview_report_v1.json", {})
    m68_data = read_json(M68 / "m68r_expansion_static_promote_report_v1.json", {})

    m65 = {
        "milestone": "M65R",
        "generated_at": now(),
        "status": "PASS_M65R_TRUSTED_POOL_RUNNER_V3_READY",
        "summary": {
            "runner": m65_data.get("runner"),
            "mode": m65_data.get("mode"),
            "prospect_count": m65_data.get("summary", {}).get("prospect_count"),
            "level_counts": m65_data.get("summary", {}).get("level_counts"),
            "pool_diff_changed_count": m65_data.get("summary", {}).get("pool_diff_changed_count"),
        },
    }
    m66 = {
        "milestone": "M66R",
        "generated_at": now(),
        "status": "PASS_M66R_STORAGE_LAYER_POLICY_READY",
        "summary": {
            "canonical_pool": str(TRUSTED_POOL.relative_to(WORKSPACE)),
            "pool_diff_changed_count": m66_diff.get("changed_count"),
            "dynamic_field_write_enabled": False,
            "old_workbook_write_enabled": False,
        },
        "update_policy": {
            "allowed_fields": ["level", "trusted_status", "static_promotion_summary", "static_gap_count", "static_evidence_count", "static_strong_evidence_count"],
            "forbidden_field_groups": ["external_feedback_decision", "sales_action_priority", "owner_or_touch_timing"],
        },
    }
    m67 = {
        "milestone": "M67R",
        "generated_at": now(),
        "status": "PASS_M67R_VAULT_OUTPUT_CLOSURE_READY",
        "summary": {
            "vault_preview_count": m67_data.get("summary", {}).get("vault_preview_count"),
            "write_vault_enabled": False,
            "dynamic_field_write_enabled": False,
        },
    }
    m68 = {
        "milestone": "M68R",
        "generated_at": now(),
        "status": "PASS_M68R_EVIDENCE_FIRST_EXPANSION_READY",
        "summary": {
            "candidate_count": m68_data.get("summary", {}).get("prospect_count"),
            "level_counts": m68_data.get("summary", {}).get("level_counts"),
            "gap_queue_count": m68_data.get("summary", {}).get("gap_queue_count"),
            "old_workbook_write_enabled": False,
            "trusted_pool_update_enabled": False,
        },
        "source_policy": "复用 M25R 已有 CNINFO/官方来源和最小字段补丁，不伪造新来源。",
    }

    tracked_diff = run(["git", "diff", "--name-only"])
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"])
    c6 = {
        "milestone": "C6",
        "generated_at": now(),
        "status": "PASS_C6_WORKSPACE_GOVERNANCE_MANIFEST_READY",
        "summary": {
            "tracked_diff_count": len(tracked_diff),
            "untracked_count": len(untracked),
            "raw_material_paths": sum(1 for path in untracked if path.startswith("static-pool-deps-20260419_151148")),
            "historical_archive_paths": sum(1 for path in untracked if path.startswith("deliveries/archive/milestones/milestone")),
            "no_delete_no_reset": True,
        },
        "categories": {
            "raw_materials_local_dependency": [path for path in untracked if path.startswith("static-pool-deps-20260419_151148")][:80],
            "historical_archive_import_later": [path for path in untracked if path.startswith("deliveries/archive/milestones/milestone")][:80],
            "suspected_user_or_legacy_tracked_changes": tracked_diff,
        },
        "recommended_gitignore_entries": ["static-pool-deps-20260419_151148/", "static-pool-deps-20260419_151148.zip"],
    }

    write_json(M65 / "milestone65r_trusted_pool_runner_v3_closure_v1.json", m65)
    write_json(M66 / "trusted_pool_storage_policy_v1.json", m66)
    write_json(M67 / "milestone67r_vault_output_closure_v1.json", m67)
    write_json(M68 / "milestone68r_expansion_closure_v1.json", m68)
    write_json(C6 / "workspace_long_term_governance_manifest_v1.json", c6)
    update_status_panel(m65, m66, m67, m68, c6)
    print(json.dumps({"m65": m65["status"], "m66": m66["status"], "m67": m67["status"], "m68": m68["status"], "c6": c6["status"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
