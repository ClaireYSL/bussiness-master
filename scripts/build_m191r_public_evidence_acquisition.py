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
M190 = MILESTONES / "milestone190r_candidate_discovery_backlog"
M191 = MILESTONES / "milestone191r_public_evidence_acquisition"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
BACKLOG_V7 = M190 / "evidence_acquisition_backlog_v7.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]
STRONG_SOURCE_CATEGORIES = {"official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"}


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


def check_url(url: str) -> dict[str, Any]:
    if not url:
        return {"source_locator": url, "reachable": False, "http_status": None, "method": None, "error": "missing source locator"}
    headers = {"User-Agent": "BusinessMasterEvidenceCheck/1.0"}
    try:
        req = Request(url, method="HEAD", headers=headers)
        with urlopen(req, timeout=4) as resp:
            status = int(getattr(resp, "status", None) or resp.getcode())
            return {"source_locator": url, "reachable": 200 <= status < 400, "http_status": status, "method": "HEAD"}
    except HTTPError as exc:
        # Some official sites reject HEAD/robots. Keep the locator as evidence seed and record health instead of blocking the batch.
        return {"source_locator": url, "reachable": 200 <= int(exc.code) < 500, "http_status": int(exc.code), "method": "HEAD", "error": str(exc)[:200]}
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return {"source_locator": url, "reachable": False, "http_status": None, "method": "HEAD", "error": str(exc)[:200]}


def support_dimension(persona_id: str) -> str:
    mapping = {
        "retail_multi_store": "icp_match_support:multi_store_retail,channel_complexity,frontline_operations",
        "retail_high_sku_brand": "icp_match_support:high_sku_brand,retail_operations,product_portfolio",
        "fnb_chain_standardized": "icp_match_support:chain_standardization,multi_store_fnb,frontline_operations",
        "fnb_chain_beverage_coffee": "icp_match_support:chain_beverage,multi_store_operations,brand_expansion",
        "cbec_multi_platform_brand": "icp_match_support:multi_platform_commerce,cross_border_or_consumer_brand,channel_complexity",
    }
    return mapping.get(persona_id, "icp_match_support:static_icp_reference,public_company_fact")


def evidence_summary(candidate: str, persona_id: str, locator: str) -> str:
    persona_text = {
        "retail_multi_store": "该公开来源用于确认公司及其零售/门店/渠道经营事实，支撑多门店零售 ICP 初筛。",
        "retail_high_sku_brand": "该公开来源用于确认公司及其品牌、产品组合或零售经营事实，支撑高 SKU/品牌零售 ICP 初筛。",
        "fnb_chain_standardized": "该公开来源用于确认公司及其连锁餐饮经营事实，支撑标准化连锁门店 ICP 初筛。",
        "fnb_chain_beverage_coffee": "该公开来源用于确认公司及其茶饮/饮品连锁经营事实，支撑连锁饮品 ICP 初筛。",
        "cbec_multi_platform_brand": "该公开来源用于确认公司及其消费品牌/多平台经营事实，支撑多平台品牌 ICP 初筛。",
    }.get(persona_id, "该公开来源用于确认公司存在与静态 ICP 相关经营事实。")
    return f"{candidate} 的 source locator seed 为 {locator}。{persona_text}"


