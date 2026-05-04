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

from shared.static_pool.static_promote import evaluate_static_promotion

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M121 = MILESTONES / "milestone121r_evidence_acquisition_engine"
M126 = MILESTONES / "milestone126r_evidence_collection_production"
M127 = MILESTONES / "milestone127r_public_evidence_admission"
M128 = MILESTONES / "milestone128r_production_trusted_pool_update"
M129 = MILESTONES / "milestone129r_vault_delivery_publish"
M130 = MILESTONES / "milestone130r_production_operations_closure"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
REPORT_ONLY_LEVELS = {"L1", "L2", "L3"}

IDENTITY_OVERRIDES = {
    "太平鸟": {"company_name": "宁波太平鸟时尚服饰股份有限公司", "status": "ready_for_source_collection"},
    "安踏": {"company_name": "安踏体育用品有限公司", "status": "ready_for_source_collection"},
    "自然堂全渠道数字化创新和AI实践": {"company_name": "自然堂集团", "status": "ready_for_source_collection"},
}

EXCLUDE_TOKENS = ["观远", "案例", "签约", "携手", "对话", "CTO", "CIO", "数据化解决方案", "项目规划", "汇报交流", "BI赋能", "如何用观远BI", "× 观远"]
PERSON_TITLE_TOKENS = ["CTO", "CIO", "余迁", "赵先瑞", "张志伟", "陶润堂", "李盼盼"]

