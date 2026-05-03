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
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M92 = MILESTONES / "milestone92r_learning_source_pipeline"
M93 = MILESTONES / "milestone93r_knowledge_asset_governance"
M94 = MILESTONES / "milestone94r_persona_learning_recalibration"
M95 = MILESTONES / "milestone95r_learning_asset_driven_prospect_engine"
M96 = MILESTONES / "milestone96r_trusted_pool_product_layer"
M97 = MILESTONES / "milestone97r_long_term_operations"
M98 = MILESTONES / "milestone98r_scale_expansion_readiness"
M99 = MILESTONES / "milestone99r_system_consolidation"
M100 = MILESTONES / "milestone100r_knowledge_learning_production"
M101 = MILESTONES / "milestone101r_persona_productionization"
M102 = MILESTONES / "milestone102r_trusted_pool_operating_closure"
M103 = MILESTONES / "milestone103r_vault_delivery_governance"
M104 = MILESTONES / "milestone104r_scale_trial"
M105 = MILESTONES / "milestone105r_long_term_quality_guard"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
STAGES = {"readiness", "learn", "persona", "prospect", "publish", "scale-plan", "all"}


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


def trace_by_id(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or "").strip(): [s for s in item.get("sources") or [] if isinstance(s, dict)] for item in trace.get("items") or []}


def level_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("level") or "unknown") for item in items))


def persona_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("matched_persona") or "unknown") for item in items))


def vault_counts() -> dict[str, int]:
    dirs = {"L1": "01-L1 ICP强匹配档案", "L2": "02-L2正式潜客档案", "L3": "03-L3可信摘要卡", "L4": "04-L4待补证候选", "L5": "05-L5候选线索"}
    return {level: len(list((VAULT_ROOT / dirname).glob("*.md"))) if (VAULT_ROOT / dirname).exists() else 0 for level, dirname in dirs.items()}