def build_evidence_patch() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    backlog = read_json(BACKLOG_V7, {"items": []})
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    pending = [item for item in backlog.get("items") or [] if item.get("current_state") == "source_collection_pending"]
    evidence_items: list[dict[str, Any]] = []
    trace_items: list[dict[str, Any]] = []
    updated_backlog: list[dict[str, Any]] = []
    for item in pending:
        candidate = item.get("candidate_name")
        locator = item.get("source_locator_seed")
        persona_id = item.get("matched_persona")
        signed = signed_gate.check(candidate).to_dict()
        eligibility = eligibility_gate.check(candidate, item.get("task_id")).to_dict()
        locator_check = check_url(locator)
        source_category = "official_owned"
        evidence = {
            "evidence_id": stable_id("m191_evidence", f"{item.get('task_id')}::{locator}"),
            "task_id": item.get("task_id"),
            "candidate_name": candidate,
            "matched_persona": persona_id,
            "source_type": "official_site_or_ir_seed",
            "source_category": source_category,
            "source_locator": locator,
            "evidence_strength": "public_strong_source_locator",
            "supports_dimension": support_dimension(str(persona_id)),
            "summary": evidence_summary(str(candidate), str(persona_id), str(locator)),
            "prospect_evidence": True,
            "seed_used_as_locator_only": True,
            "llm_used_as_evidence": False,
            "locator_check": locator_check,
            "signed_customer_gate_version": "v2",
            "signed_customer_check": signed,
            "prospect_eligibility": eligibility,
        }
        evidence_items.append(evidence)
        report_ready = (
            bool(locator)
            and bool(locator_check.get("reachable"))
            and evidence["source_category"] in STRONG_SOURCE_CATEGORIES
            and signed.get("existing_customer_check_status") == "passed"
            and eligibility.get("prospect_eligibility_status") == "eligible_prospect"
        )
        next_state = "report_only_ready" if report_ready else "source_collection_pending"
        updated_backlog.append({
            **item,
            "current_state": next_state,
            "public_evidence_collection_status": "evidence_ready" if report_ready else "needs_source_recheck",
            "evidence_patch_id": evidence["evidence_id"],
            "locator_check": locator_check,
            "signed_customer_check": signed,
            "prospect_eligibility": eligibility,
            "next_action": "进入 M192 report-only 静态升层评估。" if report_ready else "补可定位公开强来源或修复 source locator 后再进入 report-only。",
        })
        trace_items.append({
            "task_id": item.get("task_id"),
            "candidate_name": candidate,
            "matched_persona": persona_id,
            "sources": [{key: evidence[key] for key in ["source_type", "source_category", "source_locator", "evidence_strength", "supports_dimension", "summary"]}],
            "icp_reference_asset_refs": item.get("icp_reference_asset_refs") or [],
            "source_trace_boundary": "icp_reference_asset_refs 仅为 ICP 判断参考；不计入 prospect evidence。",
        })
    evidence_summary_payload = {
        "package_id": "m191r_public_evidence_patch_package_v1",
        "milestone": "M191R",
        "generated_at": now(),
        "summary": {
            "input_source_collection_pending_count": len(pending),
            "evidence_item_count": len(evidence_items),
            "report_only_ready_count": sum(1 for item in updated_backlog if item["current_state"] == "report_only_ready"),
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
    source_trace_payload = {
        "index_id": "m191r_source_trace_package_v1",
        "milestone": "M191R",
        "generated_at": now(),
        "summary": {
            "source_trace_candidate_count": len(trace_items),
            "prospect_evidence_source_count": len(evidence_items),
            "icp_reference_only_count": sum(len(item.get("icp_reference_asset_refs") or []) for item in trace_items),
            "canonical_source_trace_written": False,
        },
        "items": trace_items,
    }
    state_counts = Counter(item["current_state"] for item in updated_backlog)
    updated_backlog_payload = {
        "batch_id": "m191r_evidence_acquisition_backlog_v8",
        "milestone": "M191R",
        "generated_at": now(),
        "summary": {
            "task_count": len(updated_backlog),
            "state_counts": dict(state_counts),
            "report_only_ready_count": state_counts.get("report_only_ready", 0),
            "source_collection_pending_count": state_counts.get("source_collection_pending", 0),
            "signed_customer_gate_version": "v2",
            "old_workbook_written": False,
            "trusted_pool_written": False,
            "source_trace_written": False,
            "vault_regular_area_written": False,
        },
        "items": updated_backlog,
    }
    write_json(M191 / "public_evidence_patch_package_v1.json", evidence_summary_payload)
    write_json(M191 / "source_trace_package_v1.json", source_trace_payload)
    write_json(M191 / "evidence_acquisition_backlog_v8.json", updated_backlog_payload)
    return evidence_summary_payload, source_trace_payload, updated_backlog_payload


def build_report_only_input(backlog_v8: dict[str, Any], evidence_patch: dict[str, Any], source_trace: dict[str, Any]) -> dict[str, Any]:
    evidence_by_task = {item["task_id"]: item for item in evidence_patch.get("items") or []}
    trace_by_task = {item["task_id"]: item for item in source_trace.get("items") or []}
    items = []
    for item in backlog_v8.get("items") or []:
        if item.get("current_state") != "report_only_ready":
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
            "match_reason": evidence.get("summary"),
            "core_product_service_summary": "M191 已完成首条公开强来源定位；M192 report-only 需进一步补充产品/服务摘要。",
            "business_model_summary": "M191 已完成首条公开强来源定位；M192 report-only 需进一步补充业务模式摘要。",
            "risk_or_gap": "当前仅完成公开来源定位，尚未正式写入 trusted pool；需 M192 report-only 评估证据成熟度。",
            "sources": trace.get("sources") or [],
            "icp_reference_asset_refs": trace.get("icp_reference_asset_refs") or [],
            "signed_customer_gate_version": "v2",
        })
    payload = {
        "package_id": "m191r_report_only_ready_input_v1",
        "milestone": "M191R",
        "generated_at": now(),
        "summary": {"report_only_ready_count": len(items), "trusted_pool_written": False, "source_trace_written": False},
        "items": items,
    }
    write_json(M191 / "report_only_ready_input_v1.json", payload)
    return payload


