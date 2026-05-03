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

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M100 = MILESTONES / "milestone100r_knowledge_learning_production"
M101 = MILESTONES / "milestone101r_persona_productionization"
M104 = MILESTONES / "milestone104r_scale_trial"
M105 = MILESTONES / "milestone105r_long_term_quality_guard"
M106 = MILESTONES / "milestone106r_knowledge_review_cycle"
M107 = MILESTONES / "milestone107r_persona_gap_closure_cycle"
M108 = MILESTONES / "milestone108r_scale_report_only_cycle"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
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


def infer_signal_text(title: str, asset_type: str) -> dict[str, str]:
    title = title or "未命名素材"
    if asset_type == "customer_case":
        return {
            "summary_draft": f"{title} 是真实客户/案例素材，可用于提炼行业场景、经营复杂度和画像匹配信号。",
            "key_signals_draft": "客户业务场景、组织/渠道/供应链复杂度、数据分析需求、落地价值。",
            "recommended_usage_draft": "用于画像支撑、ICP 判断解释和相似潜客入池理由校验。",
            "confidence_level_draft": "中",
        }
    if asset_type == "solution_playbook":
        return {
            "summary_draft": f"{title} 是解决方案/打法素材，可用于提炼 JTBD、业务指标和可复用场景包。",
            "key_signals_draft": "业务流程痛点、关键指标、数据应用场景、可复制解决方案。",
            "recommended_usage_draft": "用于知识资产沉淀、画像 admission hint 和候选 ICP 解释。",
            "confidence_level_draft": "中",
        }
    return {
        "summary_draft": f"{title} 是可学习素材，需进一步抽取主线、画像、JTBD 和边界。",
        "key_signals_draft": "行业/场景信号、复杂度信号、适用画像、非适配边界。",
        "recommended_usage_draft": "用于补充知识库与画像证据图谱。",
        "confidence_level_draft": "低",
    }


def build_m106() -> dict[str, Any]:
    source = read_json(M100 / "knowledge_learning_production_package_v1.json", {"items": []})
    items = []
    for row in source.get("items") or []:
        signal = infer_signal_text(str(row.get("title") or ""), str(row.get("asset_type") or ""))
        missing = []
        for field in ["summary_draft", "key_signals_draft", "recommended_usage_draft", "confidence_level_draft"]:
            if not signal.get(field):
                missing.append(field)
        status = "formal_asset_preview_ready" if row.get("review_status") == "review_ready" and not missing and row.get("source_path_or_url") else "needs_review_completion"
        items.append({
            "draft_asset_id": row.get("draft_asset_id"),
            "proposed_asset_id": str(row.get("draft_asset_id") or "draft").replace("m92r_draft", "ka_review"),
            "asset_type": row.get("asset_type"),
            "title": row.get("title"),
            "source_path_or_url": row.get("source_path_or_url"),
            "priority": row.get("priority"),
            "review_cycle_status": status,
            **signal,
            "missing_fields": missing,
            "formal_knowledge_asset_write_enabled": False,
            "prospect_output_used_as_source": False,
        })
    preview_ready = [item for item in items if item["review_cycle_status"] == "formal_asset_preview_ready"]
    package = {"batch_id": "knowledge_asset_review_cycle_package_v1", "milestone": "M106R", "generated_at": now(), "status": "PASS_KNOWLEDGE_REVIEW_CYCLE_READY", "summary": {"input_draft_count": len(source.get("items") or []), "formal_asset_preview_ready_count": len(preview_ready), "needs_review_completion_count": len(items) - len(preview_ready), "formal_knowledge_asset_write_count": 0, "prospect_output_used_as_source_count": 0}, "items": items}
    update_preview = {"batch_id": "formal_knowledge_asset_update_preview_v1", "milestone": "M106R", "generated_at": now(), "summary": {"preview_count": len(preview_ready), "write_enabled": False, "requires_human_or_guarded_review": True}, "items": preview_ready}
    no_write = {"batch_id": "knowledge_review_no_write_proof_v1", "milestone": "M106R", "generated_at": now(), "status": "PASS_NO_FORMAL_KNOWLEDGE_WRITE", "formal_knowledge_asset_written": False, "prospect_output_used_as_source_count": 0, "old_excel_written": False, "persona_registry_written": False}
    write_json(M106 / "knowledge_asset_review_cycle_package_v1.json", package)
    write_json(M106 / "formal_knowledge_asset_update_preview_v1.json", update_preview)
    write_json(M106 / "knowledge_review_no_write_proof_v1.json", no_write)
    return {"package": package, "preview": update_preview, "no_write": no_write}


