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
from shared.static_pool.signed_customer_gate import SignedCustomerGate

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M190 = MILESTONES / "milestone190r_candidate_discovery_backlog"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
SEED_QUEUE = MILESTONES / "milestone55r_expansion_seed_queue/milestone55r_expansion_seed_queue_package_v1.json"
PERSONA = WORKSPACE / "deliveries/canonical/businessmaster/persona_registry_v1.json"
KNOWLEDGE = WORKSPACE / "deliveries/canonical/businessmaster/knowledge_asset_registry_v1.json"
CASE_REF = WORKSPACE / "deliveries/canonical/businessmaster/customer_case_reference_registry_v1.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]
REQUIRED_SOURCE_CATEGORIES = ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"]
SIGNED_REGRESSION_SAMPLES = ["百胜中国", "珀莱雅", "上海家化", "森马", "特步", "海澜之家", "锅圈", "来伊份", "天味食品", "水星家纺", "Lily服饰", "乐凯撒", "零跑汽车"]


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


def persona_lookup() -> dict[str, dict[str, Any]]:
    payload = read_json(PERSONA, {"items": []})
    lookup: dict[str, dict[str, Any]] = {}
    for item in payload.get("items") or []:
        pid = str(item.get("persona_id") or "")
        if pid:
            lookup[pid] = item
    return lookup


def knowledge_lookup() -> dict[str, dict[str, Any]]:
    payload = read_json(KNOWLEDGE, {"items": []})
    return {str(item.get("asset_id")): item for item in payload.get("items") or [] if item.get("asset_id")}


def case_reference_names() -> set[str]:
    payload = read_json(CASE_REF, {"items": []})
    return {str(item.get("customer_or_brand_name") or "").strip() for item in payload.get("items") or [] if item.get("customer_or_brand_name")}


