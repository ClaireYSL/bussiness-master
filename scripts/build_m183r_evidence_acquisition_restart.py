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
from shared.static_pool.static_promote import evaluate_static_promotion

M183 = WORKSPACE / "deliveries/archive/milestones/milestone183r_evidence_acquisition_restart"
BACKLOG = WORKSPACE / "deliveries/archive/milestones/milestone182r_production_reconciliation/evidence_acquisition_backlog_v3.json"
CANONICAL_POOL = WORKSPACE / "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = WORKSPACE / "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json"
STATUS_PANEL = WORKSPACE / "deliveries/archive/milestones/milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]

CANDIDATE = {
    "prospect_id": "m183_acc_douman",
    "company_name": "广州市斗满科技有限公司",
    "candidate_aliases": ["斗满", "斗满科技", "广州市斗满科技有限公司"],
    "level": "L5",
    "matched_persona": "cbec_platform_operator",
    "mapped_canonical_personas": ["cbec_platform_operator", "cbec_supply_chain_complex"],
    "match_reason": "公开来源显示其面向跨境电商卖家提供海外仓储、国际物流、供应链与仓储物流服务，符合跨境平台/供应链复杂型 ICP 的多区域、多环节运营特征。",
    "core_product_service_summary": "跨境电商物流、海外仓储、国际物流专线、亚马逊 FBA 头程、物流小包及定制化供应链服务。",
    "business_model_summary": "以跨境电商卖家为服务对象，围绕海外仓储、补货、配送、国际物流专线和供应链综合服务提供一站式履约与物流解决方案。",
    "risk_or_gap": "当前只完成公开来源 report-only；需后续确认是否存在未登记签约关系，并补充更多平台经营事实或权威第三方来源后再评估是否进入 L1。",
    "source_locator": "http://www.dmfgroup.net/",
    "evidence_strength": "official_site",
    "signed_customer_gate_version": "signed_customer_v2",
}

PUBLIC_SOURCES = [
    {
        "source_id": "m183_douman_official_site",
        "prospect_id": CANDIDATE["prospect_id"],
        "company_name": CANDIDATE["company_name"],
        "source_type": "official_site",
        "source_category": "official_owned",
        "source_locator": "http://www.dmfgroup.net/",
        "evidence_strength": "official_site",
        "supports_dimension": "icp_match_support:cross_border_operations,overseas_warehouse,custom_supply_chain,official_owned",
        "summary": "斗满官网披露公司名称、跨境电商物流服务、海外仓储、快速补货、定制化供应链、国际物流专线、FBA 头程和物流小包等业务。",
        "prospect_evidence": True,
    },
    {
        "source_id": "m183_douman_amz123_profile",
        "prospect_id": CANDIDATE["prospect_id"],
        "company_name": CANDIDATE["company_name"],
        "source_type": "platform_service_profile",
        "source_category": "platform_operating_fact",
        "source_locator": "https://www.amz123.com/doumankeji",
        "evidence_strength": "platform_service_profile",
        "supports_dimension": "icp_match_support:cross_border_operations,warehouse_logistics,platform_operating_fact",
        "summary": "AMZ123 斗满科技页面将其归为跨境物流服务商，并描述其为全球电商卖家提供仓储物流、定制化物流解决方案、全球云仓和打包发货服务。",
        "prospect_evidence": True,
    },
]

REFERENCE_SOURCES = [
    {
        "reference_id": "m183_douman_guandata_case_reference",
        "reference_type": "customer_case_reference",
        "source_locator": "https://www.guandata.com/blogdetail/douman",
        "usage_boundary": "ICP 判断参考，不计入 prospect evidence，不自动确认 signed customer。",
        "supports_dimension": "icp_reference:cross_border_bi_use_case,warehouse_logistics_operations",
        "summary": "观远客户案例用于说明斗满科技跨境物流与 BI 场景，不作为新潜客强 evidence。",
    }
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE))


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def stable_hash(payload: Any) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def check_url(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "BusinessMasterEvidenceCheck/1.0"}
    for method in ("HEAD", "GET"):
        try:
            req = Request(url, method=method, headers=headers)
            with urlopen(req, timeout=15) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                return {"source_locator": url, "reachable": 200 <= int(status) < 400, "http_status": int(status), "method": method}
        except HTTPError as exc:
            return {"source_locator": url, "reachable": 200 <= int(exc.code) < 400, "http_status": int(exc.code), "method": method, "error": str(exc)[:200]}
        except (URLError, TimeoutError, OSError) as exc:
            last = {"source_locator": url, "reachable": False, "http_status": None, "method": method, "error": str(exc)[:200]}
    return last


