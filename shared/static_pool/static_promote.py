from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


SOURCE_CATEGORIES = {
    "official_owned",
    "regulatory_or_capital_market",
    "platform_operating_fact",
    "authoritative_third_party",
    "internal_or_legacy_reference",
}

OFFICIAL_OWNED_TYPES = {
    "official",
    "official_site",
    "official_website",
    "brand_site",
    "official_news",
    "official_channel_page",
    "official_store_locator",
    "official_recruiting",
    "official_wechat",
    "official_miniprogram",
    "ir",
}
REGULATORY_OR_CAPITAL_TYPES = {
    "annual_report",
    "announcement",
    "exchange_announcement",
    "exchange_filing",
    "regulatory",
    "regulatory_filing",
    "sec_annual_report",
    "sec_filing",
    "hkex_filing",
    "cninfo",
    "prospectus",
    "public_transfer_statement",
}
PLATFORM_OPERATING_TYPES = {
    "tmall_store",
    "jd_store",
    "douyin_store",
    "pdd_store",
    "amazon_brand_store",
    "platform_store",
    "app_store",
    "miniprogram",
    "store_network",
    "map_store_network",
    "saas_product_page",
}
AUTHORITATIVE_THIRD_PARTY_TYPES = {
    "authoritative_media",
    "media_report",
    "financing_news",
    "investor_portfolio",
    "industry_association",
    "government_publication",
    "industry_research",
    "research_report",
}
INTERNAL_OR_LEGACY_TYPES = {
    "structured_intake_patch",
    "internal_patch",
    "manual_note",
    "legacy_profile",
    "legacy_workbook",
    "old_vault_dossier",
}

STRONG_SOURCE_CATEGORIES = {
    "official_owned",
    "regulatory_or_capital_market",
    "platform_operating_fact",
    "authoritative_third_party",
}

STRONG_SOURCE_TYPES = (
    OFFICIAL_OWNED_TYPES
    | REGULATORY_OR_CAPITAL_TYPES
    | PLATFORM_OPERATING_TYPES
    | AUTHORITATIVE_THIRD_PARTY_TYPES
)

ICP_SUPPORT_TOKENS = (
    "icp_match_support",
    "brand_product_matrix",
    "chain_store_operations",
    "chain_standardization",
    "multi_store_retail",
    "cross_border_operations",
    "platform_operator",
    "global_brand_operations",
    "channel_complexity",
    "store_network",
    "sku_matrix",
    "multi_region",
    "multi_org",
)


@dataclass
class StaticPromotionDecision:
    prospect_id: str
    company_name: str
    current_level: str
    suggested_level: str
    decision: str
    gap_queue: list[dict[str, str]]
    evidence_count: int
    strong_evidence_count: int
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clean(value: object) -> str:
    return str(value or "").strip()


def _source_category(evidence: dict[str, Any]) -> str:
    explicit = _clean(evidence.get("source_category")).lower()
    if explicit in SOURCE_CATEGORIES:
        return explicit
    strength = _clean(evidence.get("evidence_strength")).lower()
    source_type = _clean(evidence.get("source_type")).lower()
    locator = _clean(evidence.get("source_locator")).lower()
    candidates = {strength, source_type}
    if candidates & INTERNAL_OR_LEGACY_TYPES or locator.startswith("internal://"):
        return "internal_or_legacy_reference"
    if candidates & PLATFORM_OPERATING_TYPES or any(token in locator for token in ("tmall", "jd.com", "douyin", "amazon", "meituan", "dianping", "appstore", "apps.apple")):
        return "platform_operating_fact"
    if candidates & AUTHORITATIVE_THIRD_PARTY_TYPES:
        return "authoritative_third_party"
    if candidates & REGULATORY_OR_CAPITAL_TYPES or any(token in locator for token in ("cninfo", "sse.com", "szse.cn", "sec.gov", "hkexnews", "annual", "prospectus")):
        return "regulatory_or_capital_market"
    if candidates & OFFICIAL_OWNED_TYPES or any(token in locator for token in ("investor", "ir.", "官网")):
        return "official_owned"
    if locator.startswith("http"):
        return "official_owned" if any(token in locator for token in (".com", ".cn", ".com.cn")) else "authoritative_third_party"
    return "internal_or_legacy_reference"


def _is_strong_evidence(evidence: dict[str, Any]) -> bool:
    return _source_category(evidence) in STRONG_SOURCE_CATEGORIES


def _is_l1_countable_evidence(evidence: dict[str, Any]) -> bool:
    return _is_strong_evidence(evidence) and _source_category(evidence) != "internal_or_legacy_reference"


def _has_icp_support(evidence: dict[str, Any]) -> bool:
    supports = _clean(evidence.get("supports_dimension")).lower()
    summary = _clean(evidence.get("summary")).lower()
    return any(token in supports or token in summary for token in ICP_SUPPORT_TOKENS)