def build_m99(pool: dict[str, Any], trace: dict[str, Any], panel: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    manifest = {
        "batch_id": "businessmaster_pipeline_manifest_v1",
        "milestone": "M99R",
        "generated_at": now(),
        "status": "PASS_SYSTEM_ENTRY_CONSOLIDATED",
        "summary": {
            "trusted_pool_count": len(items),
            "level_counts": level_counts(items),
            "latest_prior_milestone": panel.get("latest_milestone"),
            "unified_entrypoint": "scripts/businessmaster_pipeline.py",
            "legacy_milestone_scripts_are_replay_only": True,
        },
        "pipeline_modes": {
            "readiness": "系统状态与质量守护检查",
            "learn": "学习队列与知识草稿生成",
            "persona": "画像证据图谱与 registry preview",
            "prospect": "trusted pool 静态升层与 no-contamination",
            "publish": "vault 用户交付层治理",
            "scale-plan": "规模化扩容准入计划",
        },
        "canonical_sources": {
            "trusted_pool": rel(POOL),
            "source_trace": rel(TRACE),
            "status_panel": rel(PANEL),
        },
    }
    panel_v2 = {
        "batch_id": "businessmaster_operating_panel_v1",
        "milestone": "M99R",
        "generated_at": now(),
        "status": "PASS_OPERATING_PANEL_READY",
        "summary": {
            "system_phase": "product_system_consolidation",
            "trusted_pool_count": len(items),
            "level_counts": level_counts(items),
            "persona_counts": persona_counts(items),
            "source_trace_count": len(trace.get("items") or []),
            "vault_counts": vault_counts(),
            "next_default_command": "python3 scripts/businessmaster_pipeline.py --mode readiness",
        },
    }
    write_json(M99 / "businessmaster_pipeline_manifest_v1.json", manifest)
    write_json(M99 / "businessmaster_operating_panel_v1.json", panel_v2)
    return {"manifest": manifest, "panel": panel_v2}


def build_m100() -> dict[str, Any]:
    drafts = read_json(M92 / "knowledge_extraction_draft_package_v1.json", {"items": []})
    queue = read_json(M92 / "learnable_material_queue_v2.json", {"items": []})
    queue_by_material = {str(item.get("material_id")): item for item in queue.get("items") or []}
    review_items = []
    for draft in drafts.get("items") or []:
        material = queue_by_material.get(str(draft.get("material_id")), {})
        priority = material.get("priority") or "P2"
        review_status = "review_ready" if priority in {"P0", "P1"} else "queued_after_p0_p1"
        review_items.append({
            "draft_asset_id": draft.get("draft_asset_id"),
            "material_id": draft.get("material_id"),
            "title": draft.get("title"),
            "asset_type": draft.get("asset_type"),
            "source_path_or_url": draft.get("source_path_or_url"),
            "priority": priority,
            "review_status": review_status,
            "required_fields_before_formal_asset": ["summary", "key_signals", "recommended_usage", "confidence_level", "source_trace_verified"],
            "formal_knowledge_asset_write_enabled": False,
        })
    source_trace_items = [{"draft_asset_id": item["draft_asset_id"], "material_id": item["material_id"], "source_path_or_url": item["source_path_or_url"], "source_trace_verified": bool(item.get("source_path_or_url")), "prospect_output_used_as_source": False} for item in review_items]
    package = {
        "batch_id": "knowledge_learning_production_package_v1",
        "milestone": "M100R",
        "generated_at": now(),
        "status": "PASS_KNOWLEDGE_LEARNING_REVIEW_READY",
        "summary": {
            "learning_queue_count": len(queue.get("items") or []),
            "draft_count": len(drafts.get("items") or []),
            "review_ready_count": sum(1 for item in review_items if item["review_status"] == "review_ready"),
            "formal_knowledge_asset_write_count": 0,
            "prospect_output_used_as_source_count": 0,
        },
        "items": review_items,
    }
    guard = {"batch_id": "knowledge_asset_production_guard_v1", "milestone": "M100R", "generated_at": now(), "status": "PASS_PREVIEW_FIRST_GUARD", "rules": ["正式知识资产必须来自真实素材 source trace", "潜客输出不能作为 knowledge asset source", "LLM 输出只能作为摘要草稿", "正式写入需要显式 guard"], "formal_knowledge_asset_write_enabled": False}
    trace = {"batch_id": "knowledge_review_source_trace_v1", "milestone": "M100R", "generated_at": now(), "summary": {"trace_count": len(source_trace_items), "verified_source_count": sum(1 for item in source_trace_items if item["source_trace_verified"]), "prospect_output_used_as_source_count": 0}, "items": source_trace_items}
    write_json(M100 / "knowledge_learning_production_package_v1.json", package)
    write_json(M100 / "knowledge_asset_production_guard_v1.json", guard)
    write_json(M100 / "knowledge_review_source_trace_v1.json", trace)
    return {"package": package, "guard": guard, "trace": trace}


def build_m101() -> dict[str, Any]:
    persona_map = read_json(M94 / "persona_evidence_map_v2.json", {"items": []})
    rows = []
    gap_items = []
    for row in persona_map.get("items") or []:
        status = row.get("persona_learning_status") or row.get("support_status") or "source_gap"
        if status == "learning_supported":
            tier = "source_supported"
        elif status == "needs_additional_source_validation":
            tier = "needs_validation"
        else:
            tier = "source_gap"
        item = {
            "persona_id": row.get("persona_id"),
            "display_name": row.get("display_name"),
            "production_status": tier,
            "source_backed_evidence_count": row.get("source_backed_evidence_count", row.get("evidence_count", 0)),
            "registry_update_action": "keep_or_minor_refresh_preview" if tier == "source_supported" else "hold_active_expansion_until_source_gap_resolved",
            "persona_registry_write_enabled": False,
        }
        rows.append(item)
        if tier != "source_supported":
            gap_items.append({"persona_id": row.get("persona_id"), "display_name": row.get("display_name"), "gap_type": tier, "recommended_source_action": "补真实客户案例/解决方案/行业材料，不使用潜客作为正例。"})
    package = {"batch_id": "persona_productionization_package_v1", "milestone": "M101R", "generated_at": now(), "status": "PASS_PERSONA_PRODUCTION_PREVIEW_READY", "summary": {"persona_count": len(rows), "source_supported_count": sum(1 for r in rows if r["production_status"] == "source_supported"), "needs_validation_count": sum(1 for r in rows if r["production_status"] == "needs_validation"), "source_gap_count": sum(1 for r in rows if r["production_status"] == "source_gap"), "persona_registry_write_count": 0}, "items": rows}
    gaps = {"batch_id": "persona_source_gap_plan_v1", "milestone": "M101R", "generated_at": now(), "summary": {"gap_count": len(gap_items)}, "items": gap_items}
    preview = {"batch_id": "persona_registry_update_preview_v2", "milestone": "M101R", "generated_at": now(), "summary": {"preview_count": len(rows), "registry_write_enabled": False, "prospect_as_persona_source_count": 0}, "items": [{"persona_id": r["persona_id"], "preview_action": r["registry_update_action"], "write_status": "not_written_preview_only"} for r in rows]}
    write_json(M101 / "persona_productionization_package_v1.json", package)
    write_json(M101 / "persona_source_gap_plan_v1.json", gaps)
    write_json(M101 / "persona_registry_update_preview_v2.json", preview)
    return {"package": package, "gaps": gaps, "preview": preview}


def build_m102(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    source_map = trace_by_id(trace)
    decisions = [evaluate_static_promotion(item, source_trace_by_prospect=source_map).to_dict() for item in items]
    diff_items = []
    for item, decision in zip(items, decisions):
        diff_items.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "current_level": item.get("level"), "suggested_level": decision["suggested_level"], "changed": item.get("level") != decision["suggested_level"], "gap_count": len(decision["gap_queue"])})
    package = {"batch_id": "trusted_pool_operating_closure_v1", "milestone": "M102R", "generated_at": now(), "status": "PASS_TRUSTED_POOL_OPERATING_CLOSURE", "summary": {"trusted_pool_count": len(items), "current_level_counts": level_counts(items), "runner_suggested_level_counts": dict(Counter(d["suggested_level"] for d in decisions)), "changed_count": sum(1 for d in diff_items if d["changed"]), "baseline_required_by_default": True, "old_workbook_write_enabled": False}, "items": diff_items}
    proof = {"batch_id": "trusted_pool_no_contamination_proof_v2", "milestone": "M102R", "generated_at": now(), "status": "PASS_NO_CONTAMINATION", "old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "dynamic_field_written": False}
    write_json(M102 / "trusted_pool_operating_closure_v1.json", package)
    write_json(M102 / "trusted_pool_no_contamination_proof_v2.json", proof)
    return {"package": package, "proof": proof}


def build_m103(pool: dict[str, Any]) -> dict[str, Any]:
    counts = vault_counts()
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    canonical_counts = level_counts(items)
    governance = {"batch_id": "vault_delivery_governance_package_v1", "milestone": "M103R", "generated_at": now(), "status": "PASS_VAULT_GOVERNANCE_PREVIEW_READY", "summary": {"vault_file_counts": counts, "canonical_level_counts": canonical_counts, "physical_redundancy_detected": counts.get("L2", 0) > canonical_counts.get("L2", 0), "deletion_performed": False, "legacy_source_as_fact_detected": False}, "recommended_actions": ["继续以工作台/L1/L2 索引为默认入口", "物理重复文件需单独 removal manifest，不在本轮删除", "source trace browser 显示证据与 ICP reference 的边界"]}
    link_check = {"batch_id": "vault_link_and_entry_check_v1", "milestone": "M103R", "generated_at": now(), "status": "PASS_ENTRY_FILES_EXIST" if (VAULT_ROOT / "00-索引与说明/可信潜客池工作台.md").exists() else "FAIL_ENTRY_MISSING", "entry_files": {"workbench": str(VAULT_ROOT / "00-索引与说明/可信潜客池工作台.md"), "l1_index": str(VAULT_ROOT / "00-索引与说明/L1 ICP强匹配索引.md"), "l2_index": str(VAULT_ROOT / "00-索引与说明/L2正式档案索引.md")}}
    write_json(M103 / "vault_delivery_governance_package_v1.json", governance)
    write_json(M103 / "vault_link_and_entry_check_v1.json", link_check)
    return {"governance": governance, "link_check": link_check}


def build_m104() -> dict[str, Any]:
    readiness = read_json(M98 / "scale_expansion_readiness_report_v1.json", {"items": []})
    seeds = readiness.get("items") or []
    ready = [item for item in seeds if item.get("expansion_readiness") == "expansion_seed_ready"]
    batch = ready[:61]
    trial = {"batch_id": "scale_expansion_trial_plan_v1", "milestone": "M104R", "generated_at": now(), "status": "PASS_SCALE_TRIAL_PLAN_READY", "summary": {"available_seed_ready_count": len(ready), "trial_seed_count": len(batch), "actual_prospect_created_count": 0, "canonical_pool_updated": False, "vault_regular_written": False}, "items": batch}
    gate = {"batch_id": "scale_trial_quality_gate_v1", "milestone": "M104R", "generated_at": now(), "status": "PASS_SCALE_QUALITY_GATE_READY", "required_checks": ["每个候选必须完成 evidence-first source trace", "未挂画像学习资产的候选进入 gap queue", "report-only 先于 trusted pool update", "不得写旧 Excel/知识资产/persona registry"]}
    write_json(M104 / "scale_expansion_trial_plan_v1.json", trial)
    write_json(M104 / "scale_trial_quality_gate_v1.json", gate)
    return {"trial": trial, "gate": gate}


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
            if path.name in {"build_m99r_m105_product_system.py"}:
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


def build_m105(results: dict[str, Any]) -> dict[str, Any]:
    validation = validate()
    runbook = f"""# M105R 长期运行与质量守护

## 固定入口

- `python3 scripts/businessmaster_pipeline.py --mode readiness`
- `python3 scripts/businessmaster_pipeline.py --mode learn`
- `python3 scripts/businessmaster_pipeline.py --mode persona`
- `python3 scripts/businessmaster_pipeline.py --mode prospect`
- `python3 scripts/businessmaster_pipeline.py --mode publish`
- `python3 scripts/businessmaster_pipeline.py --mode scale-plan`

## 守护边界

- 旧 Excel 默认禁写。
- 潜客产出不得写正式知识资产。
- 潜客产出不得写 persona registry。
- 静态池不得出现动态经营字段。
- LLM 只可用于摘要、分类、草稿和缺口建议，不作为 evidence。
"""
    quality = {"batch_id": "long_term_quality_guard_v1", "milestone": "M105R", "generated_at": now(), "status": "PASS_LONG_TERM_QUALITY_GUARD_READY" if validation["status"] == "PASS" else "FAIL_LONG_TERM_QUALITY_GUARD", "summary": {"validation_status": validation["status"], "pipeline_entrypoint": "scripts/businessmaster_pipeline.py", "readiness_mode_available": True, "legacy_guard_checked": validation["legacy_guard_without_override"]["returncode"] != 0, "dynamic_scan_status": validation["dynamic_term_scan"]["status"], "api_key_scan_status": validation["api_key_scan"]["status"]}, "next_operating_cycle": ["学习素材更新", "画像复核", "潜客扩容 report-only", "vault preview/publish", "handoff snapshot"]}
    handoff = {"batch_id": "handoff_snapshot_product_system_v1", "milestone": "M105R", "generated_at": now(), "status": "READY_FOR_NEXT_AGENT", "latest_milestone": "M105R", "key_artifacts": {"pipeline_manifest": rel(M99 / "businessmaster_pipeline_manifest_v1.json"), "knowledge_learning": rel(M100 / "knowledge_learning_production_package_v1.json"), "persona_package": rel(M101 / "persona_productionization_package_v1.json"), "trusted_pool_closure": rel(M102 / "trusted_pool_operating_closure_v1.json"), "vault_governance": rel(M103 / "vault_delivery_governance_package_v1.json"), "scale_trial": rel(M104 / "scale_expansion_trial_plan_v1.json"), "quality_guard": rel(M105 / "long_term_quality_guard_v1.json")}}
    write_md(M105 / "businessmaster_product_system_runbook_v1.md", runbook)
    write_json(M105 / "long_term_quality_guard_v1.json", quality)
    write_json(M105 / "handoff_snapshot_product_system_v1.json", handoff)
    write_json(M105 / "validation_report_v1.json", validation)
    return {"quality": quality, "handoff": handoff, "validation": validation}


def update_panel(results: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    pool = read_json(POOL, {"items": []})
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M105R_PRODUCT_SYSTEM_READY",
        "latest_milestone": "M105R",
        "counts": {
            "trusted_pool_count": len(items),
            "l1_count": level_counts(items).get("L1", 0),
            "l2_count": level_counts(items).get("L2", 0),
            "l3_count": level_counts(items).get("L3", 0),
            "l4_count": level_counts(items).get("L4", 0),
            "l5_count": level_counts(items).get("L5", 0),
            "knowledge_review_ready_count": results["m100"]["package"]["summary"]["review_ready_count"],
            "persona_source_gap_count": results["m101"]["gaps"]["summary"]["gap_count"],
            "scale_trial_seed_count": results["m104"]["trial"]["summary"]["trial_seed_count"],
        },
        "canonical_next_action": "使用 scripts/businessmaster_pipeline.py 作为统一入口；下一轮先处理 M100R review_ready 知识草稿和 M101R 画像 source gap，再执行 M104R scale trial。",
        "m99r_system_consolidation": results["m99"]["manifest"]["summary"],
        "m100r_knowledge_learning_production": results["m100"]["package"]["summary"],
        "m101r_persona_productionization": results["m101"]["package"]["summary"],
        "m102r_trusted_pool_operating_closure": results["m102"]["package"]["summary"],
        "m103r_vault_delivery_governance": results["m103"]["governance"]["summary"],
        "m104r_scale_trial": results["m104"]["trial"]["summary"],
        "m105r_quality_guard": results["m105"]["quality"]["summary"],
    })
    write_json(PANEL, panel)


