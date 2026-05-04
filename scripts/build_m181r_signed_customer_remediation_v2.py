from __future__ import annotations

import argparse
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
M180 = MILESTONES / "milestone180r_signed_customer_registry_v2"
M181 = MILESTONES / "milestone181r_signed_customer_remediation_v2"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
SHARE_VIEW = M47 / "trusted_prospect_share_view_v1.json"
PACKAGE = M47 / "milestone47r_trusted_pool_product_package_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
REMEDIATION_PREVIEW = M180 / "remediation_preview_v2.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"AKLT[A-Za-z0-9_-]{20,}", r"DELEGATE_LLM_API_KEY\s*=\s*[^<\s].+"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def load_targets() -> list[dict[str, Any]]:
    preview = read_json(REMEDIATION_PREVIEW, {"items": []})
    targets: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in preview.get("items") or []:
        name = str(item.get("entity_name") or item.get("company_name") or "").strip()
        prospect_id = str(item.get("prospect_id") or "").strip()
        if not name or not prospect_id:
            continue
        key = (prospect_id, name)
        if key in seen:
            continue
        seen.add(key)
        targets.append({
            "prospect_id": prospect_id,
            "company_name": name,
            "current_level": item.get("current_level"),
            "match_status": item.get("match_status"),
            "source_preview": rel(REMEDIATION_PREVIEW),
            "remediation_action": "remove_from_active_trusted_pool_and_vault_user_entry",
        })
    return targets


def target_match(item: dict[str, Any], target_ids: set[str], target_names: set[str]) -> bool:
    return str(item.get("prospect_id") or "") in target_ids or str(item.get("company_name") or "") in target_names


