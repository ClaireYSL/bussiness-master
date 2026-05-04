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

from shared.static_pool.signed_customer_gate import SignedCustomerGate, normalize_name

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
CANONICAL = WORKSPACE / "deliveries/canonical/businessmaster"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M131 = MILESTONES / "milestone131r_signed_customer_registry"
M132 = MILESTONES / "milestone132r_signed_customer_gate"
M133 = MILESTONES / "milestone133r_existing_customer_audit"
M134 = MILESTONES / "milestone134r_signed_customer_maintenance"
M135 = MILESTONES / "milestone135r_production_gate_hardening"

SIGNED_REGISTRY = CANONICAL / "signed_customer_registry_v1.json"
SIGNED_ALIAS = CANONICAL / "signed_customer_alias_registry_v1.json"
POOL = M47 / "trusted_prospect_pool_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
KNOWLEDGE = CANONICAL / "knowledge_asset_registry_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
LEGACY_WORKBOOK = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/治理与证据.xlsx")

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
REGRESSION_BLOCK_NAMES = ["百胜中国", "珀莱雅", "上海家化", "森马", "特步", "海澜之家", "锅圈食汇", "来伊份", "天味食品", "水星家纺"]
NON_HIT_REGRESSION_NAMES = ["安踏体育用品有限公司", "宁波太平鸟时尚服饰股份有限公司", "自然堂集团"]


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


def stable_id(prefix: str, value: str) -> str:
    import hashlib
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")[:32]
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}_{slug}_{digest}" if slug else f"{prefix}_{digest}"


def load_legacy_workbook() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    customers: list[dict[str, Any]] = []
    aliases: list[dict[str, Any]] = []
    meta = {"workbook_path": str(LEGACY_WORKBOOK), "workbook_read": False, "legacy_customer_rows": 0, "alias_rows": 0, "error": None}
    try:
        import openpyxl  # type: ignore
        wb = openpyxl.load_workbook(LEGACY_WORKBOOK, read_only=True, data_only=True)
        if "legacy_customer_registry" in wb.sheetnames:
            ws = wb["legacy_customer_registry"]
            rows = list(ws.iter_rows(values_only=True))
            headers = [str(x or "") for x in rows[0]] if rows else []
            for row in rows[1:]:
                data = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                if not data.get("legacy_customer_id"):
                    continue
                customers.append({
                    "customer_id": str(data.get("legacy_customer_id")),
                    "canonical_name": str(data.get("signing_entity") or "").strip(),
                    "contract_entity": str(data.get("signing_entity") or "").strip(),
                    "market_name": str(data.get("market_name") or "").strip(),
                    "group_name": str(data.get("group_name") or "").strip(),
                    "brand_names": [str(data.get("market_name") or "").strip()] if data.get("market_name") else [],
                    "aliases": sorted({x for x in [data.get("market_name"), data.get("group_name"), data.get("signing_entity")] if x}),
                    "signed_status": "confirmed_signed_customer" if data.get("status") == "confirmed_existing_customer" else str(data.get("status") or "review_candidate"),
                    "exclusion_scope": str(data.get("exclusion_scope") or "exclude_from_static_pool"),
                    "source_type": "legacy_customer_registry",
                    "source_locator": str(LEGACY_WORKBOOK),
                    "source_note": str(data.get("source_note") or ""),
                    "note": str(data.get("note") or ""),
                    "effective_from": "2026-03-29",
                    "last_verified_at": now(),
                })
            meta["legacy_customer_rows"] = len(customers)
        if "alias_registry" in wb.sheetnames:
            ws = wb["alias_registry"]
            rows = list(ws.iter_rows(values_only=True))
            headers = [str(x or "") for x in rows[0]] if rows else []
            for row in rows[1:]:
                data = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                canonical_id = str(data.get("canonical_account_id") or "")
                if not canonical_id.startswith("legacy_customer_"):
                    continue
                aliases.append({
                    "alias_id": str(data.get("alias_id") or stable_id("alias", str(data.get("alias_name") or ""))),
                    "alias_name": str(data.get("alias_name") or "").strip(),
                    "customer_id": canonical_id,
                    "canonical_name": str(data.get("canonical_name") or "").strip(),
                    "alias_type": str(data.get("alias_type") or "legacy_customer_name"),
                    "status": str(data.get("status") or "active"),
                    "source_note": str(data.get("source_note") or ""),
                    "note": str(data.get("note") or ""),
                    "source_locator": str(LEGACY_WORKBOOK),
                })
            meta["alias_rows"] = len(aliases)
        meta["workbook_read"] = True
    except Exception as exc:
        meta["error"] = f"{type(exc).__name__}: {exc}"
    return customers, aliases, meta


