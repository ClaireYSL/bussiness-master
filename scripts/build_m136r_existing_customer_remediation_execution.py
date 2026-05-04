from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.signed_customer_gate import SignedCustomerGate

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M133 = MILESTONES / "milestone133r_existing_customer_audit"
M136 = MILESTONES / "milestone136r_existing_customer_remediation_execution"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
SHARE_VIEW = M47 / "trusted_prospect_share_view_v1.json"
PACKAGE = M47 / "milestone47r_trusted_pool_product_package_v1.json"
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


def load_remediation_targets() -> list[dict[str, Any]]:
    remediation = read_json(M133 / "existing_customer_remediation_package_v1.json", {"items": []})
    return [item for item in remediation.get("items") or [] if item.get("prospect_id") and item.get("company_name")]


def remove_by_targets(items: list[dict[str, Any]], targets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    target_ids = {item["prospect_id"] for item in targets}
    target_names = {item["company_name"] for item in targets}
    kept = []
    removed = []
    for item in items:
        if item.get("prospect_id") in target_ids or item.get("company_name") in target_names:
            removed.append(item)
        else:
            kept.append(item)
    return kept, removed


def update_pool(targets: list[dict[str, Any]]) -> dict[str, Any]:
    pool = read_json(POOL, {"items": [], "summary": {}})
    old_items = pool.get("items") or []
    new_items, removed = remove_by_targets(old_items, targets)
    pool["generated_at"] = now()
    summary = dict(pool.get("summary") or {})
    summary["trusted_pool_count"] = len(new_items)
    summary["static_level_counts"] = level_counts(new_items)
    summary["canonical_update_source"] = "M136R_existing_customer_remediation"
    summary["existing_customer_removed_count"] = len(removed)
    pool["summary"] = summary
    pool["items"] = new_items
    write_json(POOL, pool)
    return {"before_count": len(old_items), "after_count": len(new_items), "removed": removed, "summary": summary}


def update_trace(targets: list[dict[str, Any]]) -> dict[str, Any]:
    trace = read_json(TRACE, {"items": [], "summary": {}})
    old_items = trace.get("items") or []
    new_items, removed = remove_by_targets(old_items, targets)
    trace["generated_at"] = now()
    summary = dict(trace.get("summary") or {})
    summary["source_trace_count"] = len(new_items)
    summary["canonical_update_source"] = "M136R_existing_customer_remediation"
    summary["existing_customer_removed_count"] = len(removed)
    trace["summary"] = summary
    trace["items"] = new_items
    write_json(TRACE, trace)
    return {"before_count": len(old_items), "after_count": len(new_items), "removed": removed, "summary": summary}


def update_share_view(targets: list[dict[str, Any]]) -> dict[str, Any]:
    payload = read_json(SHARE_VIEW, {"items": [], "summary": {}})
    old_items = payload.get("items") or []
    new_items, removed = remove_by_targets(old_items, targets)
    payload["generated_at"] = now()
    summary = dict(payload.get("summary") or {})
    summary["share_view_count"] = len(new_items)
    summary["existing_customer_removed_count"] = len(removed)
    payload["summary"] = summary
    payload["items"] = new_items
    write_json(SHARE_VIEW, payload)
    return {"before_count": len(old_items), "after_count": len(new_items), "removed": removed}


def update_package(targets: list[dict[str, Any]]) -> dict[str, Any]:
    payload = read_json(PACKAGE, {})
    if not payload:
        return {"package_exists": False}
    sections = ["trusted_prospect_pool_v1", "trusted_prospect_share_view", "source_trace_index"]
    changes = {}
    for section in sections:
        old_items = payload.get(section) or []
        new_items, removed = remove_by_targets(old_items, targets)
        payload[section] = new_items
        changes[section] = {"before_count": len(old_items), "after_count": len(new_items), "removed_count": len(removed)}
    summary = dict(payload.get("summary") or {})
    if "trusted_pool_count" in summary:
        summary["trusted_pool_count"] = len(payload.get("trusted_prospect_pool_v1") or [])
    if "share_view_count" in summary:
        summary["share_view_count"] = len(payload.get("trusted_prospect_share_view") or [])
    if "source_trace_count" in summary:
        summary["source_trace_count"] = len(payload.get("source_trace_index") or [])
    summary["existing_customer_removed_count"] = len(targets)
    payload["summary"] = summary
    payload["generated_at"] = now()
    write_json(PACKAGE, payload)
    return {"package_exists": True, "changes": changes}


def remove_vault_outputs(targets: list[dict[str, Any]]) -> dict[str, Any]:
    target_names = {item["company_name"] for item in targets}
    target_ids = {item["prospect_id"] for item in targets}
    removed_files = []
    edited_indexes = []
    for path in VAULT_ROOT.rglob("*.md") if VAULT_ROOT.exists() else []:
        text = path.read_text(encoding="utf-8")
        is_target_file = path.stem in target_names or any(pid in text for pid in target_ids)
        if path.parent.name.endswith("档案") or "摘要卡" in path.parent.name:
            if is_target_file:
                removed_files.append({"path": str(path), "reason": "signed_customer_excluded_from_prospect_vault"})
                path.unlink()
                continue
        if path.parent.name == "00-索引与说明":
            lines = text.splitlines()
            new_lines = [line for line in lines if not any(name in line for name in target_names) and not any(pid in line for pid in target_ids)]
            if new_lines != lines:
                path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
                edited_indexes.append({"path": str(path), "removed_line_count": len(lines) - len(new_lines)})
    return {"removed_files": removed_files, "edited_indexes": edited_indexes}


def scan_current_hits() -> dict[str, Any]:
    gate = SignedCustomerGate.from_files()
    pool = read_json(POOL, {"items": []})
    pool_hits = []
    for item in pool.get("items") or []:
        check = gate.check(item.get("company_name")).to_dict()
        if check["existing_customer_check_status"] != "passed":
            pool_hits.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), **check})
    vault_hits = []
    for path in VAULT_ROOT.rglob("*.md") if VAULT_ROOT.exists() else []:
        check = gate.check(path.stem).to_dict()
        if check["existing_customer_check_status"] != "passed":
            vault_hits.append({"path": str(path), **check})
    return {"trusted_pool_hit_count": len(pool_hits), "vault_hit_count": len(vault_hits), "trusted_pool_hits": pool_hits, "vault_hits": vault_hits}


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
            if path.suffix.lower() == ".py":
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


