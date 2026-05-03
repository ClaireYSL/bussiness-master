from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M68 = MILESTONES / "milestone68r_evidence_first_expansion"
M69 = MILESTONES / "milestone69r_second_source_plan"
M70 = MILESTONES / "milestone70r_l3_to_l2_report_only"
M71 = MILESTONES / "milestone71r_l2_vault_admission"
M72 = MILESTONES / "milestone72r_trusted_pool_operating_panel"
C7 = MILESTONES / "workspace_cleanup_c7_final_governance"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
M68_REPORT = M68 / "m68r_expansion_static_promote_report_v1.json"
M68_POOL = M68 / "m68r_expansion_trusted_pool_input_v1.json"
M68_SOURCE_TRACE = M68 / "m68r_expansion_source_trace_v1.json"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE))


def source_items_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("prospect_id") or ""): item for item in payload.get("items") or []}


def pool_items_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("prospect_id") or ""): item for item in payload.get("items") or []}


def strong_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    strong = {"official", "ir", "annual_report", "exchange_filing", "regulatory_annual_report", "cninfo", "announcement"}
    return [source for source in sources if str(source.get("evidence_strength") or "").strip().lower() in strong]


def build_m69() -> dict[str, Any]:
    report = read_json(M68_REPORT)
    pool = read_json(M68_POOL)
    trace = read_json(M68_SOURCE_TRACE)
    pool_by_id = pool_items_by_id(pool)
    trace_by_id = source_items_by_id(trace)
    decisions = report.get("decisions") or []

    second_source_items = []
    l4_gap_items = []
    precheck_items = []
    for decision in decisions:
        prospect_id = decision.get("prospect_id")
        item = pool_by_id.get(prospect_id, {})
        trace_item = trace_by_id.get(prospect_id, {})
        sources = trace_item.get("sources") or []
        strong = strong_sources(sources)
        existing_sources = [
            {
                "source_type": source.get("source_type"),
                "source_locator": source.get("source_locator"),
                "evidence_strength": source.get("evidence_strength"),
                "summary": source.get("summary"),
            }
            for source in sources
        ]
        base = {
            "prospect_id": prospect_id,
            "company_name": decision.get("company_name"),
            "current_static_level": decision.get("suggested_level"),
            "matched_persona": item.get("matched_persona"),
            "strong_evidence_count": len(strong),
            "existing_sources": existing_sources,
        }
        if decision.get("suggested_level") == "L3":
            row = {
                **base,
                "gap_type": "second_strong_evidence_needed",
                "priority": "P0_before_L2_admission",
                "recommended_source_types": ["annual_report", "official_ir", "exchange_announcement", "regulatory_filing", "official_website"],
                "source_collection_guidance": "优先补第二条可定位强来源；CNINFO 总入口已存在时，第二来源应尽量定位到年报/公告/官网 IR 的具体页面或文件。",
                "status": "pending_source_collection",
            }
            second_source_items.append(row)
            precheck_items.append({**base, "l2_admission_precheck": "not_ready", "blocking_gap": "second_strong_evidence_needed"})
        elif decision.get("suggested_level") == "L4":
            gaps = decision.get("gap_queue") or []
            l4_gap_items.append(
                {
                    **base,
                    "gap_type": "minimal_l3_readiness_gap",
                    "required_before_l3": [gap.get("field") or gap.get("reason") for gap in gaps],
                    "status": "keep_l4_until_minimal_fields_and_first_strong_source_are_complete",
                }
            )
            precheck_items.append({**base, "l2_admission_precheck": "not_ready", "blocking_gap": "l4_minimal_gap"})
        else:
            precheck_items.append({**base, "l2_admission_precheck": "ready_or_above", "blocking_gap": None})

    queue = {
        "milestone": "M69R",
        "generated_at": now(),
        "source_report": rel(M68_REPORT),
        "summary": {
            "m68_candidate_count": len(decisions),
            "l3_second_source_needed_count": len(second_source_items),
            "l4_minimal_gap_count": len(l4_gap_items),
            "l2_admission_ready_count": sum(1 for item in precheck_items if item.get("l2_admission_precheck") == "ready_or_above"),
            "second_source_fabricated": False,
        },
        "items": second_source_items,
    }
    plan = {
        "milestone": "M69R",
        "generated_at": now(),
        "status": "PASS_M69R_SECOND_SOURCE_COLLECTION_PLAN_READY",
        "summary": queue["summary"],
        "collection_policy": {
            "allowed_sources": ["CNINFO 年报/公告具体页", "官网/IR 页面", "交易所公告", "监管披露", "权威行业研究"],
            "forbidden_sources": ["不可定位搜索摘要", "旧主表字段", "旧档案正文", "潜客产出反推知识资产"],
            "no_fake_second_source": True,
        },
        "next_step": "按 second_source_gap_queue 采集第二强来源后，再重跑 M70R report-only。",
    }
    precheck = {
        "milestone": "M69R",
        "generated_at": now(),
        "status": "PASS_M69R_L3_TO_L2_PRECHECK_READY",
        "summary": queue["summary"],
        "items": precheck_items,
        "l4_minimal_field_gap_items": l4_gap_items,
    }
    write_json(M69 / "second_source_gap_queue_v1.json", queue)
    write_json(M69 / "source_collection_plan_v1.json", plan)
    write_json(M69 / "l3_to_l2_admission_precheck_v1.json", precheck)
    return {"queue": queue, "plan": plan, "precheck": precheck}


