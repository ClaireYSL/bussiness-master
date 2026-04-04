from __future__ import annotations

from .models import PromotionGateResult, ValidationResult, dataclass_to_dict


def render_validation_summary(result: ValidationResult) -> str:
    lines = [
        f"- account_id: `{result.account_id}`",
        f"- candidate_type: `{result.candidate_type}`",
        f"- review_status: `{result.review_status}`",
        f"- formal_l5: `{'yes' if result.is_formal_l5_candidate else 'no'}`",
        f"- normalized_persona_tag: `{result.normalized_persona_tag or 'n/a'}`",
        f"- normalized_secondary_persona_tags: `{', '.join(result.normalized_secondary_persona_tags) or 'n/a'}`",
        f"- required_queue_type: `{result.required_queue_type or 'n/a'}`",
        f"- summary: {result.summary}",
    ]
    if result.issues:
        lines.append("- blocking_issues:")
        for issue in result.issues:
            lines.append(f"  - `{issue.field_name or issue.code}`: {issue.message}")
    if result.warnings:
        lines.append("- warnings:")
        for issue in result.warnings:
            lines.append(f"  - `{issue.field_name or issue.code}`: {issue.message}")
    return "\n".join(lines)


def render_promotion_gate_summary(result: PromotionGateResult) -> str:
    lines = [
        f"- account_id: `{result.account_id}`",
        f"- decision: `{result.decision}`",
        f"- normalized_persona_tag: `{result.normalized_persona_tag or 'n/a'}`",
        f"- normalized_secondary_persona_tags: `{', '.join(result.normalized_secondary_persona_tags) or 'n/a'}`",
        f"- suggested_review_status: `{result.suggested_review_status or 'n/a'}`",
        f"- suggested_queue_type: `{result.suggested_queue_type or 'n/a'}`",
        f"- summary: {result.summary}",
    ]
    if result.blocking_issues:
        lines.append("- blocking_issues:")
        for issue in result.blocking_issues:
            lines.append(f"  - `{issue.field_name or issue.code}`: {issue.message}")
    if result.warning_issues:
        lines.append("- warning_issues:")
        for issue in result.warning_issues:
            lines.append(f"  - `{issue.field_name or issue.code}`: {issue.message}")
    return "\n".join(lines)


def to_jsonable(result) -> dict:
    return dataclass_to_dict(result)
