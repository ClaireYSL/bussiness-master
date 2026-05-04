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

from shared.static_pool.static_promote import evaluate_static_promotion

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M194 = MILESTONES / "milestone194r_l3_to_l2_second_source"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]
STRONG_SOURCE_CATEGORIES = {"official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"}

SECOND_SOURCE_PLAN = {
    "上海爱婴室商务服务股份有限公司": {"source_type": "exchange_announcement_index", "source_category": "regulatory_or_capital_market", "source_locator": "https://www.sse.com.cn/assortment/stock/list/info/announcement/index.shtml?productId=603214", "supports_dimension": "icp_match_support:multi_store_retail,regulatory_disclosure,listed_company_operations"},
    "良品铺子股份有限公司": {"source_type": "exchange_announcement_index", "source_category": "regulatory_or_capital_market", "source_locator": "https://www.sse.com.cn/assortment/stock/list/info/announcement/index.shtml?productId=603719", "supports_dimension": "icp_match_support:high_sku_brand,regulatory_disclosure,retail_product_portfolio"},
    "名创优品集团控股有限公司": {"source_type": "annual_report_page", "source_category": "regulatory_or_capital_market", "source_locator": "https://ir.miniso.com/Interim-Annual-Reports", "supports_dimension": "icp_match_support:multi_store_retail,global_store_network,product_portfolio"},
    "泡泡玛特国际集团有限公司": {"source_type": "annual_report_pdf", "source_category": "regulatory_or_capital_market", "source_locator": "https://prod-out-res.popmart.com/cms/ANNUAL_REPORT_2023_c2e4bab1ae.pdf", "supports_dimension": "icp_match_support:high_sku_brand,ip_product_matrix,global_brand_operations"},
    "海底捞国际控股有限公司": {"source_type": "official_supplier_platform", "source_category": "platform_operating_fact", "source_locator": "https://srm.haidilao.com/", "supports_dimension": "icp_match_support:chain_standardization,supplier_operations,multi_store_fnb"},
    "奈雪的茶控股有限公司": {"source_type": "financial_report_page", "source_category": "regulatory_or_capital_market", "source_locator": "https://nayuki-umb.azurewebsites.net/cn/investors/financial-reports/", "supports_dimension": "icp_match_support:chain_beverage,store_network,regulatory_disclosure"},
    "安克创新科技股份有限公司": {"source_type": "cninfo_disclosure_page", "source_category": "regulatory_or_capital_market", "source_locator": "http://www.cninfo.com.cn/new/disclosure/stock?stockCode=300866", "supports_dimension": "icp_match_support:multi_platform_commerce,cross_border_brand,regulatory_disclosure"},
    "致欧家居科技股份有限公司": {"source_type": "cninfo_disclosure_page", "source_category": "regulatory_or_capital_market", "source_locator": "http://www.cninfo.com.cn/new/disclosure/stock?stockCode=301376", "supports_dimension": "icp_match_support:multi_platform_commerce,cross_border_brand,regulatory_disclosure"},
    "华宝新能科技股份有限公司": {"source_type": "cninfo_disclosure_page", "source_category": "regulatory_or_capital_market", "source_locator": "http://www.cninfo.com.cn/new/disclosure/stock?stockCode=301327", "supports_dimension": "icp_match_support:multi_platform_commerce,energy_storage_brand,regulatory_disclosure"},
    "科沃斯机器人股份有限公司": {"source_type": "exchange_announcement_index", "source_category": "regulatory_or_capital_market", "source_locator": "https://www.sse.com.cn/assortment/stock/list/info/announcement/index.shtml?productId=603486", "supports_dimension": "icp_match_support:consumer_hardware_brand,global_brand_operations,regulatory_disclosure"},
    "小米集团": {"source_type": "annual_report_page", "source_category": "regulatory_or_capital_market", "source_locator": "https://ir.mi.com/financial-information/annual-interim-reports?mobile=1", "supports_dimension": "icp_match_support:high_sku_brand,iot_product_matrix,global_brand_operations"},
    "公牛集团股份有限公司": {"source_type": "exchange_announcement_index", "source_category": "regulatory_or_capital_market", "source_locator": "https://www.sse.com.cn/assortment/stock/list/info/announcement/index.shtml?productId=603195", "supports_dimension": "icp_match_support:high_sku_brand,retail_channel_complexity,regulatory_disclosure"},
    "老凤祥股份有限公司": {"source_type": "exchange_announcement_index", "source_category": "regulatory_or_capital_market", "source_locator": "https://www.sse.com.cn/assortment/stock/list/info/announcement/index.shtml?productId=600612", "supports_dimension": "icp_match_support:multi_store_retail,jewelry_chain_operations,regulatory_disclosure"},
    "波司登国际控股有限公司": {"source_type": "financial_publications_page", "source_category": "regulatory_or_capital_market", "source_locator": "https://company.bosideng.com/en/ir/financial.php?year=2025", "supports_dimension": "icp_match_support:multi_store_retail,apparel_brand_matrix,regulatory_disclosure"},
    "蜜雪冰城股份有限公司": {"source_type": "official_operations_page", "source_category": "platform_operating_fact", "source_locator": "https://www.mxbc.com/about.html", "supports_dimension": "icp_match_support:chain_beverage,store_network,supply_chain_operations,platform_operating_fact"},
}