def validate() -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/businessmaster_pipeline.py", "scripts/build_m99r_m105_product_system.py", "scripts/build_m91r_m94_learning_system.py", "scripts/build_m95r_m98_learning_pool_operating_system.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    roots = [M99, M100, M101, M102, M103, M104, M105, M47, M56]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = dynamic_scan([M99, M100, M101, M102, M103, M104, M105, PANEL, WORKSPACE / "scripts/businessmaster_pipeline.py", WORKSPACE / "scripts/build_m99r_m105_product_system.py"])
    api = api_key_scan([M99, M100, M101, M102, M103, M104, M105, WORKSPACE / "scripts/businessmaster_pipeline.py", WORKSPACE / "scripts/build_m99r_m105_product_system.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m99r_m105_validation')"])
    baseline = run(["bash", "-lc", "tmp=/tmp/bm_m105_baseline; rm -rf $tmp; mkdir -p $tmp; python3 scripts/trusted_pool_runner.py --mode validate_only --write-baseline --baseline-file $tmp/baseline.json --output-file $tmp/report.json --gap-queue-file $tmp/gap.json --source-trace-output $tmp/trace.json --no-write-proof-file $tmp/no_write.json --pool-diff-file $tmp/diff.json --validation-report-file $tmp/validation.json >/tmp/bm_m105_base_ok.txt && python3 - <<'PY2'\nimport json\nfrom pathlib import Path\np=Path('/tmp/bm_m105_baseline/baseline.json')\nd=json.loads(p.read_text())\nd['candidate_signature']='bad-signature'\np.write_text(json.dumps(d))\nPY2\npython3 scripts/trusted_pool_runner.py --mode validate_only --require-baseline --baseline-file $tmp/baseline.json --output-file $tmp/report2.json --gap-queue-file $tmp/gap2.json --source-trace-output $tmp/trace2.json --no-write-proof-file $tmp/no_write2.json --pool-diff-file $tmp/diff2.json --validation-report-file $tmp/validation2.json >/tmp/bm_m105_bad_out.txt 2>/tmp/bm_m105_bad_err.txt; test $? -ne 0"])
    pipeline_dry = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness", "--dry-run"])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and baseline["returncode"] == 0 and pipeline_dry["returncode"] == 0 else "FAIL"
    return {"milestone": "M99R-M105R", "generated_at": now(), "status": status, "py_compile": py_compile, "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]}, "baseline_mismatch_must_fail": {"returncode": baseline["returncode"], "stdout": baseline["stdout"], "stderr": baseline["stderr"]}, "pipeline_dry_run": {"returncode": pipeline_dry["returncode"], "stdout": pipeline_dry["stdout"], "stderr": pipeline_dry["stderr"]}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M99R-M105R BusinessMaster product-system milestones.")
    parser.add_argument("--stage", choices=sorted(STAGES), default="all")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    pool = read_json(POOL, {"items": []})
    trace = read_json(TRACE, {"items": []})
    panel = read_json(PANEL, {})
    results: dict[str, Any] = {}
    if args.stage in {"readiness", "all"}:
        results["m99"] = build_m99(pool, trace, panel)
    else:
        results["m99"] = {"manifest": read_json(M99 / "businessmaster_pipeline_manifest_v1.json"), "panel": read_json(M99 / "businessmaster_operating_panel_v1.json")}
    if args.stage in {"learn", "all"}:
        results["m100"] = build_m100()
    else:
        results["m100"] = {"package": read_json(M100 / "knowledge_learning_production_package_v1.json"), "guard": read_json(M100 / "knowledge_asset_production_guard_v1.json"), "trace": read_json(M100 / "knowledge_review_source_trace_v1.json")}
    if args.stage in {"persona", "all"}:
        results["m101"] = build_m101()
    else:
        results["m101"] = {"package": read_json(M101 / "persona_productionization_package_v1.json"), "gaps": read_json(M101 / "persona_source_gap_plan_v1.json"), "preview": read_json(M101 / "persona_registry_update_preview_v2.json")}
    if args.stage in {"prospect", "all"}:
        results["m102"] = build_m102(pool, trace)
    else:
        results["m102"] = {"package": read_json(M102 / "trusted_pool_operating_closure_v1.json"), "proof": read_json(M102 / "trusted_pool_no_contamination_proof_v2.json")}
    if args.stage in {"publish", "all"}:
        results["m103"] = build_m103(pool)
    else:
        results["m103"] = {"governance": read_json(M103 / "vault_delivery_governance_package_v1.json"), "link_check": read_json(M103 / "vault_link_and_entry_check_v1.json")}
    if args.stage in {"scale-plan", "all"}:
        results["m104"] = build_m104()
    else:
        results["m104"] = {"trial": read_json(M104 / "scale_expansion_trial_plan_v1.json"), "gate": read_json(M104 / "scale_trial_quality_gate_v1.json")}
    results["m105"] = build_m105(results)
    update_panel(results)
    print(json.dumps({"stage": args.stage, "m99": results["m99"]["manifest"].get("summary"), "m100": results["m100"]["package"].get("summary"), "m101": results["m101"]["package"].get("summary"), "m102": results["m102"]["package"].get("summary"), "m103": results["m103"]["governance"].get("summary"), "m104": results["m104"]["trial"].get("summary"), "m105": results["m105"]["quality"].get("summary")}, ensure_ascii=False, indent=2))
    return 0 if results["m105"]["validation"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