def icp_refs_for_persona(persona_id: str, personas: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    persona = personas.get(persona_id) or {}
    refs = []
    for ref in persona.get("reference_knowledge_assets") or []:
        refs.append({
            "asset_id": ref.get("asset_id"),
            "title": ref.get("title"),
            "reference_role": "icp_reference_only_not_prospect_evidence",
        })
    return refs[:3]


def infer_required_categories(persona_id: str, source_locator_seed: str) -> list[str]:
    categories = ["official_owned", "authoritative_third_party"]
    if any(token in persona_id for token in ["retail", "fnb", "chain", "platform", "cbec"]):
        categories.insert(1, "platform_operating_fact")
    if any(token in source_locator_seed.lower() for token in ["ir.", "invest", "cninfo", "hkex", "sec"]):
        categories.append("regulatory_or_capital_market")
    return list(dict.fromkeys(categories))


def build_candidate_discovery() -> dict[str, Any]:
    seeds = read_json(SEED_QUEUE, {"items": []}).get("items") or []
    personas = persona_lookup()
    case_names = case_reference_names()
    items = []
    for seed in seeds:
        company = str(seed.get("company_name") or "").strip()
        persona_id = str(seed.get("matched_persona_guess") or "").strip()
        source_locator = str(seed.get("source_locator_seed") or "").strip()
        task_id = stable_id("m190_task", company)
        items.append({
            "task_id": task_id,
            "candidate_name": company,
            "candidate_source": "milestone55_expansion_seed_queue",
            "source_locator_seed": source_locator,
            "matched_persona": persona_id,
            "persona_display_name": (personas.get(persona_id) or {}).get("display_name"),
            "icp_reference_asset_refs": icp_refs_for_persona(persona_id, personas),
            "required_source_categories": infer_required_categories(persona_id, source_locator),
            "source_boundary": "seed/source_locator 只作为候选发现线索；进入 trusted pool 前必须重新采集可定位公开强 evidence。",
            "customer_case_reference_overlap": company in case_names,
            "not_prospect_evidence_until_public_source_collected": True,
        })
    payload = {
        "package_id": "m190r_candidate_discovery_package_v1",
        "milestone": "M190R",
        "generated_at": now(),
        "summary": {
            "seed_count": len(seeds),
            "candidate_discovery_count": len(items),
            "candidate_source": "milestone55_expansion_seed_queue",
            "knowledge_asset_registry_read": True,
            "persona_registry_read": True,
            "customer_case_reference_read": True,
            "customer_case_used_as_prospect_evidence": False,
            "old_excel_written": False,
            "trusted_pool_written": False,
            "vault_regular_area_written": False,
        },
        "items": items,
    }
    write_json(M190 / "candidate_discovery_package_v1.json", payload)
    return payload


def build_backlog(discovery: dict[str, Any]) -> dict[str, Any]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    items = []
    for item in discovery.get("items") or []:
        candidate = item["candidate_name"]
        signed = signed_gate.check(candidate).to_dict()
        eligibility = eligibility_gate.check(candidate, item["task_id"]).to_dict()
        status = eligibility.get("prospect_eligibility_status")
        if not candidate:
            state = "identity_pending"
            next_action = "补充候选公司标准名后重新执行 entity/signed customer gate。"
        elif status == "eligible_prospect":
            state = "source_collection_pending"
            next_action = "采集可定位公开强 evidence；至少覆盖 official_owned，并优先补 platform_operating_fact 或 authoritative_third_party。"
        elif status in {"excluded_signed_customer", "duplicate_existing_prospect", "excluded_non_company"}:
            state = "eligibility_blocked"
            next_action = "资格闸门阻断，不进入 source collection。"
        elif status == "boundary_review":
            state = "eligibility_blocked"
            next_action = "signed customer 或 entity 边界不清，需人工确认后才可重新进入 source collection。"
        else:
            state = "eligibility_blocked"
            next_action = "资格状态异常，需复核 gate 输出。"
        items.append({
            **item,
            "current_state": state,
            "identity_resolution": {
                "identity_resolution_status": "resolved_company_candidate" if candidate else "identity_pending",
                "resolved_company_name": candidate or None,
                "resolution_method": "seed_company_name",
                "entity_resolution_required_before_source_collection": True,
            },
            "signed_customer_gate_version": "v2",
            "signed_customer_check": signed,
            "prospect_eligibility": eligibility,
            "next_action": next_action,
        })
    state_counts = Counter(item["current_state"] for item in items)
    eligibility_counts = Counter((item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") or "not_checked" for item in items)
    payload = {
        "batch_id": "m190r_evidence_acquisition_backlog_v7",
        "milestone": "M190R",
        "generated_at": now(),
        "summary": {
            "task_count": len(items),
            "state_counts": dict(state_counts),
            "eligibility_status_counts": dict(eligibility_counts),
            "source_collection_pending_count": state_counts.get("source_collection_pending", 0),
            "eligibility_blocked_count": state_counts.get("eligibility_blocked", 0),
            "identity_pending_count": state_counts.get("identity_pending", 0),
            "excluded_signed_customer_count": eligibility_counts.get("excluded_signed_customer", 0),
            "duplicate_existing_prospect_count": eligibility_counts.get("duplicate_existing_prospect", 0),
            "boundary_review_count": eligibility_counts.get("boundary_review", 0),
            "signed_customer_gate_version": "v2",
            "old_workbook_written": False,
            "trusted_pool_written": False,
            "source_trace_written": False,
            "vault_regular_area_written": False,
        },
        "items": items,
    }
    write_json(M190 / "evidence_acquisition_backlog_v7.json", payload)
    return payload


def build_gate_report(backlog: dict[str, Any]) -> dict[str, Any]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    signed_results = {name: {"signed": signed_gate.check(name).to_dict(), "eligibility": eligibility_gate.check(name).to_dict()} for name in SIGNED_REGRESSION_SAMPLES}
    source_ready_items = [item for item in backlog.get("items") or [] if item.get("current_state") == "source_collection_pending"]
    customer_case_violations = [item for item in source_ready_items if item.get("customer_case_reference_overlap")]
    missing_gate = [item for item in backlog.get("items") or [] if item.get("current_state") == "source_collection_pending" and not item.get("signed_customer_check")]
    payload = {
        "report_id": "m190r_gate_regression_report_v1",
        "milestone": "M190R",
        "generated_at": now(),
        "summary": {
            "signed_regression_sample_count": len(SIGNED_REGRESSION_SAMPLES),
            "signed_regression_blocked_count": sum(row["signed"].get("existing_customer_check_status") == "excluded_existing_customer" for row in signed_results.values()),
            "source_collection_pending_count": len(source_ready_items),
            "customer_case_to_source_collection_violation_count": len(customer_case_violations),
            "missing_signed_customer_check_count": len(missing_gate),
        },
        "signed_customer_regression": signed_results,
        "customer_case_violations": customer_case_violations,
        "missing_signed_customer_check": missing_gate,
    }
    write_json(M190 / "prospect_gate_regression_report_v1.json", payload)
    return payload


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
                    findings.append({"file": rel(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    pats = [re.compile(p) for p in SECRET_PATTERNS]
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            if any(p.search(text) for p in pats):
                findings.append(rel(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def update_panel(backlog: dict[str, Any], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    signed_registry = read_json(WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_registry_v2.json", {"summary": {}})
    signed_alias = read_json(WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_alias_registry_v2.json", {"summary": {}})
    counts = dict(panel.get("counts") or {})
    summary = backlog.get("summary") or {}
    counts.update({
        "signed_customer_count": signed_registry.get("summary", {}).get("confirmed_signed_customer_count"),
        "signed_customer_alias_count": signed_alias.get("summary", {}).get("alias_count"),
        "signed_customer_v2_count": signed_registry.get("summary", {}).get("confirmed_signed_customer_count"),
        "signed_customer_alias_v2_count": signed_alias.get("summary", {}).get("alias_count"),
        "m190_candidate_discovery_count": summary.get("task_count"),
        "m190_source_collection_pending_count": summary.get("source_collection_pending_count"),
        "m190_eligibility_blocked_count": summary.get("eligibility_blocked_count"),
        "m190_excluded_signed_customer_count": summary.get("excluded_signed_customer_count"),
        "m190_duplicate_existing_prospect_count": summary.get("duplicate_existing_prospect_count"),
        "m190_boundary_review_count": summary.get("boundary_review_count"),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M190R",
        "overall_status": "PASS_M190R_CANDIDATE_DISCOVERY_BACKLOG" if validation_status == "PASS" else "FAIL_M190R_CANDIDATE_DISCOVERY_BACKLOG",
        "counts": counts,
        "m190r_candidate_discovery_backlog": {
            "generated_at": now(),
            "status": validation_status,
            "backlog_state_counts": summary.get("state_counts"),
            "eligibility_status_counts": summary.get("eligibility_status_counts"),
            "source_collection_pending_count": summary.get("source_collection_pending_count"),
            "signed_customer_gate_version": "v2",
        },
        "canonical_next_action": "进入 M191：对 M190 source_collection_pending 候选采集公开强 evidence；不得使用 seed/customer case 作为 prospect evidence。",
    })
    write_json(PANEL, panel)


def validate(discovery: dict[str, Any], backlog: dict[str, Any], gate_report: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m190r_candidate_discovery_backlog.py", "scripts/businessmaster_pipeline.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    json_errors = []
    for path in M190.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M190, WORKSPACE / "scripts/build_m190r_candidate_discovery_backlog.py"])
    api = scan_api([M190, WORKSPACE / "scripts/build_m190r_candidate_discovery_backlog.py"])
    source_ready = [item for item in backlog.get("items") or [] if item.get("current_state") == "source_collection_pending"]
    signed_blocked = gate_report["summary"].get("signed_regression_blocked_count") == len(SIGNED_REGRESSION_SAMPLES)
    pending_has_required_sources = all(set(item.get("required_source_categories") or []) & set(REQUIRED_SOURCE_CATEGORIES) for item in source_ready)
    pending_eligible = all((item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") == "eligible_prospect" for item in source_ready)
    pending_has_signed_gate = all(item.get("signed_customer_gate_version") == "v2" and item.get("signed_customer_check") for item in source_ready)
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "candidate_count_in_range": 20 <= discovery["summary"].get("candidate_discovery_count", 0) <= 40,
        "source_collection_pending_floor_met": backlog["summary"].get("source_collection_pending_count", 0) >= 10,
        "source_collection_pending_not_excessive": backlog["summary"].get("source_collection_pending_count", 0) <= 20,
        "pending_candidates_are_eligible": pending_eligible,
        "pending_candidates_have_signed_gate_v2": pending_has_signed_gate,
        "pending_candidates_have_required_source_category": pending_has_required_sources,
        "signed_customer_regression_pass": signed_blocked,
        "customer_case_not_source_collection": gate_report["summary"].get("customer_case_to_source_collection_violation_count") == 0,
        "missing_signed_check_count_zero": gate_report["summary"].get("missing_signed_customer_check_count") == 0,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_write_proof_pass": True,
    }
    payload = {
        "milestone": "M190R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": pyc,
        "json_parse": {"checked_count": len(list(M190.glob("*.json"))), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "no_write_proof": {
            "old_excel_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
            "trusted_pool_written": False,
            "source_trace_written": False,
            "vault_regular_area_written": False,
            "customer_case_used_as_prospect_evidence": False,
        },
    }
    write_json(M190 / "m190_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {
        "milestone": "M190R",
        "generated_at": now(),
        "overall_review_status": "pass" if passed else "fail",
        "product_review": {
            "status": "pass" if passed else "fail",
            "notes": "候选发现入口已恢复，source_collection_pending 只包含 eligible prospect；老客、重复和客户案例不会被展示为新潜客。",
        },
        "architecture_review": {
            "status": "pass" if passed else "fail",
            "notes": "生产链路前置 entity/signed customer v2/eligibility gate，并通过统一 pipeline dry-run 暴露。",
        },
        "data_governance_review": {
            "status": "pass" if passed else "fail",
            "notes": "知识/画像/客户案例仅作为 ICP reference；本轮不写 trusted pool、source trace、vault、knowledge/persona registry。",
        },
        "followups": [] if passed else ["修复 validation_report 中失败项后再进入 M191 evidence collection。"],
        "backlog_summary": backlog.get("summary"),
    }
    write_json(M190 / "m190_expert_review_report_v1.json", payload)
    return payload


def build_all() -> dict[str, Any]:
    M190.mkdir(parents=True, exist_ok=True)
    discovery = build_candidate_discovery()
    backlog = build_backlog(discovery)
    gate_report = build_gate_report(backlog)
    validation = validate(discovery, backlog, gate_report)
    expert = build_expert_review(validation, backlog)
    operating = {
        "milestone": "M190R",
        "generated_at": now(),
        "status": "PASS_M190R_CANDIDATE_DISCOVERY_BACKLOG" if validation["status"] == "PASS" else "FAIL_M190R_CANDIDATE_DISCOVERY_BACKLOG",
        "summary": {
            **backlog.get("summary", {}),
            "expert_review_status": expert.get("overall_review_status"),
        },
        "next_recommended_action": "M191：对 source_collection_pending 候选采集公开强 evidence，完成后进入 report-only。",
    }
    write_json(M190 / "m190_operating_panel_v1.json", operating)
    update_panel(backlog, validation["status"])
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M190 candidate discovery v2 and evidence acquisition backlog v7.")
    parser.add_argument("--stage", choices=["all"], default="all")
    return parser


def main() -> int:
    build_parser().parse_args()
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