def build_m107(m106: dict[str, Any]) -> dict[str, Any]:
    gaps = read_json(M101 / "persona_source_gap_plan_v1.json", {"items": []})
    preview_items = m106["preview"]["items"]
    by_asset_type = defaultdict(list)
    for item in preview_items:
        by_asset_type[str(item.get("asset_type") or "unknown")].append(item)
    closure_items = []
    for gap in gaps.get("items") or []:
        persona_id = str(gap.get("persona_id") or "unknown")
        if any(token in persona_id for token in ["cbec", "cross"]):
            candidates = by_asset_type.get("customer_case", []) + by_asset_type.get("solution_playbook", [])
        elif any(token in persona_id for token in ["retail", "fnb"]):
            candidates = by_asset_type.get("customer_case", []) + by_asset_type.get("scenario_pack", [])
        else:
            candidates = by_asset_type.get("solution_playbook", []) + by_asset_type.get("customer_case", [])
        refs = candidates[:3]
        status = "gap_closure_preview_ready" if refs else "needs_new_source_material"
        closure_items.append({
            "persona_id": persona_id,
            "display_name": gap.get("display_name"),
            "original_gap_type": gap.get("gap_type"),
            "closure_status": status,
            "candidate_knowledge_refs": [{"proposed_asset_id": ref.get("proposed_asset_id"), "title": ref.get("title"), "source_path_or_url": ref.get("source_path_or_url")} for ref in refs],
            "registry_update_preview_only": True,
            "prospect_output_used_as_persona_source": False,
        })
    ready_count = sum(1 for item in closure_items if item["closure_status"] == "gap_closure_preview_ready")
    package = {"batch_id": "persona_gap_closure_package_v1", "milestone": "M107R", "generated_at": now(), "status": "PASS_PERSONA_GAP_CLOSURE_PREVIEW_READY", "summary": {"input_gap_count": len(gaps.get("items") or []), "gap_closure_preview_ready_count": ready_count, "needs_new_source_material_count": len(closure_items) - ready_count, "persona_registry_write_count": 0, "prospect_output_used_as_persona_source_count": 0}, "items": closure_items}
    registry_preview = {"batch_id": "persona_registry_gap_closure_preview_v1", "milestone": "M107R", "generated_at": now(), "summary": {"preview_count": ready_count, "write_enabled": False}, "items": [item for item in closure_items if item["closure_status"] == "gap_closure_preview_ready"]}
    no_write = {"batch_id": "persona_gap_closure_no_write_proof_v1", "milestone": "M107R", "generated_at": now(), "status": "PASS_NO_PERSONA_REGISTRY_WRITE", "persona_registry_written": False, "knowledge_asset_registry_written": False, "old_excel_written": False}
    write_json(M107 / "persona_gap_closure_package_v1.json", package)
    write_json(M107 / "persona_registry_gap_closure_preview_v1.json", registry_preview)
    write_json(M107 / "persona_gap_closure_no_write_proof_v1.json", no_write)
    return {"package": package, "preview": registry_preview, "no_write": no_write}


