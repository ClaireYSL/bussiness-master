from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.static_promote import evaluate_static_promotion

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
CANONICAL = WORKSPACE / "deliveries/canonical/businessmaster"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M109 = MILESTONES / "milestone109r_knowledge_asset_ingestion_closure"
M110 = MILESTONES / "milestone110r_persona_registry_production_closure"
M111 = MILESTONES / "milestone111r_candidate_discovery_evidence_collection"
M113 = MILESTONES / "milestone113r_vault_delivery_operations"
M120 = MILESTONES / "milestone120r_canonical_registry_production"
M121 = MILESTONES / "milestone121r_evidence_acquisition_engine"
M122 = MILESTONES / "milestone122r_production_trusted_pool_batch"
M123 = MILESTONES / "milestone123r_user_delivery_product"
M124 = MILESTONES / "milestone124r_operating_system_hardening"
M125 = MILESTONES / "milestone125r_scale_production_readiness"

KNOWLEDGE_CANONICAL = CANONICAL / "knowledge_asset_registry_v1.json"
PERSONA_CANONICAL = CANONICAL / "persona_registry_v1.json"
REFERENCE_MAP = CANONICAL / "learning_persona_reference_map_v1.json"
POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
CUSTOMER_CASE_TOKENS = ["案例", "客户", "携手", "对话", "分享", "汇报方案", "项目规划", "最佳实践"]

# Bridge old trusted-pool persona IDs to the production persona IDs supported by learning assets.
PERSONA_ALIAS_MAP = {
    "cbec_multi_platform_brand": ["cbec_platform_operator", "cbec_supply_chain_complex"],
    "cbec_platform_operator": ["cbec_platform_operator"],
    "fnb_chain_beverage_coffee": ["retail_chain_fnb", "mgmt_frontline_action_loop"],
    "fnb_chain_standardized": ["retail_chain_fnb", "mgmt_frontline_action_loop"],
    "retail_high_sku_brand": ["mgmt_inventory_supply_coordination", "mgmt_profit_improvement"],
    "retail_multi_store": ["retail_chain_fnb", "mgmt_frontline_action_loop", "mgmt_inventory_supply_coordination"],
    "mfg_multi_factory_group": ["mgmt_group_coordination", "mgmt_hq_operating_visibility"],
    "mfg_rnd_sales_complex": ["mgmt_hq_operating_visibility", "mgmt_group_coordination"],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def level_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("level") or "unknown") for item in items))


def safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower()).strip("_") or "unknown"


def is_customer_or_learning_case(title: str, asset_type: str | None = None) -> bool:
    text = f"{title} {asset_type or ''}"
    return any(token in text for token in CUSTOMER_CASE_TOKENS) or asset_type == "customer_case"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M120R-M125R sustainable BusinessMaster production system packages.")
    parser.add_argument("--stage", choices=("all", "registries", "evidence", "pool", "delivery", "hardening", "scale"), default="all")
    parser.add_argument("--allow-canonical-registry-update", action="store_true", help="Allow writing canonical knowledge/persona registry JSON under deliveries/canonical/businessmaster.")
    parser.add_argument("--allow-trusted-pool-update", action="store_true", help="Allow canonical trusted pool update if M122 has eligible candidates. This builder never writes old Excel.")
    parser.add_argument("--allow-vault-regular-write", action="store_true", help="Allow vault regular output if M123 has eligible preview outputs.")
    return parser