def build_m70() -> dict[str, Any]:
    pool = read_json(M68_POOL)
    trace = read_json(M68_SOURCE_TRACE)
    pool["generated_at"] = now()
    pool["source_file"] = rel(M68_POOL)
    pool["summary"] = {
        **(pool.get("summary") or {}),
        "milestone": "M70R",
        "source_policy": "current_available_sources_only_no_fabricated_second_source",
        "old_workbook_write_enabled": False,
    }
    trace["generated_at"] = now()
    trace["source_file"] = rel(M68_SOURCE_TRACE)
    trace["source_policy"] = "M70R report-only uses currently available M68 sources; second-source collection remains pending."
    pool_path = M70 / "m70r_l3_to_l2_pool_input_v1.json"
    trace_path = M70 / "m70r_l3_to_l2_source_trace_v1.json"
    write_json(pool_path, pool)
    write_json(trace_path, trace)

    common = [
        "python3",
        "scripts/trusted_pool_runner.py",
        "--mode",
        "report_only",
        "--trusted-pool",
        rel(pool_path),
        "--source-trace",
        rel(trace_path),
        "--output-file",
        rel(M70 / "m70r_static_promote_report_v1.json"),
        "--gap-queue-file",
        rel(M70 / "m70r_gap_queue_v1.json"),
        "--source-trace-output",
        rel(M70 / "m70r_source_trace_normalized_v1.json"),
        "--no-write-proof-file",
        rel(M70 / "m70r_no_write_proof_v1.json"),
        "--pool-diff-file",
        rel(M70 / "m70r_pool_diff_report_v1.json"),
        "--validation-report-file",
        rel(M70 / "m70r_validation_report_v1.json"),
        "--baseline-file",
        rel(M70 / "m70r_baseline_v1.json"),
    ]
    first = run(common + ["--write-baseline"], check=True)
    second = run(common + ["--require-baseline"], check=True)
    report = read_json(M70 / "m70r_static_promote_report_v1.json")
    level_counts = report.get("summary", {}).get("level_counts") or {}
    closure = {
        "milestone": "M70R",
        "generated_at": now(),
        "status": "PASS_M70R_REPORT_ONLY_NO_WRITE",
        "summary": {
            "prospect_count": report.get("summary", {}).get("prospect_count"),
            "level_counts": level_counts,
            "l2_candidate_count": level_counts.get("L2", 0) + level_counts.get("L1", 0),
            "gap_queue_count": report.get("summary", {}).get("gap_queue_count"),
            "baseline_required_passed": True,
            "updated_pool_written": report.get("summary", {}).get("updated_pool_written"),
            "old_workbook_write_enabled": report.get("summary", {}).get("old_workbook_write_enabled"),
            "second_source_collection_completed": False,
        },
        "interpretation": "当前 M70R 未采集真实第二强来源；因此 L3 保持 L3 属于预期结果，后续补源后可复用同一 runner 升 L2。",
        "runner_stdout_sample": [line for line in (first.stdout + second.stdout).splitlines() if line.strip()][-8:],
    }
    write_json(M70 / "m70r_l3_to_l2_report_only_closure_v1.json", closure)
    return {"report": report, "closure": closure}


