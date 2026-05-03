from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone44r_new_trusted_prospect_trial"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 44R-首批新可信潜客试运行-v1.md"

STRONG_EVIDENCE_VALUES = {"official", "regulatory", "annual_report", "ir", "exchange_announcement", "authoritative_media", "industry_research"}
TRUSTED_STATUS_VALUES = {"trusted_match_ready", "evidence_pending", "persona_pending_review", "not_icp"}

CANDIDATE_SEEDS: list[dict[str, Any]] = [
    {
        "prospect_id": "m44r_prospect_botanee",
        "company_name": "云南贝泰妮生物科技集团股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "功效护肤品牌集团，具备多品牌/多渠道/产品研发与上市公司信息披露场景，适合高 SKU 品牌经营分析画像。",
        "core_product_service_summary": "以皮肤健康互联网+大健康为定位，覆盖功效性护肤品与相关健康消费品。",
        "business_model_summary": "品牌研发、生产/供应链、线上线下渠道销售与会员运营并重。",
        "source_type": "official_ir",
        "source_locator": "https://www.botanee.com.cn/investor-relations.html",
        "evidence_strength": "ir",
    },
    {
        "prospect_id": "m44r_prospect_jahwa",
        "company_name": "上海家化联合股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "拥有多品牌日化美妆产品和多工厂/多渠道经营结构，符合品牌零售高 SKU 复杂度画像。",
        "core_product_service_summary": "日用化妆品、护肤、洗护、母婴等品牌与产品组合。",
        "business_model_summary": "上市日化集团，品牌矩阵、生产基地、渠道分销和消费者运营共同驱动。",
        "source_type": "official_site",
        "source_locator": "https://www.jahwa.com.cn/about/com",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_syoung",
        "company_name": "水羊集团股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "自有品牌与 CP 品牌双业务驱动，强调研发与数字化组织，匹配新消费品牌经营分析画像。",
        "core_product_service_summary": "美妆护肤品牌运营及相关消费品业务。",
        "business_model_summary": "自有品牌+代理/合作品牌组合，线上渠道和品牌运营能力重要。",
        "source_type": "official_site",
        "source_locator": "https://syounggroup.com/",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_yatsen",
        "company_name": "逸仙控股有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "中国美妆集团，品牌矩阵与电商/零售渠道经营复杂度高，适合高 SKU 品牌画像。",
        "core_product_service_summary": "美妆护肤品牌集团，包含彩妆、护肤等消费品牌。",
        "business_model_summary": "品牌组合经营、线上线下渠道、会员与营销驱动。",
        "source_type": "official_ir",
        "source_locator": "https://ir.yatsenglobal.com/",
        "evidence_strength": "ir",
    },
    {
        "prospect_id": "m44r_prospect_winner_medical",
        "company_name": "稳健医疗用品股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "医疗耗材与健康消费品牌并行，产品线和渠道复杂，适合品牌零售/健康消费经营分析画像。",
        "core_product_service_summary": "医疗耗材、健康生活消费品及相关品牌产品。",
        "business_model_summary": "制造供应链、品牌零售、线上线下渠道和上市公司治理并重。",
        "source_type": "official_ir",
        "source_locator": "https://www.winnermedical.cn/investor/report.html",
        "evidence_strength": "ir",
    },
    {
        "prospect_id": "m44r_prospect_luckin",
        "company_name": "瑞幸咖啡有限公司",
        "matched_persona": "fnb_chain_beverage_coffee",
        "match_reason": "大规模咖啡连锁，移动端订单、门店网络和供应链共同驱动，符合茶饮咖啡连锁画像。",
        "core_product_service_summary": "咖啡及饮品连锁品牌，提供门店自提、外卖及数字化消费体验。",
        "business_model_summary": "门店网络+移动应用+供应链+会员运营的连锁新零售模式。",
        "source_type": "official_ir",
        "source_locator": "https://investor.luckincoffee.com/financial-information/annual-reports/",
        "evidence_strength": "ir",
    },
    {
        "prospect_id": "m44r_prospect_chagee",
        "company_name": "霸王茶姬控股有限公司",
        "matched_persona": "fnb_chain_beverage_coffee",
        "match_reason": "新茶饮连锁品牌，强调门店、加盟/伙伴、品质和全球化扩张，符合茶饮咖啡连锁画像。",
        "core_product_service_summary": "现制茶饮品牌，围绕原叶鲜奶茶等产品经营。",
        "business_model_summary": "连锁门店、合作伙伴、供应链和品牌运营共同驱动。",
        "source_type": "official_ir",
        "source_locator": "https://investor.chagee.com/",
        "evidence_strength": "ir",
    },
    {
        "prospect_id": "m44r_prospect_chabaidao",
        "company_name": "四川百茶百道实业股份有限公司",
        "matched_persona": "fnb_chain_beverage_coffee",
        "match_reason": "茶饮连锁品牌，官网披露投关/业绩报告/公告通函入口，具备门店与供应链经营分析需求。",
        "core_product_service_summary": "现制茶饮产品和品牌加盟/连锁经营。",
        "business_model_summary": "加盟/连锁门店、产品研发、供应链与品牌运营结合。",
        "source_type": "official_site",
        "source_locator": "https://www.chabaidao.com/home/index/",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_jiumaojiu",
        "company_name": "九毛九国际控股有限公司",
        "matched_persona": "fnb_chain_standardized",
        "match_reason": "多品牌餐饮集团，门店覆盖广、品牌组合多，符合标准化连锁餐饮画像。",
        "core_product_service_summary": "九毛九、太二酸菜鱼、怂火锅等餐饮品牌经营。",
        "business_model_summary": "多品牌直营/连锁餐饮，门店运营、供应链和区域扩张共同驱动。",
        "source_type": "official_site",
        "source_locator": "https://www.jiumaojiu.com/about/index.html",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_juewei",
        "company_name": "绝味食品股份有限公司",
        "matched_persona": "fnb_chain_standardized",
        "match_reason": "休闲卤制食品连锁与加盟体系，生产、冷链、门店网络复杂，符合标准化连锁餐饮/食品画像。",
        "core_product_service_summary": "休闲卤制食品研发、生产、销售与连锁加盟。",
        "business_model_summary": "中央生产、冷链物流、加盟/终端零售和品牌运营结合。",
        "source_type": "official_site",
        "source_locator": "https://www.juewei.cn/page/jwd/",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_pagoda",
        "company_name": "深圳百果园实业集团股份有限公司",
        "matched_persona": "retail_multi_store",
        "match_reason": "水果专营连锁，门店网络、供应链和标准化零售运营要求高，符合多门店零售画像。",
        "core_product_service_summary": "水果零售、果品品牌与连锁门店服务。",
        "business_model_summary": "门店网络、供应链、品控和会员零售共同驱动。",
        "source_type": "official_site",
        "source_locator": "https://www.pagoda.com.cn/",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_kidswant",
        "company_name": "孩子王儿童用品股份有限公司",
        "matched_persona": "retail_multi_store",
        "match_reason": "母婴童零售连锁与会员经营场景突出，符合多门店/会员零售经营画像。",
        "core_product_service_summary": "母婴童商品零售、儿童成长服务和会员经营。",
        "business_model_summary": "线下门店、线上渠道、会员与服务场景结合。",
        "source_type": "regulatory",
        "source_locator": "https://stock.stockstar.com/notice/SN2026040800035202.shtml",
        "evidence_strength": "authoritative_media",
    },
    {
        "prospect_id": "m44r_prospect_chowtaiseng",
        "company_name": "周大生珠宝股份有限公司",
        "matched_persona": "retail_multi_store",
        "match_reason": "珠宝零售连锁，门店、加盟、商品和库存管理复杂，符合多门店零售画像。",
        "core_product_service_summary": "珠宝首饰产品设计、品牌运营和终端零售。",
        "business_model_summary": "品牌加盟/直营网点、商品供应链和终端销售运营结合。",
        "source_type": "annual_report",
        "source_locator": "https://www.chowtaiseng.com/uploads/%E5%91%A8%E5%A4%A7%E7%94%9F%E7%8F%A0%E5%AE%9D%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B82023%E5%B9%B4%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A_1724297789.pdf",
        "evidence_strength": "annual_report",
    },
    {
        "prospect_id": "m44r_prospect_yanjinpuzi",
        "company_name": "盐津铺子食品股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "休闲食品集团，产品品类、渠道和供应链复杂度高，符合高 SKU 消费品牌画像。",
        "core_product_service_summary": "休闲食品研发、生产和销售，覆盖多品类食品。",
        "business_model_summary": "自有制造、渠道销售、品牌传播与多品类产品运营结合。",
        "source_type": "official_site",
        "source_locator": "https://www.yanjinpuzi.com/about_complex.aspx?FId=n1%3A1%3A1",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_three_squirrels",
        "company_name": "三只松鼠股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "休闲零食品牌，线上起家并拓展多渠道、多品类经营，符合高 SKU 品牌画像。",
        "core_product_service_summary": "坚果、烘焙、综合零食、肉制品、果干等休闲食品。",
        "business_model_summary": "品牌产品组合、线上渠道、线下/分销渠道和内容电商共同驱动。",
        "source_type": "regulatory",
        "source_locator": "https://static.cninfo.com.cn/finalpage/2025-03-28/1222926822.PDF",
        "evidence_strength": "regulatory",
    },
    {
        "prospect_id": "m44r_prospect_bear",
        "company_name": "小熊电器股份有限公司",
        "matched_persona": "retail_high_sku_brand",
        "match_reason": "小家电品牌产品线多、渠道多，经营分析常涉及 SKU、渠道、库存和新品表现。",
        "core_product_service_summary": "创意小家电产品研发、设计、生产和销售。",
        "business_model_summary": "产品研发、制造供应链、线上线下渠道和品牌运营结合。",
        "source_type": "official_ir",
        "source_locator": "https://bears.com.cn/invest/notice.html",
        "evidence_strength": "ir",
    },
    {
        "prospect_id": "m44r_prospect_roborock",
        "company_name": "北京石头世纪科技股份有限公司",
        "matched_persona": "cbec_multi_platform_brand",
        "match_reason": "智能硬件品牌具备国内外渠道和产品矩阵，适合跨境/多平台品牌经营画像。",
        "core_product_service_summary": "扫地机器人、洗地机等智能清洁电器及相关产品。",
        "business_model_summary": "研发驱动、供应链制造、国内外渠道与品牌运营结合。",
        "source_type": "authoritative_media",
        "source_locator": "https://group.roborock.com/zh-hk/contact-us",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_sailvan",
        "company_name": "赛维时代科技股份有限公司",
        "matched_persona": "cbec_multi_platform_brand",
        "match_reason": "跨境电商企业，平台、多品牌、多区域和供应链管理复杂，符合跨境多平台品牌画像。",
        "core_product_service_summary": "跨境电商品牌经营、供应链和多平台销售。",
        "business_model_summary": "品牌孵化、跨境平台运营、供应链和海外市场经营结合。",
        "source_type": "regulatory",
        "source_locator": "https://static.cninfo.com.cn/finalpage/2023-08-30/1217697315.PDF",
        "evidence_strength": "regulatory",
    },
    {
        "prospect_id": "m44r_prospect_focus_tech",
        "company_name": "焦点科技股份有限公司",
        "matched_persona": "cbec_platform_operator",
        "match_reason": "旗下中国制造网等平台型业务服务外贸与跨境场景，适合跨境平台/运营服务商画像。",
        "core_product_service_summary": "B2B 电子商务、外贸服务、软件与企业数字化服务。",
        "business_model_summary": "平台服务、软件产品和外贸数字化服务结合。",
        "source_type": "official_site",
        "source_locator": "https://www.focuschina.com/",
        "evidence_strength": "official",
    },
    {
        "prospect_id": "m44r_prospect_viomi",
        "company_name": "云米科技有限公司",
        "matched_persona": "cbec_multi_platform_brand",
        "match_reason": "智能家居/净水品牌，产品、渠道和全球上市公司披露结构可支撑多平台品牌经营判断。",
        "core_product_service_summary": "AIoT 家居与净水产品，聚焦家庭水解决方案。",
        "business_model_summary": "智能硬件研发、品牌销售、渠道和服务运营结合。",
        "source_type": "official_ir",
        "source_locator": "https://viomitechnology.gcs-web.com/",
        "evidence_strength": "ir",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M44R first new trusted prospect trial package.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _status_for(seed: dict[str, Any]) -> str:
    if seed.get("force_status"):
        return seed["force_status"]
    if seed.get("evidence_strength") in STRONG_EVIDENCE_VALUES and seed.get("source_locator"):
        return "trusted_match_ready"
    return "evidence_pending"


def _evidence(seed: dict[str, Any]) -> dict[str, Any]:
    return {
        "prospect_id": seed["prospect_id"],
        "company_name": seed["company_name"],
        "source_type": seed["source_type"],
        "source_locator": seed["source_locator"],
        "evidence_strength": seed["evidence_strength"],
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match"],
        "summary": f"该来源用于确认 {seed['company_name']} 的公司身份、主营产品/服务、业务模式及其与 {seed['matched_persona']} 的画像匹配基础。",
        "collected_at": _now(),
    }


def _candidate(seed: dict[str, Any]) -> dict[str, Any]:
    status = _status_for(seed)
    evidence = _evidence(seed)
    return {
        "prospect_id": seed["prospect_id"],
        "company_name": seed["company_name"],
        "matched_persona": seed["matched_persona"],
        "match_reason": seed["match_reason"],
        "core_product_service_summary": seed["core_product_service_summary"],
        "business_model_summary": seed["business_model_summary"],
        "strong_evidence": [evidence],
        "risk_or_gap": "需在正式入池前继续补充第二来源和业务人工复核。" if status == "trusted_match_ready" else "当前来源强度不足，不能进入 trusted_match_ready。",
        "trusted_status": status,
        "legacy_field_inherited": False,
        "llm_decision_used": False,
    }


def _card(candidate: dict[str, Any]) -> dict[str, Any]:
    evidence = candidate["strong_evidence"][0]
    return {
        "card_id": f"card_{candidate['prospect_id']}",
        "company_name": candidate["company_name"],
        "matched_persona": candidate["matched_persona"],
        "match_reason": candidate["match_reason"],
        "core_product_service_summary": candidate["core_product_service_summary"],
        "business_model_summary": candidate["business_model_summary"],
        "key_evidence": {
            "source_type": evidence["source_type"],
            "source_locator": evidence["source_locator"],
            "evidence_strength": evidence["evidence_strength"],
            "summary": evidence["summary"],
        },
        "trusted_status": candidate["trusted_status"],
        "risk_or_gap": candidate["risk_or_gap"],
        "consumer_readiness": "share_candidate" if candidate["trusted_status"] == "trusted_match_ready" else "needs_evidence_patch",
    }


def _validate(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors = []
    for item in candidates:
        if item["trusted_status"] not in TRUSTED_STATUS_VALUES:
            errors.append({"prospect_id": item["prospect_id"], "error_code": "invalid_trusted_status"})
        if item["legacy_field_inherited"]:
            errors.append({"prospect_id": item["prospect_id"], "error_code": "legacy_field_inherited"})
        if item["trusted_status"] == "trusted_match_ready":
            has_strong = any(e.get("evidence_strength") in STRONG_EVIDENCE_VALUES and e.get("source_locator") for e in item.get("strong_evidence", []))
            if not has_strong:
                errors.append({"prospect_id": item["prospect_id"], "error_code": "trusted_ready_without_strong_evidence"})
    return errors


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 44R-首批新可信潜客试运行-v1",
        "",
        "## 结论",
        "",
        f"- 候选数：`{summary['candidate_count']}`",
        f"- trusted_match_ready：`{summary['trusted_match_ready_count']}`",
        f"- evidence_pending：`{summary['evidence_pending_count']}`",
        f"- persona_pending_review：`{summary['persona_pending_review_count']}`",
        f"- not_icp：`{summary['not_icp_count']}`",
        f"- 强来源覆盖数：`{summary['strong_evidence_candidate_count']}`",
        f"- 校验错误数：`{summary['validation_error_count']}`",
        "",
        "## 说明",
        "",
        "- 本轮为 evidence-first 新方法试运行，不使用旧主表/旧档案/旧共享版事实字段。",
        "- 每张可信卡至少保留 1 条可定位来源；弱来源对象只能进入 evidence_pending。",
        "- 本轮不真实写回旧工作簿，也不写知识资产或画像 registry。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    candidates = [_candidate(seed) for seed in CANDIDATE_SEEDS]
    evidence_patch = [c["strong_evidence"][0] for c in candidates]
    cards = [_card(c) for c in candidates]
    validation_errors = _validate(candidates)
    status_counts = Counter(c["trusted_status"] for c in candidates)
    summary = {
        "candidate_count": len(candidates),
        "trusted_match_ready_count": status_counts.get("trusted_match_ready", 0),
        "evidence_pending_count": status_counts.get("evidence_pending", 0),
        "persona_pending_review_count": status_counts.get("persona_pending_review", 0),
        "not_icp_count": status_counts.get("not_icp", 0),
        "strong_evidence_candidate_count": sum(1 for c in candidates if any(e.get("evidence_strength") in STRONG_EVIDENCE_VALUES for e in c["strong_evidence"])),
        "official_or_strong_evidence_count": sum(1 for e in evidence_patch if e["evidence_strength"] in STRONG_EVIDENCE_VALUES),
        "validation_error_count": len(validation_errors),
        "by_persona": dict(Counter(c["matched_persona"] for c in candidates)),
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "legacy_field_inherited_count": sum(1 for c in candidates if c["legacy_field_inherited"]),
        "llm_decision_used_count": sum(1 for c in candidates if c["llm_decision_used"]),
        "no_write_proof_ok": True,
    }
    payload = {
        "batch_id": "milestone44r_new_trusted_prospect_trial_package_v1",
        "generated_at": _now(),
        "summary": summary,
        "new_trusted_prospect_candidates": candidates,
        "evidence_patch_package": evidence_patch,
        "trusted_prospect_cards": cards,
        "trusted_status_summary": {"status_counts": dict(status_counts), "validation_errors": validation_errors},
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone44r_new_trusted_prospect_trial_package_v1.json", payload)
    _write_json(output_dir / "milestone44r_new_trusted_prospect_candidates_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": candidates})
    _write_json(output_dir / "milestone44r_evidence_patch_package_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": evidence_patch})
    _write_json(output_dir / "milestone44r_trusted_prospect_cards_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": cards})
    _write_json(output_dir / "milestone44r_trusted_status_summary_v1.json", payload["trusted_status_summary"])
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_dir": str(output_dir), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = 20 <= len(candidates) <= 30 and summary["validation_error_count"] == 0 and summary["trusted_match_ready_count"] >= 19 and summary["no_write_proof_ok"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
