from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any


@dataclass
class CandidateRecord:
    account_id: str
    account_canonical_name: str
    primary_track: str = ""
    persona_tag: str = ""
    review_status: str = ""
    validation_gap: str = ""


@dataclass
class EvidenceRecord:
    account_id: str
    source_locator: str = ""
    source_type: str = ""
    evidence_strength: str = ""
    summary: str = ""


@dataclass
class ValidationIssue:
    code: str
    severity: str
    field_name: str = ""
    message: str = ""


@dataclass
class ValidationResult:
    account_id: str
    candidate_type: str
    review_status: str
    is_formal_l5_candidate: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    required_queue_type: str = ""
    summary: str = ""
    normalized_fields: dict[str, str] = field(default_factory=dict)


@dataclass
class PromotionGateResult:
    account_id: str
    decision: str
    blocking_issues: list[ValidationIssue] = field(default_factory=list)
    warning_issues: list[ValidationIssue] = field(default_factory=list)
    suggested_review_status: str = ""
    suggested_queue_type: str = ""
    summary: str = ""


def dataclass_to_dict(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: dataclass_to_dict(item) for key, item in value.items()}
    return value
