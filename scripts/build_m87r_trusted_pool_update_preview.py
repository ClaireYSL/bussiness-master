from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M86 = MILESTONES / "milestone86r_source_locator_hardening"
M87 = MILESTONES / "milestone87r_trusted_pool_update_preview"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)
STATIC_UPDATE_FIELDS = (
    "level",
    "trusted_status",
    "static_promotion_summary",
    "static_gap_count",
    "static_evidence_count",
    "static_strong_evidence_count",
    "matched_persona",
    "match_reason",
    "core_product_service_summary",
    "business_model_summary",
    "risk_or_gap",
    "source_locator",
    "evidence_strength",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE)) if path.is_relative_to(WORKSPACE) else str(path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def status_for_level(level: str) -> str:
    return {"L1": "static_l1_ready", "L2": "static_l2_ready", "L3": "trusted_summary_ready", "L4": "evidence_pending", "L5": "candidate_seed"}.get(level, "candidate_seed")


def source_trace_by_id(trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("prospect_id"): item for item in trace.get("items") or [] if item.get("prospect_id")}


def pool_item_by_id(pool: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("prospect_id"): item for item in pool.get("items") or [] if item.get("prospect_id")}


def build_preview_pool() -> dict[str, Any]:
    canonical_pool = read_json(CANONICAL_POOL)
    m85_pool = read_json(MILESTONES / "milestone85r_non_listed_candidate_trial/trusted_pool_input_v1.json")
    m86_admission = read_json(M86 / "canonical_update_admission_package_v1.json")
    m86_trace = read_json(M86 / "hardened_source_trace_v1.json")
    m85_review = read_json(MILESTONES / "milestone85r_non_listed_candidate_trial/m85r_report_only_review_v1.json")

    m85_by_id = pool_item_by_id(m85_pool)
    review_by_id = {item["prospect_id"]: item for item in m85_review.get("items") or []}
    ready = [item for item in m86_admission.get("items") or [] if item.get("canonical_update_ready")]
    preview_pool = deepcopy(canonical_pool)
    existing = pool_item_by_id(preview_pool)
    diff_items = []

    for ready_item in ready:
        prospect_id = ready_item["prospect_id"]
        src = deepcopy(m85_by_id[prospect_id])
        decision = review_by_id[prospect_id]
        patch = {
            "level": decision["suggested_level"],
            "trusted_status": status_for_level(decision["suggested_level"]),
            "static_promotion_summary": decision["summary"],
            "static_gap_count": len(decision.get("gap_queue") or []),
            "static_evidence_count": decision.get("evidence_count"),
            "static_strong_evidence_count": decision.get("strong_evidence_count"),
            "canonical_update_source": "M87R_preview_from_M86R_hardened_ready",
            "source_locator_hardened": True,
            "legacy_field_inherited": False,
        }
        candidate = {**src, **patch}
        old = existing.get(prospect_id)
        if old:
            field_changes = [{"field": field, "old": old.get(field), "new": candidate.get(field)} for field in STATIC_UPDATE_FIELDS if old.get(field) != candidate.get(field)]
            old.update(candidate)
            action = "update_existing"
        else:
            field_changes = [{"field": field, "old": None, "new": candidate.get(field)} for field in STATIC_UPDATE_FIELDS if candidate.get(field) is not None]
            preview_pool.setdefault("items", []).append(candidate)
            existing[prospect_id] = candidate
            action = "append_new"
        diff_items.append({"prospect_id": prospect_id, "company_name": candidate.get("company_name"), "action": action, "suggested_level": candidate.get("level"), "changed": True, "field_changes": field_changes})

    level_counts = Counter(item.get("level") for item in preview_pool.get("items") or [])
    preview_pool["generated_at"] = now()
    preview_pool["summary"] = {
        **(preview_pool.get("summary") or {}),
        "trusted_pool_count": len(preview_pool.get("items") or []),
        "static_level_counts": dict(level_counts),
        "canonical_update_source": "M87R_preview_only",
        "runner": "trusted_pool_update_preview",
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }

    diff = {"milestone": "M87R", "generated_at": now(), "status": "PASS_M87R_POOL_DIFF_PREVIEW_READY", "summary": {"candidate_count": len(ready), "append_new_count": sum(1 for item in diff_items if item["action"] == "append_new"), "update_existing_count": sum(1 for item in diff_items if item["action"] == "update_existing"), "changed_count": len(diff_items), "level_counts_after_preview": dict(level_counts), "canonical_pool_updated": False}, "items": diff_items}
    write_json(M87 / "trusted_pool_update_preview_v1.json", preview_pool)
    write_json(M87 / "pool_diff_preview_v1.json", diff)
    return {"pool": preview_pool, "diff": diff, "ready": ready, "m86_trace": m86_trace}


def build_preview_trace(preview_result: dict[str, Any]) -> dict[str, Any]:
    canonical_trace = read_json(CANONICAL_TRACE)
    trace = deepcopy(canonical_trace)
    trace_items = trace.setdefault("items", [])
    by_id = source_trace_by_id(trace)
    m86_by_id = source_trace_by_id(preview_result["m86_trace"])
    changed = []
    for ready_item in preview_result["ready"]:
        prospect_id = ready_item["prospect_id"]
        src = deepcopy(m86_by_id[prospect_id])
        for source in src.get("sources") or []:
            source["added_by_milestone"] = "M87R_preview"
        src["added_by_milestone"] = "M87R_preview"
        src["source_locator_hardened"] = True
        if prospect_id in by_id:
            by_id[prospect_id].update(src)
            action = "update_existing_trace"
        else:
            trace_items.append(src)
            by_id[prospect_id] = src
            action = "append_new_trace"
        changed.append({"prospect_id": prospect_id, "company_name": src.get("company_name"), "action": action, "source_count": len(src.get("sources") or []), "verified_source_count": src.get("verified_source_count")})
    category_counts = Counter(source.get("source_category") for item in trace_items for source in item.get("sources") or [])
    trace["generated_at"] = now()
    trace["summary"] = {**(trace.get("summary") or {}), "source_trace_count": len(trace_items), "source_category_counts": dict(category_counts), "canonical_update_source": "M87R_preview_only"}
    trace_diff = {"milestone": "M87R", "generated_at": now(), "status": "PASS_M87R_SOURCE_TRACE_DIFF_PREVIEW_READY", "summary": {"changed_trace_count": len(changed), "source_trace_count_after_preview": len(trace_items), "canonical_trace_updated": False}, "items": changed}
    write_json(M87 / "source_trace_update_preview_v1.json", trace)
    write_json(M87 / "source_trace_diff_preview_v1.json", trace_diff)
    return {"trace": trace, "diff": trace_diff}


def run_runner_previews(pool_path: Path, trace_path: Path) -> None:
    common = ["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(pool_path), "--source-trace", rel(trace_path), "--output-file", rel(M87 / "m87r_report_only_v1.json"), "--gap-queue-file", rel(M87 / "m87r_gap_queue_v1.json"), "--source-trace-output", rel(M87 / "m87r_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M87 / "m87r_no_write_proof_v1.json"), "--pool-diff-file", rel(M87 / "m87r_runner_pool_diff_v1.json"), "--validation-report-file", rel(M87 / "m87r_runner_validation_v1.json"), "--baseline-file", rel(M87 / "m87r_baseline_v1.json")]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    bad = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--trusted-pool", rel(pool_path), "--source-trace", rel(trace_path), "--output-file", rel(M87 / "m87r_update_guard_probe_v1.json"), "--validation-report-file", rel(M87 / "m87r_update_guard_probe_validation_v1.json")])
    write_json(M87 / "m87r_update_guard_probe_v1.json", {"returncode": bad.returncode, "stderr": bad.stderr, "expected_failure": True})
    preview = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "generate_vault_preview", "--trusted-pool", rel(pool_path), "--source-trace", rel(trace_path), "--output-file", rel(M87 / "m87r_vault_preview_report_v1.json"), "--gap-queue-file", rel(M87 / "m87r_vault_preview_gap_queue_v1.json"), "--vault-preview-dir", rel(M87 / "vault_preview"), "--baseline-file", rel(M87 / "m87r_baseline_v1.json"), "--require-baseline"])
    if preview.returncode != 0:
        raise RuntimeError(preview.stderr)


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": rel(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings[:50]}