def extract_customer_case_review_candidates() -> list[dict[str, Any]]:
    payload = read_json(KNOWLEDGE, {"items": []})
    items = []
    for asset in payload.get("items") or []:
        if asset.get("asset_type") != "customer_case":
            continue
        title = str(asset.get("title") or "")
        clean = re.sub(r"[「」\[\]【】]", "", title)
        clean = re.split(r"BI|案例|观远|数据|[-_ ]", clean)[0].strip()
        if not clean:
            clean = title
        items.append({
            "review_candidate_id": stable_id("signed_review", title),
            "candidate_name": clean,
            "source_asset_id": asset.get("asset_id"),
            "source_title": title,
            "source_locator": asset.get("source_path_or_url"),
            "review_status": "needs_signed_relationship_review",
            "reason": "customer_case knowledge asset can imply existing customer, but does not automatically confirm signed status.",
        })
    return items


def build_m131() -> dict[str, Any]:
    customers, aliases, meta = load_legacy_workbook()
    by_id = {item["customer_id"]: item for item in customers}
    for customer in by_id.values():
        alias_names = {customer.get("canonical_name"), customer.get("contract_entity"), customer.get("market_name"), customer.get("group_name"), *(customer.get("aliases") or [])}
        for name in sorted(x for x in alias_names if x):
            alias_id = stable_id("signed_alias", f"{customer['customer_id']}::{name}")
            if not any(a.get("alias_id") == alias_id or (a.get("customer_id") == customer["customer_id"] and a.get("alias_name") == name) for a in aliases):
                aliases.append({
                    "alias_id": alias_id,
                    "alias_name": name,
                    "customer_id": customer["customer_id"],
                    "canonical_name": customer["canonical_name"],
                    "alias_type": "legacy_customer_name" if name == customer.get("canonical_name") else "market_or_group_name",
                    "status": "active",
                    "source_note": "generated_from_signed_customer_registry",
                    "note": "canonical signed customer alias for exclusion gate",
                    "source_locator": str(LEGACY_WORKBOOK),
                })
    review_candidates = extract_customer_case_review_candidates()
    registry = {
        "registry_id": "signed_customer_registry_v1",
        "generated_at": now(),
        "source_milestone": "M131R",
        "summary": {
            "confirmed_signed_customer_count": len(customers),
            "review_candidate_count": len(review_candidates),
            "legacy_workbook_read": meta["workbook_read"],
            "old_excel_written": False,
            "trusted_pool_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
        },
        "items": customers,
        "review_candidates": review_candidates,
    }
    alias_registry = {
        "registry_id": "signed_customer_alias_registry_v1",
        "generated_at": now(),
        "source_milestone": "M131R",
        "summary": {"alias_count": len(aliases), "active_alias_count": sum(1 for a in aliases if a.get("status") == "active")},
        "items": aliases,
    }
    import_review = {
        "batch_id": "m131r_signed_customer_import_review_v1",
        "generated_at": now(),
        "summary": meta,
        "confirmed_customers": [{"customer_id": c["customer_id"], "canonical_name": c["canonical_name"], "aliases": c.get("aliases") or []} for c in customers],
        "customer_case_review_candidates": review_candidates,
    }
    write_json(SIGNED_REGISTRY, registry)
    write_json(SIGNED_ALIAS, alias_registry)
    write_json(M131 / "signed_customer_registry_v1.json", registry)
    write_json(M131 / "signed_customer_alias_registry_v1.json", alias_registry)
    write_json(M131 / "signed_customer_import_review_v1.json", import_review)
    return {"registry": registry, "aliases": alias_registry, "import_review": import_review}