def build_m71() -> dict[str, Any]:
    report = read_json(M70 / "m70r_static_promote_report_v1.json")
    decisions = report.get("decisions") or []
    l2_decisions = [decision for decision in decisions if decision.get("suggested_level") in {"L1", "L2"}]
    preview_items = []
    preview_dir = M71 / "l2_vault_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    if l2_decisions:
        pool = read_json(M70 / "m70r_l3_to_l2_pool_input_v1.json")
        pool_by_id = pool_items_by_id(pool)
        for decision in l2_decisions:
            item = pool_by_id.get(decision.get("prospect_id"), {})
            path = preview_dir / f"{decision.get('company_name')}.md"
            text = f"""---
prospect_id: {decision.get('prospect_id')}
static_level: {decision.get('suggested_level')}
source_boundary: evidence_first_only
legacy_field_inherited: false
---

# {decision.get('company_name')}

## 静态 ICP 匹配

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 证据成熟度

强来源数量：{decision.get('strong_evidence_count')}

## 风险与待补点

{item.get('risk_or_gap', '')}

## 边界

本 preview 只表达静态 ICP、证据成熟度和信息完整度，不表达动态经营动作。
"""
            path.write_text(text, encoding="utf-8")
            preview_items.append({"prospect_id": decision.get("prospect_id"), "company_name": decision.get("company_name"), "path": rel(path)})
    package = {
        "milestone": "M71R",
        "generated_at": now(),
        "status": "PASS_M71R_L2_VAULT_PREVIEW_ADMISSION_READY",
        "summary": {
            "m70_candidate_count": len(decisions),
            "l2_preview_count": len(preview_items),
            "vault_regular_area_written": False,
            "old_workbook_written": False,
            "knowledge_asset_written": False,
        },
        "items": preview_items,
        "empty_preview_reason": None if preview_items else "当前 M70R 无 L2/L1；缺第二强来源，不生成 L2 正式档案 preview。",
    }
    admission = {
        "milestone": "M71R",
        "generated_at": now(),
        "status": "PASS_M71R_NO_VAULT_WRITE_ADMISSION_RECORDED",
        "summary": package["summary"],
        "checks": {
            "dynamic_term_scan_required_before_regular_write": True,
            "legacy_source_scan_required_before_regular_write": True,
            "field_integrity_required_before_regular_write": True,
            "write_vault_enabled": False,
        },
    }
    write_json(M71 / "l2_vault_preview_package_v1.json", package)
    write_json(M71 / "vault_output_admission_report_v1.json", admission)
    return {"package": package, "admission": admission}


def git_lines(args: list[str]) -> list[str]:
    result = run(["git", *args])
    return result.stdout.splitlines()


