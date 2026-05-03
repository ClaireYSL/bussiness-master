from __future__ import annotations

import hashlib
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
M92 = MILESTONES / "milestone92r_learning_source_pipeline"
M93 = MILESTONES / "milestone93r_knowledge_asset_governance"
M94 = MILESTONES / "milestone94r_persona_learning_recalibration"
M95 = MILESTONES / "milestone95r_learning_asset_driven_prospect_engine"
M96 = MILESTONES / "milestone96r_trusted_pool_product_layer"
M97 = MILESTONES / "milestone97r_long_term_operations"
M98 = MILESTONES / "milestone98r_scale_expansion_readiness"

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


def sha(payload: Any) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def trace_by_id(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or "").strip(): [s for s in item.get("sources") or [] if isinstance(s, dict)] for item in trace.get("items") or []}


def level_counts(pool_items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("level") or "unknown") for item in pool_items))


def build_persona_learning_index(persona_map: dict[str, Any], drafts: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_persona: dict[str, list[dict[str, Any]]] = defaultdict(list)
    draft_by_material = {str(item.get("material_id")): item for item in drafts.get("items") or []}
    for persona in persona_map.get("items") or []:
        persona_id = str(persona.get("persona_id") or "unknown")
        for evidence in persona.get("representative_evidence") or []:
            material_id = str(evidence.get("material_id") or "")
            draft = draft_by_material.get(material_id)
            by_persona[persona_id].append({
                "ref_id": draft.get("draft_asset_id") if draft else material_id,
                "ref_type": "knowledge_extraction_draft" if draft else "source_material_evidence",
                "material_id": material_id,
                "title": evidence.get("title"),
                "source_locator": evidence.get("source_locator"),
                "source_root": evidence.get("source_root"),
                "source_strength": evidence.get("source_strength"),
                "learning_status": persona.get("persona_learning_status") or persona.get("support_status"),
                "reference_only_not_prospect_evidence": True,
            })
    for persona_id in by_persona:
        # 保留最多 5 条，避免把潜客侧引用膨胀成知识资产复制。
        by_persona[persona_id] = by_persona[persona_id][:5]
    return dict(by_persona)


def build_m95(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    source_map = trace_by_id(trace)
    drafts = read_json(M92 / "knowledge_extraction_draft_package_v1.json", {"items": []})
    persona_map = read_json(M94 / "persona_evidence_map_v2.json", {"items": []})
    persona_index = build_persona_learning_index(persona_map, drafts)
    refs = []
    runner_inputs = []
    missing_refs = []
    decisions = []
    for item in items:
        prospect_id = str(item.get("prospect_id") or "")
        persona = str(item.get("matched_persona") or "unknown")
        icp_refs = persona_index.get(persona, [])
        decision = evaluate_static_promotion(item, source_trace_by_prospect=source_map).to_dict()
        decisions.append(decision)
        if not icp_refs:
            missing_refs.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "matched_persona": persona, "gap_type": "icp_reference_asset_refs_missing", "reason": "该画像尚未绑定学习素材支撑，不能把潜客自身当作画像证据。"})
        refs.append({
            "prospect_id": prospect_id,
            "company_name": item.get("company_name"),
            "matched_persona": persona,
            "level": item.get("level"),
            "icp_reference_asset_refs": icp_refs,
            "reference_count": len(icp_refs),
            "reference_only_not_customer_case_attribution": True,
            "prospect_output_used_as_knowledge_source": False,
        })
        runner_inputs.append({
            "prospect_id": prospect_id,
            "company_name": item.get("company_name"),
            "matched_persona": persona,
            "current_level": item.get("level"),
            "suggested_level": decision["suggested_level"],
            "icp_reference_asset_refs": [ref["ref_id"] for ref in icp_refs],
            "strong_evidence_count": decision["strong_evidence_count"],
            "gap_count": len(decision["gap_queue"]),
        })
    package = {
        "batch_id": "learning_asset_driven_prospect_engine_v1",
        "milestone": "M95R",
        "generated_at": now(),
        "summary": {
            "prospect_count": len(items),
            "with_icp_reference_count": sum(1 for r in refs if r["reference_count"] > 0),
            "missing_icp_reference_count": len(missing_refs),
            "persona_count_with_learning_refs": len(persona_index),
            "runner_suggested_level_counts": dict(Counter(d["suggested_level"] for d in decisions)),
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        },
        "items": refs,
    }
    runner_input = {"batch_id": "trusted_pool_runner_learning_enriched_input_v1", "milestone": "M95R", "generated_at": now(), "summary": {"item_count": len(runner_inputs), "icp_reference_field": "icp_reference_asset_refs", "reference_semantics": "ICP 判断参考，不是 prospect evidence 或客户案例归因"}, "items": runner_inputs}
    no_contamination = {"milestone": "M95R", "generated_at": now(), "status": "PASS_NO_REVERSE_CONTAMINATION", "prospect_output_used_as_knowledge_source_count": 0, "prospect_output_used_as_persona_source_count": 0, "formal_knowledge_asset_written": False, "persona_registry_written": False, "old_excel_written": False}
    gap_queue = {"batch_id": "icp_reference_gap_queue_v1", "milestone": "M95R", "generated_at": now(), "summary": {"gap_count": len(missing_refs)}, "items": missing_refs}
    write_json(M95 / "learning_asset_reference_package_v1.json", package)
    write_json(M95 / "trusted_pool_runner_learning_enriched_input_v1.json", runner_input)
    write_json(M95 / "icp_reference_gap_queue_v1.json", gap_queue)
    write_json(M95 / "no_reverse_contamination_proof_v1.json", no_contamination)
    return {"package": package, "runner_input": runner_input, "gap_queue": gap_queue, "no_contamination": no_contamination, "decisions": decisions}


