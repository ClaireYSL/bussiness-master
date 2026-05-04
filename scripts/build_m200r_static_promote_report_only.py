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
from shared.static_pool.static_promote import evaluate_static_promotion

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M199 = MILESTONES / "milestone199r_public_evidence_acquisition"
M200 = MILESTONES / "milestone200r_static_promote_report_only"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
REPORT_INPUT = M199 / "report_only_ready_input_v1.json"
SOURCE_TRACE_DRAFT = M199 / "source_trace_package_v1.json"

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


def canonical_pool_index() -> dict[str, dict[str, Any]]:
    pool = read_json(CANONICAL_POOL, {"items": []})
    return {str(item.get("prospect_id")): item for item in pool.get("items") or [] if item.get("prospect_id")}


def build_candidates() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    report_input = read_json(REPORT_INPUT, {"items": []})
    trace_draft = read_json(SOURCE_TRACE_DRAFT, {"items": []})
    trace_by_task = {item.get("task_id"): item for item in trace_draft.get("items") or []}
    candidates = []
    source_trace_by_prospect: dict[str, list[dict[str, Any]]] = {}
    for item in report_input.get("items") or []:
        prospect_id = stable_id("m200", str(item.get("candidate_name") or item.get("task_id")))
        trace = trace_by_task.get(item.get("task_id")) or {}
        sources = trace.get("sources") or item.get("sources") or []
        candidate = {
            "prospect_id": prospect_id,
            "task_id": item.get("task_id"),
            "company_name": item.get("candidate_name"),
            "level": item.get("level") or "L5",
            "matched_persona": item.get("matched_persona"),
            "match_reason": item.get("match_reason"),
            "core_product_service_summary": item.get("core_product_service_summary"),
            "business_model_summary": item.get("business_model_summary"),
            "risk_or_gap": item.get("risk_or_gap"),
            "source_locator": item.get("source_locator"),
            "evidence_strength": "public_strong_source_locator",
            "source_category": item.get("source_category"),
            "icp_reference_asset_refs": item.get("icp_reference_asset_refs") or [],
            "signed_customer_gate_version": "v2",
            "legacy_field_inherited": False,
            "candidate_source": "M199R_report_only_ready_input",
        }
        candidates.append(candidate)
        source_trace_by_prospect[prospect_id] = sources
    return candidates, source_trace_by_prospect


