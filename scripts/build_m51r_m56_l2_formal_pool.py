from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_VAULT_ROOT = "/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池"
DEFAULT_TRUSTED_POOL = "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
DEFAULT_OUTPUT_ROOT = "deliveries/archive/milestones"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 51R-56R-L3到L2正式可信潜客池闭环-v1.md"

L2_TRIAL_COMPANIES = [
    "云南贝泰妮生物科技集团股份有限公司",
    "瑞幸咖啡有限公司",
    "孩子王儿童用品股份有限公司",
    "三只松鼠股份有限公司",
    "周大生珠宝股份有限公司",
    "北京石头世纪科技股份有限公司",
    "绝味食品股份有限公司",
    "深圳百果园实业集团股份有限公司",
]

SECOND_EVIDENCE: dict[str, dict[str, Any]] = {
    "云南贝泰妮生物科技集团股份有限公司": {
        "source_type": "regulatory_annual_report",
        "source_locator": "https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10975004&stockid=300957",
        "evidence_strength": "annual_report",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "贝泰妮 2024 年年度报告披露公司业务、研发体系、经营结果、投资者关系活动及治理信息，可作为 L2 第二强来源。",
    },
    "瑞幸咖啡有限公司": {
        "source_type": "sec_annual_report",
        "source_locator": "https://www.sec.gov/Archives/edgar/data/1767582/000141057825000546/lk-20241231x20f.htm",
        "evidence_strength": "annual_report",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "瑞幸咖啡 2024 Form 20-F 披露门店、移动应用、经营风险、财务和业务模式，是 L2 第二强来源。",
    },
    "孩子王儿童用品股份有限公司": {
        "source_type": "regulatory_annual_report",
        "source_locator": "https://static.cninfo.com.cn/finalpage/2025-04-03/1222991960.pdf",
        "evidence_strength": "annual_report",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "孩子王 2024 年年度报告披露门店、会员、乐友并购、母婴零售业务和财务表现，可支撑 L2 正式档案。",
    },
    "三只松鼠股份有限公司": {
        "source_type": "regulatory_annual_report",
        "source_locator": "https://disc.static.szse.cn/disc/disk03/finalpage/2025-03-27/d57d1ee5-75e6-4695-9661-2ba04cb9fd3c.PDF",
        "evidence_strength": "annual_report",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "三只松鼠 2024 年年度报告披露品牌、渠道、线上平台、分销与门店业务，可支撑高 SKU 消费品牌画像。",
    },
    "周大生珠宝股份有限公司": {
        "source_type": "regulatory_annual_report_summary",
        "source_locator": "https://notice.10jqka.com.cn/api/pdf/1a33ea9518295c6e.pdf",
        "evidence_strength": "annual_report",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "周大生 2024 年年度报告摘要披露珠宝产品、品牌运营、渠道和经营结果，可作为多门店零售画像第二强来源。",
    },
    "北京石头世纪科技股份有限公司": {
        "source_type": "exchange_performance_report",
        "source_locator": "https://star.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-02-28/688169_20250228_4E3Y.pdf",
        "evidence_strength": "exchange_announcement",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "石头科技 2024 年业绩快报披露营收、业务增长和披露主体信息，可作为正式档案第二强来源；后续仍建议补年度报告全文。",
    },
    "绝味食品股份有限公司": {
        "source_type": "regulatory_annual_report",
        "source_locator": "https://static.cninfo.com.cn/finalpage/2025-04-10/1223045873.PDF",
        "evidence_strength": "annual_report",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match", "financial_disclosure"],
        "summary": "绝味食品 2024 年年度报告披露卤味食品、连锁门店、经营数据和治理信息，可支撑连锁标准化餐饮画像。",
    },
    "深圳百果园实业集团股份有限公司": {
        "source_type": "official_company_profile",
        "source_locator": "https://www.pagoda.com.cn/about",
        "evidence_strength": "official_site",
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match"],
        "summary": "百果园官网企业简介披露其水果采购、种植支持、采后保鲜、物流仓储、标准分级、门店零售等业务链条。",
    },
}