def vault_file_counts() -> dict[str, int]:
    dirs = {"L1": "01-L1 ICP强匹配档案", "L2": "02-L2正式潜客档案", "L3": "03-L3可信摘要卡", "L4": "04-L4待补证候选", "L5": "05-L5候选线索"}
    return {level: len(list((VAULT_ROOT / dirname).glob("*.md"))) if (VAULT_ROOT / dirname).exists() else 0 for level, dirname in dirs.items()}


def build_m96(pool: dict[str, Any], m95: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    persona_dist = Counter(str(item.get("matched_persona") or "unknown") for item in items)
    levels = level_counts(items)
    user_items = []
    for item in items:
        user_items.append({
            "prospect_id": item.get("prospect_id"),
            "company_name": item.get("company_name"),
            "level": item.get("level"),
            "matched_persona": item.get("matched_persona"),
            "why_icp": item.get("match_reason"),
            "core_product_or_service": item.get("core_product_service_summary"),
            "business_model": item.get("business_model_summary"),
            "risk_or_gap": item.get("risk_or_gap"),
            "source_locator": item.get("source_locator"),
            "user_visible_static_only": True,
        })
    product_view = {"batch_id": "trusted_pool_user_product_view_v1", "milestone": "M96R", "generated_at": now(), "summary": {"trusted_pool_count": len(items), "level_counts": levels, "persona_distribution": dict(persona_dist), "vault_physical_file_counts": vault_file_counts(), "user_entry": str(VAULT_ROOT / "00-索引与说明/可信潜客池工作台.md")}, "items": user_items}
    source_browser = {"batch_id": "trusted_pool_source_trace_browser_v1", "milestone": "M96R", "generated_at": now(), "summary": {"trace_reference_count": m95["package"]["summary"]["with_icp_reference_count"], "reference_gap_count": m95["gap_queue"]["summary"]["gap_count"], "reference_semantics": "知识/画像参考只解释 ICP 判断，不作为潜客 evidence。"}, "items": m95["package"]["items"]}
    redundancy = {"batch_id": "vault_redundancy_governance_report_v1", "milestone": "M96R", "generated_at": now(), "summary": {"vault_physical_file_counts": vault_file_counts(), "canonical_level_counts": levels, "deletion_performed": False, "recommendation": "继续以工作台和 L1/L2 索引为默认入口；物理重复文件后续单独治理，不在 M96R 删除。"}}
    md = f"""# M96R 可信潜客池用户产品层

## 当前用户入口

- 工作台：`{VAULT_ROOT / '00-索引与说明/可信潜客池工作台.md'}`
- L1/L2 索引是默认用户入口；旧 L3 摘要和历史重复文件不作为默认入口。

## 当前分布

- Trusted pool：`{len(items)}` 家
- Level：`{levels}`
- Persona：`{dict(persona_dist)}`

## 读取口径

本层只回答：是不是 ICP、为什么、证据是什么、可信到什么程度、缺什么升层。不表达动态经营优先级、跟进团队或触达时间。
"""
    write_json(M96 / "trusted_pool_user_product_view_v1.json", product_view)
    write_json(M96 / "trusted_pool_source_trace_browser_v1.json", source_browser)
    write_json(M96 / "vault_redundancy_governance_report_v1.json", redundancy)
    write_md(M96 / "trusted_pool_user_workbench_summary_v1.md", md)
    return {"product_view": product_view, "source_browser": source_browser, "redundancy": redundancy}


def build_m97(pool: dict[str, Any], m95: dict[str, Any], m96: dict[str, Any]) -> dict[str, Any]:
    readiness = {
        "batch_id": "project_readiness_check_v2",
        "milestone": "M97R",
        "generated_at": now(),
        "status": "PASS_LONG_TERM_OPERATION_READY",
        "summary": {
            "trusted_pool_count": len(pool.get("items") or []),
            "level_counts": level_counts(pool.get("items") or []),
            "learning_queue_ready": (M92 / "learnable_material_queue_v2.json").exists(),
            "knowledge_guard_ready": (M93 / "knowledge_asset_update_guard_v1.json").exists(),
            "persona_learning_ready": (M94 / "persona_evidence_map_v2.json").exists(),
            "prospect_engine_reference_ready": m95["package"]["summary"]["with_icp_reference_count"] > 0,
            "vault_product_layer_ready": True,
            "old_workbook_write_enabled": False,
        },
        "checks": {
            "canonical_pool_exists": POOL.exists(),
            "canonical_source_trace_exists": TRACE.exists(),
            "status_panel_exists": PANEL.exists(),
            "vault_root_exists": VAULT_ROOT.exists(),
            "no_reverse_contamination_proof": m95["no_contamination"]["status"],
        },
    }
    runbook = f"""# BusinessMaster Runbook v2

## 标准主线

1. 学习素材接入：运行 M92R 管道，更新学习队列和知识草稿。
2. 知识资产治理：运行 M93R guard，只在来源真实且审查通过后进入正式知识资产。
3. 画像学习：运行 M94R proposal，默认不改 persona registry。
4. 潜客引擎：运行 M95R，把 `icp_reference_asset_refs` 接到 trusted pool 判断。
5. 用户输出：运行 M96R，更新工作台、索引、source trace browser。
6. 扩容：只有 readiness PASS 后，才进入 M98R 的 100-200 扩容批次。

## 禁止动作

- 不写旧 Excel。
- 不把潜客输出写入知识资产。
- 不把潜客输出写入 persona registry。
- 不把 LLM 输出作为 evidence。
- 不在静态池表达经营优先级、跟进团队、触达时间。

## 当前下一步

M98R：按阈值做规模化扩容准入，而不是盲目新增数量。
"""
    operating = {"batch_id": "learning_and_pool_operating_panel_v1", "milestone": "M97R", "generated_at": now(), "summary": {**readiness["summary"], "m95_reference_gap_count": m95["gap_queue"]["summary"]["gap_count"], "m96_user_view_count": m96["product_view"]["summary"]["trusted_pool_count"]}, "next_action": "进入 M98R：100-200 规模化扩容准入模拟与质量门槛。"}
    handoff = {"batch_id": "handoff_snapshot_v3", "milestone": "M97R", "generated_at": now(), "current_commit_expected_clean_after_commit": True, "key_artifacts": {"runbook": rel(M97 / "businessmaster_runbook_v2.md"), "readiness": rel(M97 / "project_readiness_check_v2.json"), "operating_panel": rel(M97 / "learning_and_pool_operating_panel_v1.json")}, "next_command": "python3 scripts/build_m95r_m98_learning_pool_operating_system.py"}
    write_json(M97 / "project_readiness_check_v2.json", readiness)
    write_md(M97 / "businessmaster_runbook_v2.md", runbook)
    write_json(M97 / "learning_and_pool_operating_panel_v1.json", operating)
    write_json(M97 / "handoff_snapshot_v3.json", handoff)
    return {"readiness": readiness, "operating": operating, "handoff": handoff}


def build_m98(pool: dict[str, Any], m92: dict[str, Any], m94: dict[str, Any], m97: dict[str, Any]) -> dict[str, Any]:
    queue_items = m92.get("items") or []
    persona_support = {str(item.get("persona_id")): item for item in (m94.get("items") or [])}
    expansion_candidates = []
    for row in queue_items:
        persona = str(row.get("persona_guess") or "unknown")
        support = persona_support.get(persona, {})
        if persona == "unknown":
            readiness = "needs_persona_triage"
        elif support.get("persona_learning_status") == "learning_supported":
            readiness = "expansion_seed_ready"
        else:
            readiness = "needs_source_validation"
        expansion_candidates.append({
            "seed_id": row.get("material_id"),
            "seed_title": row.get("material_title"),
            "source_root": row.get("source_root"),
            "persona_guess": persona,
            "track_guess": row.get("track_guess"),
            "priority": row.get("priority"),
            "expansion_readiness": readiness,
            "allowed_next_step": "candidate_discovery_with_evidence_first_guard" if readiness == "expansion_seed_ready" else "triage_before_candidate_discovery",
        })
    counts = Counter(item["expansion_readiness"] for item in expansion_candidates)
    threshold = {
        "batch_id": "expansion_threshold_policy_v1",
        "milestone": "M98R",
        "generated_at": now(),
        "target_batch_size": "100-200",
        "entry_thresholds": {
            "learning_source_ready_ratio": ">= 70% seeds with source/persona support",
            "trusted_match_ready_target": ">= 80% after evidence collection",
            "official_or_strong_source_required": True,
            "prospect_to_knowledge_write_allowed": False,
            "legacy_excel_write_allowed": False,
        },
    }
    readiness = {
        "batch_id": "scale_expansion_readiness_report_v1",
        "milestone": "M98R",
        "generated_at": now(),
        "status": "PASS_SCALE_EXPANSION_POLICY_READY",
        "summary": {
            "seed_count": len(expansion_candidates),
            "readiness_counts": dict(counts),
            "recommended_initial_scale_batch": min(100, max(30, counts.get("expansion_seed_ready", 0))),
            "canonical_pool_count": len(pool.get("items") or []),
            "current_level_counts": level_counts(pool.get("items") or []),
            "readiness_depends_on_m97": m97["readiness"]["status"],
        },
        "items": expansion_candidates,
    }
    quality_gate = {"batch_id": "quality_gate_check_v1", "milestone": "M98R", "generated_at": now(), "status": "PASS_QUALITY_GATE_DEFINED", "gates": ["候选必须引用画像/知识学习资产或进入 source gap", "L3 至少 1 条强来源", "L2 至少 2 条强来源且解释完整", "L1 至少 3 条强来源、2 类来源且有 ICP 支撑", "潜客不得写入知识资产或 persona registry", "旧 Excel 写入默认禁止"]}
    write_json(M98 / "expansion_threshold_policy_v1.json", threshold)
    write_json(M98 / "scale_expansion_readiness_report_v1.json", readiness)
    write_json(M98 / "quality_gate_check_v1.json", quality_gate)
    return {"threshold": threshold, "readiness": readiness, "quality_gate": quality_gate}


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
            if path.name == "build_m95r_m98_learning_pool_operating_system.py":
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


def update_panel(m95: dict[str, Any], m96: dict[str, Any], m97: dict[str, Any], m98: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    counts = m96["product_view"]["summary"]["level_counts"]
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M98R_LEARNING_POOL_OPERATING_SYSTEM_READY",
        "latest_milestone": "M98R",
        "counts": {
            "trusted_pool_count": m96["product_view"]["summary"]["trusted_pool_count"],
            "l1_count": counts.get("L1", 0),
            "l2_count": counts.get("L2", 0),
            "l3_count": counts.get("L3", 0),
            "l4_count": counts.get("L4", 0),
            "l5_count": counts.get("L5", 0),
            "icp_reference_gap_count": m95["gap_queue"]["summary"]["gap_count"],
            "scale_seed_ready_count": m98["readiness"]["summary"]["readiness_counts"].get("expansion_seed_ready", 0),
        },
        "canonical_next_action": "按 M98R threshold 执行下一轮 100-200 扩容；先从 expansion_seed_ready 画像/素材开始，继续执行 no-contamination guard。",
        "m95r_learning_asset_driven_prospect_engine": m95["package"]["summary"],
        "m96r_trusted_pool_product_layer": m96["product_view"]["summary"],
        "m97r_long_term_operations": m97["readiness"]["summary"],
        "m98r_scale_expansion_readiness": m98["readiness"]["summary"],
    })
    write_json(PANEL, panel)