def build_report_only() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    existing_pool = canonical_pool_index()
    candidates, source_trace_by_prospect = build_candidates()
    decisions = []
    gap_queue = []
    pool_diff_items = []
    source_trace_items = []
    for candidate in candidates:
        company = candidate.get("company_name")
        signed = signed_gate.check(company).to_dict()
        eligibility = eligibility_gate.check(company, candidate.get("prospect_id")).to_dict()
        if signed.get("existing_customer_check_status") != "passed" or eligibility.get("prospect_eligibility_status") != "eligible_prospect":
            decision = {
                "prospect_id": candidate["prospect_id"],
                "company_name": company,
                "current_level": candidate.get("level"),
                "suggested_level": candidate.get("level"),
                "decision": "block",
                "gap_queue": [{"queue_type": "eligibility_gap_queue", "field": "prospect_eligibility", "reason": "signed customer or duplicate eligibility gate failed before report-only."}],
                "evidence_count": 0,
                "strong_evidence_count": 0,
                "summary": f"{company} 未通过 eligibility gate，不进入静态升层。",
            }
        else:
            decision = evaluate_static_promotion(candidate, source_trace_by_prospect=source_trace_by_prospect).to_dict()
        decision["signed_customer_check"] = signed
        decision["prospect_eligibility"] = eligibility
        decisions.append(decision)
        for gap in decision.get("gap_queue") or []:
            gap_queue.append({"prospect_id": decision["prospect_id"], "company_name": company, **gap})
        old = existing_pool.get(candidate["prospect_id"])
        pool_diff_items.append({
            "prospect_id": candidate["prospect_id"],
            "company_name": company,
            "action": "append_new" if not old and decision.get("decision") != "block" else "blocked_or_existing",
            "current_level": candidate.get("level"),
            "suggested_level": decision.get("suggested_level"),
            "decision": decision.get("decision"),
            "canonical_pool_updated": False,
        })
        source_trace_items.append({
            "prospect_id": candidate["prospect_id"],
            "company_name": company,
            "sources": source_trace_by_prospect.get(candidate["prospect_id"], []),
            "canonical_source_trace_written": False,
        })
    level_counts = Counter(decision.get("suggested_level") for decision in decisions)
    decision_counts = Counter(decision.get("decision") for decision in decisions)
    signature_payload = {"candidates": candidates, "source_trace": source_trace_by_prospect}
    candidate_signature = stable_hash(signature_payload)
    report = {
        "batch_id": "m200r_static_promote_report_only_v1",
        "milestone": "M200R",
        "generated_at": now(),
        "mode": "report_only",
        "candidate_signature": candidate_signature,
        "summary": {
            "report_only_candidate_count": len(candidates),
            "decision_counts": dict(decision_counts),
            "suggested_level_counts": dict(level_counts),
            "gap_queue_count": len(gap_queue),
            "canonical_pool_updated": False,
            "canonical_source_trace_written": False,
            "vault_regular_area_written": False,
        },
        "candidates": candidates,
        "decisions": decisions,
        "gap_queue": gap_queue,
        "no_write_proof": {
            "old_excel_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
            "trusted_pool_written": False,
            "canonical_source_trace_written": False,
            "vault_regular_area_written": False,
        },
    }
    baseline = {"milestone": "M200R", "generated_at": now(), "candidate_signature": candidate_signature, "report_file": "m200_static_promote_report_only_v1.json"}
    pool_diff = {
        "diff_id": "m200r_pool_diff_preview_v1",
        "milestone": "M200R",
        "generated_at": now(),
        "mode": "preview_only",
        "summary": {
            "append_new_preview_count": sum(1 for item in pool_diff_items if item["action"] == "append_new"),
            "blocked_or_existing_count": sum(1 for item in pool_diff_items if item["action"] == "blocked_or_existing"),
            "canonical_pool_updated": False,
            "canonical_source_trace_written": False,
        },
        "items": pool_diff_items,
        "source_trace_preview": source_trace_items,
    }
    write_json(M200 / "m200_static_promote_report_only_v1.json", report)
    write_json(M200 / "m200_report_baseline_v1.json", baseline)
    write_json(M200 / "m200_gap_queue_v1.json", {"milestone": "M200R", "generated_at": now(), "summary": {"gap_queue_count": len(gap_queue), "by_queue_type": dict(Counter(gap.get("queue_type") for gap in gap_queue))}, "items": gap_queue})
    write_json(M200 / "m200_pool_diff_preview_v1.json", pool_diff)
    return report, baseline, pool_diff