def build_m120(allow_update: bool) -> dict[str, Any]:
    knowledge_pkg = read_json(M109 / "knowledge_asset_registry_update_package_v1.json", {"items": []})
    persona_pkg = read_json(M110 / "persona_registry_update_package_v1.json", {"items": []})
    knowledge_items = []
    for item in knowledge_pkg.get("items") or []:
        if item.get("registry_update_status") != "knowledge_asset_write_ready":
            continue
        knowledge_items.append({
            "asset_id": item.get("asset_id"),
            "asset_type": item.get("asset_type"),
            "title": item.get("title"),
            "source_path_or_url": item.get("source_path_or_url"),
            "source_origin": item.get("source_origin"),
            "track_ids": item.get("track_ids") or [],
            "persona_ids": item.get("persona_ids") or [],
            "summary": item.get("summary"),
            "key_signals": item.get("key_signals"),
            "recommended_usage": item.get("recommended_usage"),
            "confidence_level": item.get("confidence_level"),
            "status": "active",
            "source_trace_verified": bool(item.get("source_trace_verified")),
            "prospect_output_used_as_source": False,
            "registry_version": "v1",
        })
    knowledge_registry = {
        "registry_id": "knowledge_asset_registry_v1",
        "generated_at": now(),
        "source_milestone": "M109R",
        "summary": {
            "asset_count": len(knowledge_items),
            "source_trace_verified_count": sum(1 for item in knowledge_items if item["source_trace_verified"]),
            "prospect_output_used_as_source_count": 0,
            "canonical_write_enabled": allow_update,
        },
        "items": knowledge_items,
    }

    knowledge_by_id = {str(item.get("asset_id")): item for item in knowledge_items}
    persona_items = []
    for item in persona_pkg.get("items") or []:
        refs = []
        for ref in item.get("reference_knowledge_assets") or []:
            asset = knowledge_by_id.get(str(ref.get("asset_id")))
            if asset:
                refs.append({
                    "asset_id": asset["asset_id"],
                    "title": asset["title"],
                    "asset_type": asset["asset_type"],
                    "source_path_or_url": asset["source_path_or_url"],
                })
        persona_items.append({
            "persona_id": item.get("persona_id"),
            "display_name": item.get("display_name"),
            "status": "active_supported" if refs else "active_needs_validation",
            "reference_knowledge_assets": refs,
            "fit_criteria": item.get("fit_criteria_preview"),
            "non_fit_boundary": item.get("non_fit_boundary_preview"),
            "typical_jtbd": item.get("typical_jtbd_preview"),
            "prospect_output_used_as_persona_source": False,
            "registry_version": "v1",
        })
    supported_ids = {item["persona_id"] for item in persona_items if item["status"] == "active_supported"}
    alias_items = []
    for legacy_id, canonical_ids in sorted(PERSONA_ALIAS_MAP.items()):
        supported = [pid for pid in canonical_ids if pid in supported_ids]
        alias_items.append({
            "legacy_or_pool_persona_id": legacy_id,
            "canonical_persona_refs": supported,
            "bridge_status": "mapped_to_supported_persona" if supported else "needs_persona_source_validation",
            "boundary_note": "用于潜客 ICP 解释引用映射，不把潜客作为画像正例/反例。",
        })
    persona_registry = {
        "registry_id": "persona_registry_v1",
        "generated_at": now(),
        "source_milestone": "M110R",
        "summary": {
            "persona_count": len(persona_items),
            "active_supported_count": sum(1 for item in persona_items if item["status"] == "active_supported"),
            "active_needs_validation_count": sum(1 for item in persona_items if item["status"] != "active_supported"),
            "alias_bridge_count": len(alias_items),
            "alias_bridge_supported_count": sum(1 for item in alias_items if item["bridge_status"] == "mapped_to_supported_persona"),
            "prospect_output_used_as_persona_source_count": 0,
            "canonical_write_enabled": allow_update,
        },
        "items": persona_items,
        "alias_bridge": alias_items,
    }
    reference_map = {
        "map_id": "learning_persona_reference_map_v1",
        "generated_at": now(),
        "summary": {
            "knowledge_asset_count": len(knowledge_items),
            "persona_count": len(persona_items),
            "alias_bridge_count": len(alias_items),
            "prospect_output_used_as_source_count": 0,
        },
        "knowledge_asset_refs_by_persona": {item["persona_id"]: [ref["asset_id"] for ref in item["reference_knowledge_assets"]] for item in persona_items},
        "persona_alias_bridge": alias_items,
    }
    if allow_update:
        write_json(KNOWLEDGE_CANONICAL, knowledge_registry)
        write_json(PERSONA_CANONICAL, persona_registry)
        write_json(REFERENCE_MAP, reference_map)
    package = {
        "batch_id": "m120r_canonical_registry_production_v1",
        "milestone": "M120R",
        "generated_at": now(),
        "status": "PASS_CANONICAL_REGISTRY_UPDATED" if allow_update else "PASS_CANONICAL_REGISTRY_PREVIEW_READY",
        "summary": {
            "knowledge_asset_count": len(knowledge_items),
            "persona_count": len(persona_items),
            "alias_bridge_supported_count": persona_registry["summary"]["alias_bridge_supported_count"],
            "canonical_registry_written": allow_update,
            "prospect_output_used_as_source_count": 0,
        },
        "canonical_paths": {
            "knowledge_asset_registry": rel(KNOWLEDGE_CANONICAL),
            "persona_registry": rel(PERSONA_CANONICAL),
            "learning_persona_reference_map": rel(REFERENCE_MAP),
        },
        "knowledge_registry_preview": knowledge_registry,
        "persona_registry_preview": persona_registry,
        "reference_map_preview": reference_map,
    }
    write_json(M120 / "m120r_canonical_registry_production_v1.json", package)
    write_json(M120 / "knowledge_asset_registry_v1.preview.json", knowledge_registry)
    write_json(M120 / "persona_registry_v1.preview.json", persona_registry)
    write_json(M120 / "learning_persona_reference_map_v1.preview.json", reference_map)
    return package