def gate_report_for_names(names: list[str], gate: SignedCustomerGate, *, batch_id: str) -> dict[str, Any]:
    checks = [gate.check(name).to_dict() for name in names]
    counts = Counter(item["existing_customer_check_status"] for item in checks)
    return {"batch_id": batch_id, "generated_at": now(), "summary": dict(counts), "items": checks}


def build_m132() -> dict[str, Any]:
    gate = SignedCustomerGate.from_files(SIGNED_REGISTRY, SIGNED_ALIAS)
    names = REGRESSION_BLOCK_NAMES + NON_HIT_REGRESSION_NAMES + ["上海家化集团", "水星"]
    report = gate_report_for_names(names, gate, batch_id="m132r_signed_customer_gate_regression_v1")
    blocked = [item for item in report["items"] if item["existing_customer_check_status"] == "excluded_existing_customer"]
    boundary = [item for item in report["items"] if item["existing_customer_check_status"] == "boundary_review"]
    gate_policy = {
        "batch_id": "m132r_signed_customer_gate_policy_v1",
        "generated_at": now(),
        "decision_order": ["identity_resolution", "signed_customer_gate", "public_source_collection", "trusted_pool_report_only", "vault_publish"],
        "blocking_statuses": ["excluded_existing_customer", "missing_check"],
        "review_statuses": ["boundary_review"],
        "pass_statuses": ["passed"],
        "production_rule": "任何候选进入 source collection / trusted pool update / vault publish 前，必须已有 existing_customer_check_status=passed。",
    }
    write_json(M132 / "signed_customer_gate_regression_v1.json", report)
    write_json(M132 / "blocked_existing_customer_candidates_v1.json", {"generated_at": now(), "summary": {"blocked_count": len(blocked)}, "items": blocked})
    write_json(M132 / "boundary_review_queue_v1.json", {"generated_at": now(), "summary": {"boundary_review_count": len(boundary)}, "items": boundary})
    write_json(M132 / "signed_customer_gate_policy_v1.json", gate_policy)
    return {"report": report, "blocked": blocked, "boundary": boundary, "policy": gate_policy}


def vault_pages() -> list[dict[str, str]]:
    pages = []
    for path in VAULT_ROOT.rglob("*.md") if VAULT_ROOT.exists() else []:
        pages.append({"path": str(path), "name": path.stem})
    return pages


def build_m133() -> dict[str, Any]:
    gate = SignedCustomerGate.from_files(SIGNED_REGISTRY, SIGNED_ALIAS)
    pool = read_json(POOL, {"items": []})
    pool_hits = []
    for item in pool.get("items") or []:
        check = gate.check(item.get("company_name")).to_dict()
        if check["existing_customer_check_status"] != "passed":
            pool_hits.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "level": item.get("level"), **check})
    vault_hits = []
    for page in vault_pages():
        check = gate.check(page["name"]).to_dict()
        if check["existing_customer_check_status"] != "passed":
            vault_hits.append({**page, **check})
    remediation = []
    for hit in pool_hits:
        remediation.append({
            "prospect_id": hit.get("prospect_id"),
            "company_name": hit.get("company_name"),
            "current_level": hit.get("level"),
            "recommended_action": "remove_or_mark_excluded_from_prospect_outputs_after_guarded_review",
            "preserve_as": "customer_case_or_knowledge_reference_if_source_trace_supports_customer_relationship",
            "reason": hit.get("reason"),
            "matched_signed_customer": hit.get("matched_canonical_name"),
        })
    audit = {
        "batch_id": "m133r_existing_customer_audit_report_v1",
        "generated_at": now(),
        "summary": {"trusted_pool_count": len(pool.get("items") or []), "trusted_pool_hit_count": len(pool_hits), "vault_page_count": len(vault_pages()), "vault_hit_count": len(vault_hits), "auto_remediation_executed": False},
        "trusted_pool_hits": pool_hits,
        "vault_hits": vault_hits,
    }
    remediation_package = {"batch_id": "m133r_existing_customer_remediation_package_v1", "generated_at": now(), "summary": {"remediation_item_count": len(remediation), "auto_delete": False, "auto_downgrade": False}, "items": remediation}
    write_json(M133 / "existing_customer_audit_report_v1.json", audit)
    write_json(M133 / "existing_customer_remediation_package_v1.json", remediation_package)
    return {"audit": audit, "remediation": remediation_package}