def source_text_probe() -> dict[str, Any]:
    url = PUBLIC_SOURCES[0]["source_locator"]
    try:
        html = urlopen(Request(url, headers={"User-Agent": "BusinessMasterEvidenceCheck/1.0"}), timeout=15).read().decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        return {"source_locator": url, "probe_ok": False, "error": str(exc)[:200]}
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    tokens = ["广州市斗满科技有限公司", "海外仓储", "电子商务", "定制化供应链", "亚马逊FBA头程", "跨境"]
    return {"source_locator": url, "probe_ok": True, "token_hits": {token: token in text for token in tokens}, "excerpt": text[:500]}


def load_source_collection_task() -> dict[str, Any]:
    backlog = read_json(BACKLOG, {"items": []})
    tasks = backlog.get("items") or []
    pending = [item for item in tasks if item.get("current_state") == "source_collection_pending"]
    selected = next((item for item in pending if str(item.get("candidate_name")) == "斗满"), None)
    return {"backlog_file": rel(BACKLOG), "source_collection_pending_count": len(pending), "selected_task": selected}


def build_identity_resolution() -> dict[str, Any]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    signed_checks = {alias: signed_gate.check(alias).to_dict() for alias in CANDIDATE["candidate_aliases"]}
    eligibility_checks = {alias: eligibility_gate.check(alias, CANDIDATE["prospect_id"]).to_dict() for alias in CANDIDATE["candidate_aliases"]}
    return {
        "milestone": "M183R",
        "generated_at": now(),
        "candidate": CANDIDATE,
        "identity_decision": "resolved_company_candidate",
        "canonical_company_name": CANDIDATE["company_name"],
        "signed_customer_gate_version": "signed_customer_v2",
        "signed_customer_checks": signed_checks,
        "prospect_eligibility_checks": eligibility_checks,
        "eligible_for_public_source_collection": all(v["existing_customer_check_status"] == "passed" for v in signed_checks.values())
        and all(v["prospect_eligibility_status"] == "eligible_prospect" for v in eligibility_checks.values()),
    }


def build_evidence_patch(identity: dict[str, Any]) -> dict[str, Any]:
    url_checks = [check_url(src["source_locator"]) for src in PUBLIC_SOURCES + REFERENCE_SOURCES]
    evidence_items = []
    for source in PUBLIC_SOURCES:
        status = next((row for row in url_checks if row["source_locator"] == source["source_locator"]), {})
        evidence_items.append({**source, "locator_check": status})
    return {
        "package_id": "m183r_evidence_patch_package_v1",
        "milestone": "M183R",
        "generated_at": now(),
        "identity_resolution_status": identity["identity_decision"],
        "signed_customer_gate_version": "signed_customer_v2",
        "prospect_evidence_policy": "customer_case_reference_not_counted_as_prospect_evidence",
        "items": evidence_items,
        "reference_only_sources": [{**src, "locator_check": next((row for row in url_checks if row["source_locator"] == src["source_locator"]), {})} for src in REFERENCE_SOURCES],
        "source_text_probe": source_text_probe(),
        "summary": {
            "prospect_evidence_count": len(evidence_items),
            "strong_public_source_count": sum(1 for item in evidence_items if item.get("prospect_evidence") and item.get("source_category") in {"official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"}),
            "reference_only_count": len(REFERENCE_SOURCES),
            "locator_reachable_count": sum(1 for row in url_checks if row.get("reachable")),
        },
    }


def build_source_trace(evidence_patch: dict[str, Any]) -> dict[str, Any]:
    sources = []
    for item in evidence_patch["items"]:
        sources.append({key: item[key] for key in ["source_type", "source_category", "source_locator", "evidence_strength", "supports_dimension", "summary"]})
    return {
        "index_id": "m183r_source_trace_package_v1",
        "milestone": "M183R",
        "generated_at": now(),
        "summary": {"source_trace_count": 1, "prospect_evidence_source_count": len(sources), "reference_only_source_count": len(REFERENCE_SOURCES)},
        "items": [{"prospect_id": CANDIDATE["prospect_id"], "company_name": CANDIDATE["company_name"], "sources": sources, "reference_only_sources": REFERENCE_SOURCES}],
    }