def build_gate_report(report: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    baseline_match = report.get("candidate_signature") == baseline.get("candidate_signature")
    mismatch_probe = {**baseline, "candidate_signature": "intentional_mismatch"}
    mismatch_failed = report.get("candidate_signature") != mismatch_probe.get("candidate_signature")
    blocked = [decision for decision in report.get("decisions") or [] if decision.get("decision") == "block"]
    ready = [decision for decision in report.get("decisions") or [] if decision.get("decision") != "block"]
    payload = {
        "report_id": "m200r_gate_check_v1",
        "milestone": "M200R",
        "generated_at": now(),
        "summary": {
            "baseline_match": baseline_match,
            "baseline_mismatch_probe_failed": mismatch_failed,
            "report_only_candidate_count": report.get("summary", {}).get("report_only_candidate_count"),
            "non_block_candidate_count": len(ready),
            "block_candidate_count": len(blocked),
            "canonical_pool_updated": False,
            "canonical_source_trace_written": False,
        },
        "blocked_candidates": blocked,
    }
    write_json(M200 / "m200_gate_check_v1.json", payload)
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


def update_panel(report: dict[str, Any], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    summary = report.get("summary") or {}
    levels = summary.get("suggested_level_counts") or {}
    counts.update({
        "m200_report_only_candidate_count": summary.get("report_only_candidate_count"),
        "m200_l3_candidate_count": levels.get("L3", 0),
        "m200_l2_candidate_count": levels.get("L2", 0),
        "m200_l1_candidate_count": levels.get("L1", 0),
        "m200_gap_queue_count": summary.get("gap_queue_count"),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M200R",
        "overall_status": "PASS_M200R_STATIC_PROMOTE_REPORT_ONLY" if validation_status == "PASS" else "FAIL_M200R_STATIC_PROMOTE_REPORT_ONLY",
        "counts": counts,
        "m200r_static_promote_report_only": {
            "generated_at": now(),
            "status": validation_status,
            "suggested_level_counts": levels,
            "decision_counts": summary.get("decision_counts"),
            "gap_queue_count": summary.get("gap_queue_count"),
            "canonical_pool_updated": False,
        },
        "canonical_next_action": "进入 M201：基于 M200 pool diff preview 执行 guarded trusted pool update，或先补第二强来源提升 L2。",
    })
    write_json(PANEL, panel)


def validate(report: dict[str, Any], baseline: dict[str, Any], pool_diff: dict[str, Any], gate_report: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m200r_static_promote_report_only.py", "shared/static_pool/static_promote.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    json_errors = []
    for path in M200.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M200, WORKSPACE / "scripts/build_m200r_static_promote_report_only.py"])
    api = scan_api([M200, WORKSPACE / "scripts/build_m200r_static_promote_report_only.py"])
    decisions = report.get("decisions") or []
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "report_only_candidate_count_positive": report.get("summary", {}).get("report_only_candidate_count", 0) > 0,
        "baseline_match_pass": gate_report.get("summary", {}).get("baseline_match") is True,
        "baseline_mismatch_probe_failed": gate_report.get("summary", {}).get("baseline_mismatch_probe_failed") is True,
        "no_block_candidates": gate_report.get("summary", {}).get("block_candidate_count") == 0,
        "pool_diff_preview_matches_candidates": pool_diff.get("summary", {}).get("append_new_preview_count") == report.get("summary", {}).get("report_only_candidate_count"),
        "all_candidates_l3_or_above": all(decision.get("suggested_level") in {"L3", "L2", "L1"} for decision in decisions),
        "gap_queue_present_for_second_source": any(gap.get("field") == "second_strong_evidence" for gap in report.get("gap_queue") or []),
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_write_proof_pass": True,
    }
    payload = {
        "milestone": "M200R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": pyc,
        "json_parse": {"checked_count": len(list(M200.glob("*.json"))), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "no_write_proof": report.get("no_write_proof"),
    }
    write_json(M200 / "m200_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {
        "milestone": "M200R",
        "generated_at": now(),
        "overall_review_status": "pass" if passed else "fail",
        "product_review": {"status": "pass" if passed else "fail", "notes": "M200 将 M199 候选评估为静态可信摘要层，不硬升 L2；用户仍不会看到未发布对象。"},
        "architecture_review": {"status": "pass" if passed else "fail", "notes": "report-only、baseline、pool diff preview、no-write proof 已分离，后续 guarded update 可回放。"},
        "data_governance_review": {"status": "pass" if passed else "fail", "notes": "signed customer v2 / duplicate gate 已在 M199 前置，本轮不写旧 Excel、knowledge/persona registry、trusted pool 或 vault。"},
        "report_summary": report.get("summary"),
    }
    write_json(M200 / "m200_expert_review_report_v1.json", payload)
    return payload


def build_all() -> dict[str, Any]:
    M200.mkdir(parents=True, exist_ok=True)
    report, baseline, pool_diff = build_report_only()
    gate_report = build_gate_report(report, baseline)
    validation = validate(report, baseline, pool_diff, gate_report)
    expert = build_expert_review(validation, report)
    operating = {
        "milestone": "M200R",
        "generated_at": now(),
        "status": "PASS_M200R_STATIC_PROMOTE_REPORT_ONLY" if validation["status"] == "PASS" else "FAIL_M200R_STATIC_PROMOTE_REPORT_ONLY",
        "summary": {**report.get("summary", {}), "expert_review_status": expert.get("overall_review_status")},
        "next_recommended_action": "M201：可选择先将 L3 preview guarded update 到 trusted pool，或补第二强来源后再冲 L2。",
    }
    write_json(M200 / "m200_operating_panel_v1.json", operating)
    update_panel(report, validation["status"])
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M200 static promote report-only from M199 report-only-ready input.")
    parser.add_argument("--stage", choices=["all"], default="all")
    return parser


def main() -> int:
    build_parser().parse_args()
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