def build_m121(m120: dict[str, Any]) -> dict[str, Any]:
    discovery = read_json(M111 / "candidate_discovery_package_v1.json", {"items": []})
    persona_registry = m120["persona_registry_preview"]
    alias_by_legacy = {item["legacy_or_pool_persona_id"]: item for item in persona_registry.get("alias_bridge") or []}
    tasks = []
    excluded = []
    for seed in discovery.get("items") or []:
        title = str(seed.get("seed_title") or "")
        company = seed.get("candidate_company_name")
        persona = str(seed.get("matched_persona") or "")
        alias = alias_by_legacy.get(persona, {})
        mapped_personas = alias.get("canonical_persona_refs") or []
        if is_customer_or_learning_case(title):
            excluded.append({
                "seed_id": seed.get("seed_id"),
                "seed_title": title,
                "candidate_company_name": company,
                "reason": "来源标题显示为客户案例/学习素材，不能直接转为潜客；只可用于知识/画像支撑。",
            })
            continue
        if not company:
            tasks.append({
                "seed_id": seed.get("seed_id"),
                "seed_title": title,
                "candidate_company_name": None,
                "task_status": "needs_company_identification",
                "mapped_canonical_personas": mapped_personas,
                "required_sources": ["official_owned", "platform_operating_fact", "authoritative_third_party"],
                "source_locator_required": True,
                "ready_for_trusted_pool_report_only": False,
            })
            continue
        tasks.append({
            "seed_id": seed.get("seed_id"),
            "seed_title": title,
            "candidate_company_name": company,
            "task_status": "needs_public_strong_evidence",
            "mapped_canonical_personas": mapped_personas,
            "required_sources": ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"],
            "source_locator_required": True,
            "ready_for_trusted_pool_report_only": False,
            "boundary_note": "学习素材触发的候选线索必须重新采集公开强来源；seed 本身不计入 prospect evidence。",
        })
    source_policy = {
        "policy_id": "evidence_acquisition_source_policy_v1",
        "generated_at": now(),
        "source_categories": ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"],
        "excluded_as_evidence": ["internal_or_legacy_reference", "learning_material_seed", "customer_case_title"],
        "minimum_report_only_entry": "至少 1 条可定位强来源 + mapped canonical persona + ICP 初始解释。",
    }
    package = {
        "batch_id": "m121r_evidence_acquisition_engine_v1",
        "milestone": "M121R",
        "generated_at": now(),
        "status": "PASS_EVIDENCE_ACQUISITION_TASKS_READY",
        "summary": {
            "input_seed_count": len(discovery.get("items") or []),
            "evidence_collection_task_count": len(tasks),
            "excluded_learning_source_case_count": len(excluded),
            "ready_for_trusted_pool_report_only_count": 0,
            "strong_evidence_collected_count": 0,
        },
        "source_policy": source_policy,
        "evidence_collection_tasks": tasks,
        "excluded_learning_source_cases": excluded,
    }
    write_json(M121 / "m121r_evidence_acquisition_engine_v1.json", package)
    write_json(M121 / "evidence_collection_task_queue_v1.json", {"generated_at": now(), "summary": package["summary"], "items": tasks})
    write_json(M121 / "excluded_learning_source_case_register_v1.json", {"generated_at": now(), "summary": {"excluded_count": len(excluded)}, "items": excluded})
    return package


