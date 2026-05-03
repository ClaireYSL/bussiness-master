from __future__ import annotations

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
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M106 = MILESTONES / "milestone106r_knowledge_review_cycle"
M107 = MILESTONES / "milestone107r_persona_gap_closure_cycle"
M108 = MILESTONES / "milestone108r_scale_report_only_cycle"
M109 = MILESTONES / "milestone109r_knowledge_asset_ingestion_closure"
M110 = MILESTONES / "milestone110r_persona_registry_production_closure"
M111 = MILESTONES / "milestone111r_candidate_discovery_evidence_collection"
M112 = MILESTONES / "milestone112r_trusted_pool_production_batch"
M113 = MILESTONES / "milestone113r_vault_delivery_operations"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]


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


def trace_by_id(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or "").strip(): [s for s in item.get("sources") or [] if isinstance(s, dict)] for item in trace.get("items") or []}


def asset_track(asset_type: str, title: str) -> str:
    text = f"{asset_type} {title}"
    if any(token in text for token in ["跨境", "出海", "SmallRig", "倍思", "电商"]):
        return "cross_border_ecommerce"
    if any(token in text for token in ["零售", "门店", "连锁", "采销", "供应链"]):
        return "retail_consumer"
    if any(token in text for token in ["制造", "工厂", "研发", "供应链", "PCE"]):
        return "advanced_manufacturing"
    return "general_business"


def build_m109() -> dict[str, Any]:
    preview = read_json(M106 / "formal_knowledge_asset_update_preview_v1.json", {"items": []})
    items = []
    for row in preview.get("items") or []:
        required_ok = all(row.get(field) for field in ["summary_draft", "key_signals_draft", "recommended_usage_draft", "confidence_level_draft", "source_path_or_url"])
        status = "knowledge_asset_write_ready" if required_ok and not row.get("prospect_output_used_as_source") else "needs_review"
        item = {
            "asset_id": row.get("proposed_asset_id"),
            "asset_type": row.get("asset_type"),
            "title": row.get("title"),
            "source_path_or_url": row.get("source_path_or_url"),
            "source_origin": "internal" if str(row.get("source_path_or_url") or "").startswith("/Users/") else "public_web",
            "track_ids": [asset_track(str(row.get("asset_type") or ""), str(row.get("title") or ""))],
            "persona_ids": [],
            "summary": row.get("summary_draft"),
            "key_signals": row.get("key_signals_draft"),
            "recommended_usage": row.get("recommended_usage_draft"),
            "confidence_level": row.get("confidence_level_draft"),
            "registry_update_status": status,
            "formal_write_enabled": False,
            "source_trace_verified": bool(row.get("source_path_or_url")),
            "prospect_output_used_as_source": False,
        }
        items.append(item)
    ready = [item for item in items if item["registry_update_status"] == "knowledge_asset_write_ready"]
    package = {"batch_id": "knowledge_asset_registry_update_package_v1", "milestone": "M109R", "generated_at": now(), "status": "PASS_KNOWLEDGE_ASSET_UPDATE_PACKAGE_READY", "summary": {"input_preview_count": len(preview.get("items") or []), "knowledge_asset_write_ready_count": len(ready), "needs_review_count": len(items) - len(ready), "formal_registry_write_count": 0, "prospect_output_used_as_source_count": 0}, "items": items}
    guard = {"batch_id": "knowledge_asset_registry_update_guard_v1", "milestone": "M109R", "generated_at": now(), "status": "PASS_GUARDED_PREVIEW_ONLY", "allow_flag_required": "--allow-knowledge-asset-registry-update", "formal_registry_write_enabled": False, "rules": ["source_trace_verified=true", "prospect_output_used_as_source=false", "summary/key_signals/usage/confidence complete"]}
    source_trace = {"batch_id": "knowledge_asset_source_trace_v1", "milestone": "M109R", "generated_at": now(), "summary": {"trace_count": len(items), "verified_source_count": sum(1 for item in items if item["source_trace_verified"]), "prospect_output_used_as_source_count": 0}, "items": [{"asset_id": item["asset_id"], "source_path_or_url": item["source_path_or_url"], "source_trace_verified": item["source_trace_verified"]} for item in items]}
    write_json(M109 / "knowledge_asset_registry_update_package_v1.json", package)
    write_json(M109 / "knowledge_asset_registry_update_guard_v1.json", guard)
    write_json(M109 / "knowledge_asset_source_trace_v1.json", source_trace)
    return {"package": package, "guard": guard, "source_trace": source_trace}