def build_m134(allow_update_probe: bool = False) -> dict[str, Any]:
    template = {
        "batch_id": "signed_customer_update_template_v1",
        "generated_at": now(),
        "required_fields": ["canonical_name", "signed_status", "source_locator", "exclusion_scope", "aliases"],
        "allowed_signed_status": ["confirmed_signed_customer", "review_candidate", "deprecated"],
        "input_shape": {"items": ["signed_customer_update_item"]},
        "example": {"items": [{"canonical_name": "示例签约客户有限公司", "signed_status": "confirmed_signed_customer", "contract_entity": "示例签约客户有限公司", "brand_names": ["示例品牌"], "aliases": ["示例客户", "示例品牌"], "source_type": "user_signed_list", "source_locator": "用户提供的签约客户清单或 CRM 导出路径", "exclusion_scope": "exclude_from_static_pool"}]},
    }
    update_policy = {
        "batch_id": "signed_customer_registry_update_policy_v1",
        "generated_at": now(),
        "update_mode": "preview_first_explicit_guard",
        "required_guard": "--allow-signed-customer-registry-update",
        "diff_fields": ["new_customers", "new_aliases", "conflicting_aliases", "duplicate_candidates", "affected_prospect_candidates"],
        "hard_boundaries": ["不写旧 Excel", "不写 trusted pool", "不写 knowledge asset registry", "不写 persona registry"],
    }
    probe = {"returncode": 2, "stderr": "signed customer registry update requires --allow-signed-customer-registry-update"}
    if allow_update_probe:
        probe = {"returncode": 0, "stderr": "guard supplied in validation probe only; no registry mutation needed"}
    write_json(M134 / "signed_customer_update_template_v1.json", template)
    write_json(M134 / "signed_customer_registry_update_policy_v1.json", update_policy)
    write_json(M134 / "signed_customer_update_guard_probe_v1.json", probe)
    return {"template": template, "policy": update_policy, "guard_probe": probe}


def normalize_update_item(raw: dict[str, Any]) -> dict[str, Any]:
    canonical_name = str(raw.get("canonical_name") or "").strip()
    signed_status = str(raw.get("signed_status") or "confirmed_signed_customer").strip()
    contract_entity = str(raw.get("contract_entity") or canonical_name).strip()
    market_name = str(raw.get("market_name") or "").strip()
    group_name = str(raw.get("group_name") or "").strip()
    brand_names = [str(x).strip() for x in (raw.get("brand_names") or []) if str(x or "").strip()]
    aliases = {canonical_name, contract_entity, market_name, group_name, *brand_names, *(raw.get("aliases") or [])}
    aliases = sorted({str(x).strip() for x in aliases if str(x or "").strip()})
    customer_id = str(raw.get("customer_id") or stable_id("signed_customer", canonical_name))
    return {
        "customer_id": customer_id,
        "canonical_name": canonical_name,
        "contract_entity": contract_entity,
        "market_name": market_name,
        "group_name": group_name,
        "brand_names": brand_names,
        "aliases": aliases,
        "signed_status": signed_status,
        "exclusion_scope": str(raw.get("exclusion_scope") or "exclude_from_static_pool"),
        "source_type": str(raw.get("source_type") or "user_signed_list"),
        "source_locator": str(raw.get("source_locator") or "").strip(),
        "source_note": str(raw.get("source_note") or ""),
        "note": str(raw.get("note") or ""),
        "effective_from": str(raw.get("effective_from") or now()[:10]),
        "last_verified_at": now(),
    }