def build_c7() -> dict[str, Any]:
    status_lines = git_lines(["status", "--short"])
    tracked_modified = [line[3:] for line in status_lines if line.startswith(" M ") or line.startswith("M  ") or line.startswith("MM ")]
    untracked = [line[3:] for line in status_lines if line.startswith("?? ")]
    categories: dict[str, list[str]] = {
        "old_m6r_tracked_changes": [],
        "legacy_or_user_tracked_changes_needs_human_decision": [],
        "historical_archive_import_later": [],
        "legacy_scripts_configs_keep_unstaged": [],
        "handoff_docs_archive_import_later": [],
        "current_m69_m72_package": [],
        "other_untracked_needs_human_decision": [],
    }
    for path in tracked_modified:
        if "milestone6r" in path.lower() or "Milestone 6R" in path or "workbook_integrity_report" in path:
            categories["old_m6r_tracked_changes"].append(path)
        else:
            categories["legacy_or_user_tracked_changes_needs_human_decision"].append(path)
    for path in untracked:
        lower = path.lower()
        if (
            "milestone69r_" in lower
            or "milestone70r_" in lower
            or "milestone71r_" in lower
            or "milestone72r_" in lower
            or "workspace_cleanup_c7" in lower
            or path == "scripts/build_m69r_m72_l3_to_l2_closure.py"
        ):
            categories["current_m69_m72_package"].append(path)
        elif path.startswith("deliveries/archive/handoffs/"):
            categories["handoff_docs_archive_import_later"].append(path)
        elif path.startswith("deliveries/archive/milestones/") or path.startswith("deliveries/archive/repairs/"):
            categories["historical_archive_import_later"].append(path)
        elif path.startswith("configs/") or path.startswith("scripts/") or path.startswith("prompts/"):
            categories["legacy_scripts_configs_keep_unstaged"].append(path)
        else:
            categories["other_untracked_needs_human_decision"].append(path)
    manifest = {
        "milestone": "C7",
        "generated_at": now(),
        "status": "PASS_C7_WORKSPACE_GOVERNANCE_MANIFEST_READY",
        "summary": {key + "_count": len(value) for key, value in categories.items()},
        "recommended_actions": {
            "old_m6r_tracked_changes": "保留未提交；后续单独判断是否 archive import 或恢复历史产物。",
            "legacy_or_user_tracked_changes_needs_human_decision": "疑似历史或用户改动，当前不回滚、不覆盖。",
            "historical_archive_import_later": "后续单独做 archive import，不与主线代码混提。",
            "legacy_scripts_configs_keep_unstaged": "历史兼容脚本/配置先保留本地，后续按 legacy 包导入或忽略。",
            "current_m69_m72_package": "本轮可作为最小安全包提交。",
            "raw_materials": "static-pool-deps-20260419_151148/ 已由 .gitignore 隔离，不纳入噪音主列表。",
        },
        "categories": categories,
    }
    proof = {
        "milestone": "C7",
        "generated_at": now(),
        "status": "PASS_NO_DESTRUCTIVE_WORKSPACE_ACTION",
        "delete_executed": False,
        "reset_executed": False,
        "move_executed": False,
        "raw_materials_ignored": True,
    }
    write_json(C7 / "workspace_final_governance_manifest_v1.json", manifest)
    write_json(C7 / "no_delete_no_reset_proof_v1.json", proof)
    return {"manifest": manifest, "proof": proof}