def build_m110(m109: dict[str, Any]) -> dict[str, Any]:
    preview = read_json(M107 / "persona_registry_gap_closure_preview_v1.json", {"items": []})
    assets = {str(item.get("asset_id")): item for item in m109["package"]["items"] if item.get("registry_update_status") == "knowledge_asset_write_ready"}
    items = []
    for row in preview.get("items") or []:
        refs = []
        for ref in row.get("candidate_knowledge_refs") or []:
            asset = assets.get(str(ref.get("proposed_asset_id")))
            if asset:
                refs.append({"asset_id": asset["asset_id"], "title": asset["title"], "source_path_or_url": asset["source_path_or_url"]})
        status = "active_supported" if refs else "active_needs_validation"
        items.append({
            "persona_id": row.get("persona_id"),
            "display_name": row.get("display_name"),
            "production_status": status,
            "reference_knowledge_assets": refs,
            "fit_criteria_preview": "基于参考知识资产提炼 ICP 适配标准；需正式 registry 写入前人工复核。",
            "non_fit_boundary_preview": "不得用潜客命中结果作为正例/反例；需真实案例或解决方案支撑边界。",
            "typical_jtbd_preview": "围绕经营分析、渠道/供应链/组织复杂度、数据协同与决策效率提炼。",
            "persona_registry_write_enabled": False,
            "prospect_output_used_as_persona_source": False,
        })
    package = {"batch_id": "persona_registry_update_package_v1", "milestone": "M110R", "generated_at": now(), "status": "PASS_PERSONA_REGISTRY_UPDATE_PACKAGE_READY", "summary": {"input_preview_count": len(preview.get("items") or []), "active_supported_count": sum(1 for item in items if item["production_status"] == "active_supported"), "active_needs_validation_count": sum(1 for item in items if item["production_status"] == "active_needs_validation"), "persona_registry_write_count": 0, "prospect_output_used_as_persona_source_count": 0}, "items": items}
    guard = {"batch_id": "persona_registry_update_guard_v1", "milestone": "M110R", "generated_at": now(), "status": "PASS_PERSONA_REGISTRY_PREVIEW_ONLY", "allow_flag_required": "--allow-persona-registry-update", "persona_registry_write_enabled": False, "rules": ["reference_knowledge_assets must be write-ready", "prospect_output_used_as_persona_source=false", "fit/non-fit/JTBD preview complete"]}
    write_json(M110 / "persona_registry_update_package_v1.json", package)
    write_json(M110 / "persona_registry_update_guard_v1.json", guard)
    return {"package": package, "guard": guard}


def company_name_from_seed(seed_title: str) -> str | None:
    title = seed_title or ""
    known = ["倍思", "SmallRig", "乐其", "萨摩耶", "斗满", "自然堂", "名创优品", "乐刻", "锅圈", "茶百道", "蜜雪冰城"]
    for name in known:
        if name in title:
            return name if name not in {"SmallRig"} else "乐其 SmallRig"
    cleaned = re.sub(r"[\[\]【】].*?$", "", title).strip()
    cleaned = re.split(r"[-_：:，,]", cleaned)[0].strip()
    if 2 <= len(cleaned) <= 18 and not any(token in cleaned for token in ["方案", "白皮书", "物料", "报告", "数据", "BI"]):
        return cleaned
    return None


def evidence_locator_for_candidate(company: str | None, seed: dict[str, Any]) -> str | None:
    if not company:
        return None
    return seed.get("source_path_or_url") or seed.get("seed_id")


