from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[2]
SIGNED_CUSTOMER_REGISTRY_V2 = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_registry_v2.json"
SIGNED_CUSTOMER_ALIAS_REGISTRY_V2 = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_alias_registry_v2.json"
SIGNED_CUSTOMER_REGISTRY_V1 = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_registry_v1.json"
SIGNED_CUSTOMER_ALIAS_REGISTRY_V1 = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_alias_registry_v1.json"
DEFAULT_SIGNED_CUSTOMER_REGISTRY = SIGNED_CUSTOMER_REGISTRY_V2
DEFAULT_SIGNED_CUSTOMER_ALIAS_REGISTRY = SIGNED_CUSTOMER_ALIAS_REGISTRY_V2

LEGAL_SUFFIX_PATTERNS = [
    r"股份有限公司$",
    r"有限责任公司$",
    r"有限公司$",
    r"集团股份$",
    r"集团$",
    r"控股有限公司$",
    r"控股$",
    r"\(中国\)$",
    r"（中国）$",
    r"中国$",
]


def read_json(path: str | Path, default: Any | None = None) -> Any:
    p = Path(path)
    if not p.exists():
        return {} if default is None else default
    return json.loads(p.read_text(encoding="utf-8"))


def normalize_name(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("（", "(").replace("）", ")")
    text = re.sub(r"[\s·•,，。.;；:：/\\|\-—_]+", "", text)
    for pattern in LEGAL_SUFFIX_PATTERNS:
        text = re.sub(pattern.lower(), "", text)
    return text


def compact_name(value: Any) -> str:
    return re.sub(r"[\s·•,，。.;；:：/\\|\-—_（）()]+", "", str(value or "").strip().lower())


@dataclass(frozen=True)
class SignedCustomerMatch:
    status: str
    candidate_name: str
    matched_customer_id: str | None = None
    matched_canonical_name: str | None = None
    matched_alias_name: str | None = None
    match_type: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "existing_customer_check_status": self.status,
            "candidate_name": self.candidate_name,
            "matched_customer_id": self.matched_customer_id,
            "matched_canonical_name": self.matched_canonical_name,
            "matched_alias_name": self.matched_alias_name,
            "match_type": self.match_type,
            "reason": self.reason,
        }


class SignedCustomerGate:
    def __init__(self, customers: list[dict[str, Any]], aliases: list[dict[str, Any]]) -> None:
        self.customers = [item for item in customers if item.get("signed_status") in {"confirmed_signed_customer", "confirmed_existing_customer"}]
        self.aliases = [item for item in aliases if item.get("status") == "active"]
        self.customer_by_id = {str(item.get("customer_id") or item.get("legacy_customer_id") or ""): item for item in self.customers}
        self.exact_index: dict[str, tuple[dict[str, Any], str, str]] = {}
        self.compact_index: dict[str, tuple[dict[str, Any], str, str]] = {}
        self._build_indexes()

    @classmethod
    def from_files(
        cls,
        registry_path: str | Path = DEFAULT_SIGNED_CUSTOMER_REGISTRY,
        alias_path: str | Path = DEFAULT_SIGNED_CUSTOMER_ALIAS_REGISTRY,
    ) -> "SignedCustomerGate":
        registry_file = Path(registry_path)
        alias_file = Path(alias_path)
        if registry_file == DEFAULT_SIGNED_CUSTOMER_REGISTRY and not registry_file.exists():
            registry_file = SIGNED_CUSTOMER_REGISTRY_V1
        if alias_file == DEFAULT_SIGNED_CUSTOMER_ALIAS_REGISTRY and not alias_file.exists():
            alias_file = SIGNED_CUSTOMER_ALIAS_REGISTRY_V1
        registry = read_json(registry_file, {"items": []})
        alias_registry = read_json(alias_file, {"items": []})
        return cls(registry.get("items") or [], alias_registry.get("items") or [])

    def _add_name(self, customer: dict[str, Any], name: Any, match_type: str) -> None:
        if not name:
            return
        norm = normalize_name(name)
        compact = compact_name(name)
        if norm:
            self.exact_index.setdefault(norm, (customer, str(name), match_type))
        if compact:
            self.compact_index.setdefault(compact, (customer, str(name), match_type))

    def _build_indexes(self) -> None:
        for customer in self.customers:
            self._add_name(customer, customer.get("canonical_name"), "canonical_name")
            self._add_name(customer, customer.get("contract_entity"), "contract_entity")
            self._add_name(customer, customer.get("market_name"), "market_name")
            self._add_name(customer, customer.get("group_name"), "group_name")
            for name in customer.get("brand_names") or []:
                self._add_name(customer, name, "brand_name")
            for name in customer.get("aliases") or []:
                self._add_name(customer, name, "customer_alias")
        for alias in self.aliases:
            customer = self.customer_by_id.get(str(alias.get("customer_id") or alias.get("canonical_customer_id") or alias.get("canonical_account_id") or ""))
            if not customer:
                continue
            self._add_name(customer, alias.get("alias_name"), str(alias.get("alias_type") or "alias"))

    def check(self, candidate_name: Any) -> SignedCustomerMatch:
        name = str(candidate_name or "").strip()
        if not name:
            return SignedCustomerMatch(status="missing_check", candidate_name=name, reason="candidate_name is empty")
        norm = normalize_name(name)
        compact = compact_name(name)
        if norm in self.exact_index:
            customer, alias_name, match_type = self.exact_index[norm]
            return self._excluded(name, customer, alias_name, match_type, "exact_normalized_match")
        if compact in self.compact_index:
            customer, alias_name, match_type = self.compact_index[compact]
            return self._excluded(name, customer, alias_name, match_type, "exact_compact_match")
        fuzzy = self._fuzzy_match(norm, compact)
        if fuzzy:
            customer, alias_name, match_type, reason = fuzzy
            return SignedCustomerMatch(
                status="boundary_review",
                candidate_name=name,
                matched_customer_id=customer.get("customer_id"),
                matched_canonical_name=customer.get("canonical_name"),
                matched_alias_name=alias_name,
                match_type=match_type,
                reason=reason,
            )
        return SignedCustomerMatch(status="passed", candidate_name=name, reason="no signed customer match")

    def _excluded(self, name: str, customer: dict[str, Any], alias_name: str, match_type: str, reason: str) -> SignedCustomerMatch:
        return SignedCustomerMatch(
            status="excluded_existing_customer",
            candidate_name=name,
            matched_customer_id=customer.get("customer_id"),
            matched_canonical_name=customer.get("canonical_name"),
            matched_alias_name=alias_name,
            match_type=match_type,
            reason=reason,
        )

    def _fuzzy_match(self, norm: str, compact: str) -> tuple[dict[str, Any], str, str, str] | None:
        if len(norm) < 2 and len(compact) < 3:
            return None
        for key, (customer, alias_name, match_type) in self.exact_index.items():
            if len(key) >= 3 and (key in norm or norm in key) and key != norm:
                return customer, alias_name, match_type, "partial_normalized_name_overlap"
        for key, (customer, alias_name, match_type) in self.compact_index.items():
            if len(key) >= 4 and (key in compact or compact in key) and key != compact:
                return customer, alias_name, match_type, "partial_compact_name_overlap"
        return None


def check_candidate(candidate_name: Any, registry_path: str | Path = DEFAULT_SIGNED_CUSTOMER_REGISTRY, alias_path: str | Path = DEFAULT_SIGNED_CUSTOMER_ALIAS_REGISTRY) -> dict[str, Any]:
    return SignedCustomerGate.from_files(registry_path, alias_path).check(candidate_name).to_dict()