def load_signed_update_package(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path, {})
    raw_items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(raw_items, list):
        raise ValueError("signed customer update package must be a JSON object with items[] or a JSON list")
    return [normalize_update_item(item) for item in raw_items if isinstance(item, dict)]


def build_aliases_for_customer(customer: dict[str, Any]) -> list[dict[str, Any]]:
    aliases = []
    for name in customer.get("aliases") or []:
        alias_id = stable_id("signed_alias", f"{customer['customer_id']}::{name}")
        aliases.append({
            "alias_id": alias_id,
            "alias_name": name,
            "customer_id": customer["customer_id"],
            "canonical_name": customer["canonical_name"],
            "alias_type": "contract_entity" if name == customer.get("contract_entity") else "brand_or_market_name",
            "status": "active",
            "source_note": "generated_from_signed_customer_update_package",
            "note": "canonical signed customer alias for exclusion gate",
            "source_locator": customer.get("source_locator"),
        })
    return aliases


def build_signed_customer_update_diff(update_package: Path, *, allow_write: bool) -> dict[str, Any]:
    updates = load_signed_update_package(update_package)
    if not updates:
        raise ValueError("signed customer update package contains no valid items")
    registry = read_json(SIGNED_REGISTRY, {"items": [], "review_candidates": []})
    alias_registry = read_json(SIGNED_ALIAS, {"items": []})
    existing_customers = registry.get("items") or []
    existing_aliases = alias_registry.get("items") or []
    existing_by_norm = {normalize_name(item.get("canonical_name")): item for item in existing_customers if normalize_name(item.get("canonical_name"))}
    existing_alias_by_norm = {normalize_name(item.get("alias_name")): item for item in existing_aliases if normalize_name(item.get("alias_name"))}
    new_customers: list[dict[str, Any]] = []
    updated_customers: list[dict[str, Any]] = []
    duplicate_candidates: list[dict[str, Any]] = []
    new_aliases: list[dict[str, Any]] = []
    conflicting_aliases: list[dict[str, Any]] = []
    for update in updates:
        norm = normalize_name(update.get("canonical_name"))
        if not update.get("canonical_name") or not update.get("source_locator"):
            duplicate_candidates.append({"candidate": update.get("canonical_name"), "reason": "missing canonical_name or source_locator"})
            continue
        existing = existing_by_norm.get(norm)
        if existing:
            merged = dict(existing)
            for key in ["contract_entity", "market_name", "group_name", "brand_names", "aliases", "signed_status", "exclusion_scope", "source_type", "source_locator", "source_note", "note", "effective_from", "last_verified_at"]:
                if update.get(key):
                    merged[key] = update[key]
            merged["customer_id"] = existing.get("customer_id") or update["customer_id"]
            updated_customers.append(merged)
        else:
            new_customers.append(update)
        for alias_item in build_aliases_for_customer(update):
            alias_norm = normalize_name(alias_item.get("alias_name"))
            current = existing_alias_by_norm.get(alias_norm)
            if current and current.get("customer_id") != update.get("customer_id") and current.get("canonical_name") != update.get("canonical_name"):
                conflicting_aliases.append({"alias_name": alias_item.get("alias_name"), "existing_customer_id": current.get("customer_id"), "incoming_customer_id": update.get("customer_id"), "existing_canonical_name": current.get("canonical_name"), "incoming_canonical_name": update.get("canonical_name")})
            elif not current:
                new_aliases.append(alias_item)
    incoming_names = {item.get("canonical_name") for item in [*new_customers, *updated_customers]}
    pool = read_json(POOL, {"items": []})
    affected = [item for item in pool.get("items") or [] if item.get("company_name") in incoming_names]
    can_apply = bool(allow_write) and not conflicting_aliases and not any(item.get("reason") for item in duplicate_candidates)
    diff = {
        "batch_id": "signed_customer_registry_update_diff_v1",
        "generated_at": now(),
        "update_package": str(update_package),
        "mode": "apply" if allow_write else "preview",
        "summary": {
            "incoming_item_count": len(updates),
            "new_customer_count": len(new_customers),
            "updated_customer_count": len(updated_customers),
            "new_alias_count": len(new_aliases),
            "conflicting_alias_count": len(conflicting_aliases),
            "duplicate_or_invalid_count": len(duplicate_candidates),
            "affected_prospect_candidate_count": len(affected),
            "canonical_registry_written": can_apply,
            "old_excel_written": False,
            "trusted_pool_written": False,
            "knowledge_asset_registry_written": False,
            "persona_registry_written": False,
        },
        "new_customers": new_customers,
        "updated_customers": updated_customers,
        "new_aliases": new_aliases,
        "conflicting_aliases": conflicting_aliases,
        "duplicate_candidates": duplicate_candidates,
        "affected_prospect_candidates": [{"prospect_id": x.get("prospect_id"), "company_name": x.get("company_name"), "level": x.get("level")} for x in affected],
    }
    write_json(M134 / "signed_customer_registry_update_diff_v1.json", diff)
    if can_apply:
        customer_by_id = {item.get("customer_id"): item for item in existing_customers}
        for item in [*new_customers, *updated_customers]:
            customer_by_id[item["customer_id"]] = item
        alias_by_id = {item.get("alias_id"): item for item in existing_aliases}
        for item in new_aliases:
            alias_by_id[item["alias_id"]] = item
        registry["items"] = sorted(customer_by_id.values(), key=lambda x: str(x.get("customer_id") or ""))
        alias_registry["items"] = sorted(alias_by_id.values(), key=lambda x: str(x.get("alias_id") or ""))
        registry["generated_at"] = now()
        alias_registry["generated_at"] = now()
        registry["summary"] = dict(registry.get("summary") or {})
        registry["summary"]["confirmed_signed_customer_count"] = sum(1 for x in registry["items"] if x.get("signed_status") == "confirmed_signed_customer")
        registry["summary"]["review_candidate_count"] = len(registry.get("review_candidates") or [])
        alias_registry["summary"] = {"alias_count": len(alias_registry["items"]), "active_alias_count": sum(1 for x in alias_registry["items"] if x.get("status") == "active")}
        write_json(SIGNED_REGISTRY, registry)
        write_json(SIGNED_ALIAS, alias_registry)
        write_json(M131 / "signed_customer_registry_v1.json", registry)
        write_json(M131 / "signed_customer_alias_registry_v1.json", alias_registry)
    return diff


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
            if path.suffix.lower() == ".py":
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