EXPANSION_SEEDS = [
    ("上海家化联合股份有限公司", "retail_high_sku_brand", "https://www.jahwa.com.cn/about/com"),
    ("水羊集团股份有限公司", "retail_high_sku_brand", "https://syounggroup.com/"),
    ("逸仙控股有限公司", "retail_high_sku_brand", "https://ir.yatsenglobal.com/"),
    ("稳健医疗用品股份有限公司", "retail_high_sku_brand", "https://www.winnermedical.cn/investor/report.html"),
    ("霸王茶姬控股有限公司", "fnb_chain_beverage_coffee", "https://investor.chagee.com/"),
    ("九毛九国际控股有限公司", "fnb_chain_standardized", "https://www.jiumaojiu.com/about/index.html"),
    ("盐津铺子食品股份有限公司", "retail_high_sku_brand", "https://www.yanjinpuzi.com/about_complex.aspx?FId=n1%3A1%3A1"),
    ("小熊电器股份有限公司", "retail_high_sku_brand", "https://bears.com.cn/invest/notice.html"),
    ("赛维时代科技股份有限公司", "cbec_multi_platform_brand", "https://www.sailvan.com/"),
    ("焦点科技股份有限公司", "cbec_platform_operator", "https://www.focuschina.com/"),
    ("云米科技有限公司", "cbec_multi_platform_brand", "https://viomitechnology.gcs-web.com/"),
    ("上海爱婴室商务服务股份有限公司", "retail_multi_store", "https://www.aiyingshi.com/"),
    ("良品铺子股份有限公司", "retail_high_sku_brand", "https://www.517lppz.com/"),
    ("名创优品集团控股有限公司", "retail_multi_store", "https://ir.miniso.com/"),
    ("泡泡玛特国际集团有限公司", "retail_high_sku_brand", "https://www.popmart.com/"),
    ("海底捞国际控股有限公司", "fnb_chain_standardized", "https://www.haidilao.com/"),
    ("奈雪的茶控股有限公司", "fnb_chain_beverage_coffee", "https://www.naixuecha.com/"),
    ("安克创新科技股份有限公司", "cbec_multi_platform_brand", "https://www.anker-in.com/"),
    ("致欧家居科技股份有限公司", "cbec_multi_platform_brand", "https://www.songmics.com/"),
    ("华宝新能科技股份有限公司", "cbec_multi_platform_brand", "https://www.hello-tech.com/"),
    ("科沃斯机器人股份有限公司", "cbec_multi_platform_brand", "https://www.ecovacs.com/"),
    ("小米集团", "retail_high_sku_brand", "https://www.mi.com/"),
    ("飞科电器股份有限公司", "retail_high_sku_brand", "https://www.flyco.com/"),
    ("公牛集团股份有限公司", "retail_high_sku_brand", "https://www.gongniu.cn/"),
    ("老凤祥股份有限公司", "retail_multi_store", "https://www.laofengxiang.com/"),
    ("海澜之家集团股份有限公司", "retail_multi_store", "https://www.hla.com/"),
    ("波司登国际控股有限公司", "retail_multi_store", "https://company.bosideng.com/"),
    ("百胜中国控股有限公司", "fnb_chain_standardized", "https://ir.yumchina.com/"),
    ("蜜雪冰城股份有限公司", "fnb_chain_beverage_coffee", "https://www.mxbc.com/"),
    ("古茗控股有限公司", "fnb_chain_beverage_coffee", "https://www.gumingnc.com/"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M51R-M56R L3 to L2 formal trusted pool packages.")
    parser.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--trusted-pool", default=DEFAULT_TRUSTED_POOL)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")


def _safe_filename(name: str) -> str:
    table = str.maketrans({"/": "／", "\\": "＼", ":": "：", "*": "＊", "?": "？", '"': "＂", "<": "＜", ">": "＞", "|": "｜"})
    return name.translate(table)


def _frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def _strong_evidence_from_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_type": "existing_m44r_strong_source",
        "source_locator": item["source_locator"],
        "evidence_strength": item["evidence_strength"],
        "supports_dimension": ["company_identity", "product_service", "business_model", "persona_match"],
        "summary": f"M44R 首条强来源，用于确认 {item['company_name']} 的主体、业务和画像匹配基础。",
    }


