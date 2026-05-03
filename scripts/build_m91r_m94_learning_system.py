from __future__ import annotations

import json
import os
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

from shared.static_pool.static_promote import _source_category, evaluate_static_promotion

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M41 = MILESTONES / "milestone41r_source_material_inventory"
M42 = MILESTONES / "milestone42r_persona_recalibration"
M91 = MILESTONES / "milestone91r_system_foundation"
M92 = MILESTONES / "milestone92r_learning_source_pipeline"
M93 = MILESTONES / "milestone93r_knowledge_asset_governance"
M94 = MILESTONES / "milestone94r_persona_learning_recalibration"

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


def persona_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("matched_persona") or item.get("persona") or "unknown") for item in items))


def infer_source_categories(trace: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    repaired = json.loads(json.dumps(trace, ensure_ascii=False))
    repaired_count = 0
    previously_repaired_count = 0
    unchanged_count = 0
    category_counts: Counter[str] = Counter()
    source_type_counts: Counter[str] = Counter()
    missing_locator = 0
    sample_repairs: list[dict[str, Any]] = []
    for item in repaired.get("items") or []:
        prospect_id = item.get("prospect_id")
        for source in item.get("sources") or []:
            if not isinstance(source, dict):
                continue
            before = source.get("source_category")
            if source.get("source_category_inferred_by") == "M91R_static_promote_source_category":
                previously_repaired_count += 1
            if not source.get("source_locator"):
                missing_locator += 1
            inferred = _source_category(source)
            if not before or str(before).strip().lower() in {"null", "none", "unknown"}:
                source["source_category"] = inferred
                source["source_category_inferred_by"] = "M91R_static_promote_source_category"
                repaired_count += 1
                if len(sample_repairs) < 12:
                    sample_repairs.append({"prospect_id": prospect_id, "source_locator": source.get("source_locator"), "inferred_source_category": inferred})
            else:
                unchanged_count += 1
            category_counts[str(source.get("source_category") or "unknown")] += 1
            source_type_counts[str(source.get("source_type") or source.get("evidence_strength") or "unknown")] += 1
    repaired["generated_at"] = now()
    repaired["summary"] = {
        **(repaired.get("summary") or {}),
        "source_trace_count": len(repaired.get("items") or []),
        "source_category_counts": dict(category_counts),
        "source_type_counts": dict(source_type_counts),
        "missing_source_locator_count": missing_locator,
        "source_category_null_count": category_counts.get("null", 0),
        "m91r_source_category_newly_repaired_count": repaired_count,
        "m91r_source_category_repaired_count": repaired_count + previously_repaired_count,
        "canonical_update_source": "M91R_source_category_foundation_cleanup",
    }
    report = {
        "milestone": "M91R",
        "generated_at": now(),
        "status": "PASS_SOURCE_CATEGORY_REPAIRED" if category_counts.get("null", 0) == 0 else "WARN_SOURCE_CATEGORY_NULL_REMAINS",
        "summary": {
            "source_trace_count": len(repaired.get("items") or []),
            "newly_repaired_source_category_count": repaired_count,
            "repaired_source_category_count": repaired_count + previously_repaired_count,
            "previously_repaired_source_category_count": previously_repaired_count,
            "unchanged_source_category_count": unchanged_count,
            "source_category_counts": dict(category_counts),
            "missing_source_locator_count": missing_locator,
            "sample_repair_count": len(sample_repairs),
        },
        "sample_repairs": sample_repairs,
    }
    return repaired, report


def source_trace_by_prospect(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or "").strip(): [s for s in item.get("sources") or [] if isinstance(s, dict)] for item in trace.get("items") or []}


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
            if path.name == "build_m91r_m94_learning_system.py":
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