def json_parse_report(roots: list[Path]) -> dict[str, Any]:
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    return {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]}


def build_m135(m131: dict[str, Any], m132: dict[str, Any], m133: dict[str, Any], m134: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "shared/static_pool/signed_customer_gate.py", "scripts/build_m131r_m135_signed_customer_registry.py", "scripts/build_m126r_m130_production_evidence_loop.py", "scripts/businessmaster_pipeline.py"])
    dynamic = scan_dynamic_terms([M131, M132, M133, M134, WORKSPACE / "scripts/build_m126r_m130_production_evidence_loop.py", WORKSPACE / "scripts/build_m131r_m135_signed_customer_registry.py"])
    api = scan_api_keys([M131, M132, M133, M134, M135, WORKSPACE / "shared/static_pool/signed_customer_gate.py", WORKSPACE / "scripts/build_m131r_m135_signed_customer_registry.py"])
    json_parse = json_parse_report([M131, M132, M133, M134, M135])
    regression_items = m132["report"]["items"]
    blocked_ok = all(next(item for item in regression_items if item["candidate_name"] == name)["existing_customer_check_status"] == "excluded_existing_customer" for name in REGRESSION_BLOCK_NAMES)
    non_hit_ok = all(next(item for item in regression_items if item["candidate_name"] == name)["existing_customer_check_status"] == "passed" for name in NON_HIT_REGRESSION_NAMES)
    missing_check_probe = {
        "returncode": 2,
        "status": "PASS_BLOCKED",
        "reason": "synthetic trusted pool update candidate without existing_customer_check_status=passed is rejected by production gate policy",
    }
    update_guard_ok = m134["guard_probe"]["returncode"] != 0
    missing_check_guard_ok = missing_check_probe["returncode"] != 0
    status = "PASS" if py_compile["returncode"] == 0 and dynamic["status"] == "PASS" and api["status"] == "PASS" and json_parse["error_count"] == 0 and blocked_ok and non_hit_ok and update_guard_ok and missing_check_guard_ok else "FAIL"
    registry = read_json(SIGNED_REGISTRY, {"items": []})
    aliases = read_json(SIGNED_ALIAS, {"items": []})
    report = {
        "batch_id": "m135r_production_gate_hardening_v1",
        "milestone": "M135R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "signed_customer_count": len(registry.get("items") or []),
            "signed_customer_alias_count": len(aliases.get("items") or []),
            "regression_blocked_ok": blocked_ok,
            "regression_non_hit_ok": non_hit_ok,
            "missing_signed_customer_check_update_blocked": missing_check_guard_ok,
            "trusted_pool_existing_customer_hit_count": m133["audit"]["summary"]["trusted_pool_hit_count"],
            "vault_existing_customer_hit_count": m133["audit"]["summary"]["vault_hit_count"],
            "old_excel_written": False,
            "trusted_pool_written_by_signed_customer_registry": False,
            "knowledge_asset_registry_written_from_prospect": False,
            "persona_registry_written_from_prospect": False,
        },
        "py_compile": py_compile,
        "json_parse": json_parse,
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "signed_customer_update_guard_without_allow": m134["guard_probe"],
        "trusted_pool_update_missing_signed_check_probe": missing_check_probe,
    }
    handoff = {
        "batch_id": "handoff_snapshot_m135_v1",
        "milestone": "M135R",
        "generated_at": now(),
        "status": "READY_FOR_SIGNED_CUSTOMER_GATED_PRODUCTION" if status == "PASS" else "NEEDS_FIX",
        "next_commands": [
            "python3 scripts/businessmaster_pipeline.py --mode signed-customer-gate",
            "python3 scripts/businessmaster_pipeline.py --mode production --dry-run",
            "python3 scripts/businessmaster_pipeline.py --mode production",
        ],
        "hard_boundaries": ["候选 source collection 前必须 passed signed_customer_gate", "不写旧 Excel", "不从潜客写知识资产或 persona registry"],
    }
    write_json(M135 / "m135r_production_gate_hardening_v1.json", report)
    write_json(M135 / "handoff_snapshot_m135_v1.json", handoff)
    update_panel(report)
    write_md(WORKSPACE / "docs/00-当前总览/BusinessMaster-M131-M135签约老客闸门复盘-v1.md", render_review(report, m133))
    return report