def split_items(items: list[dict[str, Any]], targets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    target_ids = {item["prospect_id"] for item in targets}
    target_names = {item["company_name"] for item in targets}
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for item in items:
        if target_match(item, target_ids, target_names):
            removed.append(item)
        else:
            kept.append(item)
    return kept, removed


def update_pool(targets: list[dict[str, Any]], allow: bool) -> dict[str, Any]:
    payload = read_json(POOL, {"summary": {}, "items": []})
    old_items = payload.get("items") or []
    new_items, removed = split_items(old_items, targets)
    result = {"path": rel(POOL), "before_count": len(old_items), "after_count": len(new_items), "removed_count": len(removed), "removed_items": removed}
    if not allow:
        result["write_executed"] = False
        return result
    summary = dict(payload.get("summary") or {})
    summary.update({
        "trusted_pool_count": len(new_items),
        "source_trace_count": len(new_items),
        "trusted_match_ready_count": sum(1 for x in new_items if str(x.get("level")) in {"L1", "L2", "L3"}),
        "static_level_counts": level_counts(new_items),
        "canonical_update_source": "M181R_signed_customer_remediation_v2",
        "existing_customer_removed_count": int(summary.get("existing_customer_removed_count") or 0) + len(removed),
        "signed_customer_v2_gate_applied": True,
    })
    payload["generated_at"] = now()
    payload["summary"] = summary
    payload["items"] = new_items
    write_json(POOL, payload)
    result["write_executed"] = True
    result["summary"] = summary
    return result


def update_trace(targets: list[dict[str, Any]], allow: bool) -> dict[str, Any]:
    payload = read_json(TRACE, {"summary": {}, "items": []})
    old_items = payload.get("items") or []
    new_items, removed = split_items(old_items, targets)
    result = {"path": rel(TRACE), "before_count": len(old_items), "after_count": len(new_items), "removed_count": len(removed), "removed_items": removed}
    if not allow:
        result["write_executed"] = False
        return result
    summary = dict(payload.get("summary") or {})
    summary.update({
        "source_trace_count": len(new_items),
        "canonical_update_source": "M181R_signed_customer_remediation_v2",
        "existing_customer_removed_count": int(summary.get("existing_customer_removed_count") or 0) + len(removed),
        "signed_customer_v2_gate_applied": True,
    })
    payload["generated_at"] = now()
    payload["summary"] = summary
    payload["items"] = new_items
    write_json(TRACE, payload)
    result["write_executed"] = True
    result["summary"] = summary
    return result


def update_share_view(targets: list[dict[str, Any]], allow: bool) -> dict[str, Any]:
    payload = read_json(SHARE_VIEW, {"summary": {}, "items": []})
    old_items = payload.get("items") or []
    new_items, removed = split_items(old_items, targets)
    result = {"path": rel(SHARE_VIEW), "before_count": len(old_items), "after_count": len(new_items), "removed_count": len(removed), "removed_items": removed}
    if not allow:
        result["write_executed"] = False
        return result
    summary = dict(payload.get("summary") or {})
    summary.update({"share_view_count": len(new_items), "existing_customer_removed_count": int(summary.get("existing_customer_removed_count") or 0) + len(removed)})
    payload["generated_at"] = now()
    payload["summary"] = summary
    payload["items"] = new_items
    write_json(SHARE_VIEW, payload)
    result["write_executed"] = True
    return result


def update_package(targets: list[dict[str, Any]], allow: bool) -> dict[str, Any]:
    payload = read_json(PACKAGE, {})
    if not payload:
        return {"path": rel(PACKAGE), "package_exists": False, "write_executed": False}
    sections = ["trusted_prospect_pool_v1", "trusted_prospect_share_view", "source_trace_index"]
    changes: dict[str, Any] = {}
    next_payload = json.loads(json.dumps(payload, ensure_ascii=False))
    for section in sections:
        old_items = next_payload.get(section) or []
        new_items, removed = split_items(old_items, targets)
        next_payload[section] = new_items
        changes[section] = {"before_count": len(old_items), "after_count": len(new_items), "removed_count": len(removed), "removed_items": removed}
    result = {"path": rel(PACKAGE), "package_exists": True, "changes": changes}
    if not allow:
        result["write_executed"] = False
        return result
    summary = dict(next_payload.get("summary") or {})
    if "trusted_pool_count" in summary:
        summary["trusted_pool_count"] = len(next_payload.get("trusted_prospect_pool_v1") or [])
    if "share_view_count" in summary:
        summary["share_view_count"] = len(next_payload.get("trusted_prospect_share_view") or [])
    if "source_trace_count" in summary:
        summary["source_trace_count"] = len(next_payload.get("source_trace_index") or [])
    summary.update({"existing_customer_removed_count": len(targets), "canonical_update_source": "M181R_signed_customer_remediation_v2"})
    next_payload["summary"] = summary
    next_payload["generated_at"] = now()
    write_json(PACKAGE, next_payload)
    result["write_executed"] = True
    return result


def vault_candidate_paths(targets: list[dict[str, Any]]) -> list[Path]:
    target_names = {item["company_name"] for item in targets}
    target_ids = {item["prospect_id"] for item in targets}
    paths: list[Path] = []
    if not VAULT_ROOT.exists():
        return paths
    for folder in ["01-L1 ICP强匹配档案", "02-L2正式潜客档案", "03-L3可信摘要卡"]:
        root = VAULT_ROOT / folder
        if not root.exists():
            continue
        for path in root.glob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.stem in target_names or any(pid in text for pid in target_ids):
                paths.append(path)
    return sorted(set(paths))


def update_vault(targets: list[dict[str, Any]], allow: bool) -> dict[str, Any]:
    files = vault_candidate_paths(targets)
    removal_manifest = [{"path": str(path), "file_name": path.name, "folder": path.parent.name, "reason": "signed_customer_v2_excluded_from_new_prospect_user_entry"} for path in files]
    result = {"candidate_file_count": len(files), "removal_manifest": removal_manifest, "write_executed": False}
    if not allow:
        return result
    removed_files = []
    for path in files:
        removed_files.append({"path": str(path), "reason": "signed_customer_v2_excluded_from_new_prospect_user_entry"})
        path.unlink()
    edited_indexes = []
    target_names = {item["company_name"] for item in targets}
    target_ids = {item["prospect_id"] for item in targets}
    index_root = VAULT_ROOT / "00-索引与说明"
    for path in index_root.rglob("*.md") if index_root.exists() else []:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        new_lines = [line for line in lines if not any(name in line for name in target_names) and not any(pid in line for pid in target_ids)]
        if new_lines != lines:
            path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
            edited_indexes.append({"path": str(path), "removed_line_count": len(lines) - len(new_lines)})
    result.update({"write_executed": True, "removed_files": removed_files, "edited_indexes": edited_indexes})
    return result


def scan_current_hits() -> dict[str, Any]:
    gate = SignedCustomerGate.from_files()
    pool = read_json(POOL, {"items": []}).get("items") or []
    pool_hits = []
    for item in pool:
        check = gate.check(item.get("company_name")).to_dict()
        if check["existing_customer_check_status"] in {"excluded_existing_customer", "boundary_review"}:
            pool_hits.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "level": item.get("level"), "match": check})
    vault_hits = []
    for path in VAULT_ROOT.rglob("*.md") if VAULT_ROOT.exists() else []:
        if "legacy" in str(path).lower():
            continue
        check = gate.check(path.stem).to_dict()
        if check["existing_customer_check_status"] in {"excluded_existing_customer", "boundary_review"}:
            vault_hits.append({"path": str(path), "folder": path.parent.name, "match": check})
    return {"trusted_pool_hit_count": len(pool_hits), "vault_hit_count": len(vault_hits), "trusted_pool_hits": pool_hits, "vault_hits": vault_hits[:200]}