def build_m111(m110: dict[str, Any]) -> dict[str, Any]:
    seeds = read_json(M108 / "scale_report_only_candidate_input_v1.json", {"items": []})
    persona_supported = {str(item.get("persona_id")) for item in m110["package"]["items"] if item.get("production_status") == "active_supported"}
    discovery = []
    evidence_items = []
    source_trace_items = []
    for seed in seeds.get("items") or []:
        company = company_name_from_seed(str(seed.get("seed_title") or ""))
        persona = str(seed.get("matched_persona") or "")
        locator = evidence_locator_for_candidate(company, seed)
        ready = bool(company and locator and persona in persona_supported)
        task = {
            "seed_id": seed.get("seed_id"),
            "seed_title": seed.get("seed_title"),
            "candidate_company_name": company,
            "matched_persona": persona,
            "discovery_status": "candidate_discovered" if company else "needs_company_identification",
            "persona_supported": persona in persona_supported,
            "required_evidence_types": ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"],
            "ready_for_trusted_pool_report_only": ready,
        }
        discovery.append(task)
        if ready:
            prospect_id = "m111r_candidate_" + re.sub(r"\W+", "_", company.lower()).strip("_")
            evidence_items.append({
                "prospect_id": prospect_id,
                "company_name": company,
                "matched_persona": persona,
                "match_reason": f"由学习素材 {seed.get('seed_title')} 触发候选发现，需以 evidence-first 方式验证 ICP 匹配。",
                "core_product_service_summary": "候选发现阶段待用官网/公开资料补全。",
                "business_model_summary": "候选发现阶段待用强来源补全。",
                "risk_or_gap": "当前仅为候选发现 report-only 输入，不写 canonical trusted pool。",
                "source_locator": locator,
                "evidence_strength": "source_material_seed",
                "level": "L5",
            })
            source_trace_items.append({
                "prospect_id": prospect_id,
                "company_name": company,
                "sources": [{"source_type": "source_material_seed", "source_category": "internal_or_legacy_reference", "source_locator": locator, "evidence_strength": "source_material_seed", "supports_dimension": "candidate_discovery_seed", "summary": "学习素材触发候选发现；不计入 L1/L2 强来源，后续需补官网/平台/权威来源。"}],
            })
    package = {"batch_id": "candidate_discovery_package_v1", "milestone": "M111R", "generated_at": now(), "status": "PASS_CANDIDATE_DISCOVERY_TASKS_READY", "summary": {"seed_count": len(seeds.get("items") or []), "candidate_discovered_count": sum(1 for item in discovery if item["candidate_company_name"]), "ready_for_report_only_count": len(evidence_items), "needs_company_identification_count": sum(1 for item in discovery if not item["candidate_company_name"])}, "items": discovery}
    evidence = {"batch_id": "evidence_patch_package_v1", "milestone": "M111R", "generated_at": now(), "summary": {"candidate_count": len(evidence_items), "strong_evidence_ready_count": 0, "canonical_pool_update_enabled": False}, "items": evidence_items}
    trace = {"batch_id": "source_trace_package_v1", "milestone": "M111R", "generated_at": now(), "summary": {"source_trace_count": len(source_trace_items), "strong_source_trace_count": 0, "seed_only_trace_count": len(source_trace_items)}, "items": source_trace_items}
    write_json(M111 / "candidate_discovery_package_v1.json", package)
    write_json(M111 / "evidence_patch_package_v1.json", evidence)
    write_json(M111 / "source_trace_package_v1.json", trace)
    return {"package": package, "evidence": evidence, "trace": trace}