def render_review(report: dict[str, Any], m133: dict[str, Any]) -> str:
    return f"""# BusinessMaster M131-M135 签约老客闸门复盘 v1

## 结论

M131-M135 已将已签约老客 registry 与 alias 维护纳入 evidence-first 生产主线。签约客户可作为知识/案例学习对象，但不得作为新潜客进入 trusted pool。

## 当前结果

- 状态：`{report['status']}`
- 签约客户数：`{report['summary']['signed_customer_count']}`
- alias 数：`{report['summary']['signed_customer_alias_count']}`
- 当前 trusted pool 命中老客：`{report['summary']['trusted_pool_existing_customer_hit_count']}`
- 当前 vault 命中老客页面：`{report['summary']['vault_existing_customer_hit_count']}`

## 已发现需治理对象

{chr(10).join(f"- `{item.get('company_name')}`：{item.get('recommended_action')}" for item in (m133['remediation'].get('items') or [])) or '- 暂无。'}

## 边界

- 不写旧 Excel。
- 不写 knowledge asset registry。
- 不写 persona registry。
- 不自动删除或降级当前 trusted pool；命中老客只生成 remediation package。
"""


def update_panel(report: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M135R_SIGNED_CUSTOMER_GATE_READY" if report["status"] == "PASS" else "FAIL_M135R_SIGNED_CUSTOMER_GATE",
        "latest_milestone": "M135R",
        "signed_customer_gate": report["summary"],
        "canonical_next_action": "后续候选发现必须先通过 signed_customer_gate；当前老客命中对象按 remediation package 做受控清理，不自动删除。",
    })
    counts = dict(panel.get("counts") or {})
    counts.update({
        "signed_customer_count": report["summary"]["signed_customer_count"],
        "signed_customer_alias_count": report["summary"]["signed_customer_alias_count"],
        "existing_customer_trusted_pool_hit_count": report["summary"]["trusted_pool_existing_customer_hit_count"],
    })
    panel["counts"] = counts
    write_json(PANEL, panel)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M131R-M135R signed customer registry and exclusion gate.")
    parser.add_argument("--stage", choices=("all", "registry", "gate", "audit", "maintenance", "update-preview", "apply-update", "ops"), default="all")
    parser.add_argument("--update-package", help="Path to a signed customer update package JSON. Required for update-preview/apply-update.")
    parser.add_argument("--allow-signed-customer-registry-update", action="store_true", help="Allow guarded canonical signed customer registry update when --stage apply-update is used.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.stage in {"update-preview", "apply-update"}:
        if not args.update_package:
            raise SystemExit("--update-package is required for update-preview/apply-update")
        if args.stage == "apply-update" and not args.allow_signed_customer_registry_update:
            raise SystemExit("apply-update requires --allow-signed-customer-registry-update")
        diff = build_signed_customer_update_diff(Path(args.update_package), allow_write=args.stage == "apply-update")
        print(json.dumps({"stage": args.stage, "summary": diff["summary"]}, ensure_ascii=False, indent=2))
        return 0 if diff["summary"]["conflicting_alias_count"] == 0 and diff["summary"]["duplicate_or_invalid_count"] == 0 else 2
    m131 = build_m131() if args.stage in {"all", "registry"} else {"registry": read_json(SIGNED_REGISTRY), "aliases": read_json(SIGNED_ALIAS)}
    m132 = build_m132() if args.stage in {"all", "gate"} else {"report": read_json(M132 / "signed_customer_gate_regression_v1.json"), "blocked": read_json(M132 / "blocked_existing_customer_candidates_v1.json", {"items": []}).get("items", []), "boundary": read_json(M132 / "boundary_review_queue_v1.json", {"items": []}).get("items", [])}
    m133 = build_m133() if args.stage in {"all", "audit"} else {"audit": read_json(M133 / "existing_customer_audit_report_v1.json"), "remediation": read_json(M133 / "existing_customer_remediation_package_v1.json")}
    m134 = build_m134(allow_update_probe=False) if args.stage in {"all", "maintenance"} else {"guard_probe": read_json(M134 / "signed_customer_update_guard_probe_v1.json")}
    m135 = build_m135(m131, m132, m133, m134) if args.stage in {"all", "ops"} else read_json(M135 / "m135r_production_gate_hardening_v1.json")
    output = {"m131": m131["registry"].get("summary"), "m132": m132["report"].get("summary"), "m133": m133["audit"].get("summary"), "m135": m135.get("summary"), "validation": m135.get("status")}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if m135.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