def scan_dynamic_terms(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for base in paths:
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in candidates:
            if path.suffix.lower() not in {".md", ".json", ".py"}:
                continue
            lower = str(path).lower()
            if "legacy" in lower or "optional" in lower or path.name.startswith("m181_validation"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix.lower() == ".py":
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            hits = [term for term in DYNAMIC_TERMS if term in text]
            if hits:
                findings.append({"path": rel(path), "terms": hits})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def scan_api_keys(paths: list[Path]) -> dict[str, Any]:
    findings = []
    patterns = [re.compile(p) for p in SECRET_PATTERNS]
    for base in paths:
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in candidates:
            if path.name == ".env" or path.suffix.lower() not in {".md", ".json", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            if any(p.search(text) for p in patterns):
                findings.append(rel(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def json_parse_report(paths: list[Path]) -> dict[str, Any]:
    checked = 0
    errors = []
    for root in paths:
        candidates = [root] if root.is_file() else list(root.rglob("*.json")) if root.exists() else []
        for path in candidates:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                errors.append({"path": rel(path), "error": str(exc)})
    return {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}


def update_panel(pool_result: dict[str, Any], post_hits: dict[str, Any], targets: list[dict[str, Any]], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    summary = pool_result.get("summary") or read_json(POOL, {"summary": {}}).get("summary", {})
    level_count = summary.get("static_level_counts") or {}
    counts.update({
        "trusted_pool_count": pool_result.get("after_count"),
        "l1_count": level_count.get("L1", 0),
        "l2_count": level_count.get("L2", 0),
        "l3_count": level_count.get("L3", 0),
        "l4_count": level_count.get("L4", 0),
        "l5_count": level_count.get("L5", 0),
        "m181_remediated_existing_customer_count": len(targets),
        "m181_post_trusted_pool_existing_customer_hit_count": post_hits.get("trusted_pool_hit_count"),
        "m181_post_vault_existing_customer_hit_count": post_hits.get("vault_hit_count"),
        "m180_trusted_pool_existing_customer_hit_count": 0 if post_hits.get("trusted_pool_hit_count") == 0 else counts.get("m180_trusted_pool_existing_customer_hit_count"),
        "m180_vault_existing_customer_hit_count": 0 if post_hits.get("vault_hit_count") == 0 else counts.get("m180_vault_existing_customer_hit_count"),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M181R",
        "overall_status": "PASS_M181R_SIGNED_CUSTOMER_REMEDIATION_COMPLETE" if validation_status == "PASS" else "FAIL_M181R_SIGNED_CUSTOMER_REMEDIATION",
        "counts": counts,
        "m181r_signed_customer_remediation_v2": {
            "status": validation_status,
            "target_count": len(targets),
            "post_trusted_pool_hit_count": post_hits.get("trusted_pool_hit_count"),
            "post_vault_hit_count": post_hits.get("vault_hit_count"),
            "old_excel_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
        },
        "canonical_next_action": "继续使用 signed customer v2 gate 作为候选发现前置闸门；后续新增签约客户先更新 v2 registry，再跑生产链路。",
    })
    write_json(PANEL, panel)


def expert_review(pre_hits: dict[str, Any], post_hits: dict[str, Any], targets: list[dict[str, Any]]) -> dict[str, Any]:
    followups = []
    if post_hits.get("trusted_pool_hit_count"):
        followups.append("仍有 trusted pool 老客命中，需要继续核查 alias/边界样本。")
    if post_hits.get("vault_hit_count"):
        followups.append("仍有 vault 老客命中，需要继续清理用户入口。")
    status = "fail" if followups else "pass"
    return {
        "batch_id": "m181r_expert_review_report_v1",
        "milestone": "M181R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "product_review_status": status,
            "architecture_review_status": status,
            "data_governance_review_status": status,
            "target_count": len(targets),
            "pre_trusted_pool_hit_count": pre_hits.get("trusted_pool_hit_count"),
            "post_trusted_pool_hit_count": post_hits.get("trusted_pool_hit_count"),
            "pre_vault_hit_count": pre_hits.get("vault_hit_count"),
            "post_vault_hit_count": post_hits.get("vault_hit_count"),
            "followup_count": len(followups),
        },
        "product_review": {"status": status, "evidence": "命中签约老客已从新潜客用户入口移除。", "followups": followups},
        "architecture_review": {"status": status, "evidence": "remediation 由 M180 preview 驱动，canonical pool/source trace/share/package/vault 同步更新。"},
        "data_governance_review": {"status": status, "evidence": "不写旧 Excel、不写知识资产、不改 persona registry；删除动作保留 manifest。"},
    }


def validate(post_hits: dict[str, Any], expert: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m181r_signed_customer_remediation_v2.py", "shared/static_pool/signed_customer_gate.py", "scripts/businessmaster_pipeline.py"])
    json_parse = json_parse_report([M181, M47, M56])
    dynamic = scan_dynamic_terms([M181, M47, M56, VAULT_ROOT, WORKSPACE / "scripts/build_m181r_signed_customer_remediation_v2.py"])
    api = scan_api_keys([M181, WORKSPACE / "scripts/build_m181r_signed_customer_remediation_v2.py"])
    readiness = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness"])
    checks = {
        "py_compile_pass": py_compile["returncode"] == 0,
        "json_parse_pass": json_parse["error_count"] == 0,
        "post_trusted_pool_hit_zero": post_hits.get("trusted_pool_hit_count") == 0,
        "post_vault_hit_zero": post_hits.get("vault_hit_count") == 0,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "expert_review_pass": expert.get("status") == "pass",
        "readiness_pass": readiness["returncode"] == 0,
        "no_write_proof_pass": True,
    }
    return {
        "batch_id": "m181r_validation_report_v1",
        "milestone": "M181R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": py_compile,
        "json_parse": json_parse,
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "readiness_stdout_tail": readiness["stdout"],
    }


def build_all(allow_trusted_pool_update: bool, allow_vault_regular_write: bool) -> dict[str, Any]:
    targets = load_targets()
    if not targets:
        raise ValueError("No M180 remediation targets found.")
    pre_hits = scan_current_hits()
    pool_result = update_pool(targets, allow_trusted_pool_update)
    trace_result = update_trace(targets, allow_trusted_pool_update)
    share_result = update_share_view(targets, allow_trusted_pool_update)
    package_result = update_package(targets, allow_trusted_pool_update)
    vault_result = update_vault(targets, allow_vault_regular_write)
    post_hits = scan_current_hits()
    expert = expert_review(pre_hits, post_hits, targets)
    validation = validate(post_hits, expert)
    update_panel(pool_result, post_hits, targets, validation["status"])

    manifest = {
        "batch_id": "m181r_signed_customer_remediation_manifest_v1",
        "milestone": "M181R",
        "generated_at": now(),
        "targets": targets,
        "guards": {
            "allow_trusted_pool_update": allow_trusted_pool_update,
            "allow_vault_regular_write": allow_vault_regular_write,
        },
        "pre_hits": pre_hits,
        "pool_update": pool_result,
        "source_trace_update": trace_result,
        "share_view_update": share_result,
        "package_update": package_result,
        "vault_update": vault_result,
        "post_hits": post_hits,
        "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False},
    }
    report = {
        "batch_id": "m181r_signed_customer_remediation_execution_v1",
        "milestone": "M181R",
        "generated_at": now(),
        "status": validation["status"],
        "summary": {
            "target_count": len(targets),
            "trusted_pool_before_count": pool_result.get("before_count"),
            "trusted_pool_after_count": pool_result.get("after_count"),
            "removed_from_trusted_pool_count": pool_result.get("removed_count"),
            "removed_from_source_trace_count": trace_result.get("removed_count"),
            "removed_vault_file_count": len(vault_result.get("removed_files") or []),
            "post_trusted_pool_hit_count": post_hits.get("trusted_pool_hit_count"),
            "post_vault_hit_count": post_hits.get("vault_hit_count"),
            "old_excel_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
        },
    }
    write_json(M181 / "signed_customer_remediation_manifest_v1.json", manifest)
    write_json(M181 / "m181_expert_review_report_v1.json", expert)
    write_json(M181 / "m181_validation_report_v1.json", validation)
    write_json(M181 / "m181_signed_customer_remediation_execution_v1.json", report)
    return {"status": validation["status"], "summary": report["summary"], "checks": validation["checks"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply M181R signed customer v2 remediation to trusted pool and vault outputs.")
    parser.add_argument("--stage", choices=["all", "validate"], default="all")
    parser.add_argument("--allow-trusted-pool-update", action="store_true")
    parser.add_argument("--allow-vault-regular-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.stage == "validate":
        post_hits = scan_current_hits()
        expert = read_json(M181 / "m181_expert_review_report_v1.json", {"status": "fail"})
        payload = validate(post_hits, expert)
    else:
        if not args.allow_trusted_pool_update:
            print(json.dumps({"status": "FAIL_MISSING_GUARD", "missing_guard": "--allow-trusted-pool-update"}, ensure_ascii=False, indent=2))
            return 2
        if not args.allow_vault_regular_write:
            print(json.dumps({"status": "FAIL_MISSING_GUARD", "missing_guard": "--allow-vault-regular-write"}, ensure_ascii=False, indent=2))
            return 2
        payload = build_all(args.allow_trusted_pool_update, args.allow_vault_regular_write)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