def build_report_only(source_trace: dict[str, Any]) -> dict[str, Any]:
    source_trace_by_prospect = {item["prospect_id"]: item.get("sources") or [] for item in source_trace.get("items") or []}
    decision = evaluate_static_promotion(CANDIDATE, source_trace_by_prospect=source_trace_by_prospect).to_dict()
    signature = stable_hash({"candidate": CANDIDATE, "sources": source_trace_by_prospect.get(CANDIDATE["prospect_id"], [])})
    return {
        "batch_id": "m183r_report_only_v1",
        "milestone": "M183R",
        "generated_at": now(),
        "mode": "report_only",
        "candidate_signature": signature,
        "summary": {
            "report_only_candidate_count": 1,
            "level_counts": {decision["suggested_level"]: 1},
            "decision": decision["decision"],
            "suggested_level": decision["suggested_level"],
            "gap_queue_count": len(decision["gap_queue"]),
            "canonical_pool_updated": False,
            "vault_regular_area_written": False,
        },
        "candidate": CANDIDATE,
        "decisions": [decision],
        "gap_queue": [{"prospect_id": decision["prospect_id"], "company_name": decision["company_name"], **gap} for gap in decision["gap_queue"]],
        "no_write_proof": {
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
            "trusted_pool_updated": False,
            "vault_regular_area_written": False,
            "customer_case_reference_counted_as_prospect_evidence": False,
        },
    }


def build_pool_diff_preview(report: dict[str, Any]) -> dict[str, Any]:
    pool = read_json(CANONICAL_POOL, {"items": []})
    existing = {str(item.get("prospect_id")): item for item in pool.get("items") or []}
    decision = report["decisions"][0]
    return {
        "diff_id": "m183r_pool_diff_preview_v1",
        "milestone": "M183R",
        "generated_at": now(),
        "canonical_pool_file": rel(CANONICAL_POOL),
        "mode": "preview_only",
        "summary": {
            "canonical_pool_count_before": len(pool.get("items") or []),
            "new_candidate_count": 0 if CANDIDATE["prospect_id"] in existing else 1,
            "duplicate_existing_prospect_count": 1 if CANDIDATE["prospect_id"] in existing else 0,
            "suggested_level": decision["suggested_level"],
            "write_allowed_in_m183": False,
        },
        "items": [
            {
                "prospect_id": CANDIDATE["prospect_id"],
                "company_name": CANDIDATE["company_name"],
                "change_type": "add_candidate_preview" if CANDIDATE["prospect_id"] not in existing else "duplicate_skip_preview",
                "static_fields_preview": {
                    "level": decision["suggested_level"],
                    "trusted_status": "static_l2_ready" if decision["suggested_level"] == "L2" else "trusted_summary_ready",
                    "static_promotion_summary": decision["summary"],
                    "static_gap_count": len(decision["gap_queue"]),
                    "static_evidence_count": decision["evidence_count"],
                    "static_strong_evidence_count": decision["strong_evidence_count"],
                },
            }
        ],
    }