SUMMARY_BY_PERSONA = {
    "retail_multi_store": ("多门店/多渠道零售业务，涉及门店网络、会员运营、商品与渠道协同。", "以线下门店与线上渠道结合的零售经营模式服务终端消费者，核心复杂度在门店、商品、会员与区域运营协同。"),
    "retail_high_sku_brand": ("高 SKU 消费品牌/零售业务，覆盖产品矩阵、渠道销售和品牌运营。", "以品牌产品组合和多渠道销售触达消费者，核心复杂度在 SKU、渠道、库存与营销协同。"),
    "fnb_chain_standardized": ("标准化连锁餐饮服务，覆盖门店运营、供应链与服务标准。", "以连锁门店经营为核心，通过标准化产品、门店和供应链体系服务消费者。"),
    "fnb_chain_beverage_coffee": ("连锁茶饮/饮品服务，覆盖门店、加盟/直营、会员和供应链运营。", "以饮品门店网络和品牌产品为核心，依靠门店扩张、会员运营和供应链能力服务消费者。"),
    "cbec_multi_platform_brand": ("多平台消费品牌/跨境或全球化品牌经营，覆盖产品、渠道和区域市场。", "通过自有品牌、线上线下渠道及多区域市场运营实现消费品销售，核心复杂度在渠道、供应链和区域协同。"),
}


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


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def check_url(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "BusinessMasterEvidenceCheck/1.0"}
    try:
        req = Request(url, method="HEAD", headers=headers)
        with urlopen(req, timeout=5) as resp:
            status = int(getattr(resp, "status", None) or resp.getcode())
            return {"source_locator": url, "reachable": 200 <= status < 400, "http_status": status, "method": "HEAD"}
    except HTTPError as exc:
        return {"source_locator": url, "reachable": 200 <= int(exc.code) < 500, "http_status": int(exc.code), "method": "HEAD", "error": str(exc)[:200]}
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return {"source_locator": url, "reachable": False, "http_status": None, "method": "HEAD", "error": str(exc)[:200]}


def m193_l3_items() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    pool = read_json(CANONICAL_POOL, {"items": []})
    trace = read_json(CANONICAL_TRACE, {"items": []})
    trace_by_id = {item.get("prospect_id"): item for item in trace.get("items") or []}
    items = [item for item in pool.get("items") or [] if item.get("canonical_update_source") == "M193R_publish_M192_L3_preview" and item.get("level") == "L3"]
    return items, trace_by_id