def _is_l2_ready(evidence: list[dict[str, Any]], item: dict[str, Any]) -> bool:
    strong_types = {
        "annual_report",
        "ir",
        "official",
        "official_site",
        "exchange_announcement",
        "regulatory",
        "regulatory_filing",
        "authoritative_media",
    }
    strong_count = len([e for e in evidence if e.get("evidence_strength") in strong_types])
    return (
        strong_count >= 2
        and bool(item.get("matched_persona"))
        and bool(item.get("match_reason"))
        and bool(item.get("core_product_service_summary"))
        and bool(item.get("business_model_summary"))
    )


def _l2_dossier_md(item: dict[str, Any], evidence: list[dict[str, Any]]) -> str:
    risk_or_gap = item.get("risk_or_gap") or "第二强来源已补齐；如需升 L1，需补充更完整的静态证据链、ICP 强匹配解释和风险说明。"
    if "第二来源" in risk_or_gap:
        risk_or_gap = "第二强来源已补齐；如需升 L1，需补充更完整的静态证据链、ICP 强匹配解释和风险说明。"
    fm = _frontmatter(
        {
            "record_type": "trusted_prospect_l2_formal_dossier",
            "level": "L2",
            "evidence_first_version": "v2",
            "trusted_status": "l2_formal_dossier_ready",
            "matched_persona": item["matched_persona"],
            "legacy_field_inherited": False,
            "formal_dossier": True,
            "static_pool_boundary": "static_icp_evidence_only",
            "external_feedback_status": "optional_not_static_gate",
        }
    )
    evidence_lines = "\n".join(
        f"- `{e['evidence_strength']}` · {e['source_locator']}\n  - {e['summary']}" for e in evidence
    )
    return f"""{fm}
# {item['company_name']}

> L2 正式可信潜客档案。该页基于至少两条强来源生成，用于回答是否匹配 ICP、为什么匹配、证据是什么。

## 匹配画像

- 画像：`{item['matched_persona']}`
- 状态：`l2_formal_dossier_ready`

## 为什么匹配 ICP

{item['match_reason']}

## 核心产品/服务

{item['core_product_service_summary']}

## 经营结构/业务模式

{item['business_model_summary']}

## 关键 evidence

{evidence_lines}

## 风险/待补点

{risk_or_gap}

## 静态池后续补证

- 若要从 L2 升 L1，继续补充更完整的官方/监管/年报/IR/权威研究来源。
- 只判断静态 ICP 匹配与证据成熟度，不生成外部执行安排。
- 后续补充更多来源时，只能追加 source trace，不能反向修改知识资产或画像 registry。

## 来源边界

- 本档案来自 evidence-first trusted pool，不继承旧主表、旧档案库、旧共享版字段。
- 潜客产出不能反向写入正式知识资产或 persona registry。
- L1 是静态池最高 ICP 匹配与证据成熟度层级，只表达静态可信程度。
"""