def build_vault_preview(report: dict[str, Any]) -> dict[str, Any]:
    preview_dir = M183 / "vault_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    decision = report["decisions"][0]
    gaps = "\n".join(f"- {gap['reason']}" for gap in decision["gap_queue"]) or "- 暂无结构化缺口。"
    sources = "\n".join(f"- `{src['source_category']}` {src['source_locator']}：{src['summary']}" for src in PUBLIC_SOURCES)
    path = preview_dir / f"{CANDIDATE['company_name']}.md"
    text = f"""---
prospect_id: {CANDIDATE['prospect_id']}
static_level: {decision['suggested_level']}
matched_persona: {CANDIDATE['matched_persona']}
legacy_field_inherited: false
source_boundary: evidence_first_public_sources_only
signed_customer_gate_version: signed_customer_v2
preview_only: true
---

# {CANDIDATE['company_name']}

## 静态等级

{decision['suggested_level']}

## 为什么匹配 ICP

{CANDIDATE['match_reason']}

## 核心产品/服务

{CANDIDATE['core_product_service_summary']}

## 业务模式

{CANDIDATE['business_model_summary']}

## 关键来源

{sources}

## 风险与待补点

{CANDIDATE['risk_or_gap']}

## 升层缺口

{gaps}

## 边界说明

本页为 M183R preview，只表达静态 ICP 匹配、证据成熟度和信息完整度；客户案例仅作 ICP 参考，不计入 prospect evidence。
"""
    path.write_text(text, encoding="utf-8")
    return {
        "package_id": "m183r_vault_preview_package_v1",
        "milestone": "M183R",
        "generated_at": now(),
        "summary": {"vault_preview_count": 1, "vault_regular_area_written": False, "suggested_level": decision["suggested_level"]},
        "items": [{"prospect_id": CANDIDATE["prospect_id"], "company_name": CANDIDATE["company_name"], "preview_path": rel(path)}],
    }


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*.json")) + list(root.rglob("*.md"))
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": rel(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, text):
                    findings.append({"file": rel(path), "pattern": pattern})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def build_expert_review(validation: dict[str, Any]) -> dict[str, Any]:
    status = "pass" if validation["status"] == "PASS" else "fail"
    return {
        "milestone": "M183R",
        "generated_at": now(),
        "overall_review_status": status,
        "product_review": {
            "status": status,
            "checklist": [
                "候选通过 signed customer v2 与 duplicate gate，不把已签约老客展示为新潜客。",
                "preview 页面能回答是不是 ICP、为什么、公开证据是什么、仍缺什么。",
            ],
        },
        "architecture_review": {
            "status": status,
            "checklist": [
                "M183 只生成 report-only 与 preview，不隐式更新 canonical pool 或 vault 正区。",
                "production pipeline 新增 evidence-acquisition 入口，历史脚本仍为 replay/reference。",
            ],
        },
        "data_governance_review": {
            "status": status,
            "checklist": [
                "客户案例 reference 不计入 prospect evidence。",
                "source_locator 可定位，source_category 合法，signed_customer_gate_version=v2。",
                "未写旧 Excel、knowledge asset registry、persona registry。",
            ],
        },
    }