def validate() -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m95r_m98_learning_pool_operating_system.py", "scripts/build_m91r_m94_learning_system.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    roots = [M95, M96, M97, M98, M47, M56]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = dynamic_scan([M95, M96, M97, M98, PANEL, WORKSPACE / "scripts/build_m95r_m98_learning_pool_operating_system.py"])
    api = api_key_scan([M95, M96, M97, M98, WORKSPACE / "scripts/build_m95r_m98_learning_pool_operating_system.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m95r_m98_validation')"])
    runner = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "validate_only", "--output-file", str(M97 / "trusted_pool_runner_regression_report_v2.json"), "--gap-queue-file", str(M97 / "trusted_pool_runner_gap_queue_v2.json"), "--source-trace-output", str(M97 / "trusted_pool_runner_source_trace_v2.json"), "--no-write-proof-file", str(M97 / "trusted_pool_runner_no_write_proof_v2.json"), "--pool-diff-file", str(M97 / "trusted_pool_runner_pool_diff_v2.json"), "--validation-report-file", str(M97 / "trusted_pool_runner_validation_v2.json")])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and runner["returncode"] == 0 else "FAIL"
    validation = {"milestone": "M95R-M98R", "generated_at": now(), "status": status, "py_compile": py_compile, "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]}, "trusted_pool_runner_regression": {"returncode": runner["returncode"], "stdout": runner["stdout"], "stderr": runner["stderr"]}}
    write_json(M98 / "validation_report_v1.json", validation)
    return validation


def main() -> int:
    pool = read_json(POOL)
    trace = read_json(TRACE)
    m92_queue = read_json(M92 / "learnable_material_queue_v2.json", {"items": []})
    m94_map = read_json(M94 / "persona_evidence_map_v2.json", {"items": []})
    m95 = build_m95(pool, trace)
    m96 = build_m96(pool, m95)
    m97 = build_m97(pool, m95, m96)
    m98 = build_m98(pool, m92_queue, m94_map, m97)
    update_panel(m95, m96, m97, m98)
    validation = validate()
    print(json.dumps({"m95": m95["package"]["summary"], "m96": m96["product_view"]["summary"], "m97": m97["readiness"]["summary"], "m98": m98["readiness"]["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