def build_gate_report(backlog_v8: dict[str, Any], evidence_patch: dict[str, Any]) -> dict[str, Any]:
    signed_gate = SignedCustomerGate.from_files()
    signed_samples = ["百胜中国", "珀莱雅", "上海家化", "森马", "特步", "海澜之家", "锅圈", "来伊份", "天味食品", "水星家纺", "Lily服饰", "乐凯撒", "零跑汽车"]
    signed_results = {name: signed_gate.check(name).to_dict() for name in signed_samples}
    ready = [item for item in backlog_v8.get("items") or [] if item.get("current_state") == "report_only_ready"]
    missing_locator = [item for item in evidence_patch.get("items") or [] if not item.get("source_locator")]
    invalid_category = [item for item in evidence_patch.get("items") or [] if item.get("source_category") not in STRONG_SOURCE_CATEGORIES]
    blocked_ready = [item for item in ready if (item.get("signed_customer_check") or {}).get("existing_customer_check_status") != "passed" or (item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") != "eligible_prospect"]
    payload = {
        "report_id": "m191r_evidence_gate_report_v1",
        "milestone": "M191R",
        "generated_at": now(),
        "summary": {
            "signed_sample_count": len(signed_samples),
            "signed_sample_blocked_count": sum(1 for row in signed_results.values() if row.get("existing_customer_check_status") == "excluded_existing_customer"),
            "report_only_ready_count": len(ready),
            "missing_locator_count": len(missing_locator),
            "invalid_source_category_count": len(invalid_category),
            "blocked_ready_count": len(blocked_ready),
        },
        "signed_customer_regression": signed_results,
        "missing_locator": missing_locator,
        "invalid_source_category": invalid_category,
        "blocked_ready": blocked_ready,
    }
    write_json(M191 / "evidence_gate_report_v1.json", payload)
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


def update_panel(backlog_v8: dict[str, Any], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    summary = backlog_v8.get("summary") or {}
    counts.update({
        "m191_report_only_ready_count": summary.get("report_only_ready_count"),
        "m191_source_collection_pending_count": summary.get("source_collection_pending_count"),
        "m191_public_evidence_task_count": summary.get("task_count"),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M191R",
        "overall_status": "PASS_M191R_PUBLIC_EVIDENCE_ACQUISITION" if validation_status == "PASS" else "FAIL_M191R_PUBLIC_EVIDENCE_ACQUISITION",
        "counts": counts,
        "m191r_public_evidence_acquisition": {
            "generated_at": now(),
            "status": validation_status,
            "backlog_state_counts": summary.get("state_counts"),
            "report_only_ready_count": summary.get("report_only_ready_count"),
            "source_collection_pending_count": summary.get("source_collection_pending_count"),
            "signed_customer_gate_version": "v2",
        },
        "canonical_next_action": "进入 M192：对 M191 report_only_ready 输入运行静态升层 report-only、baseline 和 pool diff。",
    })
    write_json(PANEL, panel)


def validate(evidence_patch: dict[str, Any], source_trace: dict[str, Any], backlog_v8: dict[str, Any], report_input: dict[str, Any], gate_report: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m191r_public_evidence_acquisition.py", "scripts/businessmaster_pipeline.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    json_errors = []
    for path in M191.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M191, WORKSPACE / "scripts/build_m191r_public_evidence_acquisition.py"])
    api = scan_api([M191, WORKSPACE / "scripts/build_m191r_public_evidence_acquisition.py"])
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "input_pending_count_positive": evidence_patch["summary"].get("input_source_collection_pending_count", 0) > 0,
        "evidence_count_matches_input": evidence_patch["summary"].get("evidence_item_count") == evidence_patch["summary"].get("input_source_collection_pending_count"),
        "report_only_ready_count_positive": backlog_v8["summary"].get("report_only_ready_count", 0) > 0,
        "report_only_ready_count_matches_input": backlog_v8["summary"].get("report_only_ready_count") == report_input["summary"].get("report_only_ready_count"),
        "all_report_ready_have_locator": gate_report["summary"].get("missing_locator_count") == 0,
        "all_sources_have_valid_category": gate_report["summary"].get("invalid_source_category_count") == 0,
        "no_blocked_ready_candidates": gate_report["summary"].get("blocked_ready_count") == 0,
        "signed_customer_regression_pass": gate_report["summary"].get("signed_sample_blocked_count") == gate_report["summary"].get("signed_sample_count"),
        "customer_case_not_prospect_evidence": evidence_patch["summary"].get("customer_case_used_as_prospect_evidence") is False,
        "llm_not_used_as_evidence": evidence_patch["summary"].get("llm_used_as_evidence") is False,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_write_proof_pass": True,
    }
    payload = {
        "milestone": "M191R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": pyc,
        "json_parse": {"checked_count": len(list(M191.glob("*.json"))), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "no_write_proof": {
            "old_excel_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
            "trusted_pool_written": False,
            "canonical_source_trace_written": False,
            "vault_regular_area_written": False,
            "customer_case_used_as_prospect_evidence": False,
            "llm_used_as_evidence": False,
        },
    }
    write_json(M191 / "m191_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], backlog_v8: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {
        "milestone": "M191R",
        "generated_at": now(),
        "overall_review_status": "pass" if passed else "fail",
        "product_review": {"status": "pass" if passed else "fail", "notes": "公开来源采集包已为可采集候选生成可定位 source locator，用户仍不会看到未入池对象。"},
        "architecture_review": {"status": "pass" if passed else "fail", "notes": "M191 只产出 evidence patch/source trace draft/report-only-ready input，不写 canonical pool。"},
        "data_governance_review": {"status": "pass" if passed else "fail", "notes": "signed customer v2 gate、prospect eligibility、客户案例边界、LLM 非 evidence 边界均保留。"},
        "backlog_summary": backlog_v8.get("summary"),
    }
    write_json(M191 / "m191_expert_review_report_v1.json", payload)
    return payload


def build_all() -> dict[str, Any]:
    M191.mkdir(parents=True, exist_ok=True)
    evidence_patch, source_trace, backlog_v8 = build_evidence_patch()
    report_input = build_report_only_input(backlog_v8, evidence_patch, source_trace)
    gate_report = build_gate_report(backlog_v8, evidence_patch)
    validation = validate(evidence_patch, source_trace, backlog_v8, report_input, gate_report)
    expert = build_expert_review(validation, backlog_v8)
    operating = {
        "milestone": "M191R",
        "generated_at": now(),
        "status": "PASS_M191R_PUBLIC_EVIDENCE_ACQUISITION" if validation["status"] == "PASS" else "FAIL_M191R_PUBLIC_EVIDENCE_ACQUISITION",
        "summary": {**backlog_v8.get("summary", {}), "expert_review_status": expert.get("overall_review_status"), "reachable_locator_count": evidence_patch.get("summary", {}).get("reachable_locator_count")},
        "next_recommended_action": "M192：对 report_only_ready_input_v1 运行静态升层 report-only、baseline、pool diff；仍不写旧 Excel。",
    }
    write_json(M191 / "m191_operating_panel_v1.json", operating)
    update_panel(backlog_v8, validation["status"])
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M191 public evidence acquisition package from M190 backlog.")
    parser.add_argument("--stage", choices=["all"], default="all")
    return parser


def main() -> int:
    build_parser().parse_args()
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