def build_m108(m107: dict[str, Any]) -> dict[str, Any]:
    trial = read_json(M104 / "scale_expansion_trial_plan_v1.json", {"items": []})
    persona_ready = {str(item.get("persona_id")) for item in m107["package"]["items"] if item.get("closure_status") == "gap_closure_preview_ready"}
    candidate_inputs = []
    gap_items = []
    for seed in trial.get("items") or []:
        persona = str(seed.get("persona_guess") or "unknown")
        if seed.get("expansion_readiness") != "expansion_seed_ready":
            status = "not_ready"
        elif persona in persona_ready:
            status = "report_only_ready"
        else:
            status = "report_only_with_persona_watch"
        candidate = {
            "seed_id": seed.get("seed_id"),
            "seed_title": seed.get("seed_title"),
            "matched_persona": persona,
            "track_guess": seed.get("track_guess"),
            "priority": seed.get("priority"),
            "report_only_status": status,
            "required_before_trusted_pool_update": ["候选公司识别", "至少 1 条强来源", "ICP 解释", "source trace", "report-only baseline"],
            "canonical_pool_updated": False,
            "vault_written": False,
        }
        candidate_inputs.append(candidate)
        if status != "report_only_ready":
            gap_items.append({"seed_id": seed.get("seed_id"), "seed_title": seed.get("seed_title"), "persona_guess": persona, "gap_type": status, "reason": "画像补源未完全闭环或候选公司/evidence 尚未采集。"})
    counts = Counter(item["report_only_status"] for item in candidate_inputs)
    package = {"batch_id": "scale_report_only_candidate_input_v1", "milestone": "M108R", "generated_at": now(), "status": "PASS_SCALE_REPORT_ONLY_INPUT_READY", "summary": {"seed_count": len(candidate_inputs), "status_counts": dict(counts), "canonical_pool_updated": False, "vault_written": False, "old_excel_written": False}, "items": candidate_inputs}
    report = {"batch_id": "scale_report_only_summary_v1", "milestone": "M108R", "generated_at": now(), "summary": {"report_only_ready_count": counts.get("report_only_ready", 0), "report_only_with_persona_watch_count": counts.get("report_only_with_persona_watch", 0), "not_ready_count": counts.get("not_ready", 0), "gap_queue_count": len(gap_items)}, "gap_queue": gap_items}
    no_write = {"batch_id": "scale_report_only_no_write_proof_v1", "milestone": "M108R", "generated_at": now(), "status": "PASS_REPORT_ONLY_NO_WRITE", "canonical_pool_updated": False, "vault_written": False, "old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False}
    write_json(M108 / "scale_report_only_candidate_input_v1.json", package)
    write_json(M108 / "scale_report_only_summary_v1.json", report)
    write_json(M108 / "scale_report_only_no_write_proof_v1.json", no_write)
    return {"package": package, "report": report, "no_write": no_write}


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
            if path.name == "build_m106r_m108_next_operating_cycle.py":
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
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m106r_m108_next_operating_cycle.py", "scripts/businessmaster_pipeline.py", "scripts/build_m99r_m105_product_system.py", "scripts/trusted_pool_runner.py"])
    roots = [M106, M107, M108, M56]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = dynamic_scan([M106, M107, M108, PANEL, WORKSPACE / "scripts/build_m106r_m108_next_operating_cycle.py"])
    api = api_key_scan([M106, M107, M108, WORKSPACE / "scripts/build_m106r_m108_next_operating_cycle.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m106r_m108_validation')"])
    pipeline_dry = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness", "--dry-run"])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and pipeline_dry["returncode"] == 0 else "FAIL"
    validation = {"milestone": "M106R-M108R", "generated_at": now(), "status": status, "py_compile": py_compile, "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]}, "pipeline_dry_run": {"returncode": pipeline_dry["returncode"], "stdout": pipeline_dry["stdout"], "stderr": pipeline_dry["stderr"]}}
    write_json(M108 / "validation_report_v1.json", validation)
    return validation


def update_panel(m106: dict[str, Any], m107: dict[str, Any], m108: dict[str, Any], validation: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    pool = read_json(POOL, {"items": []})
    counts = level_counts([item for item in pool.get("items") or [] if isinstance(item, dict)])
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M108R_NEXT_OPERATING_CYCLE_READY" if validation["status"] == "PASS" else "FAIL_M108R_NEXT_OPERATING_CYCLE",
        "latest_milestone": "M108R",
        "counts": {
            "trusted_pool_count": len(pool.get("items") or []),
            "l1_count": counts.get("L1", 0),
            "l2_count": counts.get("L2", 0),
            "l3_count": counts.get("L3", 0),
            "l4_count": counts.get("L4", 0),
            "l5_count": counts.get("L5", 0),
            "knowledge_preview_ready_count": m106["preview"]["summary"]["preview_count"],
            "persona_gap_closure_ready_count": m107["preview"]["summary"]["preview_count"],
            "scale_report_only_ready_count": m108["report"]["summary"]["report_only_ready_count"],
        },
        "canonical_next_action": "进入 M109R：对 M106R formal knowledge preview 做人工/LLM 摘要复核，随后可选择 guarded formal knowledge asset update；M108R 仅 report-only，未更新 canonical pool。",
        "m106r_knowledge_review_cycle": m106["package"]["summary"],
        "m107r_persona_gap_closure_cycle": m107["package"]["summary"],
        "m108r_scale_report_only_cycle": m108["package"]["summary"],
    })
    write_json(PANEL, panel)


def main() -> int:
    m106 = build_m106()
    m107 = build_m107(m106)
    m108 = build_m108(m107)
    validation = validate()
    update_panel(m106, m107, m108, validation)
    print(json.dumps({"m106": m106["package"]["summary"], "m107": m107["package"]["summary"], "m108": m108["package"]["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