def build_m122(m121: dict[str, Any], allow_update: bool) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    source_trace: dict[str, list[dict[str, Any]]] = {}
    for task in m121.get("evidence_collection_tasks") or []:
        if not task.get("ready_for_trusted_pool_report_only"):
            continue
        company = str(task.get("candidate_company_name") or "").strip()
        if not company:
            continue
        pid = "m122r_" + safe_id(company)
        candidates.append({
            "prospect_id": pid,
            "company_name": company,
            "matched_persona": (task.get("mapped_canonical_personas") or [""])[0],
            "match_reason": "由 M121R evidence acquisition task 形成，需公开强来源支撑。",
            "core_product_service_summary": "待由公开来源补齐。",
            "business_model_summary": "待由公开来源补齐。",
            "risk_or_gap": "待补公开强来源与 ICP 解释。",
            "level": "L5",
        })
        source_trace[pid] = []
    decisions = [evaluate_static_promotion(item, source_trace_by_prospect=source_trace).to_dict() for item in candidates]
    counts = dict(Counter(decision["suggested_level"] for decision in decisions))
    report = {
        "batch_id": "m122r_production_trusted_pool_report_only_v1",
        "milestone": "M122R",
        "generated_at": now(),
        "status": "PASS_REPORT_ONLY_NO_READY_CANDIDATES" if not candidates else "PASS_REPORT_ONLY_COMPLETE",
        "summary": {
            "candidate_count": len(candidates),
            "suggested_level_counts": counts,
            "canonical_pool_updated": False,
            "trusted_pool_update_allowed": allow_update,
            "old_excel_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
        },
        "decisions": decisions,
    }
    diff = {
        "batch_id": "m122r_pool_diff_report_v1",
        "milestone": "M122R",
        "generated_at": now(),
        "summary": {
            "append_candidate_count": 0,
            "update_candidate_count": 0,
            "reason": "M121R 仅生成 evidence acquisition tasks，尚无可定位强来源候选；不更新 canonical trusted pool。",
        },
        "items": [],
    }
    no_write = {
        "batch_id": "m122r_no_contamination_proof_v1",
        "milestone": "M122R",
        "generated_at": now(),
        "status": "PASS_NO_WRITE_NO_READY_CANDIDATES",
        "trusted_pool_updated": False,
        "old_excel_written": False,
        "knowledge_asset_registry_written_from_prospect": False,
        "persona_registry_written_from_prospect": False,
        "vault_regular_written": False,
    }
    write_json(M122 / "m122r_production_trusted_pool_report_only_v1.json", report)
    write_json(M122 / "m122r_pool_diff_report_v1.json", diff)
    write_json(M122 / "m122r_no_contamination_proof_v1.json", no_write)
    return {"report": report, "diff": diff, "no_write": no_write}


def count_vault_files() -> dict[str, int]:
    dirs = {
        "l1_vault_file_count": VAULT_ROOT / "01-L1 ICP强匹配档案",
        "l2_vault_file_count": VAULT_ROOT / "02-L2正式潜客档案",
        "l3_vault_file_count": VAULT_ROOT / "03-L3可信摘要卡",
    }
    counts = {}
    for key, path in dirs.items():
        counts[key] = len([p for p in path.glob("*.md") if p.name != "README.md"]) if path.exists() else 0
    return counts


