from __future__ import annotations

from collections import Counter

from .constants import (
    FORMAL_L5_REVIEW_STATUS,
    FROZEN_SOURCE_TAGS,
    GENERIC_ADMISSION_HINTS,
    GENERIC_MODEL_HINTS,
    GENERIC_PRODUCT_HINTS,
    GENERIC_PROFILE_TEXT_HINTS,
    LEGACY_REVIEW_STATUS_MAP,
    OBSERVATION_L5_REVIEW_STATUS,
    PLACEHOLDER_VALUES,
    VALID_REVIEW_STATUSES,
)
from .models import PromotionGateResult, ValidationIssue, ValidationResult


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def is_placeholder(value: str) -> bool:
    clean = _clean_text(value)
    if clean in PLACEHOLDER_VALUES:
        return True
    normalized = clean.replace(" ", "")
    return normalized in {item.replace(" ", "") for item in PLACEHOLDER_VALUES}


def normalize_review_status(value: str) -> str:
    clean = _clean_text(value).lower()
    if clean in LEGACY_REVIEW_STATUS_MAP:
        return LEGACY_REVIEW_STATUS_MAP[clean]
    if clean in VALID_REVIEW_STATUSES:
        return clean
    return clean or OBSERVATION_L5_REVIEW_STATUS


def _contains_any(text: object, patterns: tuple[str, ...]) -> bool:
    clean = _clean_text(text)
    if not clean:
        return False
    return any(pattern in clean for pattern in patterns)


def _count_official_evidence(evidence_rows: list[dict]) -> int:
    count = 0
    for row in evidence_rows:
        locator = _clean_text(row.get("source_locator"))
        source_type = _clean_text(row.get("source_type"))
        strength = _clean_text(row.get("evidence_strength") or row.get("strength"))
        if strength.upper() in {"A", "S"}:
            count += 1
            continue
        if any(token in locator.lower() for token in ("官网", "年报", "ir", "investor", "annual", "cninfo", "公告")):
            count += 1
            continue
        if any(token in source_type.lower() for token in ("official", "annual", "ir", "website")):
            count += 1
    return count