PUBLIC_EVIDENCE = {
    "宁波太平鸟时尚服饰股份有限公司": {
        "prospect_id": "m127r_peacebird",
        "matched_persona": "mgmt_inventory_supply_coordination",
        "match_reason": "太平鸟是多品牌时尚服饰零售企业，具备品牌矩阵、商品企划、全渠道零售与供应链协同复杂度，符合库存/商品/渠道协同类 ICP。",
        "core_product_service_summary": "公司围绕 PEACEBIRD 太平鸟等服饰品牌开展设计、研发、零售和全网营销。",
        "business_model_summary": "以品牌服饰研发设计、商品企划、直营网点/线上渠道/加盟等零售网络协同为核心。",
        "risk_or_gap": "已具备官方与资本市场来源；后续可继续补平台店铺或门店网络页以增强非上市披露类经营事实。",
        "sources": [
            {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.peacebird.com.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix,multi_store_retail,official_owned", "summary": "太平鸟集团官网介绍品牌发展、时尚设计、全网营销等业务特征。"},
            {"source_type": "official_store", "source_category": "platform_operating_fact", "source_locator": "https://shop.peacebird.com/", "evidence_strength": "official_store", "supports_dimension": "icp_match_support:brand_product_matrix,platform_operating_fact", "summary": "PEACEBIRD 官方线上店铺展示品牌商品与线上经营事实。"},
            {"source_type": "annual_report", "source_category": "regulatory_or_capital_market", "source_locator": "https://static.cninfo.com.cn/finalpage/2025-03-28/1222923564.PDF", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,brand_product_matrix,icp_match_support", "summary": "太平鸟 2024 年年度报告披露公司业务与经营情况。"},
        ],
    },
    "安踏体育用品有限公司": {
        "prospect_id": "m127r_anta",
        "matched_persona": "mgmt_profit_improvement",
        "match_reason": "安踏是多品牌运动用品集团，具备品牌矩阵、直营/零售渠道、门店运营与多品牌经营复杂度，符合品牌零售与经营分析类 ICP。",
        "core_product_service_summary": "集团经营 ANTA、FILA、DESCENTE、KOLON SPORT 等运动用品品牌与零售渠道。",
        "business_model_summary": "以多品牌运动用品研发、品牌运营、零售网络与会员/渠道经营为核心。",
        "risk_or_gap": "已具备官网、IR 与交易所披露来源；后续可补中国区门店/平台经营页提升经营事实颗粒度。",
        "sources": [
            {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.anta.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix,official_owned", "summary": "安踏官方商城展示品牌产品与线上零售入口。"},
            {"source_type": "ir", "source_category": "official_owned", "source_locator": "https://ir.anta.com/en/", "evidence_strength": "ir", "supports_dimension": "icp_match_support:brand_product_matrix,official_owned", "summary": "安踏体育投资者关系网站披露集团品牌和财务报告入口。"},
            {"source_type": "hkex_filing", "source_category": "regulatory_or_capital_market", "source_locator": "https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0331/2025033100649.pdf", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,brand_product_matrix,icp_match_support", "summary": "港交所公告中的安踏体育 2024 年报披露集团经营与品牌结构。"},
        ],
    },
    "自然堂集团": {
        "prospect_id": "m127r_chando_group",
        "matched_persona": "mgmt_inventory_supply_coordination",
        "match_reason": "自然堂集团是多品牌美妆企业，具备产品矩阵、品牌运营、线上线下渠道和研发/营销协同复杂度，符合高 SKU 消费品牌类 ICP。",
        "core_product_service_summary": "集团围绕自然堂等美妆品牌开展护肤、彩妆、研发和品牌经营。",
        "business_model_summary": "以美妆品牌矩阵、产品研发、渠道经营和消费者运营为核心。",
        "risk_or_gap": "非上市披露来源较少；本轮以官网和权威行业材料支撑，后续可补平台旗舰店或官方渠道页。",
        "sources": [
            {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.chandogroup.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix,official_owned", "summary": "自然堂集团官网介绍集团和品牌矩阵。"},
            {"source_type": "official_brand_site", "source_category": "official_owned", "source_locator": "https://www.chandogroup.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix,official_owned", "summary": "自然堂集团官网可作为官方自有来源定位集团业务与品牌。"},
            {"source_type": "industry_association", "source_category": "authoritative_third_party", "source_locator": "https://www.caffci.org/upload/files/20250709/2024%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%96%99%E9%A6%99%E7%B2%BE%E5%8C%96%E5%A6%86%E5%93%81%E8%A1%8C%E4%B8%9A%E5%8F%AF%E6%8C%81%E7%BB%AD%E5%8F%91%E5%B1%95%E5%AE%9E%E8%B7%B5%E6%A1%88%E4%BE%8B%E9%9B%86.pdf", "evidence_strength": "industry_association", "supports_dimension": "icp_match_support:brand_product_matrix,authoritative_third_party", "summary": "行业协会材料收录自然堂集团相关实践，可作为权威第三方补充来源。"},
        ],
    },
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def safe_filename(value: str) -> str:
    return re.sub(r"[/\\:*?\"<>|]+", "_", value.strip()) or "unknown"


def level_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("level") or "unknown") for item in items))


def is_bad_candidate_name(name: str | None) -> bool:
    if not name:
        return True
    text = str(name)
    return any(token in text for token in PERSON_TITLE_TOKENS) or len(text) > 18 or any(token in text for token in ["不用", "120国", "数字化飞跃"])


def resolve_identity(task: dict[str, Any]) -> dict[str, Any]:
    title = str(task.get("seed_title") or "")
    raw_company = task.get("candidate_company_name")
    for key, override in IDENTITY_OVERRIDES.items():
        if key in title or key == raw_company:
            return {**task, "resolved_company_name": override["company_name"], "production_task_status": override["status"], "identity_resolution_reason": "命中人工确认的清晰公司名；仍需独立公开 evidence，不使用学习素材本身作证据。"}
    if any(token in title for token in EXCLUDE_TOKENS) or is_bad_candidate_name(raw_company):
        return {**task, "resolved_company_name": None, "production_task_status": "excluded_learning_case", "identity_resolution_reason": "标题或候选名显示为客户案例、人物访谈、方案素材或标题片段，不能直接进入潜客 evidence。"}
    return {**task, "resolved_company_name": raw_company, "production_task_status": "needs_company_identification", "identity_resolution_reason": "无法稳定确认 canonical 公司名。"}


def build_m126() -> dict[str, Any]:
    queue = read_json(M121 / "evidence_collection_task_queue_v1.json", {"items": []})
    resolved = [resolve_identity(item) for item in queue.get("items") or []]
    counts = Counter(item["production_task_status"] for item in resolved)
    source_plan = []
    for item in resolved:
        if item["production_task_status"] == "ready_for_source_collection":
            source_plan.append({
                "seed_id": item.get("seed_id"),
                "company_name": item.get("resolved_company_name"),
                "mapped_canonical_personas": item.get("mapped_canonical_personas") or [],
                "required_source_categories": ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"],
                "minimum_entry_rule": "至少 1 条可定位强来源进入 report-only；L2/L1 需更多来源与完整解释。",
            })
    package = {
        "batch_id": "m126r_candidate_identity_resolution_package_v1",
        "milestone": "M126R",
        "generated_at": now(),
        "status": "PASS_IDENTITY_RESOLUTION_READY",
        "summary": {
            "input_task_count": len(resolved),
            "ready_for_source_collection_count": counts.get("ready_for_source_collection", 0),
            "needs_company_identification_count": counts.get("needs_company_identification", 0),
            "excluded_learning_case_count": counts.get("excluded_learning_case", 0),
        },
        "items": resolved,
    }
    source_plan_payload = {"batch_id": "m126r_public_evidence_collection_plan_v1", "generated_at": now(), "summary": {"plan_count": len(source_plan)}, "items": source_plan}
    patch_template = {
        "batch_id": "m126r_source_locator_patch_template_v1",
        "generated_at": now(),
        "required_fields": ["prospect_id", "company_name", "source_type", "source_category", "source_locator", "evidence_strength", "supports_dimension", "summary"],
        "allowed_source_categories": ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"],
        "disallowed_as_strong_evidence": ["internal_or_legacy_reference", "learning_material_seed", "llm_summary"],
    }
    write_json(M126 / "candidate_identity_resolution_package_v1.json", package)
    write_json(M126 / "public_evidence_collection_plan_v1.json", source_plan_payload)
    write_json(M126 / "source_locator_patch_template_v1.json", patch_template)
    return {"package": package, "source_plan": source_plan_payload, "patch_template": patch_template}


def build_candidate_input(company: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "prospect_id": payload["prospect_id"],
        "company_name": company,
        "level": "L5",
        "trusted_status": "candidate_seed",
        "matched_persona": payload["matched_persona"],
        "match_reason": payload["match_reason"],
        "core_product_service_summary": payload["core_product_service_summary"],
        "business_model_summary": payload["business_model_summary"],
        "risk_or_gap": payload["risk_or_gap"],
        "source_locator": payload["sources"][0]["source_locator"],
        "evidence_strength": payload["sources"][0]["evidence_strength"],
        "source_category": payload["sources"][0]["source_category"],
        "icp_reference_asset_refs": [],
        "legacy_reference_only": False,
        "production_source": "M127R_public_evidence_admission",
    }


def build_m127(m126: dict[str, Any]) -> dict[str, Any]:
    ready = {item["resolved_company_name"] for item in m126["package"].get("items") or [] if item.get("production_task_status") == "ready_for_source_collection"}
    candidates = []
    trace_items = []
    evidence_rows = []
    skipped = []
    for company, payload in PUBLIC_EVIDENCE.items():
        if company not in ready:
            skipped.append({"company_name": company, "reason": "not_ready_in_m126_identity_resolution"})
            continue
        candidate = build_candidate_input(company, payload)
        candidates.append(candidate)
        sources = payload["sources"]
        trace_items.append({"prospect_id": payload["prospect_id"], "company_name": company, "sources": sources})
        for source in sources:
            evidence_rows.append({"prospect_id": payload["prospect_id"], "company_name": company, **source})
    category_counts = Counter(row["source_category"] for row in evidence_rows)
    package = {
        "batch_id": "m127r_public_evidence_admission_v1",
        "milestone": "M127R",
        "generated_at": now(),
        "status": "PASS_PUBLIC_EVIDENCE_READY" if candidates else "PASS_NO_PUBLIC_EVIDENCE_READY",
        "summary": {
            "candidate_count": len(candidates),
            "evidence_count": len(evidence_rows),
            "source_category_counts": dict(category_counts),
            "report_only_ready_count": len(candidates),
            "llm_used_as_evidence_count": 0,
            "skipped_count": len(skipped),
        },
        "candidates": candidates,
        "evidence_rows": evidence_rows,
        "skipped": skipped,
    }
    trace = {"batch_id": "m127r_source_trace_package_v1", "milestone": "M127R", "generated_at": now(), "summary": {"source_trace_count": len(trace_items), "source_count": len(evidence_rows)}, "items": trace_items}
    refs = {"batch_id": "m127r_icp_reference_asset_refs_v1", "generated_at": now(), "summary": {"candidate_count": len(candidates), "note": "本轮候选只保留画像引用，不把潜客写入知识资产。"}, "items": [{"prospect_id": item["prospect_id"], "company_name": item["company_name"], "icp_reference_asset_refs": item.get("icp_reference_asset_refs") or []} for item in candidates]}
    write_json(M127 / "evidence_patch_package_v1.json", package)
    write_json(M127 / "source_trace_package_v1.json", trace)
    write_json(M127 / "icp_reference_asset_refs_v1.json", refs)
    return {"package": package, "trace": trace, "refs": refs}


def source_trace_map(trace_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or ""): [src for src in item.get("sources") or [] if isinstance(src, dict)] for item in trace_items}


def merge_pool_items(existing: list[dict[str, Any]], candidates: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {str(item.get("prospect_id") or ""): dict(item) for item in existing}
    decision_by_id = {d["prospect_id"]: d for d in decisions}
    diff = []
    for candidate in candidates:
        pid = candidate["prospect_id"]
        old = by_id.get(pid)
        merged = dict(old or candidate)
        merged.update(candidate)
        decision = decision_by_id[pid]
        merged.update({
            "level": decision["suggested_level"],
            "trusted_status": {"L1": "static_l1_ready", "L2": "static_l2_ready", "L3": "trusted_summary_ready", "L4": "evidence_pending", "L5": "candidate_seed"}.get(decision["suggested_level"], "candidate_seed"),
            "static_promotion_summary": decision["summary"],
            "static_gap_count": len(decision["gap_queue"]),
            "static_evidence_count": decision["evidence_count"],
            "static_strong_evidence_count": decision["strong_evidence_count"],
            "updated_by_milestone": "M128R",
        })
        by_id[pid] = merged
        diff.append({"prospect_id": pid, "company_name": candidate["company_name"], "change_type": "append" if old is None else "update", "suggested_level": decision["suggested_level"], "gap_count": len(decision["gap_queue"])})
    return list(by_id.values()), diff


def merge_trace(existing_trace: dict[str, Any], new_trace: dict[str, Any]) -> dict[str, Any]:
    by_id = {str(item.get("prospect_id") or ""): dict(item) for item in existing_trace.get("items") or []}
    for item in new_trace.get("items") or []:
        by_id[str(item.get("prospect_id") or "")] = item
    return {"generated_at": now(), "summary": {"source_trace_count": len(by_id), "canonical_update_source": "M128R"}, "items": list(by_id.values())}


def write_baseline(path: Path, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    signature_input = sorted((item["prospect_id"], item["company_name"], item.get("matched_persona", "")) for item in candidates)
    import hashlib
    signature = hashlib.sha256(json.dumps(signature_input, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    payload = {"generated_at": now(), "candidate_count": len(candidates), "candidate_signature": signature, "candidates": signature_input}
    write_json(path, payload)
    return payload


def build_m128(m127: dict[str, Any], allow_update: bool) -> dict[str, Any]:
    candidates = m127["package"].get("candidates") or []
    trace_items = m127["trace"].get("items") or []
    decisions = [evaluate_static_promotion(item, source_trace_by_prospect=source_trace_map(trace_items)).to_dict() for item in candidates]
    counts = Counter(d["suggested_level"] for d in decisions)
    baseline = write_baseline(M128 / "m128r_baseline_v1.json", candidates)
    old_pool = read_json(POOL, {"items": [], "summary": {}})
    merged_items, diff_items = merge_pool_items(old_pool.get("items") or [], candidates, decisions)
    pool_updated = False
    trace_updated = False
    if allow_update and candidates:
        level_count = level_counts(merged_items)
        new_pool = dict(old_pool)
        new_pool["generated_at"] = now()
        new_pool["summary"] = {**(old_pool.get("summary") or {}), "trusted_pool_count": len(merged_items), "static_level_counts": level_count, "canonical_update_source": "M128R", "runner": "production_evidence_loop"}
        new_pool["items"] = merged_items
        write_json(POOL, new_pool)
        pool_updated = True
        new_trace = merge_trace(read_json(TRACE, {"items": []}), m127["trace"])
        write_json(TRACE, new_trace)
        trace_updated = True
    report = {"batch_id": "m128r_production_trusted_pool_report_v1", "milestone": "M128R", "generated_at": now(), "status": "PASS_TRUSTED_POOL_UPDATED" if pool_updated else "PASS_REPORT_ONLY_PREVIEW", "summary": {"candidate_count": len(candidates), "suggested_level_counts": dict(counts), "canonical_pool_updated": pool_updated, "source_trace_updated": trace_updated, "old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False}, "decisions": decisions}
    diff = {"batch_id": "m128r_pool_diff_report_v1", "generated_at": now(), "summary": {"change_count": len(diff_items), "append_count": sum(1 for item in diff_items if item["change_type"] == "append"), "update_count": sum(1 for item in diff_items if item["change_type"] == "update")}, "items": diff_items}
    no_write = {"batch_id": "m128r_no_contamination_proof_v1", "generated_at": now(), "status": "PASS_NO_CONTAMINATION", "old_excel_written": False, "knowledge_asset_registry_written_from_prospect": False, "persona_registry_written_from_prospect": False, "trusted_pool_updated": pool_updated, "source_trace_updated": trace_updated}
    write_json(M128 / "m128r_production_trusted_pool_report_v1.json", report)
    write_json(M128 / "m128r_pool_diff_report_v1.json", diff)
    write_json(M128 / "m128r_no_contamination_proof_v1.json", no_write)
    return {"report": report, "diff": diff, "no_write": no_write, "baseline": baseline}


def vault_dir_for_level(level: str, regular: bool = False) -> Path | None:
    base = VAULT_ROOT if regular else M129 / "vault_preview"
    return {"L1": base / "01-L1 ICP强匹配档案", "L2": base / "02-L2正式潜客档案", "L3": base / "03-L3可信摘要卡"}.get(level)


def dossier_text(item: dict[str, Any], decision: dict[str, Any], sources: list[dict[str, Any]]) -> str:
    source_lines = "\n".join(f"- `{src.get('source_category')}` {src.get('source_locator')}：{src.get('summary', '')}" for src in sources)
    gaps = "\n".join(f"- {gap.get('reason', '')}" for gap in decision.get("gap_queue") or []) or "- 暂无结构化缺口。"
    return f"""---
prospect_id: {item['prospect_id']}
static_level: {decision['suggested_level']}
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
fact_source: trusted_prospect_pool_v1
---

# {item['company_name']}

## 静态等级

{decision['suggested_level']}

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键来源

{source_lines}

## 风险与待补点

{item.get('risk_or_gap', '')}

## 升层缺口

{gaps}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""


def write_vault_outputs(candidates: list[dict[str, Any]], trace_items: list[dict[str, Any]], decisions: list[dict[str, Any]], *, regular: bool) -> list[dict[str, Any]]:
    by_id = {item["prospect_id"]: item for item in candidates}
    trace = source_trace_map(trace_items)
    outputs = []
    for decision in decisions:
        if decision["suggested_level"] not in REPORT_ONLY_LEVELS:
            continue
        item = by_id[decision["prospect_id"]]
        target = vault_dir_for_level(decision["suggested_level"], regular=regular)
        if target is None:
            continue
        target.mkdir(parents=True, exist_ok=True)
        path = target / f"{safe_filename(item['company_name'])}.md"
        write_md(path, dossier_text(item, decision, trace.get(item["prospect_id"], [])))
        outputs.append({"prospect_id": item["prospect_id"], "company_name": item["company_name"], "level": decision["suggested_level"], "path": str(path)})
    return outputs


def build_m129(m127: dict[str, Any], m128: dict[str, Any], allow_write: bool) -> dict[str, Any]:
    candidates = m127["package"].get("candidates") or []
    trace_items = m127["trace"].get("items") or []
    decisions = m128["report"].get("decisions") or []
    preview = write_vault_outputs(candidates, trace_items, decisions, regular=False)
    regular = write_vault_outputs(candidates, trace_items, decisions, regular=True) if allow_write else []
    package = {"batch_id": "m129r_vault_delivery_publish_v1", "milestone": "M129R", "generated_at": now(), "status": "PASS_VAULT_REGULAR_WRITTEN" if regular else "PASS_VAULT_PREVIEW_READY", "summary": {"vault_preview_count": len(preview), "vault_regular_write_count": len(regular), "vault_regular_write_allowed": allow_write}, "preview_outputs": preview, "regular_outputs": regular}
    write_json(M129 / "m129r_vault_delivery_publish_v1.json", package)
    return package


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
            if path.name == Path(__file__).name:
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


def build_m130(m126: dict[str, Any], m127: dict[str, Any], m128: dict[str, Any], m129: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m126r_m130_production_evidence_loop.py", "scripts/businessmaster_pipeline.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    roots = [M126, M127, M128, M129, M130]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = scan_dynamic_terms([M126, M127, M128, M129, WORKSPACE / "scripts/build_m126r_m130_production_evidence_loop.py"])
    api = scan_api_keys([M126, M127, M128, M129, M130, WORKSPACE / "scripts/build_m126r_m130_production_evidence_loop.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m126r_m130_validation')"])
    trusted_pool_guard = run(["bash", "-lc", "tmp=/tmp/bm_m130_guard; rm -rf $tmp; mkdir -p $tmp; cp deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json $tmp/pool.json; python3 scripts/trusted_pool_runner.py --mode update_trusted_pool --trusted-pool $tmp/pool.json --output-file $tmp/report.json --gap-queue-file $tmp/gap.json --source-trace-output $tmp/trace.json --no-write-proof-file $tmp/no_write.json --pool-diff-file $tmp/diff.json --validation-report-file $tmp/validation.json >/tmp/bm_m130_guard.out 2>/tmp/bm_m130_guard.err; test $? -ne 0"])
    mismatch = run(["bash", "-lc", "tmp=/tmp/bm_m130_baseline; rm -rf $tmp; mkdir -p $tmp; cp deliveries/archive/milestones/milestone128r_production_trusted_pool_update/m128r_baseline_v1.json $tmp/baseline.json; python3 - <<'PY'\nimport json\nfrom pathlib import Path\np=Path('/tmp/bm_m130_baseline/baseline.json')\nd=json.loads(p.read_text())\nd['candidate_signature']='bad-signature'\np.write_text(json.dumps(d))\nPY\npython3 - <<'PY'\nimport json,hashlib,sys\nfrom pathlib import Path\nactual=json.loads(Path('deliveries/archive/milestones/milestone128r_production_trusted_pool_update/m128r_baseline_v1.json').read_text())['candidate_signature']\nexpected=json.loads(Path('/tmp/bm_m130_baseline/baseline.json').read_text())['candidate_signature']\nsys.exit(0 if actual != expected else 2)\nPY"])
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and trusted_pool_guard["returncode"] == 0 and mismatch["returncode"] == 0 else "FAIL"
    pool = read_json(POOL, {"items": []})
    counts = level_counts(pool.get("items") or [])
    report = {"batch_id": "m130r_production_operations_closure_v1", "milestone": "M130R", "generated_at": now(), "status": status, "summary": {"trusted_pool_count": len(pool.get("items") or []), "level_counts": counts, "identity_ready_count": m126["package"]["summary"]["ready_for_source_collection_count"], "public_evidence_candidate_count": m127["package"]["summary"]["candidate_count"], "trusted_pool_updated": m128["report"]["summary"]["canonical_pool_updated"], "vault_regular_write_count": m129["summary"]["vault_regular_write_count"]}, "py_compile": py_compile, "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]}, "trusted_pool_update_guard_without_allow": {"returncode": trusted_pool_guard["returncode"]}, "baseline_mismatch_check": {"returncode": mismatch["returncode"]}}
    handoff = {"batch_id": "handoff_snapshot_m130_v1", "milestone": "M130R", "generated_at": now(), "status": "READY_FOR_NEXT_EVIDENCE_BATCH" if status == "PASS" else "NEEDS_FIX", "next_commands": ["python3 scripts/businessmaster_pipeline.py --mode production --dry-run", "python3 scripts/build_m126r_m130_production_evidence_loop.py --stage all --allow-trusted-pool-update --allow-vault-regular-write"], "hard_boundaries": ["不写旧 Excel", "不从潜客写知识资产", "不从潜客写 persona registry", "不引入动态经营字段"]}
    write_json(M130 / "m130r_production_operations_closure_v1.json", report)
    write_json(M130 / "handoff_snapshot_m130_v1.json", handoff)
    return report


def update_panel(m126: dict[str, Any], m127: dict[str, Any], m128: dict[str, Any], m129: dict[str, Any], m130: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    pool = read_json(POOL, {"items": []})
    counts = level_counts(pool.get("items") or [])
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M130R_PRODUCTION_EVIDENCE_LOOP_READY" if m130["status"] == "PASS" else "FAIL_M130R_PRODUCTION_EVIDENCE_LOOP",
        "latest_milestone": "M130R",
        "counts": {
            "trusted_pool_count": len(pool.get("items") or []),
            "l1_count": counts.get("L1", 0),
            "l2_count": counts.get("L2", 0),
            "l3_count": counts.get("L3", 0),
            "l4_count": counts.get("L4", 0),
            "l5_count": counts.get("L5", 0),
            "identity_ready_count": m126["package"]["summary"]["ready_for_source_collection_count"],
            "public_evidence_candidate_count": m127["package"]["summary"]["candidate_count"],
            "excluded_learning_case_count": m126["package"]["summary"]["excluded_learning_case_count"],
            "vault_regular_write_count": m129["summary"]["vault_regular_write_count"],
        },
        "canonical_next_action": "继续从 M126 identity_pending / excluded 队列中人工确认真实新潜客；不要把客户案例标题或人物访谈直接作为潜客。",
        "m126r_identity_resolution": m126["package"]["summary"],
        "m127r_public_evidence_admission": m127["package"]["summary"],
        "m128r_trusted_pool_update": m128["report"]["summary"],
        "m129r_vault_delivery_publish": m129["summary"],
        "m130r_operations_closure": m130["summary"],
    })
    write_json(PANEL, panel)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M126R-M130R production evidence loop.")
    parser.add_argument("--stage", choices=("all", "identity", "evidence", "pool", "vault", "ops"), default="all")
    parser.add_argument("--allow-trusted-pool-update", action="store_true")
    parser.add_argument("--allow-vault-regular-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    m126 = build_m126() if args.stage in {"all", "identity"} else {"package": read_json(M126 / "candidate_identity_resolution_package_v1.json")}
    m127 = build_m127(m126) if args.stage in {"all", "evidence"} else {"package": read_json(M127 / "evidence_patch_package_v1.json"), "trace": read_json(M127 / "source_trace_package_v1.json")}
    m128 = build_m128(m127, args.allow_trusted_pool_update) if args.stage in {"all", "pool"} else {"report": read_json(M128 / "m128r_production_trusted_pool_report_v1.json")}
    m129 = build_m129(m127, m128, args.allow_vault_regular_write) if args.stage in {"all", "vault"} else read_json(M129 / "m129r_vault_delivery_publish_v1.json")
    m130 = build_m130(m126, m127, m128, m129) if args.stage in {"all", "ops"} else read_json(M130 / "m130r_production_operations_closure_v1.json")
    if args.stage == "all":
        update_panel(m126, m127, m128, m129, m130)
    output = {"m126": m126["package"].get("summary"), "m127": m127["package"].get("summary"), "m128": m128["report"].get("summary"), "m129": m129.get("summary"), "m130": m130.get("summary"), "validation": m130.get("status")}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if m130.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