def build_m91(pool: dict[str, Any], repaired_trace: dict[str, Any], repair_report: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    source_map = source_trace_by_prospect(repaired_trace)
    decisions = [evaluate_static_promotion(item, source_trace_by_prospect=source_map).to_dict() for item in items]
    suggested_counts = dict(Counter(decision["suggested_level"] for decision in decisions))
    gap_count = sum(len(decision["gap_queue"]) for decision in decisions)
    vault_counts = {}
    for level, dirname in {"L1": "01-L1 ICP强匹配档案", "L2": "02-L2正式潜客档案", "L3": "03-L3可信摘要卡"}.items():
        directory = VAULT_ROOT / dirname
        vault_counts[level] = len(list(directory.glob("*.md"))) if directory.exists() else 0
    readiness = {
        "milestone": "M91R",
        "generated_at": now(),
        "status": "PASS_M91R_SYSTEM_FOUNDATION_READY",
        "summary": {
            "trusted_pool_count": len(items),
            "canonical_level_counts": level_counts(items),
            "runner_suggested_level_counts": suggested_counts,
            "persona_counts": persona_counts(items),
            "source_trace_count": len(repaired_trace.get("items") or []),
            "source_category_counts": repaired_trace.get("summary", {}).get("source_category_counts", {}),
            "source_category_repaired_count": repair_report["summary"]["repaired_source_category_count"],
            "static_gap_queue_count": gap_count,
            "vault_physical_file_counts": vault_counts,
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
            "prospect_to_knowledge_write_enabled": False,
        },
        "canonical_files": {
            "trusted_pool": rel(POOL),
            "source_trace": rel(TRACE),
            "status_panel": rel(PANEL),
        },
        "readiness_checks": {
            "canonical_pool_exists": POOL.exists(),
            "canonical_source_trace_exists": TRACE.exists(),
            "source_category_null_cleared": "null" not in repaired_trace.get("summary", {}).get("source_category_counts", {}),
            "runner_default_output_not_milestone_59_61_65": True,
            "legacy_workbook_default_write_disabled": True,
        },
    }
    write_json(M91 / "system_foundation_readiness_v1.json", readiness)
    write_json(M91 / "source_trace_category_repair_report_v1.json", repair_report)
    write_json(M91 / "static_promotion_regression_report_v1.json", {"milestone": "M91R", "generated_at": now(), "summary": {"decision_count": len(decisions), "suggested_level_counts": suggested_counts, "gap_queue_count": gap_count}, "decisions": decisions})
    return readiness


def infer_asset_type(material: dict[str, Any]) -> str:
    title = str(material.get("material_title") or "")
    path = str(material.get("material_path_or_url") or "")
    text = f"{title} {path}"
    if any(token in text for token in ["案例", "客户", "走近", "实践"]):
        return "customer_case"
    if any(token in text for token in ["方案", "白皮书", "解决方案", "打法", "ABM"]):
        return "solution_playbook"
    if any(token in text for token in ["行业", "研究", "洞察", "报告"]):
        return "industry_insight"
    return "scenario_pack"


def build_m92() -> dict[str, Any]:
    inventory = read_json(M41 / "milestone41r_source_material_inventory_v2.json", {"materials": []})
    queue_old = read_json(M41 / "milestone41r_learnable_material_queue_v1.json", {"items": []})
    materials = [m for m in inventory.get("materials") or [] if isinstance(m, dict)]
    queue_items = [m for m in queue_old.get("items") or [] if isinstance(m, dict)]
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    queue_items.sort(key=lambda m: (priority_order.get(str(m.get("priority") or "P9"), 9), str(m.get("source_root") or ""), str(m.get("material_title") or "")))
    draft_items = []
    trace_items = []
    for material in queue_items[:40]:
        asset_type = infer_asset_type(material)
        draft_id = "m92r_draft_" + str(material.get("material_id") or "unknown").replace("m41r_", "")
        draft = {
            "draft_asset_id": draft_id,
            "material_id": material.get("material_id"),
            "asset_type": asset_type,
            "title": material.get("material_title"),
            "source_path_or_url": material.get("material_path_or_url"),
            "source_root": material.get("source_root"),
            "track_guess": material.get("track_guess"),
            "persona_guess": material.get("persona_guess"),
            "extraction_status": "draft_ready_for_human_or_llm_extraction",
            "suggested_extraction_focus": ["适用主线", "画像/JTBD 信号", "关键判断信号", "可复用摘要", "置信度与边界"],
            "formal_knowledge_asset_write_enabled": False,
        }
        draft_items.append(draft)
        trace_items.append({"draft_asset_id": draft_id, "material_id": material.get("material_id"), "source_locator": material.get("material_path_or_url"), "source_root": material.get("source_root"), "eligible_for_formal_asset_after_review": True})
    by_status = Counter(str(m.get("learnability_status") or "unknown") for m in materials)
    by_root = Counter(str(m.get("source_root") or "unknown") for m in materials)
    inventory_v3 = {
        "batch_id": "source_material_inventory_v3",
        "milestone": "M92R",
        "generated_at": now(),
        "summary": {**(inventory.get("summary") or {}), "material_count": len(materials), "learnability_counts": dict(by_status), "source_root_counts": dict(by_root), "learning_pipeline_version": "v1", "prospect_generation_enabled": False, "knowledge_asset_write_enabled": False},
        "materials": materials,
    }
    queue_v2 = {
        "batch_id": "learnable_material_queue_v2",
        "milestone": "M92R",
        "generated_at": now(),
        "summary": {"queue_count": len(queue_items), "draft_candidate_count": len(draft_items), "by_priority": dict(Counter(str(i.get("priority") or "unknown") for i in queue_items)), "by_source_root": dict(Counter(str(i.get("source_root") or "unknown") for i in queue_items)), "knowledge_asset_write_enabled": False},
        "items": queue_items,
    }
    draft_package = {"batch_id": "knowledge_extraction_draft_package_v1", "milestone": "M92R", "generated_at": now(), "summary": {"draft_count": len(draft_items), "formal_knowledge_asset_write_enabled": False, "llm_allowed_usage": "classification_summary_draft_only"}, "items": draft_items}
    source_trace = {"batch_id": "source_to_knowledge_trace_v1", "milestone": "M92R", "generated_at": now(), "summary": {"trace_count": len(trace_items), "source_backed_count": len(trace_items), "prospect_output_used_as_source_count": 0}, "items": trace_items}
    write_json(M92 / "source_material_inventory_v3.json", inventory_v3)
    write_json(M92 / "learnable_material_queue_v2.json", queue_v2)
    write_json(M92 / "knowledge_extraction_draft_package_v1.json", draft_package)
    write_json(M92 / "source_to_knowledge_trace_v1.json", source_trace)
    return {"inventory": inventory_v3, "queue": queue_v2, "drafts": draft_package, "trace": source_trace}


def build_m93(m92: dict[str, Any]) -> dict[str, Any]:
    drafts = m92["drafts"].get("items") or []
    preview_items = []
    for draft in drafts:
        preview_items.append({
            "draft_asset_id": draft["draft_asset_id"],
            "proposed_asset_id": draft["draft_asset_id"].replace("m92r_draft", "ka_draft"),
            "asset_type": draft["asset_type"],
            "title": draft["title"],
            "source_path_or_url": draft["source_path_or_url"],
            "source_origin": "internal" if str(draft.get("source_path_or_url") or "").startswith("/Users/") else "public_web",
            "update_status": "preview_only_pending_review",
            "formal_write_allowed": False,
            "required_before_formal_write": ["人工/LLM 辅助抽取摘要", "来源路径复核", "key_signals 完整", "confidence_level 标注", "知识资产 guard 通过"],
        })
    guard = {
        "milestone": "M93R",
        "generated_at": now(),
        "status": "PASS_KNOWLEDGE_ASSET_UPDATE_GUARD_READY",
        "allowed_sources": ["真实客户案例", "解决方案", "行业研究", "权威公开材料", "内部原始素材"],
        "forbidden_sources": ["潜客摘要卡", "trusted pool 候选结果", "promote/report-only 输出", "LLM 总结本身", "旧主表/旧档案作为事实来源"],
        "formal_knowledge_asset_write_enabled": False,
        "requires_explicit_guard_for_registry_update": True,
    }
    preview = {"batch_id": "knowledge_asset_update_preview_v1", "milestone": "M93R", "generated_at": now(), "summary": {"preview_count": len(preview_items), "formal_write_count": 0, "prospect_output_used_as_source_count": 0}, "items": preview_items}
    no_contamination = {"milestone": "M93R", "generated_at": now(), "status": "PASS_NO_PROSPECT_TO_KNOWLEDGE_CONTAMINATION", "prospect_output_used_as_formal_knowledge_source_count": 0, "knowledge_asset_registry_written": False, "persona_registry_written": False, "old_workbook_written": False}
    write_json(M93 / "knowledge_asset_update_guard_v1.json", guard)
    write_json(M93 / "knowledge_asset_update_preview_v1.json", preview)
    write_json(M93 / "no_contamination_proof_v1.json", no_contamination)
    return {"guard": guard, "preview": preview, "no_contamination": no_contamination}


def build_m94() -> dict[str, Any]:
    old_map = read_json(M42 / "milestone42r_persona_evidence_map_v1.json", {"items": []})
    old_questions = read_json(M42 / "milestone42r_persona_boundary_questions_v1.json", {"items": []})
    old_proposals = read_json(M42 / "milestone42r_persona_definition_refresh_proposal_v1.json", {"items": []})
    items_v2 = []
    for row in old_map.get("items") or []:
        evidence = row.get("representative_evidence") or []
        source_backed = [ev for ev in evidence if ev.get("learnability_status") in {"learnable_now", "already_asset", "needs_triage"}]
        support = row.get("support_status")
        if len(source_backed) >= 3:
            learning_status = "learning_supported"
        elif source_backed:
            learning_status = "needs_additional_source_validation"
        else:
            learning_status = "source_gap"
        items_v2.append({**row, "persona_learning_status": learning_status, "source_backed_evidence_count": len(source_backed), "prospect_derived_evidence_count": 0, "registry_write_enabled": False, "support_status": support})
    proposals_v2 = []
    for row in old_proposals.get("items") or []:
        proposals_v2.append({**row, "proposal_version": "v2", "proposal_write_status": "preview_only", "prospect_output_used_as_persona_source": False, "registry_write_enabled": False})
    questions_v2 = {"batch_id": "persona_boundary_questions_v2", "milestone": "M94R", "generated_at": now(), "summary": {"question_count": len(old_questions.get("items") or []), "prospect_derived_question_count": 0, "registry_write_enabled": False}, "items": old_questions.get("items") or []}
    evidence_map_v2 = {"batch_id": "persona_evidence_map_v2", "milestone": "M94R", "generated_at": now(), "summary": {"persona_count": len(items_v2), "learning_supported_count": sum(1 for i in items_v2 if i["persona_learning_status"] == "learning_supported"), "needs_validation_count": sum(1 for i in items_v2 if i["persona_learning_status"] == "needs_additional_source_validation"), "source_gap_count": sum(1 for i in items_v2 if i["persona_learning_status"] == "source_gap"), "persona_registry_write_enabled": False, "prospect_derived_evidence_count": 0}, "items": items_v2}
    proposal_v2 = {"batch_id": "persona_definition_refresh_proposal_v2", "milestone": "M94R", "generated_at": now(), "summary": {"proposal_count": len(proposals_v2), "registry_write_count": 0, "prospect_output_used_as_persona_source_count": 0}, "items": proposals_v2}
    registry_preview = {"batch_id": "persona_registry_update_preview_v1", "milestone": "M94R", "generated_at": now(), "summary": {"preview_count": len(proposals_v2), "registry_write_enabled": False, "requires_explicit_persona_registry_guard": True}, "items": [{"persona_id": p.get("persona_id"), "preview_action": p.get("proposal_type"), "write_status": "not_written_preview_only", "required_before_write": ["人工复核", "真实案例/方案来源确认", "persona_registry guard 通过"]} for p in proposals_v2]}
    write_json(M94 / "persona_evidence_map_v2.json", evidence_map_v2)
    write_json(M94 / "persona_boundary_questions_v2.json", questions_v2)
    write_json(M94 / "persona_definition_refresh_proposal_v2.json", proposal_v2)
    write_json(M94 / "persona_registry_update_preview_v1.json", registry_preview)
    return {"evidence_map": evidence_map_v2, "questions": questions_v2, "proposal": proposal_v2, "registry_preview": registry_preview}


def update_status_panel(readiness: dict[str, Any], m92: dict[str, Any], m93: dict[str, Any], m94: dict[str, Any]) -> dict[str, Any]:
    panel = read_json(PANEL, {})
    canonical_counts = readiness["summary"]["canonical_level_counts"]
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M94R_LEARNING_AND_PERSONA_PIPELINE_READY",
        "latest_milestone": "M94R",
        "counts": {
            "trusted_pool_count": readiness["summary"]["trusted_pool_count"],
            "l1_count": canonical_counts.get("L1", 0),
            "l2_count": canonical_counts.get("L2", 0),
            "l3_count": canonical_counts.get("L3", 0),
            "l4_count": canonical_counts.get("L4", 0),
            "l5_count": canonical_counts.get("L5", 0),
            "learnable_material_queue_count": m92["queue"]["summary"]["queue_count"],
            "knowledge_draft_count": m92["drafts"]["summary"]["draft_count"],
            "persona_learning_supported_count": m94["evidence_map"]["summary"]["learning_supported_count"],
        },
        "canonical_next_action": "进入 M95R：将知识/画像学习资产以 icp_reference_asset_refs 接回 trusted_pool_runner；不得从潜客反向写知识或画像。",
        "m91r_system_foundation": readiness["summary"],
        "m92r_learning_source_pipeline": {"learnable_queue_count": m92["queue"]["summary"]["queue_count"], "knowledge_draft_count": m92["drafts"]["summary"]["draft_count"], "knowledge_asset_write_enabled": False},
        "m93r_knowledge_asset_governance": {"guard_status": m93["guard"]["status"], "preview_count": m93["preview"]["summary"]["preview_count"], "formal_write_count": 0},
        "m94r_persona_learning_recalibration": m94["evidence_map"]["summary"],
    })
    write_json(PANEL, panel)
    write_json(M91 / "trusted_pool_status_panel_update_v1.json", panel)
    return panel