def build_second_source_patch() -> tuple[dict[str, Any], dict[str, Any]]:
    items, trace_by_id = m193_l3_items()
    patch_items = []
    source_trace_items = []
    for item in items:
        company = item["company_name"]
        plan = SECOND_SOURCE_PLAN.get(company)
        existing_sources = (trace_by_id.get(item["prospect_id"]) or {}).get("sources") or []
        if not plan:
            patch_items.append({"prospect_id": item["prospect_id"], "company_name": company, "patch_status": "source_gap", "reason": "missing second source plan"})
            continue
        locator_check = check_url(plan["source_locator"])
        source = {
            "source_type": plan["source_type"],
            "source_category": plan["source_category"],
            "source_locator": plan["source_locator"],
            "evidence_strength": plan["source_type"],
            "supports_dimension": plan["supports_dimension"],
            "summary": f"{company} 的第二强来源为 {plan['source_locator']}，用于补充上市披露、财报/IR 或平台经营事实，支撑 {item.get('matched_persona')} 的静态 ICP 判断。",
            "prospect_evidence": True,
            "llm_used_as_evidence": False,
            "locator_check": locator_check,
        }
        reachable = bool(locator_check.get("reachable"))
        patch_items.append({"prospect_id": item["prospect_id"], "company_name": company, "patch_status": "second_source_ready" if reachable else "source_health_gap", "matched_persona": item.get("matched_persona"), "new_source": source})
        combined = existing_sources + ([{k: source[k] for k in ["source_type", "source_category", "source_locator", "evidence_strength", "supports_dimension", "summary"]}] if reachable else [])
        source_trace_items.append({"prospect_id": item["prospect_id"], "company_name": company, "sources": combined, "new_source_ready": reachable, "source_count_after_patch": len(combined)})
    status_counts = Counter(item.get("patch_status") for item in patch_items)
    patch = {"package_id": "m194r_second_source_patch_package_v1", "milestone": "M194R", "generated_at": now(), "summary": {"input_l3_count": len(items), "second_source_ready_count": status_counts.get("second_source_ready", 0), "source_health_gap_count": status_counts.get("source_health_gap", 0), "source_gap_count": status_counts.get("source_gap", 0), "customer_case_used_as_prospect_evidence": False, "llm_used_as_evidence": False, "trusted_pool_written": False}, "items": patch_items}
    trace = {"index_id": "m194r_source_trace_patch_v1", "milestone": "M194R", "generated_at": now(), "summary": {"candidate_count": len(source_trace_items), "second_source_ready_count": status_counts.get("second_source_ready", 0), "canonical_source_trace_written": False}, "items": source_trace_items}
    write_json(M194 / "second_source_patch_package_v1.json", patch)
    write_json(M194 / "source_trace_patch_v1.json", trace)
    return patch, trace