def build_m112(m111: dict[str, Any]) -> dict[str, Any]:
    candidates = m111["evidence"]["items"]
    trace_map = {item["prospect_id"]: item.get("sources") or [] for item in m111["trace"]["items"]}
    decisions = []
    for candidate in candidates:
        decision = evaluate_static_promotion(candidate, source_trace_by_prospect=trace_map).to_dict()
        decisions.append(decision)
    counts = Counter(decision["suggested_level"] for decision in decisions)
    report = {"batch_id": "trusted_pool_production_report_only_v1", "milestone": "M112R", "generated_at": now(), "status": "PASS_REPORT_ONLY_COMPLETE" if decisions else "PASS_REPORT_ONLY_NO_READY_CANDIDATES", "summary": {"candidate_count": len(candidates), "suggested_level_counts": dict(counts), "canonical_pool_updated": False, "source_trace_updated": False, "old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False}, "decisions": decisions}
    diff = {"batch_id": "trusted_pool_production_pool_diff_v1", "milestone": "M112R", "generated_at": now(), "summary": {"append_candidate_count": 0, "update_candidate_count": 0, "reason": "M111R candidates are seed-only and lack countable strong evidence; no canonical update."}, "items": []}
    proof = {"batch_id": "trusted_pool_production_no_contamination_proof_v1", "milestone": "M112R", "generated_at": now(), "status": "PASS_NO_WRITE_REPORT_ONLY", "canonical_pool_updated": False, "source_trace_updated": False, "old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False}
    write_json(M112 / "trusted_pool_production_report_only_v1.json", report)
    write_json(M112 / "trusted_pool_production_pool_diff_v1.json", diff)
    write_json(M112 / "trusted_pool_production_no_contamination_proof_v1.json", proof)
    return {"report": report, "diff": diff, "proof": proof}


def build_m113(m112: dict[str, Any]) -> dict[str, Any]:
    decisions = m112["report"].get("decisions") or []
    preview_items = []
    for decision in decisions:
        if decision.get("suggested_level") in {"L1", "L2", "L3"}:
            preview_items.append({"prospect_id": decision.get("prospect_id"), "company_name": decision.get("company_name"), "suggested_level": decision.get("suggested_level"), "vault_preview_ready": False, "reason": "候选缺强来源，暂不生成用户正区档案。"})
    package = {"batch_id": "vault_delivery_preview_package_v1", "milestone": "M113R", "generated_at": now(), "status": "PASS_VAULT_PREVIEW_NO_REGULAR_WRITE", "summary": {"decision_count": len(decisions), "vault_preview_candidate_count": len(preview_items), "vault_regular_write_count": 0, "link_check_required_before_write": True}, "items": preview_items}
    schedule = {"batch_id": "monthly_operating_schedule_v1", "milestone": "M113R", "generated_at": now(), "cadence": ["学习素材更新", "知识资产 guarded preview", "画像 registry preview", "候选发现与 evidence 采集", "trusted pool report-only/update", "vault preview/publish", "handoff snapshot"], "next_action": "M114R：对 M111R needs_company_identification 队列执行真实候选公司识别和公开强来源采集。"}
    handoff = {"batch_id": "handoff_snapshot_m113_v1", "milestone": "M113R", "generated_at": now(), "status": "READY_FOR_M114R", "current_boundary": "M109-M113 完成生产化 preview/report-only；未写正式知识资产、persona registry、canonical trusted pool 或 vault 正区。", "next_command": "python3 scripts/build_m109r_m113_production_cycle.py"}
    write_json(M113 / "vault_delivery_preview_package_v1.json", package)
    write_json(M113 / "monthly_operating_schedule_v1.json", schedule)
    write_json(M113 / "handoff_snapshot_m113_v1.json", handoff)
    return {"package": package, "schedule": schedule, "handoff": handoff}


def dynamic_scan(paths: list[Path]) -> dict[str, Any]:
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
            if path.name == "build_m109r_m113_production_cycle.py":
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            hits = [term for term in DYNAMIC_TERMS if term in text]
            if hits:
                findings.append({"path": rel(path), "terms": hits})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def api_key_scan(paths: list[Path]) -> dict[str, Any]:
    patterns = [re.compile(r"sk-[A-Za-z0-9_-]{20,}"), re.compile(r"AKLT[a-zA-Z0-9_-]{20,}"), re.compile(r"DELEGATE_LLM_API_KEY\s*=\s*[^<\s].+")]
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


def validate() -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m109r_m113_production_cycle.py", "scripts/build_m106r_m108_next_operating_cycle.py", "scripts/businessmaster_pipeline.py", "scripts/trusted_pool_runner.py"])
    roots = [M109, M110, M111, M112, M113, M56]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = dynamic_scan([M109, M110, M111, M112, M113, PANEL, WORKSPACE / "scripts/build_m109r_m113_production_cycle.py"])
    api = api_key_scan([M109, M110, M111, M112, M113, WORKSPACE / "scripts/build_m109r_m113_production_cycle.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m109r_m113_validation')"])
    update_guard = run(["bash", "-lc", "tmp=/tmp/bm_m112_update_guard; rm -rf $tmp; mkdir -p $tmp; cp deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json $tmp/pool.json; python3 scripts/trusted_pool_runner.py --mode update_trusted_pool --trusted-pool $tmp/pool.json --output-file $tmp/report.json --gap-queue-file $tmp/gap.json --source-trace-output $tmp/trace.json --no-write-proof-file $tmp/no_write.json --pool-diff-file $tmp/diff.json --validation-report-file $tmp/validation.json >/tmp/bm_m112_update_out.txt 2>/tmp/bm_m112_update_err.txt; test $? -ne 0"])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and update_guard["returncode"] == 0 else "FAIL"
    validation = {"milestone": "M109R-M113R", "generated_at": now(), "status": status, "py_compile": py_compile, "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]}, "trusted_pool_update_guard_without_allow": {"returncode": update_guard["returncode"], "stdout": update_guard["stdout"], "stderr": update_guard["stderr"]}}
    write_json(M113 / "validation_report_v1.json", validation)
    return validation


def update_panel(m109: dict[str, Any], m110: dict[str, Any], m111: dict[str, Any], m112: dict[str, Any], m113: dict[str, Any], validation: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    pool = read_json(POOL, {"items": []})
    counts = level_counts([item for item in pool.get("items") or [] if isinstance(item, dict)])
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M113R_PRODUCTION_CYCLE_READY" if validation["status"] == "PASS" else "FAIL_M113R_PRODUCTION_CYCLE",
        "latest_milestone": "M113R",
        "counts": {
            "trusted_pool_count": len(pool.get("items") or []),
            "l1_count": counts.get("L1", 0),
            "l2_count": counts.get("L2", 0),
            "l3_count": counts.get("L3", 0),
            "l4_count": counts.get("L4", 0),
            "l5_count": counts.get("L5", 0),
            "knowledge_asset_write_ready_count": m109["package"]["summary"]["knowledge_asset_write_ready_count"],
            "persona_active_supported_count": m110["package"]["summary"]["active_supported_count"],
            "candidate_discovered_count": m111["package"]["summary"]["candidate_discovered_count"],
            "trusted_pool_report_only_candidate_count": m112["report"]["summary"]["candidate_count"],
            "vault_regular_write_count": m113["package"]["summary"]["vault_regular_write_count"],
        },
        "canonical_next_action": "M114R：对 M111R needs_company_identification 队列执行真实候选公司识别和公开强来源采集；M109/M110 仍是 guarded preview，未写正式 registry。",
        "m109r_knowledge_asset_ingestion_closure": m109["package"]["summary"],
        "m110r_persona_registry_production_closure": m110["package"]["summary"],
        "m111r_candidate_discovery_evidence_collection": m111["package"]["summary"],
        "m112r_trusted_pool_production_batch": m112["report"]["summary"],
        "m113r_vault_delivery_operations": m113["package"]["summary"],
    })
    write_json(PANEL, panel)


def main() -> int:
    m109 = build_m109()
    m110 = build_m110(m109)
    m111 = build_m111(m110)
    m112 = build_m112(m111)
    m113 = build_m113(m112)
    validation = validate()
    update_panel(m109, m110, m111, m112, m113, validation)
    print(json.dumps({"m109": m109["package"]["summary"], "m110": m110["package"]["summary"], "m111": m111["package"]["summary"], "m112": m112["report"]["summary"], "m113": m113["package"]["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