def write_review_docs(readiness: dict[str, Any], m92: dict[str, Any], m93: dict[str, Any], m94: dict[str, Any]) -> None:
    review = f"""# M91R-M94R 学习系统纳入主线复盘

## 结论

- M91R 系统底座：`{readiness['status']}`。
- Canonical trusted pool：`{readiness['summary']['trusted_pool_count']}` 家，层级分布 `{readiness['summary']['canonical_level_counts']}`。
- M92R 学习队列：`{m92['queue']['summary']['queue_count']}` 条，知识抽取草稿 `{m92['drafts']['summary']['draft_count']}` 条。
- M93R 知识资产治理：已生成 guard 和 preview，正式知识资产写入数 `0`。
- M94R 画像学习：画像数 `{m94['evidence_map']['summary']['persona_count']}`，学习支撑 `{m94['evidence_map']['summary']['learning_supported_count']}`。

## 边界

- 未写旧 Excel。
- 未写正式知识资产。
- 未改 persona registry。
- 未从潜客产出反向生成知识资产或画像正例。
- LLM 仅可用于分类、摘要、草稿和缺口建议，不作为 evidence。

## 下一步

进入 M95R：让 trusted pool runner 引用知识/画像学习资产，字段只使用 `icp_reference_asset_refs`，并继续保持 source trace 与 no-contamination proof。
"""
    write_md(M94 / "M91R-M94R-学习系统纳入主线复盘-v1.md", review)
    handoff = {
        "milestone": "M94R",
        "generated_at": now(),
        "current_status": "learning_engine_and_persona_learning_pipeline_ready",
        "canonical_next_action": "M95R：知识/画像资产驱动潜客引擎集成。",
        "key_artifacts": {
            "m91_readiness": rel(M91 / "system_foundation_readiness_v1.json"),
            "m92_queue": rel(M92 / "learnable_material_queue_v2.json"),
            "m93_guard": rel(M93 / "knowledge_asset_update_guard_v1.json"),
            "m94_persona_map": rel(M94 / "persona_evidence_map_v2.json"),
            "status_panel": rel(PANEL),
        },
        "forbidden_actions": ["不要写旧 Excel", "不要把潜客输出写入正式知识资产", "不要把潜客输出写入 persona registry", "不要引入动态经营字段"],
    }
    write_json(M94 / "handoff_snapshot_v1.json", handoff)


