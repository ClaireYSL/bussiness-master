from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


STRONG_SOURCE_TYPES = {
    "annual_report",
    "exchange_announcement",
    "ir",
    "official",
    "official_site",
    "regulatory",
    "regulatory_filing",
    "sec_annual_report",
}


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


def _is_strong_evidence(evidence: dict[str, Any]) -> bool:
    strength = _clean(evidence.get("evidence_strength")).lower()
    source_type = _clean(evidence.get("source_type")).lower()
    locator = _clean(evidence.get("source_locator")).lower()
    return (
        strength in STRONG_SOURCE_TYPES
        or source_type in STRONG_SOURCE_TYPES
        or any(token in locator for token in ("annual", "ir.", "investor", "cninfo", "sse.com", "szse.cn", "sec.gov", "官网"))
    )


def collect_evidence(item: dict[str, Any], source_trace_by_prospect: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    if _clean(item.get("source_locator")):
        evidence.append(
            {
                "source_locator": item.get("source_locator"),
                "evidence_strength": item.get("evidence_strength"),
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
    if strong_count == 2:
        gaps.append({"queue_type": "source_gap_queue", "field": "l1_evidence_chain", "reason": "L1 需要更完整的静态证据链。"})

    if strong_count >= 3 and all([has_persona, has_match_reason, has_product, has_business_model, has_risk]):
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
        summary=f"{_clean(item.get('company_name'))} 静态升层建议：{current_level} -> {suggested}，强来源={strong_count}。",
    )
