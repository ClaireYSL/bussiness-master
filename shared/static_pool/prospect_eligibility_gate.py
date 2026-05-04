from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shared.static_pool.signed_customer_gate import SignedCustomerGate, normalize_name

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_ENTITY_REGISTRY = WORKSPACE / "deliveries/canonical/businessmaster/account_entity_registry_v1.json"

NON_COMPANY_TOKENS = ["案例", "方案", "对话", "CTO", "CIO", "访谈", "复盘", "方法论", "汇报", "交流", "观远", "不用", "如何用"]


def read_json(path: str | Path, default: Any | None = None) -> Any:
    p = Path(path)
    if not p.exists():
        return {} if default is None else default
    return json.loads(p.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ProspectEligibilityResult:
    status: str
    candidate_name: str
    reason: str
    matched_entity_id: str | None = None
    matched_entity_name: str | None = None
    matched_prospect_id: str | None = None
    signed_customer_match: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "prospect_eligibility_status": self.status,
            "candidate_name": self.candidate_name,
            "reason": self.reason,
            "matched_entity_id": self.matched_entity_id,
            "matched_entity_name": self.matched_entity_name,
            "matched_prospect_id": self.matched_prospect_id,
            "signed_customer_match": self.signed_customer_match,
        }


class ProspectEligibilityGate:
    def __init__(self, entity_registry: dict[str, Any] | None = None, signed_gate: SignedCustomerGate | None = None) -> None:
        self.entity_registry = entity_registry or read_json(DEFAULT_ENTITY_REGISTRY, {"items": []})
        self.signed_gate = signed_gate or SignedCustomerGate.from_files()
        self.entity_index: dict[str, dict[str, Any]] = {}
        self._build_index()

    @classmethod
    def from_files(cls, entity_registry_path: str | Path = DEFAULT_ENTITY_REGISTRY) -> "ProspectEligibilityGate":
        return cls(read_json(entity_registry_path, {"items": []}))

    def _build_index(self) -> None:
        for entity in self.entity_registry.get("items") or []:
            names = {entity.get("canonical_name"), *(entity.get("aliases") or [])}
            for name in names:
                key = normalize_name(name)
                if key:
                    self.entity_index.setdefault(key, entity)

    def check(self, candidate_name: Any, prospect_id: Any | None = None) -> ProspectEligibilityResult:
        name = str(candidate_name or "").strip()
        if not name:
            return ProspectEligibilityResult("missing_entity_check", name, "candidate_name is empty")
        if self._looks_non_company(name):
            return ProspectEligibilityResult("excluded_non_company", name, "candidate name looks like a case title/person/material, not a company")
        signed = self.signed_gate.check(name).to_dict()
        if signed["existing_customer_check_status"] == "excluded_existing_customer":
            return ProspectEligibilityResult("excluded_signed_customer", name, "matched signed customer registry", signed_customer_match=signed)
        if signed["existing_customer_check_status"] == "boundary_review":
            return ProspectEligibilityResult("boundary_review", name, "possible signed customer alias overlap", signed_customer_match=signed)
        key = normalize_name(name)
        entity = self.entity_index.get(key)
        if entity and "trusted_pool" in (entity.get("entity_roles") or []):
            existing_pid = str(entity.get("prospect_id") or "")
            if prospect_id and existing_pid and existing_pid == str(prospect_id):
                return ProspectEligibilityResult("eligible_prospect", name, "same prospect_id update is allowed", entity.get("entity_id"), entity.get("canonical_name"), existing_pid)
            return ProspectEligibilityResult("duplicate_existing_prospect", name, "entity already exists in trusted pool", entity.get("entity_id"), entity.get("canonical_name"), existing_pid)
        return ProspectEligibilityResult("eligible_prospect", name, "passed eligibility gate")

    def _looks_non_company(self, name: str) -> bool:
        if len(name) > 36:
            return True
        return any(token in name for token in NON_COMPANY_TOKENS)


def check_candidate(candidate_name: Any, prospect_id: Any | None = None) -> dict[str, Any]:
    return ProspectEligibilityGate.from_files().check(candidate_name, prospect_id).to_dict()