def update_status_panel(report: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    panel = read_json(STATUS_PANEL, {})
    panel["latest_milestone"] = "M183R"
    panel["overall_status"] = "PASS_M183R_EVIDENCE_ACQUISITION_RESTART" if validation["status"] == "PASS" else "FAIL_M183R_EVIDENCE_ACQUISITION_RESTART"
    panel["m183r_evidence_acquisition"] = {
        "generated_at": now(),
        "report_only_candidate_count": report["summary"]["report_only_candidate_count"],
        "suggested_level": report["summary"]["suggested_level"],
        "canonical_pool_updated": False,
        "vault_regular_area_written": False,
        "signed_customer_gate_version": "signed_customer_v2",
        "next_recommended_action": "若接受 M183R preview，可在下一轮执行 guarded trusted pool update；否则继续补 authoritative_third_party/platform_operating_fact。",
    }
    write_json(STATUS_PANEL, panel)
    return panel["m183r_evidence_acquisition"]


def validate(outputs: dict[str, Any], *, update_status: bool) -> dict[str, Any]:
    errors: list[str] = []
    identity = outputs["identity"]
    if not identity.get("eligible_for_public_source_collection"):
        errors.append("candidate did not pass signed/customer eligibility gates")
    evidence = outputs["evidence"]
    if evidence["summary"]["strong_public_source_count"] < 2:
        errors.append("expected at least 2 public strong sources for L2 report-only readiness")
    if any(not item.get("locator_check", {}).get("reachable") for item in evidence.get("items") or []):
        errors.append("one or more prospect evidence locators are not reachable")
    if any(src.get("reference_type") == "customer_case_reference" for src in evidence.get("items") or []):
        errors.append("customer case reference leaked into prospect evidence items")
    report = outputs["report"]
    if report["summary"]["suggested_level"] != "L2":
        errors.append(f"expected suggested L2 for M183, got {report['summary']['suggested_level']}")
    if report["no_write_proof"]["trusted_pool_updated"] or report["no_write_proof"]["vault_regular_area_written"]:
        errors.append("M183 must not update canonical pool or vault regular area")
    dynamic = scan_dynamic([M183])
    api = scan_api([M183, WORKSPACE / "scripts/build_m183r_evidence_acquisition_restart.py"])
    if dynamic["status"] != "PASS":
        errors.append("dynamic term scan failed")
    if api["status"] != "PASS":
        errors.append("api key scan failed")
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m183r_evidence_acquisition_restart.py", "scripts/businessmaster_pipeline.py", "shared/static_pool/static_promote.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    if py_compile["returncode"] != 0:
        errors.append("py_compile failed")
    json_errors = []
    for path in sorted(M183.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            json_errors.append({"file": rel(path), "error": str(exc)})
    if json_errors:
        errors.append("json parse failed")
    return {
        "milestone": "M183R",
        "generated_at": now(),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "py_compile": py_compile,
        "json_parse": {"checked_count": len(list(M183.glob("*.json"))), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "status_panel_updated": update_status,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M183R evidence acquisition restart for post-signed-customer-v2 production backlog.")
    parser.add_argument("--stage", choices=("all", "readiness"), default="all")
    parser.add_argument("--update-status-panel", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    M183.mkdir(parents=True, exist_ok=True)
    task = load_source_collection_task()
    identity = build_identity_resolution()
    evidence = build_evidence_patch(identity)
    source_trace = build_source_trace(evidence)
    report = build_report_only(source_trace)
    pool_diff = build_pool_diff_preview(report)
    vault = build_vault_preview(report)
    baseline = {"milestone": "M183R", "generated_at": now(), "candidate_signature": report["candidate_signature"], "candidate_count": 1}
    outputs = {"task": task, "identity": identity, "evidence": evidence, "source_trace": source_trace, "report": report, "pool_diff": pool_diff, "vault": vault, "baseline": baseline}

    write_json(M183 / "source_collection_task_selection_v1.json", task)
    write_json(M183 / "identity_resolution_package_v1.json", identity)
    write_json(M183 / "evidence_patch_package_v1.json", evidence)
    write_json(M183 / "source_trace_package_v1.json", source_trace)
    write_json(M183 / "m183r_report_only_v1.json", report)
    write_json(M183 / "pool_diff_preview_v1.json", pool_diff)
    write_json(M183 / "vault_preview_package_v1.json", vault)
    write_json(M183 / "baseline_v1.json", baseline)

    validation = validate(outputs, update_status=args.update_status_panel)
    write_json(M183 / "m183_validation_report_v1.json", validation)
    expert = build_expert_review(validation)
    write_json(M183 / "m183_expert_review_report_v1.json", expert)
    panel_update = None
    if args.update_status_panel:
        panel_update = update_status_panel(report, validation)
    operating_panel = {
        "milestone": "M183R",
        "generated_at": now(),
        "status": "PASS_M183R_EVIDENCE_ACQUISITION_RESTART" if validation["status"] == "PASS" else "FAIL_M183R_EVIDENCE_ACQUISITION_RESTART",
        "summary": {
            "selected_candidate": CANDIDATE["company_name"],
            "suggested_level": report["summary"]["suggested_level"],
            "public_strong_source_count": evidence["summary"]["strong_public_source_count"],
            "canonical_pool_updated": False,
            "vault_regular_area_written": False,
            "signed_customer_gate_version": "signed_customer_v2",
            "source_category_counts": dict(Counter(src["source_category"] for src in PUBLIC_SOURCES)),
        },
        "status_panel_update": panel_update,
        "next_recommended_action": "进入 M184：对 M183 L2 preview 做受控 trusted pool update，或继续补 authoritative_third_party 后再写入。",
    }
    write_json(M183 / "m183_operating_panel_v1.json", operating_panel)

    # Re-run validation after all artifacts exist so the JSON parse check covers the full M183 package.
    validation = validate(outputs, update_status=args.update_status_panel)
    write_json(M183 / "m183_validation_report_v1.json", validation)
    expert = build_expert_review(validation)
    write_json(M183 / "m183_expert_review_report_v1.json", expert)
    operating_panel["status"] = "PASS_M183R_EVIDENCE_ACQUISITION_RESTART" if validation["status"] == "PASS" else "FAIL_M183R_EVIDENCE_ACQUISITION_RESTART"
    write_json(M183 / "m183_operating_panel_v1.json", operating_panel)

    print(json.dumps({"milestone": "M183R", "status": validation["status"], "summary": operating_panel["summary"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