def scan_dynamic_terms(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for base in paths:
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in candidates:
            if path.suffix.lower() not in {".md", ".json", ".py"}:
                continue
            if "legacy" in str(path).lower() or "optional" in str(path).lower():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if path.name == Path(__file__).name:
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            hits = [term for term in DYNAMIC_TERMS if term in text]
            if hits:
                findings.append({"path": rel(path), "terms": hits})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def scan_api_keys(paths: list[Path]) -> dict[str, Any]:
    patterns = [re.compile(r"sk-[A-Za-z0-9_-]{20,}"), re.compile(r"AKLT[A-Za-z0-9_-]{20,}"), re.compile(r"DELEGATE_LLM_API_KEY\s*=\s*[^<\s].+")]
    findings = []
    for base in paths:
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in candidates:
            if path.name == ".env" or path.suffix.lower() not in {".md", ".json", ".py", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(text) for pattern in patterns):
                findings.append(rel(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def build_m123(m122: dict[str, Any], allow_write: bool) -> dict[str, Any]:
    vault_counts = count_vault_files()
    package = {
        "batch_id": "m123r_user_delivery_product_v1",
        "milestone": "M123R",
        "generated_at": now(),
        "status": "PASS_USER_DELIVERY_PRODUCT_READY",
        "summary": {
            **vault_counts,
            "new_vault_preview_count": 0,
            "new_vault_regular_write_count": 0,
            "vault_regular_write_allowed": allow_write,
            "source_of_truth": "trusted_prospect_pool_v1 + source_trace_index; vault is reading layer only",
        },
        "delivery_contract": {
            "user_visible_levels": ["L1", "L2", "L3"],
            "hidden_or_work_queue_levels": ["L4", "L5"],
            "must_show_fields": ["company_name", "matched_persona", "why_icp", "strong_evidence", "risk_or_gap", "static_level"],
            "must_not_show_as_static_state_policy": "dynamic_sales_or_followup_terms_blocked_by_static_boundary_scan",
        },
        "next_publish_condition": "M122R 产生新增 L1/L2/L3 或 canonical pool diff 后，先生成 preview，再通过链接/动态字段/legacy-source 检查，最后显式 allow 写 vault 正区。",
    }
    write_json(M123 / "m123r_user_delivery_product_v1.json", package)
    return package


def build_m124(m120: dict[str, Any], m121: dict[str, Any], m122: dict[str, Any], m123: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m120r_m125_sustainable_production_system.py", "scripts/businessmaster_pipeline.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    roots = [M120, M121, M122, M123, M124, M125, CANONICAL]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = scan_dynamic_terms([M120, M121, M122, M123, CANONICAL, WORKSPACE / "scripts/build_m120r_m125_sustainable_production_system.py"])
    api = scan_api_keys([M120, M121, M122, M123, M124, M125, CANONICAL, WORKSPACE / "scripts/build_m120r_m125_sustainable_production_system.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m120r_m125_validation')"])
    pipeline_dry_run = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "production", "--dry-run"])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and pipeline_dry_run["returncode"] == 0 else "FAIL"
    report = {
        "batch_id": "m124r_operating_system_hardening_v1",
        "milestone": "M124R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "canonical_knowledge_asset_count": m120["summary"]["knowledge_asset_count"],
            "canonical_persona_count": m120["summary"]["persona_count"],
            "evidence_collection_task_count": m121["summary"]["evidence_collection_task_count"],
            "trusted_pool_report_only_candidate_count": m122["report"]["summary"]["candidate_count"],
            "vault_regular_write_count": m123["summary"]["new_vault_regular_write_count"],
            "system_entrypoint": "scripts/businessmaster_pipeline.py --mode production",
        },
        "py_compile": py_compile,
        "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]},
        "pipeline_production_dry_run": pipeline_dry_run,
    }
    handoff = {
        "batch_id": "handoff_snapshot_m124_v1",
        "milestone": "M124R",
        "generated_at": now(),
        "status": "READY_FOR_EVIDENCE_COLLECTION_AND_M125_SCALE" if status == "PASS" else "NEEDS_FIX",
        "current_state": "M120-M124 已把知识/画像 canonical registry、证据采集任务、trusted pool report-only 边界、vault 用户层和系统入口固化。",
        "next_commands": [
            "python3 scripts/businessmaster_pipeline.py --mode production --dry-run",
            "python3 scripts/build_m120r_m125_sustainable_production_system.py --stage all --allow-canonical-registry-update",
            "python3 scripts/businessmaster_pipeline.py --mode readiness --dry-run",
        ],
        "hard_boundaries": ["不写旧 Excel", "不从潜客写知识资产", "不从潜客写 persona registry", "不引入动态经营字段"],
    }
    write_json(M124 / "m124r_operating_system_hardening_v1.json", report)
    write_json(M124 / "handoff_snapshot_m124_v1.json", handoff)
    return report


def build_m125(m121: dict[str, Any]) -> dict[str, Any]:
    tasks = m121.get("evidence_collection_tasks") or []
    by_status = Counter(task.get("task_status") for task in tasks)
    by_persona = defaultdict(int)
    for task in tasks:
        for persona in task.get("mapped_canonical_personas") or ["unmapped"]:
            by_persona[persona] += 1
    package = {
        "batch_id": "m125r_scale_production_readiness_v1",
        "milestone": "M125R",
        "generated_at": now(),
        "status": "PASS_SCALE_PRODUCTION_READY_FOR_MANAGED_EVIDENCE_COLLECTION",
        "summary": {
            "task_count": len(tasks),
            "task_status_counts": dict(by_status),
            "mapped_persona_task_counts": dict(sorted(by_persona.items())),
            "recommended_next_batch_size": min(30, len(tasks)),
            "scale_target_after_m120_m124": "100-200 prospects only after evidence collection quality is stable",
        },
        "scale_policy": {
            "do_not_scale_until": ["official/platform/authoritative source locators collected", "report_only nonzero", "pool diff explainable", "vault preview passes checks"],
            "quality_first_metrics": ["source_category coverage", "ICP explanation specificity", "L1/L2/L3 distribution", "gap queue closure rate"],
        },
    }
    write_json(M125 / "m125r_scale_production_readiness_v1.json", package)
    return package


def update_panel(m120: dict[str, Any], m121: dict[str, Any], m122: dict[str, Any], m123: dict[str, Any], m124: dict[str, Any], m125: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    pool = read_json(POOL, {"items": []})
    counts = level_counts([item for item in pool.get("items") or [] if isinstance(item, dict)])
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M125R_SUSTAINABLE_PRODUCTION_SYSTEM_READY" if m124["status"] == "PASS" else "FAIL_M124R_OPERATING_SYSTEM_HARDENING",
        "latest_milestone": "M125R",
        "counts": {
            "trusted_pool_count": len(pool.get("items") or []),
            "l1_count": counts.get("L1", 0),
            "l2_count": counts.get("L2", 0),
            "l3_count": counts.get("L3", 0),
            "l4_count": counts.get("L4", 0),
            "l5_count": counts.get("L5", 0),
            "canonical_knowledge_asset_count": m120["summary"]["knowledge_asset_count"],
            "canonical_persona_count": m120["summary"]["persona_count"],
            "evidence_collection_task_count": m121["summary"]["evidence_collection_task_count"],
            "excluded_learning_source_case_count": m121["summary"]["excluded_learning_source_case_count"],
            "trusted_pool_report_only_candidate_count": m122["report"]["summary"]["candidate_count"],
            "vault_regular_write_count": m123["summary"]["new_vault_regular_write_count"],
        },
        "canonical_next_action": "进入受控 evidence collection：先为 M121R 任务补 official/platform/authoritative source locator，再跑 M122 report-only；不要从学习素材标题直接转潜客。",
        "m120r_canonical_registry_production": m120["summary"],
        "m121r_evidence_acquisition_engine": m121["summary"],
        "m122r_production_trusted_pool_batch": m122["report"]["summary"],
        "m123r_user_delivery_product": m123["summary"],
        "m124r_operating_system_hardening": m124["summary"],
        "m125r_scale_production_readiness": m125["summary"],
    })
    write_json(PANEL, panel)


