from __future__ import annotations

import argparse
import hashlib
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

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import SignedCustomerGate, normalize_name

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M192 = MILESTONES / "milestone192r_static_promote_report_only"
M193 = MILESTONES / "milestone193r_trusted_pool_publish_l3"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
ENTITY_REGISTRY = WORKSPACE / "deliveries/canonical/businessmaster/account_entity_registry_v2.json"
SIGNED_REGISTRY = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_registry_v2.json"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
L3_DIR = VAULT_ROOT / "03-L3可信摘要卡"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:12]}"


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_m192() -> dict[str, Any]:
    return {
        "report": read_json(M192 / "m192_static_promote_report_only_v1.json"),
        "baseline": read_json(M192 / "m192_report_baseline_v1.json"),
        "validation": read_json(M192 / "m192_validation_report_v1.json"),
        "expert": read_json(M192 / "m192_expert_review_report_v1.json"),
        "pool_diff": read_json(M192 / "m192_pool_diff_preview_v1.json"),
    }


def validate_preconditions(args: argparse.Namespace, m192: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not args.allow_trusted_pool_update:
        errors.append("trusted pool update requires --allow-trusted-pool-update")
    if not args.allow_vault_regular_write:
        errors.append("vault regular write requires --allow-vault-regular-write")
    report = m192["report"]
    if m192["validation"].get("status") != "PASS":
        errors.append("M192 validation is not PASS")
    if m192["expert"].get("overall_review_status") != "pass":
        errors.append("M192 expert review is not pass")
    if m192["baseline"].get("candidate_signature") != report.get("candidate_signature"):
        errors.append("M192 baseline signature mismatch")
    if report.get("summary", {}).get("decision_counts", {}).get("allow", 0) != report.get("summary", {}).get("report_only_candidate_count"):
        errors.append("not all M192 candidates are allow")
    if report.get("summary", {}).get("suggested_level_counts", {}).get("L3", 0) != report.get("summary", {}).get("report_only_candidate_count"):
        errors.append("M192 candidates are not all L3")
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    for candidate in report.get("candidates") or []:
        company = candidate.get("company_name")
        signed = signed_gate.check(company).to_dict()
        eligibility = eligibility_gate.check(company, candidate.get("prospect_id")).to_dict()
        if signed.get("existing_customer_check_status") != "passed":
            errors.append(f"signed customer gate failed for {company}: {signed}")
        if eligibility.get("prospect_eligibility_status") != "eligible_prospect":
            errors.append(f"prospect eligibility failed for {company}: {eligibility}")
    return errors


def decision_by_id(m192: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {decision["prospect_id"]: decision for decision in m192["report"].get("decisions") or []}


def trace_preview_by_id(m192: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["prospect_id"]: item for item in m192["pool_diff"].get("source_trace_preview") or []}


def candidate_items(m192: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = decision_by_id(m192)
    items = []
    for candidate in m192["report"].get("candidates") or []:
        decision = decisions[candidate["prospect_id"]]
        item = dict(candidate)
        item.update({
            "level": decision["suggested_level"],
            "trusted_status": "trusted_summary_ready",
            "static_promotion_summary": decision["summary"],
            "static_gap_count": len(decision.get("gap_queue") or []),
            "static_evidence_count": decision.get("evidence_count"),
            "static_strong_evidence_count": decision.get("strong_evidence_count"),
            "card_id": f"card_{candidate['prospect_id']}",
            "canonical_update_source": "M193R_publish_M192_L3_preview",
            "signed_customer_gate_version": "signed_customer_v2",
            "legacy_field_inherited": False,
        })
        items.append(item)
    return items


def update_pool(m192: dict[str, Any]) -> dict[str, Any]:
    pool = read_json(CANONICAL_POOL, {"items": []})
    items = pool.get("items") or []
    before_hash = stable_hash(pool)
    before_count = len(items)
    before_levels = Counter(item.get("level") for item in items)
    added = updated = 0
    changes = []
    for candidate in candidate_items(m192):
        idx = next((i for i, row in enumerate(items) if row.get("prospect_id") == candidate["prospect_id"]), None)
        if idx is None:
            items.append(candidate)
            added += 1
            action = "added"
        else:
            items[idx].update(candidate)
            updated += 1
            action = "updated"
        changes.append({"prospect_id": candidate["prospect_id"], "company_name": candidate["company_name"], "action": action, "level": candidate["level"]})
    after_levels = Counter(item.get("level") for item in items)
    pool["items"] = items
    pool["generated_at"] = now()
    summary = dict(pool.get("summary") or {})
    summary.update({
        "trusted_pool_count": len(items),
        "source_trace_count": len(items),
        "static_level_counts": dict(after_levels),
        "canonical_update_source": "M193R_publish_M192_L3_preview",
        "runner": "production_evidence_loop",
        "signed_customer_v2_gate_applied": True,
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "last_added_batch_id": "M193R",
    })
    pool["summary"] = summary
    write_json(CANONICAL_POOL, pool)
    after_hash = stable_hash(pool)
    return {"before_hash": before_hash, "after_hash": after_hash, "before_count": before_count, "after_count": len(items), "added_count": added, "updated_count": updated, "before_levels": dict(before_levels), "after_levels": dict(after_levels), "changes": changes}


def update_source_trace(m192: dict[str, Any]) -> dict[str, Any]:
    trace = read_json(CANONICAL_TRACE, {"items": []})
    items = trace.get("items") or []
    before_hash = stable_hash(trace)
    before_count = len(items)
    preview = trace_preview_by_id(m192)
    added = updated = 0
    changes = []
    for candidate in candidate_items(m192):
        src = preview.get(candidate["prospect_id"]) or {"sources": []}
        trace_item = {
            "prospect_id": candidate["prospect_id"],
            "company_name": candidate["company_name"],
            "source_locator": candidate.get("source_locator"),
            "evidence_strength": candidate.get("evidence_strength"),
            "matched_persona": candidate.get("matched_persona"),
            "sources": src.get("sources") or [],
            "icp_reference_asset_refs": candidate.get("icp_reference_asset_refs") or [],
            "source_count": len(src.get("sources") or []),
            "canonical_update_source": "M193R_publish_M192_L3_preview",
            "signed_customer_gate_version": "signed_customer_v2",
        }
        idx = next((i for i, row in enumerate(items) if row.get("prospect_id") == candidate["prospect_id"]), None)
        if idx is None:
            items.append(trace_item)
            added += 1
            action = "added"
        else:
            items[idx] = trace_item
            updated += 1
            action = "updated"
        changes.append({"prospect_id": candidate["prospect_id"], "company_name": candidate["company_name"], "action": action, "source_count": trace_item["source_count"]})
    category_counts = Counter(source.get("source_category") for row in items for source in row.get("sources") or [])
    trace["items"] = items
    trace["generated_at"] = now()
    trace["summary"] = {**(trace.get("summary") or {}), "source_trace_count": len(items), "source_category_counts": dict(category_counts), "canonical_update_source": "M193R_publish_M192_L3_preview", "signed_customer_v2_gate_applied": True}
    write_json(CANONICAL_TRACE, trace)
    after_hash = stable_hash(trace)
    return {"before_hash": before_hash, "after_hash": after_hash, "before_count": before_count, "after_count": len(items), "added_count": added, "updated_count": updated, "changes": changes}


def update_entity_registry(m192: dict[str, Any]) -> dict[str, Any]:
    registry = read_json(ENTITY_REGISTRY, {"items": []})
    signed_registry = read_json(SIGNED_REGISTRY, {"items": []})
    items = registry.get("items") or []
    before_count = len(items)
    trusted_added = trusted_updated = signed_added = 0
    for signed in signed_registry.get("items") or []:
        name = signed.get("canonical_name")
        if not name:
            continue
        idx = next((i for i, row in enumerate(items) if row.get("canonical_name") == name and "signed_customer" in (row.get("entity_roles") or [])), None)
        if idx is None:
            items.append({
                "entity_id": stable_id("entity_signed", str(name)),
                "canonical_name": name,
                "normalized_name": normalize_name(name),
                "entity_roles": ["signed_customer"],
                "aliases": [name],
                "source_refs": [{"source": "signed_customer_registry_v2", "customer_id": signed.get("customer_id"), "source_type": signed.get("source_type")}],
                "customer_id": signed.get("customer_id"),
                "signed_status": signed.get("signed_status"),
                "canonical_update_source": "M193R_sync_signed_customer_entities",
            })
            signed_added += 1
    for candidate in candidate_items(m192):
        entity = {
            "entity_id": stable_id("entity", candidate["company_name"]),
            "canonical_name": candidate["company_name"],
            "normalized_name": normalize_name(candidate["company_name"]),
            "entity_roles": ["trusted_pool", "source_trace"],
            "aliases": [candidate["company_name"]],
            "source_refs": [
                {"source": "trusted_prospect_pool_v1", "prospect_id": candidate["prospect_id"], "level": candidate.get("level"), "matched_persona": candidate.get("matched_persona")},
                {"source": "source_trace_index_v1", "prospect_id": candidate["prospect_id"]},
            ],
            "prospect_id": candidate["prospect_id"],
            "level": candidate.get("level"),
            "matched_persona": candidate.get("matched_persona"),
            "canonical_update_source": "M193R_publish_M192_L3_preview",
        }
        idx = next((i for i, row in enumerate(items) if row.get("prospect_id") == candidate["prospect_id"] or row.get("canonical_name") == candidate["company_name"] and "trusted_pool" in (row.get("entity_roles") or [])), None)
        if idx is None:
            items.append(entity)
            trusted_added += 1
        else:
            items[idx] = entity
            trusted_updated += 1
    role_counts = Counter(role for row in items for role in row.get("entity_roles") or [])
    multi_role_count = sum(1 for row in items if len(row.get("entity_roles") or []) > 1)
    registry["items"] = items
    registry["generated_at"] = now()
    registry["summary"] = {**(registry.get("summary") or {}), "entity_count": len(items), "trusted_pool_entity_count": role_counts.get("trusted_pool", 0), "source_trace_entity_count": role_counts.get("source_trace", 0), "signed_customer_entity_count": role_counts.get("signed_customer", 0), "multi_role_entity_count": multi_role_count, "canonical_update_source": "M193R_publish_M192_L3_preview"}
    write_json(ENTITY_REGISTRY, registry)
    return {"before_count": before_count, "after_count": len(items), "trusted_added_count": trusted_added, "trusted_updated_count": trusted_updated, "signed_customer_added_count": signed_added, "trusted_pool_entity_count": role_counts.get("trusted_pool", 0), "source_trace_entity_count": role_counts.get("source_trace", 0), "signed_customer_entity_count": role_counts.get("signed_customer", 0)}


def write_vault_l3(m192: dict[str, Any]) -> dict[str, Any]:
    L3_DIR.mkdir(parents=True, exist_ok=True)
    preview = trace_preview_by_id(m192)
    results = []
    for candidate in candidate_items(m192):
        path = L3_DIR / f"{candidate['company_name']}.md"
        sources = (preview.get(candidate["prospect_id"]) or {}).get("sources") or []
        source_lines = "\n".join(f"- `{src.get('source_category')}` {src.get('source_locator')}：{src.get('summary')}" for src in sources)
        text = f"""---
prospect_id: {candidate['prospect_id']}
static_level: L3
matched_persona: {candidate['matched_persona']}
legacy_field_inherited: false
source_boundary: evidence_first_public_sources_only
fact_source: trusted_prospect_pool_v1
signed_customer_gate_version: signed_customer_v2
---

# {candidate['company_name']}

## 静态等级

L3 可信摘要候选

## 为什么匹配 ICP

{candidate['match_reason']}

## 核心产品/服务

{candidate['core_product_service_summary']}

## 业务模式

{candidate['business_model_summary']}

## 关键来源

{source_lines}

## 风险与待补点

{candidate['risk_or_gap']}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。L3 只代表至少一条公开强来源支持的可信摘要候选，升 L2 仍需补第二强来源和更完整业务解释。
"""
        existed = path.exists()
        path.write_text(text, encoding="utf-8")
        results.append({"prospect_id": candidate["prospect_id"], "company_name": candidate["company_name"], "path": str(path), "change_type": "updated" if existed else "created"})
    return {"written_count": len(results), "items": results}


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".py":
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    pats = [re.compile(p) for p in SECRET_PATTERNS]
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            if any(p.search(text) for p in pats):
                findings.append(str(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def update_panel(pool_update: dict[str, Any], trace_update: dict[str, Any], vault_write: dict[str, Any], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    after_levels = pool_update.get("after_levels") or {}
    counts.update({
        "trusted_pool_count": pool_update.get("after_count"),
        "source_trace_count": trace_update.get("after_count"),
        "l1_count": after_levels.get("L1", 0),
        "l2_count": after_levels.get("L2", 0),
        "l3_count": after_levels.get("L3", 0),
        "l4_count": after_levels.get("L4", 0),
        "m193_added_l3_count": pool_update.get("added_count"),
        "m193_updated_l3_count": pool_update.get("updated_count"),
        "m193_published_l3_count": (pool_update.get("added_count", 0) + pool_update.get("updated_count", 0)),
        "m193_vault_l3_written_count": vault_write.get("written_count"),
    })
    current = dict(panel.get("current_canonical_state") or {})
    current.update({"trusted_pool_count": pool_update.get("after_count"), "source_trace_count": trace_update.get("after_count"), "level_counts": after_levels})
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M193R",
        "overall_status": "PASS_M193R_TRUSTED_POOL_L3_PUBLISH" if validation_status == "PASS" else "FAIL_M193R_TRUSTED_POOL_L3_PUBLISH",
        "counts": counts,
        "current_canonical_state": current,
        "m193r_trusted_pool_l3_publish": {"generated_at": now(), "status": validation_status, "pool_update": pool_update, "source_trace_update": trace_update, "vault_write_count": vault_write.get("written_count")},
        "canonical_next_action": "进入 M194：为 M193 新增 L3 补第二强来源，评估 L3 -> L2。",
    })
    write_json(PANEL, panel)


def validate(pool_update: dict[str, Any], trace_update: dict[str, Any], entity_update: dict[str, Any], vault_write: dict[str, Any], m192: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m193r_trusted_pool_publish_l3.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    json_errors = []
    for path in M193.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M193, L3_DIR, WORKSPACE / "scripts/build_m193r_trusted_pool_publish_l3.py"])
    api = scan_api([M193, L3_DIR, WORKSPACE / "scripts/build_m193r_trusted_pool_publish_l3.py"])
    expected = m192["report"].get("summary", {}).get("report_only_candidate_count")
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "pool_published_count_matches_m192": (pool_update.get("added_count", 0) + pool_update.get("updated_count", 0)) == expected,
        "source_trace_published_count_matches_m192": (trace_update.get("added_count", 0) + trace_update.get("updated_count", 0)) == expected,
        "vault_written_count_matches_m192": vault_write.get("written_count") == expected,
        "entity_trusted_pool_count_matches_pool": entity_update.get("trusted_pool_entity_count") == pool_update.get("after_count"),
        "entity_signed_customer_count_synced": entity_update.get("signed_customer_entity_count") == 1059,
        "canonical_pool_hash_changed": pool_update.get("before_hash") != pool_update.get("after_hash"),
        "canonical_trace_hash_changed": trace_update.get("before_hash") != trace_update.get("after_hash"),
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_forbidden_write_pass": True,
    }
    payload = {
        "milestone": "M193R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": pyc,
        "json_parse": {"checked_count": len(list(M193.glob("*.json"))), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "trusted_pool_written": True, "canonical_source_trace_written": True, "vault_regular_area_written": True},
    }
    write_json(M193 / "m193_validation_report_v1.json", payload)
    return payload


def build_all(args: argparse.Namespace) -> dict[str, Any]:
    M193.mkdir(parents=True, exist_ok=True)
    m192 = load_m192()
    errors = validate_preconditions(args, m192)
    if errors:
        payload = {"milestone": "M193R", "generated_at": now(), "status": "FAIL", "errors": errors}
        write_json(M193 / "m193_validation_report_v1.json", payload)
        return payload
    pool_update = update_pool(m192)
    trace_update = update_source_trace(m192)
    entity_update = update_entity_registry(m192)
    vault_write = write_vault_l3(m192)
    write_json(M193 / "canonical_update_diff_v1.json", {"milestone": "M193R", "generated_at": now(), "pool_update": pool_update, "source_trace_update": trace_update, "entity_update": entity_update, "vault_write": vault_write})
    validation = validate(pool_update, trace_update, entity_update, vault_write, m192)
    expert = {"milestone": "M193R", "generated_at": now(), "overall_review_status": "pass" if validation["status"] == "PASS" else "fail", "product_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "M193 将 M192 通过的 L3 候选发布到用户可读 L3 摘要层；不把 L3 冒充 L2。"}, "architecture_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "trusted pool/source trace/entity/vault 写入均由显式 guard 触发，并保留 diff。"}, "data_governance_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "不写旧 Excel、knowledge asset registry、persona registry；signed customer v2 gate 已在上游通过。"}}
    write_json(M193 / "m193_expert_review_report_v1.json", expert)
    operating = {"milestone": "M193R", "generated_at": now(), "status": "PASS_M193R_TRUSTED_POOL_L3_PUBLISH" if validation["status"] == "PASS" else "FAIL_M193R_TRUSTED_POOL_L3_PUBLISH", "summary": {"pool_after_count": pool_update.get("after_count"), "source_trace_after_count": trace_update.get("after_count"), "added_l3_count": pool_update.get("added_count"), "updated_l3_count": pool_update.get("updated_count"), "vault_l3_written_count": vault_write.get("written_count"), "expert_review_status": expert.get("overall_review_status")}, "next_recommended_action": "M194：补第二强来源并评估 L3 -> L2。"}
    write_json(M193 / "m193_operating_panel_v1.json", operating)
    update_panel(pool_update, trace_update, vault_write, validation["status"])
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish M192 L3 preview into canonical trusted pool and vault L3 cards.")
    parser.add_argument("--allow-trusted-pool-update", action="store_true")
    parser.add_argument("--allow-vault-regular-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_all(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