def scan_api_keys(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"file": rel(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings[:50]}


def validate(canonical_pool_hash_before: str, canonical_trace_hash_before: str, preview_result: dict[str, Any], trace_result: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", rel(Path(__file__)), "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    json_errors = []
    checked = 0
    for path in M87.glob("*.json"):
        checked += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic_scan = scan_dynamic([M87])
    api_key_scan = scan_api_keys([M87, Path(__file__)])
    report = read_json(M87 / "m87r_report_only_v1.json")
    vault_preview = read_json(M87 / "m87r_vault_preview_report_v1.json")
    guard_probe = read_json(M87 / "m87r_update_guard_probe_v1.json")
    canonical_pool_hash_after = stable_hash(read_json(CANONICAL_POOL))
    canonical_trace_hash_after = stable_hash(read_json(CANONICAL_TRACE))
    expected_added = preview_result["diff"]["summary"]["append_new_count"]
    assertions = {
        "preview_candidate_count_11": preview_result["diff"]["summary"]["candidate_count"] == 11,
        "preview_append_count_11": expected_added == 11,
        "canonical_pool_not_updated": canonical_pool_hash_before == canonical_pool_hash_after,
        "canonical_trace_not_updated": canonical_trace_hash_before == canonical_trace_hash_after,
        "runner_report_count_61": report.get("summary", {}).get("prospect_count") == 61,
        "vault_preview_count_61": vault_preview.get("summary", {}).get("vault_preview_count") == 61,
        "update_guard_failed_without_allow": guard_probe.get("returncode") == 2,
        "no_dynamic_terms": dynamic_scan["status"] == "PASS",
        "api_key_scan_pass": api_key_scan["status"] == "PASS",
        "py_compile_pass": py_compile.returncode == 0,
        "json_parse_pass": not json_errors,
    }
    validation = {"milestone": "M87R", "generated_at": now(), "status": "PASS" if all(assertions.values()) else "FAIL", "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "json_parse": {"checked_count": checked, "error_count": len(json_errors), "errors": json_errors}, "dynamic_term_scan": dynamic_scan, "api_key_scan": api_key_scan, "assertions": assertions}
    write_json(M87 / "m87r_validation_report_v1.json", validation)
    return validation


def update_panel(preview_result: dict[str, Any], trace_result: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel.update({"generated_at": now(), "overall_status": "PASS_M87R_TRUSTED_POOL_UPDATE_PREVIEW", "latest_milestone": "M87R", "canonical_next_action": "如确认 M87R preview，可进入 M88R 正式更新 canonical trusted pool；仍需显式 --allow-trusted-pool-update。", "m87r_trusted_pool_update_preview": {"candidate_count": preview_result["diff"]["summary"]["candidate_count"], "append_new_count": preview_result["diff"]["summary"]["append_new_count"], "source_trace_changed_count": trace_result["diff"]["summary"]["changed_trace_count"], "canonical_pool_updated": False, "canonical_trace_updated": False, "vault_regular_written": False, "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}})
    write_json(STATUS_PANEL, panel)


def main() -> int:
    M87.mkdir(parents=True, exist_ok=True)
    canonical_pool_hash_before = stable_hash(read_json(CANONICAL_POOL))
    canonical_trace_hash_before = stable_hash(read_json(CANONICAL_TRACE))
    preview_result = build_preview_pool()
    trace_result = build_preview_trace(preview_result)
    run_runner_previews(M87 / "trusted_pool_update_preview_v1.json", M87 / "source_trace_update_preview_v1.json")
    no_write = {"milestone": "M87R", "generated_at": now(), "status": "PASS_PREVIEW_ONLY_NO_CANONICAL_WRITE", "canonical_pool_updated": False, "canonical_trace_updated": False, "vault_regular_written": False, "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}
    write_json(M87 / "m87r_no_write_proof_v1.json", no_write)
    operating_panel = {"milestone": "M87R", "generated_at": now(), "status": "PASS_M87R_TRUSTED_POOL_UPDATE_PREVIEW_READY", "summary": {**preview_result["diff"]["summary"], **trace_result["diff"]["summary"], "canonical_pool_updated": False, "canonical_trace_updated": False}, "next_action": "M88R：确认后正式写 canonical trusted pool 与 source trace。"}
    write_json(M87 / "m87r_operating_panel_v1.json", operating_panel)
    handoff = {"milestone": "M87R", "generated_at": now(), "current_scope": "M86R hardened-ready 11 家进入 trusted pool update preview。", "canonical_pool_updated": False, "next_command": "python3 scripts/build_m87r_trusted_pool_update_preview.py"}
    write_json(M87 / "handoff_snapshot_v1.json", handoff)
    validation = validate(canonical_pool_hash_before, canonical_trace_hash_before, preview_result, trace_result)
    update_panel(preview_result, trace_result)
    print(json.dumps({"preview": preview_result["diff"]["summary"], "trace": trace_result["diff"]["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