def _strong_source_categories(evidence: list[dict[str, Any]]) -> set[str]:
    return {_source_category(row) for row in evidence if _is_l1_countable_evidence(row)}


def collect_evidence(item: dict[str, Any], source_trace_by_prospect: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    if _clean(item.get("source_locator")):
        evidence.append(
            {
                "source_locator": item.get("source_locator"),
                "evidence_strength": item.get("evidence_strength"),
                "source_type": item.get("evidence_strength"),
                "summary": item.get("match_reason") or item.get("core_product_service_summary") or "",
            }
        )
    for source in (source_trace_by_prospect or {}).get(_clean(item.get("prospect_id")), []):
        if isinstance(source, dict):
            evidence.append(source)
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for row in evidence:
        key = (_clean(row.get("source_locator")), _clean(row.get("evidence_strength")))
        if not key[0] or key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def evaluate_static_promotion(
    item: dict[str, Any],
    *,
    source_trace_by_prospect: dict[str, list[dict[str, Any]]] | None = None,
) -> StaticPromotionDecision:
    evidence = collect_evidence(item, source_trace_by_prospect)
    strong_count = sum(1 for row in evidence if _is_strong_evidence(row))
    l1_countable = [row for row in evidence if _is_l1_countable_evidence(row)]
    l1_countable_count = len(l1_countable)
    l1_category_count = len(_strong_source_categories(evidence))
    has_l1_icp_support = any(_has_icp_support(row) for row in l1_countable)
    has_persona = bool(_clean(item.get("matched_persona")))
    has_match_reason = bool(_clean(item.get("match_reason")))
    has_product = bool(_clean(item.get("core_product_service_summary")))
    has_business_model = bool(_clean(item.get("business_model_summary")))
    has_risk = bool(_clean(item.get("risk_or_gap")))
    current_level = _clean(item.get("level") or item.get("current_level") or "L5")
    gaps: list[dict[str, str]] = []

    if not has_persona:
        gaps.append({"queue_type": "persona_gap_queue", "field": "matched_persona", "reason": "缺少 ICP/画像匹配。"})
    if not has_match_reason:
        gaps.append({"queue_type": "persona_gap_queue", "field": "match_reason", "reason": "缺少为什么匹配 ICP 的解释。"})
    if not has_product:
        gaps.append({"queue_type": "evidence_gap_queue", "field": "core_product_service_summary", "reason": "缺少核心产品/服务概述。"})
    if not has_business_model:
        gaps.append({"queue_type": "evidence_gap_queue", "field": "business_model_summary", "reason": "缺少经营结构/业务模式说明。"})
    if not has_risk:
        gaps.append({"queue_type": "source_gap_queue", "field": "risk_or_gap", "reason": "缺少风险/待补点。"})
    if strong_count < 1:
        gaps.append({"queue_type": "source_gap_queue", "field": "strong_evidence", "reason": "至少需要 1 条强来源才能进入 L3。"})
    if strong_count == 1:
        gaps.append({"queue_type": "source_gap_queue", "field": "second_strong_evidence", "reason": "至少需要 2 条强来源才能进入 L2。"})
    if l1_countable_count < 3:
        gaps.append({"queue_type": "source_gap_queue", "field": "l1_evidence_chain", "reason": "L1 需要至少 3 条可定位强来源，且 internal/legacy 不计入。"})
    if l1_category_count < 2:
        gaps.append({"queue_type": "source_gap_queue", "field": "l1_source_category", "reason": "L1 需要至少 2 个不同 source_category，避免只堆叠上市披露。"})
    if not has_l1_icp_support:
        gaps.append({"queue_type": "persona_gap_queue", "field": "l1_icp_support_source", "reason": "L1 至少需要 1 条来源直接支撑 ICP 匹配。"})

    l1_ready = l1_countable_count >= 3 and l1_category_count >= 2 and has_l1_icp_support
    if l1_ready and all([has_persona, has_match_reason, has_product, has_business_model, has_risk]):
        suggested = "L1"
    elif strong_count >= 2 and all([has_persona, has_match_reason, has_product, has_business_model]):
        suggested = "L2"
    elif strong_count >= 1:
        suggested = "L3"
    elif has_persona or has_match_reason:
        suggested = "L4"
    else:
        suggested = "L5"

    order = {"L5": 0, "L4": 1, "L3": 2, "L2": 3, "L1": 4}
    decision = "allow" if order.get(suggested, 0) > order.get(current_level, 0) else "warn" if gaps else "allow"
    return StaticPromotionDecision(
        prospect_id=_clean(item.get("prospect_id")),
        company_name=_clean(item.get("company_name")),
        current_level=current_level,
        suggested_level=suggested,
        decision=decision,
        gap_queue=gaps,
        evidence_count=len(evidence),
        strong_evidence_count=strong_count,
        summary=f"{_clean(item.get('company_name'))} 静态升层建议：{current_level} -> {suggested}，强来源={strong_count}，L1来源类别={l1_category_count}。",
    )
