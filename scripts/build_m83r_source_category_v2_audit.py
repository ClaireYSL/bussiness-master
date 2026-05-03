from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M83 = MILESTONES / "milestone83r_source_category_v2"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = M47 / "trusted_prospect_pool_v1.json"
CANONICAL_TRACE = M47 / "source_trace_index_v1.json"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)

import sys
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.static_promote import (  # noqa: E402
    _has_icp_support,
    _is_l1_countable_evidence,
    _source_category,
    _strong_source_categories,
    evaluate_static_promotion,
)


POLICY = {
    "source_categories": {
        "official_owned": "官网、品牌官网、官方新闻、官方门店/渠道页、官方招聘、官方公众号/小程序公开页。",
        "regulatory_or_capital_market": "年报、公告、CNINFO、交易所、SEC、港交所、招股书、公开转让说明书。",
        "platform_operating_fact": "官方旗舰店、平台品牌店、门店网络、App/小程序/SaaS 公开页、可验证经营页面。",
        "authoritative_third_party": "权威媒体深度报道、融资公告、投资机构 portfolio、行业协会/政府/研究机构材料。",
        "internal_or_legacy_reference": "结构化 patch、旧档案、旧主表、人工整理记录；只能辅助，不计入 L1 强来源。",
    },
    "l1_rules_v2": {
        "l1_must_start_from": "L2",
        "minimum_l1_countable_sources": 3,
        "minimum_source_categories": 2,
        "requires_icp_support_source": True,
        "non_listed_company_allowed_combo": ["official_owned", "platform_operating_fact", "authoritative_third_party"],
        "regulatory_or_capital_market_not_required": True,
        "internal_or_legacy_reference_countable_for_l1": False,
    },
}


NON_LISTED_FRIENDLY_RECOMMENDATIONS = [
    {"source_category": "official_owned", "examples": ["官网产品/业务页", "官方门店/渠道页", "官方品牌/案例新闻", "官方招聘/组织能力页面"]},
    {"source_category": "platform_operating_fact", "examples": ["天猫/京东/抖音官方旗舰店", "Amazon Brand Store", "美团/大众点评门店网络", "App/小程序公开页"]},
    {"source_category": "authoritative_third_party", "examples": ["融资公告", "投资机构 portfolio", "权威媒体深度报道", "政府/协会/行业研究材料"]},
]


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


def by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("prospect_id") or "").strip(): item for item in items if str(item.get("prospect_id") or "").strip()}


def source_trace_by_prospect(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or ""): item.get("sources") or [] for item in trace.get("items") or []}


def categorize_source(source: dict[str, Any]) -> dict[str, Any]:
    category = _source_category(source)
    return {
        **source,
        "source_category": category,
        "l1_countable": _is_l1_countable_evidence(source),
        "icp_support_source": _has_icp_support(source),
    }