def main() -> int:
    args = build_parser().parse_args()
    m120 = build_m120(args.allow_canonical_registry_update) if args.stage in {"all", "registries"} else read_json(M120 / "m120r_canonical_registry_production_v1.json")
    m121 = build_m121(m120) if args.stage in {"all", "evidence"} else read_json(M121 / "m121r_evidence_acquisition_engine_v1.json")
    m122 = build_m122(m121, args.allow_trusted_pool_update) if args.stage in {"all", "pool"} else {"report": read_json(M122 / "m122r_production_trusted_pool_report_only_v1.json")}
    m123 = build_m123(m122, args.allow_vault_regular_write) if args.stage in {"all", "delivery"} else read_json(M123 / "m123r_user_delivery_product_v1.json")
    m125 = build_m125(m121) if args.stage in {"all", "scale"} else read_json(M125 / "m125r_scale_production_readiness_v1.json")
    m124 = build_m124(m120, m121, m122, m123) if args.stage in {"all", "hardening"} else read_json(M124 / "m124r_operating_system_hardening_v1.json")
    if args.stage == "all":
        update_panel(m120, m121, m122, m123, m124, m125)
    output = {
        "m120": m120.get("summary"),
        "m121": m121.get("summary"),
        "m122": m122.get("report", {}).get("summary"),
        "m123": m123.get("summary"),
        "m124": m124.get("summary"),
        "m125": m125.get("summary"),
        "validation": m124.get("status"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if m124.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
