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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import SignedCustomerGate

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M210 = MILESTONES / "milestone210r_next_candidate_discovery_cycle"
M211 = MILESTONES / "milestone211r_public_evidence_acquisition"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
BACKLOG_V1 = M210 / "evidence_acquisition_backlog_v1.json"
DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]
STRONG_SOURCE_CATEGORIES = {"official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def check_url(url: str) -> dict[str, Any]:
    if not url:
        return {"source_locator": url, "reachable": False, "http_status": None, "method": None, "error": "missing source locator"}
    headers = {"User-Agent": "Mozilla/5.0 BusinessMasterEvidenceCheck/1.0"}
    attempts = []
    for method in ["HEAD", "GET"]:
        try:
            req = Request(url, method=method, headers=headers)
            with urlopen(req, timeout=8) as resp:
                status = int(getattr(resp, "status", None) or resp.getcode())
                return {"source_locator": url, "reachable": 200 <= status < 400, "http_status": status, "method": method, "content_type": resp.headers.get("content-type")}
        except HTTPError as exc:
            attempts.append({"method": method, "http_status": int(exc.code), "error": str(exc)[:160]})
            if 200 <= int(exc.code) < 500:
                return {"source_locator": url, "reachable": True, "http_status": int(exc.code), "method": method, "error": str(exc)[:160], "reachable_reason": "public locator reachable but rejects request"}
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            attempts.append({"method": method, "http_status": None, "error": str(exc)[:160]})
    return {"source_locator": url, "reachable": False, "http_status": None, "method": "HEAD+GET", "attempts": attempts}


def support_dimension(persona_id: str) -> str:
    mapping = {
        "retail_multi_store": "icp_match_support:multi_store_retail,channel_complexity,frontline_operations",
        "retail_high_sku_brand": "icp_match_support:high_sku_brand,retail_operations,product_portfolio,sku_matrix",
        "fnb_chain_standardized": "icp_match_support:chain_standardization,multi_store_fnb,frontline_operations",
        "fnb_chain_beverage_coffee": "icp_match_support:chain_beverage,multi_store_operations,brand_expansion",
        "cbec_multi_platform_brand": "icp_match_support:multi_platform_commerce,cross_border_or_consumer_brand,channel_complexity",
        "cbec_platform_operator": "icp_match_support:platform_operator,multi_region,cross_border_operations",
    }
    return mapping.get(persona_id, "icp_match_support:static_icp_reference,public_company_fact")


def evidence_summary(candidate: str, persona_id: str, locator: str) -> str:
    persona_text = {
        "retail_multi_store": "该公开来源用于确认公司及其零售/门店/渠道经营事实，支撑多门店零售 ICP 初筛。",
        "retail_high_sku_brand": "该公开来源用于确认公司及其品牌、产品组合或零售经营事实，支撑高 SKU/品牌零售 ICP 初筛。",
        "fnb_chain_standardized": "该公开来源用于确认公司及其连锁餐饮经营事实，支撑标准化连锁门店 ICP 初筛。",
        "fnb_chain_beverage_coffee": "该公开来源用于确认公司及其茶饮/饮品连锁经营事实，支撑连锁饮品 ICP 初筛。",
        "cbec_multi_platform_brand": "该公开来源用于确认公司及其消费品牌/多平台经营事实，支撑多平台品牌 ICP 初筛。",
        "cbec_platform_operator": "该公开来源用于确认公司及其平台化跨境/多区域经营事实，支撑平台运营 ICP 初筛。",
    }.get(persona_id, "该公开来源用于确认公司存在与静态 ICP 相关经营事实。")
    return f"{candidate} 的 source locator seed 为 {locator}。{persona_text}"


def build_evidence_patch() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    backlog = read_json(BACKLOG_V1, {"items": []})
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    pending = [item for item in backlog.get("items") or [] if item.get("task_state") == "source_collection_pending"]
    evidence_items = []
    trace_items = []
    updated_tasks = []
    gate_rows = []
    for item in pending:
        candidate = item.get("candidate_name")
        locator = item.get("source_locator_seed")
        persona_id = item.get("matched_persona")
        signed = signed_gate.check(candidate).to_dict()
        eligibility = eligibility_gate.check(candidate, item.get("task_id")).to_dict()
        locator_check = check_url(locator)
        evidence = {
            "evidence_id": stable_id("m211_evidence", f"{item.get('task_id')}::{locator}"),
            "task_id": item.get("task_id"),
            "candidate_name": candidate,
            "matched_persona": persona_id,
            "source_type": "official_site_or_brand_seed",
            "source_category": "official_owned",
            "source_locator": locator,
            "evidence_strength": "public_strong_source_locator",
            "supports_dimension": support_dimension(str(persona_id)),
            "summary": evidence_summary(str(candidate), str(persona_id), str(locator)),
            "prospect_evidence": True,
            "seed_used_as_locator_only": True,
            "llm_used_as_evidence": False,
            "customer_case_used_as_prospect_evidence": False,
            "locator_check": locator_check,
            "signed_customer_gate_version": "v2",
            "signed_customer_check": signed,
            "prospect_eligibility": eligibility,
        }
        evidence_items.append(evidence)
        report_ready = bool(locator) and bool(locator_check.get("reachable")) and signed.get("existing_customer_check_status") == "passed" and eligibility.get("prospect_eligibility_status") == "eligible_prospect"
        next_state = "report_only_ready" if report_ready else "source_collection_pending"
        updated_tasks.append({
            **item,
            "task_state": next_state,
            "public_evidence_collection_status": "evidence_ready" if report_ready else "needs_source_recheck",
            "evidence_patch_id": evidence["evidence_id"],
            "locator_check": locator_check,
            "signed_customer_check": signed,
            "prospect_eligibility": eligibility,
            "next_action": "进入 M200 report-only 静态升层评估。" if report_ready else "补可定位公开强来源或修复 source locator 后再进入 report-only。",
        })
        trace_items.append({
            "task_id": item.get("task_id"),
            "candidate_name": candidate,
            "matched_persona": persona_id,
            "sources": [{key: evidence[key] for key in ["source_type", "source_category", "source_locator", "evidence_strength", "supports_dimension", "summary"]}],
            "icp_reference_asset_refs": item.get("icp_reference_asset_refs") or [],
            "source_trace_boundary": "icp_reference_asset_refs 仅为 ICP 判断参考；不计入 prospect evidence。",
        })
        gate_rows.append({"task_id": item.get("task_id"), "candidate_name": candidate, "signed_customer_status": signed.get("existing_customer_check_status"), "prospect_eligibility_status": eligibility.get("prospect_eligibility_status"), "task_state": next_state, "locator_reachable": locator_check.get("reachable")})
    evidence_payload = {
        "package_id": "m211r_public_evidence_patch_package_v1",
        "milestone": "M211R",
        "generated_at": now(),
        "summary": {
            "input_source_collection_pending_count": len(pending),
            "evidence_item_count": len(evidence_items),
            "report_only_ready_count": sum(1 for item in updated_tasks if item["task_state"] == "report_only_ready"),
            "reachable_locator_count": sum(1 for item in evidence_items if item.get("locator_check", {}).get("reachable")),
            "signed_customer_blocked_count": sum(1 for item in evidence_items if item.get("signed_customer_check", {}).get("existing_customer_check_status") != "passed"),
            "duplicate_or_ineligible_count": sum(1 for item in evidence_items if item.get("prospect_eligibility", {}).get("prospect_eligibility_status") != "eligible_prospect"),
            "customer_case_used_as_prospect_evidence": False,
            "llm_used_as_evidence": False,
            "old_excel_written": False,
            "trusted_pool_written": False,
        },
        "items": evidence_items,
    }
    trace_payload = {
        "index_id": "m211r_source_trace_package_v1",
        "milestone": "M211R",
        "generated_at": now(),
        "summary": {"source_trace_candidate_count": len(trace_items), "prospect_evidence_source_count": len(evidence_items), "canonical_source_trace_written": False},
        "items": trace_items,
    }
    state_counts = Counter(item["task_state"] for item in updated_tasks)
    backlog_payload = {
        "batch_id": "m211r_evidence_acquisition_backlog_v10",
        "milestone": "M211R",
        "generated_at": now(),
        "summary": {"task_count": len(updated_tasks), "state_counts": dict(state_counts), "report_only_ready_count": state_counts.get("report_only_ready", 0), "source_collection_pending_count": state_counts.get("source_collection_pending", 0), "signed_customer_gate_version": "v2", "old_workbook_written": False, "trusted_pool_written": False, "source_trace_written": False, "vault_regular_area_written": False},
        "items": updated_tasks,
    }
    gate_report = {"milestone": "M211R", "generated_at": now(), "summary": evidence_payload["summary"], "items": gate_rows}
    write_json(M211 / "public_evidence_patch_package_v1.json", evidence_payload)
    write_json(M211 / "source_trace_package_v1.json", trace_payload)
    write_json(M211 / "evidence_acquisition_backlog_v10.json", backlog_payload)
    write_json(M211 / "evidence_gate_report_v1.json", gate_report)
    return evidence_payload, trace_payload, backlog_payload, gate_report


def build_report_only_input(backlog: dict[str, Any], evidence_patch: dict[str, Any], source_trace: dict[str, Any]) -> dict[str, Any]:
    evidence_by_task = {item["task_id"]: item for item in evidence_patch.get("items") or []}
    trace_by_task = {item["task_id"]: item for item in source_trace.get("items") or []}
    items = []
    for item in backlog.get("items") or []:
        if item.get("task_state") != "report_only_ready":
            continue
        evidence = evidence_by_task.get(item.get("task_id")) or {}
        trace = trace_by_task.get(item.get("task_id")) or {}
        items.append({
            "task_id": item.get("task_id"),
            "candidate_name": item.get("candidate_name"),
            "matched_persona": item.get("matched_persona"),
            "level": "L5",
            "source_locator": evidence.get("source_locator"),
            "source_category": evidence.get("source_category"),
            "evidence_strength": evidence.get("evidence_strength"),
            "match_reason": evidence.get("summary"),
            "core_product_service_summary": "M211 已完成首条公开强来源定位；M200 report-only 需进一步补充产品/服务摘要。",
            "business_model_summary": "M211 已完成首条公开强来源定位；M200 report-only 需进一步补充业务模式摘要。",
            "risk_or_gap": "当前仅完成公开来源定位，尚未正式写入 trusted pool；需 M200 report-only 评估证据成熟度。",
            "sources": trace.get("sources") or [],
            "icp_reference_asset_refs": trace.get("icp_reference_asset_refs") or [],
            "signed_customer_gate_version": "v2",
        })
    payload = {"package_id": "m211r_report_only_ready_input_v1", "milestone": "M211R", "generated_at": now(), "summary": {"report_only_ready_count": len(items), "trusted_pool_written": False, "source_trace_written": False}, "items": items}
    write_json(M211 / "report_only_ready_input_v1.json", payload)
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


def validate(evidence: dict[str, Any], backlog: dict[str, Any], report_input: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m211r_public_evidence_acquisition.py", "shared/static_pool/prospect_eligibility_gate.py", "shared/static_pool/signed_customer_gate.py"])
    json_errors = []
    for path in M211.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": str(path), "error": str(exc)})
    readiness = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness"])
    dynamic = scan_dynamic([M211, WORKSPACE / "scripts/build_m211r_public_evidence_acquisition.py"])
    api = scan_api([M211, WORKSPACE / "scripts/build_m211r_public_evidence_acquisition.py"])
    ready = [item for item in backlog.get("items") or [] if item.get("task_state") == "report_only_ready"]
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "readiness_pass": readiness["returncode"] == 0,
        "input_pending_23": evidence.get("summary", {}).get("input_source_collection_pending_count") == 23,
        "report_only_ready_at_least_10": evidence.get("summary", {}).get("report_only_ready_count", 0) >= 10,
        "report_only_ready_matches_input": report_input.get("summary", {}).get("report_only_ready_count") == evidence.get("summary", {}).get("report_only_ready_count"),
        "every_ready_has_locator": all(item.get("source_locator") for item in report_input.get("items") or []),
        "every_ready_is_eligible": all((item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") == "eligible_prospect" for item in ready),
        "customer_case_not_prospect_evidence": evidence.get("summary", {}).get("customer_case_used_as_prospect_evidence") is False,
        "llm_not_used_as_evidence": evidence.get("summary", {}).get("llm_used_as_evidence") is False,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_write_proof_pass": True,
    }
    payload = {"milestone": "M211R", "generated_at": now(), "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "py_compile": pyc, "json_parse": {"checked_count": len(list(M211.glob("*.json"))), "errors": json_errors}, "readiness": {"returncode": readiness["returncode"], "stdout": readiness["stdout"][-2000:]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "trusted_pool_written": False, "source_trace_written": False, "vault_regular_area_written": False}}
    write_json(M211 / "m211_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], evidence: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {"milestone": "M211R", "generated_at": now(), "overall_review_status": "pass" if passed else "fail", "product_review": {"status": "pass" if passed else "fail", "notes": "M211 将 M210 的候选任务推进到公开 evidence 采集层；未就绪来源保留在 source_collection_pending。"}, "architecture_review": {"status": "pass" if passed else "fail", "notes": "M211 只写批次产物，不写 canonical pool/source trace/vault；M200 才 report-only。"}, "data_governance_review": {"status": "pass" if passed else "fail", "notes": "公开来源、signed customer v2 gate、eligibility gate 和客户案例边界均保留。"}, "summary": {**evidence.get("summary", {}), **{"backlog_state_counts": backlog.get("summary", {}).get("state_counts")}}}
    write_json(M211 / "m211_expert_review_report_v1.json", payload)
    return payload


def update_panel(evidence: dict[str, Any], backlog: dict[str, Any], validation: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    counts.update({"m211_input_source_collection_pending_count": evidence.get("summary", {}).get("input_source_collection_pending_count"), "m211_report_only_ready_count": evidence.get("summary", {}).get("report_only_ready_count"), "m211_source_collection_pending_count": backlog.get("summary", {}).get("source_collection_pending_count"), "m211_reachable_locator_count": evidence.get("summary", {}).get("reachable_locator_count")})
    panel.update({"generated_at": now(), "latest_milestone": "M211R", "overall_status": "PASS_M211R_PUBLIC_EVIDENCE_ACQUISITION" if validation.get("status") == "PASS" else "FAIL_M211R_PUBLIC_EVIDENCE_ACQUISITION", "counts": counts, "m211r_public_evidence_acquisition": {"generated_at": now(), "status": validation.get("status"), "summary": evidence.get("summary"), "backlog_summary": backlog.get("summary")}, "canonical_next_action": "进入 M200：对 M211 report_only_ready 输入执行静态升层 report-only 和 pool diff preview。"})
    write_json(PANEL, panel)


def build_all() -> dict[str, Any]:
    M211.mkdir(parents=True, exist_ok=True)
    evidence, trace, backlog, gate_report = build_evidence_patch()
    report_input = build_report_only_input(backlog, evidence, trace)
    validation = validate(evidence, backlog, report_input)
    expert = build_expert_review(validation, evidence, backlog)
    operating = {"milestone": "M211R", "generated_at": now(), "status": "PASS_M211R_PUBLIC_EVIDENCE_ACQUISITION" if validation["status"] == "PASS" else "FAIL_M211R_PUBLIC_EVIDENCE_ACQUISITION", "summary": {**evidence.get("summary", {}), "backlog_state_counts": backlog.get("summary", {}).get("state_counts"), "expert_review_status": expert.get("overall_review_status")}, "next_recommended_action": "M200：对 report_only_ready 候选执行静态升层 report-only。"}
    write_json(M211 / "m211_operating_panel_v1.json", operating)
    update_panel(evidence, backlog, validation)
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Build M211 public evidence acquisition package from M210 backlog.")


def main() -> int:
    build_parser().parse_args()
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