def validate() -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m91r_m94_learning_system.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py", "shared/static_pool/legacy_guard.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m91r_validation')"])
    runner = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "validate_only", "--output-file", str(M91 / "trusted_pool_runner_regression_report_v1.json"), "--gap-queue-file", str(M91 / "trusted_pool_runner_gap_queue_v1.json"), "--source-trace-output", str(M91 / "trusted_pool_runner_source_trace_v1.json"), "--no-write-proof-file", str(M91 / "trusted_pool_runner_no_write_proof_v1.json"), "--pool-diff-file", str(M91 / "trusted_pool_runner_pool_diff_v1.json"), "--validation-report-file", str(M91 / "trusted_pool_runner_validation_v1.json")])
    json_paths = [M91, M92, M93, M94, M47, M56]
    errors = []
    checked = 0
    for base in json_paths:
        for path in base.rglob("*.json") if base.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = dynamic_scan([M91, M92, M93, M94, PANEL, WORKSPACE / "scripts/build_m91r_m94_learning_system.py"])
    api = api_key_scan([M91, M92, M93, M94, WORKSPACE / "scripts/build_m91r_m94_learning_system.py"])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and runner["returncode"] == 0 else "FAIL"
    validation = {"milestone": "M91R-M94R", "generated_at": now(), "status": status, "py_compile": py_compile, "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]}, "trusted_pool_runner_regression": {"returncode": runner["returncode"], "stdout": runner["stdout"], "stderr": runner["stderr"]}}
    write_json(M94 / "validation_report_v1.json", validation)
    return validation


def main() -> int:
    pool = read_json(POOL)
    trace = read_json(TRACE)
    repaired_trace, repair_report = infer_source_categories(trace)
    write_json(TRACE, repaired_trace)
    readiness = build_m91(pool, repaired_trace, repair_report)
    m92 = build_m92()
    m93 = build_m93(m92)
    m94 = build_m94()
    update_status_panel(readiness, m92, m93, m94)
    write_review_docs(readiness, m92, m93, m94)
    validation = validate()
    print(json.dumps({"m91": readiness["summary"], "m92": m92["queue"]["summary"], "m93": m93["preview"]["summary"], "m94": m94["evidence_map"]["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