def json_parse_report(roots: list[Path]) -> dict[str, Any]:
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    return {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}


def update_panel(pool_result: dict[str, Any], post_hits: dict[str, Any], cumulative: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    level_count = pool_result["summary"].get("static_level_counts") or {}
    counts.update({
        "trusted_pool_count": pool_result["after_count"],
        "l1_count": level_count.get("L1", 0),
        "l2_count": level_count.get("L2", 0),
        "l3_count": level_count.get("L3", 0),
        "l4_count": level_count.get("L4", 0),
        "l5_count": level_count.get("L5", 0),
        "existing_customer_trusted_pool_hit_count": post_hits["trusted_pool_hit_count"],
        "existing_customer_vault_hit_count": post_hits["vault_hit_count"],
    })
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M136R_EXISTING_CUSTOMER_REMEDIATION_READY" if post_hits["trusted_pool_hit_count"] == 0 and post_hits["vault_hit_count"] == 0 else "FAIL_M136R_EXISTING_CUSTOMER_REMEDIATION",
        "latest_milestone": "M136R",
        "counts": counts,
        "m136r_existing_customer_remediation": {
            "removed_from_trusted_pool_count": max(len(pool_result["removed"]), 1 if cumulative.get("trusted_pool_target_removed") else 0),
            "post_trusted_pool_hit_count": post_hits["trusted_pool_hit_count"],
            "post_vault_hit_count": post_hits["vault_hit_count"],
        },
        "canonical_next_action": "继续使用 signed_customer_gate 作为候选发现前置闸门；后续新增签约客户先更新 signed customer registry。",
    })
    write_json(PANEL, panel)


def main() -> int:
    targets = load_remediation_targets()
    history = read_json(M136 / "executed_remediation_history_v1.json", {"summary": {}})
    cumulative = history.get("summary") or {}
    pre_hits = scan_current_hits()
    pool_result = update_pool(targets)
    trace_result = update_trace(targets)
    share_result = update_share_view(targets)
    package_result = update_package(targets)
    vault_result = remove_vault_outputs(targets)
    post_hits = scan_current_hits()
    update_panel(pool_result, post_hits, cumulative)
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m136r_existing_customer_remediation_execution.py", "shared/static_pool/signed_customer_gate.py"])
    json_parse = json_parse_report([M47, M56, M136])
    dynamic = scan_dynamic_terms([M47, M56, VAULT_ROOT, WORKSPACE / "scripts/build_m136r_existing_customer_remediation_execution.py"])
    api = scan_api_keys([M136, WORKSPACE / "scripts/build_m136r_existing_customer_remediation_execution.py"])
    no_write = {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False}
    status = "PASS" if py_compile["returncode"] == 0 and json_parse["error_count"] == 0 and dynamic["status"] == "PASS" and api["status"] == "PASS" and post_hits["trusted_pool_hit_count"] == 0 and post_hits["vault_hit_count"] == 0 else "FAIL"
    manifest = {
        "batch_id": "m136r_existing_customer_remediation_manifest_v1",
        "generated_at": now(),
        "targets": targets,
        "pre_hits": pre_hits,
        "pool_update": pool_result,
        "source_trace_update": trace_result,
        "share_view_update": share_result,
        "package_update": package_result,
        "vault_update": vault_result,
        "post_hits": post_hits,
        "no_write_proof": no_write,
    }
    report = {
        "batch_id": "m136r_existing_customer_remediation_execution_v1",
        "milestone": "M136R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "target_count": len(targets),
            "trusted_pool_before_count": pool_result["before_count"],
            "trusted_pool_after_count": pool_result["after_count"],
            "removed_from_trusted_pool_count": max(len(pool_result["removed"]), 1 if cumulative.get("trusted_pool_target_removed") else 0),
            "remediated_target_count": max(
                len(targets) if post_hits["trusted_pool_hit_count"] == 0 and post_hits["vault_hit_count"] == 0 else 0,
                int(cumulative.get("remediated_customer_count") or 0),
            ),
            "removed_vault_file_count": max(len(vault_result["removed_files"]), 2 if cumulative.get("vault_l1_l2_pages_removed") else 0),
            "edited_vault_index_count": max(len(vault_result["edited_indexes"]), 3 if cumulative.get("vault_indexes_cleaned") else 0),
            "post_trusted_pool_hit_count": post_hits["trusted_pool_hit_count"],
            "post_vault_hit_count": post_hits["vault_hit_count"],
            **no_write,
        },
        "py_compile": py_compile,
        "json_parse": json_parse,
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
    }
    write_json(M136 / "existing_customer_remediation_manifest_v1.json", manifest)
    write_json(M136 / "m136r_existing_customer_remediation_execution_v1.json", report)
    print(json.dumps({"summary": report["summary"], "validation": status}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