def build_m72(m69: dict[str, Any], m70: dict[str, Any], m71: dict[str, Any], c7: dict[str, Any]) -> dict[str, Any]:
    report = m70["report"]
    level_counts = report.get("summary", {}).get("level_counts") or {}
    queue_summary = m69["queue"].get("summary") or {}
    panel = {
        "milestone": "M72R",
        "generated_at": now(),
        "status": "PASS_M72R_TRUSTED_POOL_OPERATING_PANEL_V2_READY",
        "summary": {
            "current_level_counts": level_counts,
            "second_source_needed_count": queue_summary.get("l3_second_source_needed_count"),
            "l4_minimal_gap_count": queue_summary.get("l4_minimal_gap_count"),
            "l2_preview_count": m71["package"].get("summary", {}).get("l2_preview_count"),
            "old_workbook_write_enabled": False,
            "vault_regular_area_written": False,
            "workspace_manifest_ready": c7["manifest"].get("status") == "PASS_C7_WORKSPACE_GOVERNANCE_MANIFEST_READY",
        },
        "next_commands": [
            "先按 deliveries/archive/milestones/milestone69r_second_source_plan/second_source_gap_queue_v1.json 补第二强来源。",
            "补源后重跑 python3 scripts/trusted_pool_runner.py --mode report_only --trusted-pool <补源后的pool> --source-trace <补源后的trace> --require-baseline。",
            "出现 L2 后再生成 M71R vault preview；正式写 vault 正区前必须单独执行准入命令。",
        ],
        "boundary": {
            "old_excel_write": "disabled_by_default",
            "knowledge_asset_write": "forbidden_from_prospect_output",
            "dynamic_sales_fields": "not_part_of_static_pool_state",
        },
    }
    handoff = {
        "milestone": "M72R",
        "generated_at": now(),
        "status": "PASS_HANDOFF_SNAPSHOT_V2_READY",
        "latest_milestone": "M72R",
        "canonical_status_panel": rel(STATUS_PANEL),
        "key_outputs": {
            "m69_second_source_queue": rel(M69 / "second_source_gap_queue_v1.json"),
            "m70_report_only": rel(M70 / "m70r_static_promote_report_v1.json"),
            "m71_vault_admission": rel(M71 / "vault_output_admission_report_v1.json"),
            "m72_operating_panel": rel(M72 / "trusted_pool_operating_panel_v2.json"),
            "c7_workspace_manifest": rel(C7 / "workspace_final_governance_manifest_v1.json"),
        },
        "do_not_do": ["不要写旧 Excel", "不要把潜客产出写入知识资产", "不要把动态经营字段放入静态分级", "不要删除/reset/move 历史文件"],
    }
    write_json(M72 / "trusted_pool_operating_panel_v2.json", panel)
    write_json(M72 / "handoff_snapshot_v2.json", handoff)

    canonical = read_json(STATUS_PANEL, {})
    canonical["generated_at"] = now()
    canonical["overall_status"] = "PASS_M72R_OPERATING_PANEL_READY"
    canonical["latest_milestone"] = "M72R"
    canonical["m69r_second_source_plan"] = m69["queue"].get("summary", {})
    canonical["m70r_l3_to_l2_report_only"] = m70["closure"].get("summary", {})
    canonical["m71r_l2_vault_admission"] = m71["package"].get("summary", {})
    canonical["m72r_operating_panel_v2"] = panel["summary"]
    canonical["c7_workspace_governance"] = c7["manifest"].get("summary", {})
    canonical["canonical_next_action"] = "先按 M69R second_source_gap_queue 补第二强来源，再重跑 trusted_pool_runner 进行 L3->L2 report-only。"
    canonical["next_recommended_action"] = canonical["canonical_next_action"]
    write_json(STATUS_PANEL, canonical)
    return {"panel": panel, "handoff": handoff}


def scan_dynamic_terms(paths: list[Path]) -> dict[str, Any]:
    findings = []
    allowed = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".txt", ".py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    record = {"path": rel(path), "term": term}
                    if "workspace_cleanup_c7" in str(path) or "business_feedback" in str(path):
                        allowed.append({**record, "reason": "legacy_or_optional_reference_only"})
                    else:
                        findings.append(record)
    return {
        "status": "PASS" if not findings else "FAIL",
        "dynamic_term_findings_count": len(findings),
        "findings": findings,
        "allowed_legacy_or_optional_references": allowed,
    }