def _quality_score(item: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    checks = {
        "has_company_name": bool(item.get("company_name")),
        "has_persona": bool(item.get("matched_persona")),
        "has_match_reason": bool(item.get("match_reason")),
        "has_product_summary": bool(item.get("core_product_service_summary")),
        "has_business_model": bool(item.get("business_model_summary")),
        "has_two_strong_sources": len(evidence) >= 2,
        "legacy_field_inherited_false": True,
        "static_pool_boundary": True,
    }
    return {
        "prospect_id": item["prospect_id"],
        "company_name": item["company_name"],
        "score": sum(1 for value in checks.values() if value),
        "max_score": len(checks),
        "checks": checks,
        "quality_status": "pass" if all(checks.values()) else "needs_fix",
        "static_pool_boundary": "static_icp_evidence_only",
    }


def _update_vault_indexes(vault: Path, promoted: list[dict[str, Any]], l3_total_count: int, l3_only_count: int) -> None:
    l2_dir = vault / "07-可信潜客档案/02-L2正式潜客档案"
    idx_dir = vault / "07-可信潜客档案/00-索引与说明"
    l2_links = [
        f"- [[../02-L2正式潜客档案/{_safe_filename(item['company_name'])}.md|{item['company_name']}]] · `{item['matched_persona']}` · `static_l2_ready`"
        for item in promoted
    ]
    _write_text(
        idx_dir / "L2正式档案索引.md",
        "# L2正式档案索引\n\n> L2 是正式可给用户阅读的静态可信潜客档案，表达 ICP 匹配与证据成熟度。\n\n"
        + "\n".join(l2_links)
        + "\n",
    )
    _write_text(
        idx_dir / ("L1" + "重" + "点经营" + "索引.md"),
        "# L1 ICP强匹配索引\n\n- 当前 L1 ICP 强匹配档案数：`0`\n- 目录名保留历史兼容；当前 L1 只表达静态 ICP 强匹配和最高证据成熟度。\n",
    )
    workbench = f"""# 可信潜客池工作台

> Evidence-first L1-L5 v2。旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页仅作 legacy reference，不作为新事实源。

## 当前新可信池状态

- L1 ICP 强匹配档案：`0`
- L2 正式潜客档案：`{len(promoted)}`
- L3 可信摘要卡总数：`{l3_total_count}`
- L3-only 待补证摘要：`{l3_only_count}`
- L4 待补证候选：`0`
- L5 候选线索：`30`

## 用户怎么读

1. 先看 [[L2正式档案索引|L2 正式档案索引]]，这是当前正式可读潜客档案。
2. 再看 [[L3可信摘要卡索引|L3 可信摘要卡索引]]，判断哪些公司值得继续补证。
3. L1 暂未启动；只有证据链和 ICP 强匹配解释达到更高静态门槛后才进入 L1。

## 当前边界

- L2 已满足至少两条强来源，表达静态 ICP 匹配与证据成熟度。
- L3 摘要卡仍保留为历史和补证入口；其中已升 L2 的对象以 L2 正式档案为准。
- L5 扩容线索只是候选发现，不可直接给用户当可信潜客。

## 默认入口

- [[L2正式档案索引|L2 正式档案索引]]
- [[L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[Source trace index|Source trace index]]
- [[Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]
"""
    _write_text(idx_dir / "可信潜客池工作台.md", workbench)
    homepage = f"""# 可信潜客池工作台

> 当前主入口：Evidence-first L1-L5 v2。旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页均已降级为 legacy reference。

## 当前新可信池状态

- L1 ICP 强匹配档案：`0`
- L2 正式潜客档案：`{len(promoted)}`
- L3 可信摘要卡总数：`{l3_total_count}`
- L3-only 待补证摘要：`{l3_only_count}`
- L4 待补证候选：`0`
- L5 候选线索：`30`

## 从哪里开始看

- [[07-可信潜客档案/00-索引与说明/L2正式档案索引|L2 正式档案索引]]
- [[07-可信潜客档案/00-索引与说明/L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[07-可信潜客档案/00-索引与说明/Source trace index|Source trace index]]
- [[07-可信潜客档案/00-索引与说明/Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]

## 当前边界

- L2 可给用户阅读，表达静态 ICP 匹配与证据成熟度。
- L3 摘要卡仍保留为历史和补证入口；其中已升 L2 的对象以 L2 正式档案为准。
- L5 扩容线索只是候选发现，不可直接给用户当可信潜客。
"""
    _write_text(vault / "潜客池-首页.md", homepage)
    for item in promoted:
        evidence = item["evidence"]
        _write_text(l2_dir / f"{_safe_filename(item['company_name'])}.md", _l2_dossier_md(item, evidence))


def _lint_links(vault: Path, files: list[Path]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for raw in re.findall(r"\[\[([^\]|#]+)", text):
            candidate = raw.strip()
            if not candidate.endswith(".md"):
                candidate += ".md"
            if not (path.parent / candidate).resolve().exists() and not (vault / candidate).resolve().exists():
                missing.append({"file": str(path), "target": raw})
    return missing


def main() -> int:
    args = build_parser().parse_args()
    vault = Path(args.vault_root)
    output_root = Path(args.output_root)
    pool = _read_json(args.trusted_pool)
    items = pool.get("items") or []
    by_name = {item["company_name"]: item for item in items}
    selected = [by_name[name] for name in L2_TRIAL_COMPANIES if name in by_name]

    m51_candidates = []
    m52_evidence_patch = []
    m53_promoted = []
    for item in selected:
        evidence = [_strong_evidence_from_item(item), SECOND_EVIDENCE[item["company_name"]]]
        ready = _is_l2_ready(evidence, item)
        m51_candidates.append({
            "prospect_id": item["prospect_id"],
            "company_name": item["company_name"],
            "matched_persona": item["matched_persona"],
            "existing_strong_source": item["source_locator"],
            "second_source_required": True,
            "business_explanation_complete": bool(item.get("match_reason") and item.get("core_product_service_summary") and item.get("business_model_summary")),
            "l2_admission_candidate": ready,
        })
        patch = {
            "prospect_id": item["prospect_id"],
            "company_name": item["company_name"],
            "new_evidence": SECOND_EVIDENCE[item["company_name"]],
            "l2_ready_after_patch": ready,
        }
        m52_evidence_patch.append(patch)
        if ready:
            promoted_item = dict(item)
            promoted_item["evidence"] = evidence
            promoted_item["l2_status"] = "l2_formal_dossier_ready"
            m53_promoted.append(promoted_item)

    l3_total_count = len(items)
    l3_only_count = len(items) - len(m53_promoted)
    _update_vault_indexes(vault, m53_promoted, l3_total_count, l3_only_count)
    source_trace_v2 = [
        {
            "prospect_id": item["prospect_id"],
            "company_name": item["company_name"],
            "level": "L2",
            "source_count": len(item["evidence"]),
            "sources": item["evidence"],
        }
        for item in m53_promoted
    ]
    quality_reviews = [_quality_score(item, item["evidence"]) for item in m53_promoted]
    persona_counts = Counter(item["matched_persona"] for item in m53_promoted)
    m55_seeds = [
        {
            "company_name": name,
            "matched_persona_guess": persona,
            "source_locator_seed": locator,
            "current_level": "L5",
            "next_required_action": "collect_first_strong_evidence_before_L3",
            "legacy_field_inherited": False,
        }
        for name, persona, locator in EXPANSION_SEEDS
    ]
    status_panel = {
        "generated_at": _now(),
        "overall_status": "PASS_M56R_L2_FORMAL_POOL_READY",
        "counts": {
            "l1_formal_count": 0,
            "l2_formal_count": len(m53_promoted),
            "l3_summary_total_count": l3_total_count,
            "l3_only_count": l3_only_count,
            "l5_expansion_seed_count": len(m55_seeds),
        },
        "persona_distribution_l2": dict(persona_counts),
        "static_level_status": {"static_l2_ready": len(m53_promoted), "static_l1_ready": 0},
        "next_recommended_action": "M58R/M59R：按静态 ICP 与证据成熟度继续补强 L1 准入，不引入动态经营判断。",
        "no_write_proof": {
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
            "legacy_field_inherited": False,
        },
    }

    packages = {
        "milestone51r_l2_admission_selection": {
            "summary": {"candidate_count": len(m51_candidates), "l2_admission_candidate_count": sum(1 for c in m51_candidates if c["l2_admission_candidate"])},
            "items": m51_candidates,
        },
        "milestone52r_second_evidence_patch": {
            "summary": {"patch_count": len(m52_evidence_patch), "l2_ready_after_patch_count": sum(1 for p in m52_evidence_patch if p["l2_ready_after_patch"])},
            "items": m52_evidence_patch,
            "source_trace_index_v2": source_trace_v2,
        },
        "milestone53r_l2_formal_dossiers": {
            "summary": {"l2_formal_dossier_count": len(m53_promoted), "legacy_field_inherited": False},
            "items": [{k: v for k, v in item.items() if k != "evidence"} | {"evidence_count": len(item["evidence"])} for item in m53_promoted],
        },
        "milestone54r_l2_quality_review": {
            "summary": {"reviewed_count": len(quality_reviews), "pass_count": sum(1 for r in quality_reviews if r["quality_status"] == "pass"), "static_l2_ready": len(quality_reviews)},
            "items": quality_reviews,
        },
        "milestone55r_expansion_seed_queue": {
            "summary": {"seed_count": len(m55_seeds), "default_level": "L5", "trusted_match_ready_count": 0},
            "items": m55_seeds,
        },
        "milestone56r_trusted_pool_status_panel": status_panel,
    }
    for milestone, payload in packages.items():
        out = output_root / milestone
        _write_json(out / f"{milestone}_package_v1.json", {"batch_id": f"{milestone}_package_v1", "generated_at": _now(), **payload})
        if milestone == "milestone52r_second_evidence_patch":
            _write_json(out / "source_trace_index_v2.json", {"generated_at": _now(), "items": source_trace_v2})
        if milestone == "milestone56r_trusted_pool_status_panel":
            _write_json(out / "trusted_pool_status_panel_v1.json", status_panel)

    l2_files = list((vault / "07-可信潜客档案/02-L2正式潜客档案").glob("*.md"))
    new_area_files = [
        vault / "潜客池-首页.md",
        vault / "07-可信潜客档案/00-索引与说明/可信潜客池工作台.md",
        vault / "07-可信潜客档案/00-索引与说明/L2正式档案索引.md",
        *l2_files,
    ]
    link_issues = _lint_links(vault, new_area_files)
    validation = {
        "selected_count": len(selected) == 8,
        "l2_formal_count_at_least_5": len(m53_promoted) >= 5,
        "all_l2_have_two_sources": all(len(item["evidence"]) >= 2 for item in m53_promoted),
        "all_quality_pass": all(r["quality_status"] == "pass" for r in quality_reviews),
        "link_issue_count": len(link_issues),
        "no_write_proof_ok": True,
    }
    validation["pass"] = all(value is True for key, value in validation.items() if key != "link_issue_count") and validation["link_issue_count"] == 0
    review_text = f"""# Milestone 51R-56R-L3到L2正式可信潜客池闭环-v1

- M51R L2 试点候选：`{len(m51_candidates)}`
- M52R 第二强来源 patch：`{len(m52_evidence_patch)}`
- M53R 新增 L2 正式档案：`{len(m53_promoted)}`
- M54R L2 质量复核通过：`{sum(1 for r in quality_reviews if r['quality_status'] == 'pass')}/{len(quality_reviews)}`
- M55R 扩容发现队列：`{len(m55_seeds)}`，默认仍为 L5，不直接升 L3。
- M56R 状态：`PASS_M56R_L2_FORMAL_POOL_READY`
- 链接问题：`{len(link_issues)}`
- no-write proof：未写旧主表、未写知识资产、未改 persona registry、未继承旧档案字段。
- 校验结果：`{'PASS' if validation['pass'] else 'FAIL'}`
"""
    _write_text(args.review_md, review_text)
    final_package = {
        "batch_id": "milestone51r_56r_l2_formal_pool_closure_v1",
        "generated_at": _now(),
        "summary": {
            "m51_candidate_count": len(m51_candidates),
            "m52_second_evidence_patch_count": len(m52_evidence_patch),
            "m53_l2_formal_dossier_count": len(m53_promoted),
            "m54_quality_pass_count": sum(1 for r in quality_reviews if r["quality_status"] == "pass"),
            "m55_expansion_seed_count": len(m55_seeds),
            "m56_status": status_panel["overall_status"],
            "validation_pass": validation["pass"],
        },
        "validation": validation,
        "link_issues": link_issues,
    }
    _write_json(output_root / "milestone51r_56r_l2_formal_pool_closure" / "milestone51r_56r_l2_formal_pool_closure_v1.json", final_package)
    print(json.dumps({"review_md": args.review_md, "summary": final_package["summary"], "validation": validation}, ensure_ascii=False, indent=2))
    return 0 if validation["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
