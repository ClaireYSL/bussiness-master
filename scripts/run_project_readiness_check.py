from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import check_workbook_integrity, resolve_static_pool_paths, should_allow_frozen_text_as_input

DEFAULT_OUTPUT_JSON = "deliveries/archive/handoffs/milestone16_project_readiness_check_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 16-迁移交接自检复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run non-writeback readiness checks for project handoff.")
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _run(cmd: list[str]) -> dict[str, object]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True)
    return {"cmd": cmd, "return_code": proc.returncode, "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}


def _load_json(path: str) -> dict[str, Any]:
    try:
        return json.loads((WORKSPACE / path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _env_check() -> dict[str, object]:
    dot_env = WORKSPACE / ".env"
    values = {}
    if dot_env.exists():
        for line in dot_env.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    keys = ["DELEGATE_LLM_BASE_URL", "DELEGATE_LLM_API_KEY", "DELEGATE_LLM_MODEL"]
    return {
        "env_file_exists": dot_env.exists(),
        "delegate_llm": {key: bool(os.getenv(key) or values.get(key)) for key in keys},
        "static_pool_root": os.getenv("STATIC_POOL_ROOT", ""),
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Milestone 16-迁移交接自检复盘-v1",
        "",
        f"- 生成时间：`{payload.get('checked_at')}`",
        f"- 总结论：`{'PASS' if payload.get('ok') else 'FAIL'}`",
        "",
        "## 检查项",
        "",
    ]
    for key, item in (payload.get("checks") or {}).items():
        lines.append(f"- {key}：`{'PASS' if item.get('ok') else 'FAIL'}`")
    lines.extend(["", "## 当前里程碑摘要", ""])
    for key, item in (payload.get("milestones") or {}).items():
        lines.append(f"- {key}：`{item}`")
    lines.extend(
        [
            "",
            "## 接力建议",
            "",
            "1. 当前仍不执行真实 write_back；M22R 只完成可信潜客写回准入材料。",
            "2. M23A/M21 业务反馈类产物仅作为可读性参考，不作为主写回准入依据。",
            "3. 若要真实写回 30 家，必须由用户单独确认，并使用 M22R baseline + `--require-report-baseline`。",
            "4. M24R 只能做知识资产来源治理与潜客观察隔离，不能从潜客结果直接生成正式知识资产。",
            "5. M25R 已完成 50 家补证、report-only/gate 和可信复核；真实写回仍需单独确认。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["governance"]], deep_scan=True)
    source_tags_ok = (
        should_allow_frozen_text_as_input("abstracted_persona_review_package")
        and not should_allow_frozen_text_as_input("raw_source_file")
        and not should_allow_frozen_text_as_input("legacy_profile_long_text")
    )
    py_compile = _run([
        "python3", "-m", "py_compile",
        "scripts/build_manual_persona_review_package.py",
        "scripts/build_share_consumption_package.py",
        "scripts/build_intake_quality_patch.py",
        "scripts/build_candidate_preflight_package.py",
        "scripts/build_writeback_admission_package.py",
        "scripts/build_post_writeback_operational_package.py",
        "scripts/build_expansion_feedback_package.py",
        "scripts/build_batch_intake_patch_from_m19.py",
        "scripts/build_business_feedback_fast_run_package.py",
        "scripts/build_persona_business_confirmation_package.py",
        "scripts/build_trusted_match_review_package.py",
        "scripts/build_trusted_writeback_admission_package.py",
        "scripts/build_trusted_prospect_summary_package.py",
        "scripts/build_knowledge_source_governance_package.py",
        "scripts/build_trusted_expansion_preflight_package.py",
        "scripts/build_trusted_expansion_intake_patch.py",
        "scripts/build_trusted_expansion_review_package.py",
        "scripts/build_autonomous_status_panel.py",
        "scripts/build_persona_boundary_rule_package.py",
        "scripts/run_project_readiness_check.py",
        "scripts/run_execution_batch.py",
        "scripts/pre_writeback_gate_check.py",
    ])
    m13 = _load_json("deliveries/archive/milestones/milestone13_persona_boundary_rules/milestone13_persona_boundary_rule_package_v1.json")
    m14 = _load_json("deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_promote_v1.json")
    m142 = _load_json("deliveries/archive/milestones/milestone14_2_intake_quality_unblock/milestone14_2_intake_quality_promote_v1.json")
    m143 = _load_json("deliveries/archive/milestones/milestone14_3_candidate_preflight/milestone14_3_candidate_preflight_package_v1.json")
    m15 = _load_json("deliveries/archive/milestones/milestone15_2_share_consumption/milestone15_2_share_consumption_package_v1.json")
    m17 = _load_json("deliveries/archive/milestones/milestone17_writeback_admission/milestone17_writeback_admission_package_v1.json")
    m18 = _load_json("deliveries/archive/milestones/milestone18_l3_operationalization/milestone18_l3_operational_package_v1.json")
    m19 = _load_json("deliveries/archive/milestones/milestone19_expansion_feedback/milestone19_expansion_feedback_package_v1.json")
    m20 = _load_json("deliveries/archive/milestones/milestone20_batch_intake_patch/milestone20_batch_intake_promote_v1.json")
    m20_gate = _load_json("deliveries/archive/repairs/milestone20_batch_intake_gate_check_v1.json")
    m23a = _load_json("deliveries/archive/milestones/milestone23a_l3_business_feedback/milestone23a_l3_business_feedback_package_v1.json")
    m21 = _load_json("deliveries/archive/milestones/milestone21_persona_business_confirmation/milestone21_persona_business_confirmation_package_v1.json")
    m21r = _load_json("deliveries/archive/milestones/milestone21r_trusted_match_review/milestone21r_trusted_match_review_package_v1.json")
    m22r = _load_json("deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_admission_package_v1.json")
    m22r_gate = _load_json("deliveries/archive/repairs/milestone22r_trusted_writeback_admission_gate_check_v1.json")
    m23r = _load_json("deliveries/archive/milestones/milestone23r_trusted_prospect_summary/milestone23r_trusted_prospect_summary_package_v1.json")
    m24r = _load_json("deliveries/archive/milestones/milestone24r_knowledge_source_governance/milestone24r_knowledge_source_governance_package_v1.json")
    m25r = _load_json("deliveries/archive/milestones/milestone25r_trusted_expansion_preflight/milestone25r_trusted_expansion_preflight_package_v1.json")
    m25r_patch = _load_json("deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_intake_patch_v1.json")
    m25r_gate = _load_json("deliveries/archive/repairs/milestone25r_trusted_expansion_gate_check_v1.json")
    m25r_review = _load_json("deliveries/archive/milestones/milestone25r_trusted_expansion_review/milestone25r_trusted_expansion_review_package_v1.json")
    m142_gate = _load_json("deliveries/archive/repairs/milestone14_2_intake_quality_gate_check_v1.json")
    checks = {
        "workbook_integrity": {"ok": bool(integrity.get("ok")), "detail": integrity},
        "env": {"ok": bool(_env_check().get("env_file_exists")), "detail": _env_check()},
        "source_tag_guard": {"ok": source_tags_ok},
        "py_compile": {"ok": py_compile["return_code"] == 0, "detail": py_compile},
        "m13_rule_package": {"ok": (m13.get("summary") or {}).get("account_count") == 12},
        "m14_report_only": {"ok": (m14.get("batch_summary") or {}).get("block") == 15},
        "m14_2_report_only": {
            "ok": (
                (m142.get("batch_summary") or {}).get("allow") == 15
                or (
                    (m142.get("batch_summary") or {}).get("block") == 0
                    and (m17.get("summary") or {}).get("writeback_executed") is True
                )
            )
        },
        "m14_2_gate_check": {"ok": bool(m142_gate.get("ok"))},
        "m14_3_preflight": {"ok": (m143.get("summary") or {}).get("preflight_status_counts", {}).get("executable_now") == 15},
        "m15_2_share_package": {"ok": (m15.get("summary") or {}).get("item_count") == 27},
        "m17_admission_package": {
            "ok": (m17.get("summary") or {}).get("allow_candidate_count") == 15
            and (
                not bool((m17.get("summary") or {}).get("writeback_executed"))
                or (
                    (m17.get("summary") or {}).get("promoted") == 15
                    and (m17.get("summary") or {}).get("skipped") == 0
                )
            )
        },
        "m18_operational_package": {
            "ok": (m18.get("summary") or {}).get("share_ready_count") == 15
            and (m18.get("summary") or {}).get("needs_fix_count") == 0
            and bool((m18.get("summary") or {}).get("workbook_integrity_ok"))
        },
        "m19_feedback_package": {
            "ok": (m19.get("summary") or {}).get("feedback_item_count") == 15
            and (m19.get("next_batch_plan") or {}).get("picked_count", 0) > 0
        },
        "m20_batch_intake": {
            "ok": (m20.get("batch_summary") or {}).get("block") == 0
            and len(m20.get("results") or []) == 30
            and bool(m20_gate.get("ok"))
        },
        "m23a_business_feedback_package": {
            "ok": (m23a.get("summary") or {}).get("account_count") == 15
            and (m23a.get("summary") or {}).get("share_ready_count") == 15
            and all((item.get("action_card") or {}).get("why_worth_review") for item in (m23a.get("feedback_items") or []))
        },
        "m21_persona_business_confirmation_package": {
            "ok": (m21.get("summary") or {}).get("account_count") == 30
            and (m21.get("summary") or {}).get("confirm_active_high_value_count") == 0
            and (m21.get("summary") or {}).get("business_reviewed_count") == 0
        },
        "m21r_trusted_match_review": {
            "ok": (m21r.get("summary") or {}).get("trusted_match_ready_count") == 30
            and (m21r.get("summary") or {}).get("official_evidence_coverage_rate") == 1.0
            and (m21r.get("summary") or {}).get("core_info_complete_rate") == 1.0
        },
        "m22r_trusted_writeback_admission": {
            "ok": (m22r.get("summary") or {}).get("admission_candidate_count") == 30
            and (m22r.get("summary") or {}).get("report_only_allow") == 30
            and (m22r.get("summary") or {}).get("report_only_result_count") == 30
            and bool((m22r.get("summary") or {}).get("gate_ok"))
            and bool(m22r_gate.get("ok"))
        },
        "m23r_trusted_prospect_summary": {
            "ok": (m23r.get("summary") or {}).get("card_count") == 30
            and (m23r.get("summary") or {}).get("missing_strong_evidence_count") == 0
            and not bool((m23r.get("summary") or {}).get("sales_action_terms_detected"))
            and (m23r.get("summary") or {}).get("formal_knowledge_write_enabled") is False
        },
        "m24r_knowledge_source_governance": {
            "ok": (m24r.get("summary") or {}).get("candidate_observation_count") == 30
            and (m24r.get("summary") or {}).get("no_write_proof_ok") is True
            and (m24r.get("summary") or {}).get("formal_knowledge_write_enabled") is False
        },
        "m25r_expansion_preflight": {
            "ok": (m25r.get("summary") or {}).get("candidate_count") == 50
            and (m25r.get("summary") or {}).get("report_only_status") == "not_run_pre_patch_required"
            and (m25r.get("summary") or {}).get("true_writeback_executed") is False
        },
        "m25r_expansion_intake_patch_report_only": {
            "ok": (m25r_patch.get("summary") or {}).get("account_count") == 50
            and (m25r_patch.get("summary") or {}).get("official_source_ready_count") == 50
            and (m25r_patch.get("summary") or {}).get("report_only_result_count") == 50
            and (m25r_patch.get("summary") or {}).get("report_only_block") == 0
            and bool(m25r_gate.get("ok"))
        },
        "m25r_trusted_expansion_review": {
            "ok": (m25r_review.get("summary") or {}).get("trusted_match_ready_count") == 50
            and (m25r_review.get("summary") or {}).get("official_evidence_coverage_rate") == 1.0
            and (m25r_review.get("summary") or {}).get("core_info_complete_rate") == 1.0
        },
    }
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ok": all(bool(item.get("ok")) for item in checks.values()),
        "workspace": str(WORKSPACE),
        "checks": checks,
        "milestones": {
            "M13": (m13.get("summary") or {}),
            "M14": (m14.get("batch_summary") or {}),
            "M14.2": (m142.get("batch_summary") or {}),
            "M14.3": (m143.get("summary") or {}),
            "M15.2": (m15.get("summary") or {}),
            "M17": (m17.get("summary") or {}),
            "M18": (m18.get("summary") or {}),
            "M19": (m19.get("summary") or {}),
            "M20": (m20.get("batch_summary") or {}),
            "M23A": (m23a.get("summary") or {}),
            "M21": (m21.get("summary") or {}),
            "M21R": (m21r.get("summary") or {}),
            "M22R": (m22r.get("summary") or {}),
            "M23R": (m23r.get("summary") or {}),
            "M24R": (m24r.get("summary") or {}),
            "M25R": (m25r.get("summary") or {}),
            "M25R_patch": (m25r_patch.get("summary") or {}),
            "M25R_review": (m25r_review.get("summary") or {}),
        },
    }
    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(_render_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "ok": payload["ok"]}, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