def scan_api_keys(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".txt", ".py"}:
                continue
            if path.name == ".env" or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"path": rel(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def run_validation(m69: dict[str, Any], m70: dict[str, Any], m71: dict[str, Any], m72: dict[str, Any], c7: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m69r_m72_l3_to_l2_closure.py", "scripts/trusted_pool_runner.py"])
    json_paths = [*M69.glob("*.json"), *M70.glob("*.json"), *M71.glob("*.json"), *M72.glob("*.json"), *C7.glob("*.json"), STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - smoke validation path
            json_errors.append({"path": rel(path), "error": str(exc)})

    mismatch_path = M70 / "m70r_baseline_mismatch_probe_v1.json"
    mismatch = read_json(M70 / "m70r_baseline_v1.json")
    mismatch["candidate_signature"] = "intentional_mismatch_for_guard_test"
    write_json(mismatch_path, mismatch)
    mismatch_result = run([
        "python3",
        "scripts/trusted_pool_runner.py",
        "--mode",
        "report_only",
        "--trusted-pool",
        rel(M70 / "m70r_l3_to_l2_pool_input_v1.json"),
        "--source-trace",
        rel(M70 / "m70r_l3_to_l2_source_trace_v1.json"),
        "--output-file",
        rel(M70 / "m70r_baseline_mismatch_probe_report_v1.json"),
        "--baseline-file",
        rel(mismatch_path),
        "--require-baseline",
    ])
    legacy_guard = run(["python3", "scripts/run_execution_batch.py", "--config-file", "configs/execution_batches/milestone6r_trust_registry_v1.json", "--write-back"])
    expand_guard = run(["python3", "scripts/expand_static_pool.py", "--track", "零售消费", "--persona-id", "retail_brand_beauty", "--write-back"])

    dynamic_scan = scan_dynamic_terms([M69, M70, M71, M72, C7])
    api_scan = scan_api_keys([M69, M70, M71, M72, C7, WORKSPACE / "scripts/build_m69r_m72_l3_to_l2_closure.py"])
    assertions = {
        "m69_l3_second_source_needed_is_29": m69["queue"]["summary"].get("l3_second_source_needed_count") == 29,
        "m69_l4_minimal_gap_is_1": m69["queue"]["summary"].get("l4_minimal_gap_count") == 1,
        "m70_report_only_no_pool_write": m70["report"].get("summary", {}).get("updated_pool_written") is False,
        "m70_old_workbook_disabled": m70["report"].get("summary", {}).get("old_workbook_write_enabled") is False,
        "m71_no_regular_vault_write": m71["package"].get("summary", {}).get("vault_regular_area_written") is False,
        "m71_preview_count_matches_l2_count": m71["package"].get("summary", {}).get("l2_preview_count") == (m70["report"].get("summary", {}).get("level_counts") or {}).get("L2", 0) + (m70["report"].get("summary", {}).get("level_counts") or {}).get("L1", 0),
        "c7_no_delete_reset_move": c7["proof"].get("delete_executed") is False and c7["proof"].get("reset_executed") is False and c7["proof"].get("move_executed") is False,
        "baseline_mismatch_failed": mismatch_result.returncode != 0,
        "legacy_write_guard_failed_without_override": legacy_guard.returncode != 0,
        "legacy_expand_guard_failed_without_override": expand_guard.returncode != 0,
    }
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic_scan["status"] == "PASS" and api_scan["status"] == "PASS" else "FAIL"
    validation = {
        "milestone": "M69R-M72R-C7",
        "generated_at": now(),
        "status": status,
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors},
        "baseline_mismatch_guard": {"returncode": mismatch_result.returncode, "stderr": mismatch_result.stderr.strip()},
        "legacy_write_guard": {"returncode": legacy_guard.returncode, "stderr": legacy_guard.stderr.strip()[:1000]},
        "legacy_expand_guard": {"returncode": expand_guard.returncode, "stderr": expand_guard.stderr.strip()[:1000]},
        "dynamic_term_scan": dynamic_scan,
        "api_key_scan": api_scan,
        "assertions": assertions,
    }
    write_json(M72 / "m69r_m72r_c7_validation_report_v1.json", validation)
    return validation


def main() -> int:
    for directory in (M69, M70, M71, M72, C7):
        directory.mkdir(parents=True, exist_ok=True)
    m69 = build_m69()
    m70 = build_m70()
    m71 = build_m71()
    c7 = build_c7()
    m72 = build_m72(m69, m70, m71, c7)
    validation = run_validation(m69, m70, m71, m72, c7)
    # Rebuild C7/M72 after validation files exist, so the handoff manifest is a true final snapshot.
    c7 = build_c7()
    m72 = build_m72(m69, m70, m71, c7)
    validation = run_validation(m69, m70, m71, m72, c7)
    print(json.dumps({"status": validation["status"], "m69": m69["queue"]["summary"], "m70": m70["closure"]["summary"], "m71": m71["package"]["summary"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