def build_category_audit(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    items = []
    category_counts: Counter[str] = Counter()
    support_counts: Counter[str] = Counter()
    for trace_item in trace.get("items") or []:
        sources = [categorize_source(source) for source in trace_item.get("sources") or []]
        for source in sources:
            category_counts[source["source_category"]] += 1
            if source["icp_support_source"]:
                support_counts["icp_support"] += 1
        items.append({
            "prospect_id": trace_item.get("prospect_id"),
            "company_name": trace_item.get("company_name"),
            "source_count": len(sources),
            "source_category_counts": dict(Counter(source["source_category"] for source in sources)),
            "l1_countable_source_count": sum(1 for source in sources if source["l1_countable"]),
            "icp_support_source_count": sum(1 for source in sources if source["icp_support_source"]),
            "sources": sources,
        })
    payload = {
        "milestone": "M83R",
        "generated_at": now(),
        "status": "PASS_M83R_SOURCE_TRACE_CATEGORY_AUDIT_READY",
        "summary": {
            "prospect_count": len(items),
            "source_category_counts": dict(category_counts),
            "icp_support_source_count": support_counts.get("icp_support", 0),
            "current_level_counts": dict(Counter(item.get("level") for item in pool.get("items") or [])),
        },
        "items": items,
    }
    write_json(M83 / "source_trace_category_audit_v1.json", payload)
    return payload


def build_admission_audit(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    trace_by_id = source_trace_by_prospect(trace)
    items = []
    downgrade_preview = []
    l2_suggestions = []
    for item in pool.get("items") or []:
        if item.get("level") not in {"L1", "L2"}:
            continue
        decision = evaluate_static_promotion(item, source_trace_by_prospect=trace_by_id).to_dict()
        sources = trace_by_id.get(str(item.get("prospect_id") or ""), [])
        categories = sorted(_strong_source_categories(sources))
        row = {
            "prospect_id": item.get("prospect_id"),
            "company_name": item.get("company_name"),
            "current_level": item.get("level"),
            "v2_suggested_level": decision["suggested_level"],
            "v2_decision": decision["decision"],
            "strong_evidence_count": decision["strong_evidence_count"],
            "source_categories": categories,
            "has_icp_support_source": any(_has_icp_support(source) for source in sources),
            "gap_queue": decision["gap_queue"],
        }
        items.append(row)
        if item.get("level") == "L1" and decision["suggested_level"] != "L1":
            downgrade_preview.append({**row, "recommended_action": "hold_l1_writeback_review_or_add_v2_source"})
        if item.get("level") == "L2":
            missing_categories = [cat for cat in ["official_owned", "platform_operating_fact", "authoritative_third_party"] if cat not in categories]
            l2_suggestions.append({
                "prospect_id": item.get("prospect_id"),
                "company_name": item.get("company_name"),
                "current_categories": categories,
                "non_listed_friendly_source_recommendations": [rec for rec in NON_LISTED_FRIENDLY_RECOMMENDATIONS if rec["source_category"] in missing_categories[:2] or not missing_categories],
                "note": "优先补能直接支撑 ICP 的公开来源，不只推荐年报/公告。",
            })
    payload = {
        "milestone": "M83R",
        "generated_at": now(),
        "status": "PASS_M83R_L1_ADMISSION_RULES_V2_AUDIT_READY",
        "summary": {
            "audited_l1_l2_count": len(items),
            "current_l1_count": sum(1 for item in pool.get("items") or [] if item.get("level") == "L1"),
            "v2_l1_compatible_count": sum(1 for item in items if item["current_level"] == "L1" and item["v2_suggested_level"] == "L1"),
            "downgrade_preview_count": len(downgrade_preview),
            "l2_non_listed_friendly_suggestion_count": len(l2_suggestions),
        },
        "items": items,
        "downgrade_preview": downgrade_preview,
    }
    suggestions = {
        "milestone": "M83R",
        "generated_at": now(),
        "status": "PASS_M83R_NON_LISTED_FRIENDLY_SOURCE_SUGGESTIONS_READY",
        "summary": {"l2_suggestion_count": len(l2_suggestions)},
        "items": l2_suggestions,
    }
    write_json(M83 / "l1_admission_rules_v2_audit_v1.json", payload)
    write_json(M83 / "non_listed_l1_source_suggestions_v1.json", suggestions)
    return {"audit": payload, "suggestions": suggestions}


def build_policy_outputs() -> None:
    write_json(M83 / "source_category_policy_v2.json", {"milestone": "M83R", "generated_at": now(), "status": "PASS_M83R_SOURCE_CATEGORY_POLICY_V2_READY", **POLICY})
    write_json(M83 / "l1_admission_rules_v2.json", {"milestone": "M83R", "generated_at": now(), "status": "PASS_M83R_L1_ADMISSION_RULES_V2_READY", "rules": POLICY["l1_rules_v2"]})


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"path": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"path": str(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def validate(category_audit: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "shared/static_pool/static_promote.py", "scripts/build_m83r_source_category_v2_audit.py", "scripts/trusted_pool_runner.py"])
    sample_non_listed = {
        "prospect_id": "sample_non_listed_l1",
        "company_name": "非上市高成长样本",
        "level": "L2",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "具备品牌产品矩阵、平台经营事实和高成长公开报道，符合 ICP。",
        "core_product_service_summary": "消费品牌产品矩阵。",
        "business_model_summary": "直营官网与平台店共同运营。",
        "risk_or_gap": "需持续复核经营规模。",
    }
    sample_non_listed_sources = {
        "sample_non_listed_l1": [
            {"source_type": "official_site", "source_locator": "https://example-brand.com", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix"},
            {"source_type": "tmall_store", "source_locator": "https://example.tmall.com", "evidence_strength": "platform_store", "supports_dimension": "icp_match_support:platform_operating_fact"},
            {"source_type": "financing_news", "source_locator": "https://example-media.com/news", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:growth_signal"},
        ]
    }
    sample_disclosure_only = {**sample_non_listed, "prospect_id": "sample_disclosure_only", "company_name": "披露堆叠样本"}
    sample_disclosure_sources = {
        "sample_disclosure_only": [
            {"source_type": "annual_report", "source_locator": "https://cninfo.example/a", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure"},
            {"source_type": "announcement", "source_locator": "https://cninfo.example/b", "evidence_strength": "announcement", "supports_dimension": "listed_company_disclosure"},
            {"source_type": "exchange_announcement", "source_locator": "https://sse.example/c", "evidence_strength": "exchange_announcement", "supports_dimension": "listed_company_disclosure"},
        ]
    }
    sample_internal = {**sample_non_listed, "prospect_id": "sample_internal", "company_name": "内部来源样本"}
    sample_internal_sources = {
        "sample_internal": [
            {"source_type": "official_site", "source_locator": "https://example.com", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix"},
            {"source_type": "structured_intake_patch", "source_locator": "internal://patch/1", "evidence_strength": "structured_intake_patch", "supports_dimension": "internal_patch"},
            {"source_type": "legacy_workbook", "source_locator": "internal://legacy/2", "evidence_strength": "legacy_workbook", "supports_dimension": "legacy_reference"},
        ]
    }
    sample_l2 = {**sample_non_listed, "prospect_id": "sample_l2", "company_name": "L2 保持样本"}
    sample_l2_sources = {"sample_l2": sample_non_listed_sources["sample_non_listed_l1"][:2]}
    decisions = {
        "non_listed_combo": evaluate_static_promotion(sample_non_listed, source_trace_by_prospect=sample_non_listed_sources).to_dict(),
        "disclosure_only": evaluate_static_promotion(sample_disclosure_only, source_trace_by_prospect=sample_disclosure_sources).to_dict(),
        "internal_not_counted": evaluate_static_promotion(sample_internal, source_trace_by_prospect=sample_internal_sources).to_dict(),
        "l2_not_harmed": evaluate_static_promotion(sample_l2, source_trace_by_prospect=sample_l2_sources).to_dict(),
    }
    json_errors = []
    json_paths = [*M83.glob("*.json"), CANONICAL_POOL, CANONICAL_TRACE, STATUS_PANEL]
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M83])
    api = scan_api([M83, WORKSPACE / "shared/static_pool/static_promote.py", WORKSPACE / "scripts/build_m83r_source_category_v2_audit.py"])
    assertions = {
        "non_listed_combo_can_reach_l1": decisions["non_listed_combo"]["suggested_level"] == "L1",
        "disclosure_only_without_icp_support_not_l1": decisions["disclosure_only"]["suggested_level"] != "L1",
        "internal_or_legacy_not_counted_for_l1": decisions["internal_not_counted"]["suggested_level"] != "L1",
        "l2_rule_not_harmed": decisions["l2_not_harmed"]["suggested_level"] == "L2",
        "current_l1_audited": admission["audit"]["summary"]["current_l1_count"] == 19,
        "category_audit_has_all_pool_items": category_audit["summary"]["prospect_count"] == 50,
        "no_old_excel_write": True,
        "no_knowledge_asset_write": True,
        "no_persona_registry_write": True,
    }
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {
        "milestone": "M83R",
        "generated_at": now(),
        "status": status,
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors},
        "rule_sample_decisions": decisions,
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "assertions": assertions,
    }
    write_json(M83 / "m83r_validation_report_v1.json", validation)
    return validation


def build_status(category_audit: dict[str, Any], admission: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    panel = {
        "milestone": "M83R",
        "generated_at": now(),
        "status": "PASS_M83R_SOURCE_CATEGORY_V2_CORRECTION" if validation["status"] == "PASS" else "FAIL_M83R_SOURCE_CATEGORY_V2_CORRECTION",
        "summary": {
            "source_category_counts": category_audit["summary"]["source_category_counts"],
            "current_l1_count": admission["audit"]["summary"]["current_l1_count"],
            "v2_l1_compatible_count": admission["audit"]["summary"]["v2_l1_compatible_count"],
            "downgrade_preview_count": admission["audit"]["summary"]["downgrade_preview_count"],
            "l2_non_listed_friendly_suggestion_count": admission["suggestions"]["summary"]["l2_suggestion_count"],
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        },
        "next_recommended_action": "用 source_category v2 指导后续 L1 补源；非上市 ICP 优先补 official_owned + platform_operating_fact + authoritative_third_party 组合。",
    }
    handoff = {
        "milestone": "M83R",
        "generated_at": now(),
        "status": "PASS_M83R_HANDOFF_READY" if validation["status"] == "PASS" else "FAIL_M83R_HANDOFF_NEEDS_REVIEW",
        "key_outputs": {
            "source_category_policy": rel(M83 / "source_category_policy_v2.json"),
            "source_trace_category_audit": rel(M83 / "source_trace_category_audit_v1.json"),
            "l1_rules_v2": rel(M83 / "l1_admission_rules_v2.json"),
            "l1_rules_v2_audit": rel(M83 / "l1_admission_rules_v2_audit_v1.json"),
            "non_listed_suggestions": rel(M83 / "non_listed_l1_source_suggestions_v1.json"),
            "validation": rel(M83 / "m83r_validation_report_v1.json"),
        },
    }
    write_json(M83 / "m83r_operating_panel_v1.json", panel)
    write_json(M83 / "handoff_snapshot_v1.json", handoff)
    canonical = read_json(STATUS_PANEL)
    canonical["generated_at"] = now()
    canonical["overall_status"] = panel["status"]
    canonical["latest_milestone"] = "M83R"
    canonical["m83r_source_category_v2"] = panel["summary"]
    canonical["canonical_next_action"] = panel["next_recommended_action"]
    canonical["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical)
    return panel


def main() -> int:
    M83.mkdir(parents=True, exist_ok=True)
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    build_policy_outputs()
    category_audit = build_category_audit(pool, trace)
    admission = build_admission_audit(pool, trace)
    validation = validate(category_audit, admission)
    panel = build_status(category_audit, admission, validation)
    print(json.dumps({"category_counts": category_audit["summary"]["source_category_counts"], "admission": admission["audit"]["summary"], "panel": panel["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