def evaluate_minimum_fact_set(main_row: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    fact_fields = (
        "account_canonical_name",
        "primary_track",
        "persona_tag",
        "公司产品与服务概述",
        "商业模式概述",
        "admission_reason_summary",
        "validation_gap",
    )
    for field_name in fact_fields:
        value = _clean_text(main_row.get(field_name))
        if not value:
            issues.append(ValidationIssue("missing_field", "block", field_name, f"{field_name} 不能为空。"))
        elif is_placeholder(value):
            issues.append(ValidationIssue("placeholder_field", "block", field_name, f"{field_name} 仍是占位值。"))

    if _contains_any(main_row.get("公司产品与服务概述"), GENERIC_PRODUCT_HINTS):
        issues.append(ValidationIssue("generic_product", "warn", "公司产品与服务概述", "产品与服务字段仍偏模板句。"))
    if _contains_any(main_row.get("商业模式概述"), GENERIC_MODEL_HINTS):
        issues.append(ValidationIssue("generic_model", "warn", "商业模式概述", "商业模式字段仍偏模板句。"))
    if _contains_any(main_row.get("admission_reason_summary"), GENERIC_ADMISSION_HINTS):
        issues.append(ValidationIssue("generic_admission", "warn", "admission_reason_summary", "入池理由仍偏画像模板。"))
    return issues


def evaluate_track_persona_stability(main_row: dict, evidence_rows: list[dict]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not _clean_text(main_row.get("primary_track")):
        issues.append(ValidationIssue("track_missing", "block", "primary_track", "主线未明确。"))
    if not _clean_text(main_row.get("persona_tag")):
        issues.append(ValidationIssue("persona_missing", "block", "persona_tag", "画像未明确。"))

    official_evidence_count = _count_official_evidence(evidence_rows)
    if official_evidence_count == 0:
        issues.append(ValidationIssue("official_source_missing", "block", "evidence", "缺少可定位的官方或高可信来源。"))
    elif official_evidence_count == 1:
        issues.append(ValidationIssue("evidence_thin", "warn", "evidence", "仅有 1 条较强来源，仍偏薄。"))

    if normalize_review_status(_clean_text(main_row.get("review_status"))) == OBSERVATION_L5_REVIEW_STATUS:
        issues.append(ValidationIssue("persona_boundary_unstable", "warn", "review_status", "当前仍处于观察/边界状态。"))
    return issues


def classify_l5_candidate(main_row: dict, evidence_rows: list[dict]) -> ValidationResult:
    account_id = _clean_text(main_row.get("account_id"))
    normalized_fields = {
        "review_status": normalize_review_status(_clean_text(main_row.get("review_status"))),
        "validation_gap": _clean_text(main_row.get("validation_gap")),
    }
    issues = evaluate_minimum_fact_set(main_row)
    issues.extend(evaluate_track_persona_stability(main_row, evidence_rows))

    blocking = [issue for issue in issues if issue.severity == "block"]
    warnings = [issue for issue in issues if issue.severity != "block"]
    if blocking:
        queue_type = "boundary_review" if any(issue.field_name in {"primary_track", "persona_tag", "review_status"} for issue in blocking + warnings) else "verification"
        summary = "当前对象只满足观察/边界对象条件，不能视为正式 L5 候选。"
        return ValidationResult(
            account_id=account_id,
            candidate_type="observation",
            review_status=OBSERVATION_L5_REVIEW_STATUS,
            is_formal_l5_candidate=False,
            issues=blocking,
            warnings=warnings,
            required_queue_type=queue_type,
            summary=summary,
            normalized_fields=normalized_fields,
        )

    low_confidence_warnings = [issue for issue in warnings if issue.code in {"generic_product", "generic_model", "generic_admission", "evidence_thin"}]
    if low_confidence_warnings:
        summary = "当前对象可入观察/待核验状态，需补强事实或来源后再视作正式候选。"
        return ValidationResult(
            account_id=account_id,
            candidate_type="observation",
            review_status=OBSERVATION_L5_REVIEW_STATUS,
            is_formal_l5_candidate=False,
            issues=[],
            warnings=warnings,
            required_queue_type="verification",
            summary=summary,
            normalized_fields=normalized_fields,
        )

    summary = "当前对象满足正式 L5 候选的最小可信字段集。"
    return ValidationResult(
        account_id=account_id,
        candidate_type="formal_candidate",
        review_status=FORMAL_L5_REVIEW_STATUS,
        is_formal_l5_candidate=True,
        issues=[],
        warnings=warnings,
        required_queue_type="verification",
        summary=summary,
        normalized_fields=normalized_fields,
    )


def evaluate_promotion_gate(main_row: dict, profile_row: dict | None, evidence_rows: list[dict], queue_rows: list[dict]) -> PromotionGateResult:
    account_id = _clean_text(main_row.get("account_id"))
    blocking_issues: list[ValidationIssue] = []
    warning_issues: list[ValidationIssue] = []

    minimum_issues = evaluate_minimum_fact_set(main_row)
    for issue in minimum_issues:
        if issue.severity == "block":
            blocking_issues.append(issue)
        else:
            warning_issues.append(issue)

    stability_issues = evaluate_track_persona_stability(main_row, evidence_rows)
    for issue in stability_issues:
        if issue.severity == "block":
            blocking_issues.append(issue)
        else:
            warning_issues.append(issue)

    normalized_status = normalize_review_status(_clean_text(main_row.get("review_status")))
    if normalized_status not in {FORMAL_L5_REVIEW_STATUS, OBSERVATION_L5_REVIEW_STATUS}:
        blocking_issues.append(ValidationIssue("invalid_review_status", "block", "review_status", "当前状态不在可评估上移范围。"))

    profile_gap = _clean_text((profile_row or {}).get("validation_gap"))
    if profile_gap and any(token in profile_gap for token in ("待补更多信息", "待进一步完善", "待持续观察")):
        blocking_issues.append(ValidationIssue("generic_validation_gap", "block", "validation_gap", "待验证项过于空泛，不能支撑上移。"))

    if _contains_any((profile_row or {}).get("产品与服务长摘录"), GENERIC_PROFILE_TEXT_HINTS):
        warning_issues.append(ValidationIssue("generic_profile_projection", "warn", "产品与服务长摘录", "档案长摘录仍偏阅读层模板。"))
    if _contains_any((profile_row or {}).get("商业模式长摘录"), GENERIC_PROFILE_TEXT_HINTS):
        warning_issues.append(ValidationIssue("generic_profile_projection", "warn", "商业模式长摘录", "商业模式长摘录仍偏阅读层模板。"))

    open_queue_types = Counter(
        _clean_text(row.get("queue_type"))
        for row in queue_rows
        if _clean_text(row.get("status")) in {"", "open", "in_progress"}
    )
    if not open_queue_types["promotion_review"]:
        warning_issues.append(ValidationIssue("promotion_review_missing", "warn", "review_queue", "当前没有开放的 promotion_review 队列项。"))

    if blocking_issues:
        return PromotionGateResult(
            account_id=account_id,
            decision="block",
            blocking_issues=blocking_issues,
            warning_issues=warning_issues,
            suggested_review_status=normalized_status or OBSERVATION_L5_REVIEW_STATUS,
            suggested_queue_type="promotion_review" if not open_queue_types["promotion_review"] else "verification",
            summary="关键判断点仍未收敛，程序不建议推进上移。",
        )
    if warning_issues:
        return PromotionGateResult(
            account_id=account_id,
            decision="warn",
            blocking_issues=[],
            warning_issues=warning_issues,
            suggested_review_status=normalized_status or FORMAL_L5_REVIEW_STATUS,
            suggested_queue_type="promotion_review",
            summary="可继续推进，但仍需显式暴露风险和待补证点。",
        )
    return PromotionGateResult(
        account_id=account_id,
        decision="allow",
        blocking_issues=[],
        warning_issues=[],
        suggested_review_status=FORMAL_L5_REVIEW_STATUS,
        suggested_queue_type="promotion_review",
        summary="关键判断点已收敛，可作为本轮建议推进对象。",
    )


def should_allow_frozen_text_as_input(source_tag: str) -> bool:
    clean = _clean_text(source_tag)
    if not clean:
        return True
    return clean not in FROZEN_SOURCE_TAGS