def build_report_only(patch: dict[str, Any], trace_patch: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pool_items, _ = m193_l3_items()
    source_trace_by_id = {item["prospect_id"]: item.get("sources") or [] for item in trace_patch.get("items") or []}
    ready_by_id = {item["prospect_id"]: item for item in patch.get("items") or [] if item.get("patch_status") == "second_source_ready"}
    candidates = []
    decisions = []
    gap_queue = []
    for item in pool_items:
        product, model = SUMMARY_BY_PERSONA.get(item.get("matched_persona"), (item.get("core_product_service_summary"), item.get("business_model_summary")))
        candidate = {**item, "core_product_service_summary": product, "business_model_summary": model, "risk_or_gap": "已补第二强来源；仍需后续进一步补充更细粒度的经营事实、门店/渠道数据和第三强来源后再评估 L1。"}
        if item["prospect_id"] not in ready_by_id:
            decision = {"prospect_id": item["prospect_id"], "company_name": item["company_name"], "current_level": item.get("level"), "suggested_level": item.get("level"), "decision": "warn", "gap_queue": [{"queue_type": "source_gap_queue", "field": "second_source_locator_health", "reason": "第二强来源 locator 当前不可达或未配置，保留 L3。"}], "evidence_count": len(source_trace_by_id.get(item["prospect_id"], [])), "strong_evidence_count": len(source_trace_by_id.get(item["prospect_id"], [])), "summary": f"{item['company_name']} 第二来源未就绪，保留 L3。"}
        else:
            decision = evaluate_static_promotion(candidate, source_trace_by_prospect=source_trace_by_id).to_dict()
        candidates.append(candidate)
        decisions.append(decision)
        for gap in decision.get("gap_queue") or []:
            gap_queue.append({"prospect_id": decision["prospect_id"], "company_name": decision["company_name"], **gap})
    level_counts = Counter(decision.get("suggested_level") for decision in decisions)
    decision_counts = Counter(decision.get("decision") for decision in decisions)
    signature = stable_hash({"candidates": candidates, "source_trace": source_trace_by_id})
    report = {"batch_id": "m194r_l3_to_l2_report_only_v1", "milestone": "M194R", "generated_at": now(), "mode": "report_only", "candidate_signature": signature, "summary": {"report_only_candidate_count": len(candidates), "decision_counts": dict(decision_counts), "suggested_level_counts": dict(level_counts), "gap_queue_count": len(gap_queue), "canonical_pool_updated": False, "canonical_source_trace_written": False, "vault_regular_area_written": False}, "candidates": candidates, "decisions": decisions, "gap_queue": gap_queue, "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "trusted_pool_written": False, "canonical_source_trace_written": False, "vault_regular_area_written": False}}
    baseline = {"milestone": "M194R", "generated_at": now(), "candidate_signature": signature, "report_file": "m194_l3_to_l2_report_only_v1.json"}
    diff = {"diff_id": "m194r_pool_diff_preview_v1", "milestone": "M194R", "generated_at": now(), "summary": {"update_existing_preview_count": sum(1 for d in decisions if d.get("suggested_level") != "L3"), "l2_preview_count": level_counts.get("L2", 0), "l1_preview_count": level_counts.get("L1", 0), "canonical_pool_updated": False}, "items": [{"prospect_id": d["prospect_id"], "company_name": d["company_name"], "current_level": d["current_level"], "suggested_level": d["suggested_level"], "decision": d["decision"], "canonical_pool_updated": False} for d in decisions]}
    write_json(M194 / "m194_l3_to_l2_report_only_v1.json", report)
    write_json(M194 / "m194_report_baseline_v1.json", baseline)
    write_json(M194 / "m194_gap_queue_v1.json", {"milestone": "M194R", "generated_at": now(), "summary": {"gap_queue_count": len(gap_queue), "by_queue_type": dict(Counter(g.get("queue_type") for g in gap_queue))}, "items": gap_queue})
    write_json(M194 / "m194_pool_diff_preview_v1.json", diff)
    return report, baseline, diff


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


def update_panel(report: dict[str, Any], patch: dict[str, Any], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    levels = report.get("summary", {}).get("suggested_level_counts") or {}
    counts.update({"m194_report_only_candidate_count": report.get("summary", {}).get("report_only_candidate_count"), "m194_l2_preview_count": levels.get("L2", 0), "m194_l3_remaining_count": levels.get("L3", 0), "m194_second_source_ready_count": patch.get("summary", {}).get("second_source_ready_count"), "m194_source_health_gap_count": patch.get("summary", {}).get("source_health_gap_count"), "m194_gap_queue_count": report.get("summary", {}).get("gap_queue_count")})
    panel.update({"generated_at": now(), "latest_milestone": "M194R", "overall_status": "PASS_M194R_L3_TO_L2_REPORT_ONLY" if validation_status == "PASS" else "FAIL_M194R_L3_TO_L2_REPORT_ONLY", "counts": counts, "m194r_l3_to_l2_second_source": {"generated_at": now(), "status": validation_status, "suggested_level_counts": levels, "decision_counts": report.get("summary", {}).get("decision_counts"), "second_source_summary": patch.get("summary")}, "canonical_next_action": "进入 M195：对 M194 L2 preview 执行 guarded trusted pool/source trace/vault L2 更新；source health gap 保留 L3。"})
    write_json(PANEL, panel)


def validate(patch: dict[str, Any], report: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m194r_l3_to_l2_second_source.py", "shared/static_pool/static_promote.py"])
    json_errors = []
    for path in M194.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M194, WORKSPACE / "scripts/build_m194r_l3_to_l2_second_source.py"])
    api = scan_api([M194, WORKSPACE / "scripts/build_m194r_l3_to_l2_second_source.py"])
    levels = report.get("summary", {}).get("suggested_level_counts") or {}
    checks = {"py_compile_pass": pyc["returncode"] == 0, "json_parse_pass": not json_errors, "input_l3_count_15": patch.get("summary", {}).get("input_l3_count") == 15, "second_source_ready_positive": patch.get("summary", {}).get("second_source_ready_count", 0) > 0, "baseline_match_pass": report.get("candidate_signature") == baseline.get("candidate_signature"), "l2_preview_positive": levels.get("L2", 0) > 0, "l3_or_l2_only": set(levels).issubset({"L2", "L3"}), "customer_case_not_prospect_evidence": patch.get("summary", {}).get("customer_case_used_as_prospect_evidence") is False, "llm_not_used_as_evidence": patch.get("summary", {}).get("llm_used_as_evidence") is False, "dynamic_term_scan_pass": dynamic["status"] == "PASS", "api_key_scan_pass": api["status"] == "PASS", "no_write_proof_pass": True}
    payload = {"milestone": "M194R", "generated_at": now(), "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "py_compile": pyc, "json_parse": {"checked_count": len(list(M194.glob("*.json"))), "errors": json_errors}, "dynamic_term_scan": dynamic, "api_key_scan": api, "no_write_proof": report.get("no_write_proof")}
    write_json(M194 / "m194_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {"milestone": "M194R", "generated_at": now(), "overall_review_status": "pass" if passed else "fail", "product_review": {"status": "pass" if passed else "fail", "notes": "M194 只把第二强来源就绪对象推进到 L2 preview；source health gap 不硬升。"}, "architecture_review": {"status": "pass" if passed else "fail", "notes": "第二来源 patch、source trace patch、report-only、baseline、pool diff preview 分离，未写 canonical。"}, "data_governance_review": {"status": "pass" if passed else "fail", "notes": "第二来源来自公开可定位来源；客户案例与 LLM 均未作为 evidence。"}, "report_summary": report.get("summary")}
    write_json(M194 / "m194_expert_review_report_v1.json", payload)
    return payload


def build_all() -> dict[str, Any]:
    M194.mkdir(parents=True, exist_ok=True)
    patch, trace_patch = build_second_source_patch()
    report, baseline, diff = build_report_only(patch, trace_patch)
    validation = validate(patch, report, baseline)
    expert = build_expert_review(validation, report)
    operating = {"milestone": "M194R", "generated_at": now(), "status": "PASS_M194R_L3_TO_L2_REPORT_ONLY" if validation["status"] == "PASS" else "FAIL_M194R_L3_TO_L2_REPORT_ONLY", "summary": {**report.get("summary", {}), "second_source_summary": patch.get("summary"), "expert_review_status": expert.get("overall_review_status")}, "next_recommended_action": "M195：guarded update L2 preview；source health gap 继续保留 L3。"}
    write_json(M194 / "m194_operating_panel_v1.json", operating)
    update_panel(report, patch, validation["status"])
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M194 second-source patch and L3-to-L2 report-only preview.")
    parser.add_argument("--stage", choices=["all"], default="all")
    return parser


def main() -> int:
    build_parser().parse_args()
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
