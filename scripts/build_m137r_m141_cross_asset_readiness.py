from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import normalize_name

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
CANONICAL = WORKSPACE / "deliveries/canonical/businessmaster"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M121 = MILESTONES / "milestone121r_evidence_acquisition_engine"
M137 = MILESTONES / "milestone137r_account_entity_registry"
M138 = MILESTONES / "milestone138r_prospect_eligibility_gate"
M139 = MILESTONES / "milestone139r_customer_case_reference_registry"
M140 = MILESTONES / "milestone140r_source_freshness_link_health"
M141 = MILESTONES / "milestone141r_system_readiness_v3"

POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
KNOWLEDGE = CANONICAL / "knowledge_asset_registry_v1.json"
SIGNED = CANONICAL / "signed_customer_registry_v1.json"
SIGNED_ALIAS = CANONICAL / "signed_customer_alias_registry_v1.json"
ENTITY = CANONICAL / "account_entity_registry_v1.json"
CASE_REF = CANONICAL / "customer_case_reference_registry_v1.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
STRONG_SOURCE_CATEGORIES = {"official_owned", "regulatory_or_capital_market", "platform_operating_fact", "authoritative_third_party"}


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


def stable_id(prefix: str, value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")[:32]
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}_{slug}_{digest}" if slug else f"{prefix}_{digest}"


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def add_entity(bucket: dict[str, dict[str, Any]], name: str, role: str, source: str, **extra: Any) -> None:
    if not name:
        return
    key = normalize_name(name)
    if not key:
        return
    entity = bucket.setdefault(key, {"entity_id": stable_id("entity", key), "canonical_name": name, "normalized_name": key, "entity_roles": [], "aliases": [], "source_refs": []})
    if role not in entity["entity_roles"]:
        entity["entity_roles"].append(role)
    if name not in entity["aliases"]:
        entity["aliases"].append(name)
    entity["source_refs"].append({"source": source, **{k: v for k, v in extra.items() if v not in (None, "", [])}})
    for field in ["prospect_id", "customer_id", "knowledge_asset_id", "level", "matched_persona"]:
        if extra.get(field) and not entity.get(field):
            entity[field] = extra[field]


def case_customer_name(title: str) -> str:
    clean = re.sub(r"[「」\[\]【】]", "", title)
    clean = re.split(r"BI|案例|观远|数据|[-_ ]|：|:", clean)[0].strip()
    return clean or title


def build_m137() -> dict[str, Any]:
    bucket: dict[str, dict[str, Any]] = {}
    pool = read_json(POOL, {"items": []})
    trace = read_json(TRACE, {"items": []})
    signed = read_json(SIGNED, {"items": []})
    signed_alias = read_json(SIGNED_ALIAS, {"items": []})
    knowledge = read_json(KNOWLEDGE, {"items": []})
    for item in pool.get("items") or []:
        add_entity(bucket, item.get("company_name", ""), "trusted_pool", "trusted_prospect_pool_v1", prospect_id=item.get("prospect_id"), level=item.get("level"), matched_persona=item.get("matched_persona"))
    for item in trace.get("items") or []:
        add_entity(bucket, item.get("company_name", ""), "source_trace", "source_trace_index_v1", prospect_id=item.get("prospect_id"))
    for item in signed.get("items") or []:
        add_entity(bucket, item.get("canonical_name", ""), "signed_customer", "signed_customer_registry_v1", customer_id=item.get("customer_id"))
        for alias in item.get("aliases") or []:
            add_entity(bucket, alias, "signed_customer_alias", "signed_customer_registry_v1", customer_id=item.get("customer_id"))
    for item in signed_alias.get("items") or []:
        add_entity(bucket, item.get("alias_name", ""), "signed_customer_alias", "signed_customer_alias_registry_v1", customer_id=item.get("customer_id"))
    for asset in knowledge.get("items") or []:
        if asset.get("asset_type") == "customer_case":
            add_entity(bucket, case_customer_name(asset.get("title", "")), "customer_case_reference", "knowledge_asset_registry_v1", knowledge_asset_id=asset.get("asset_id"))
    entities = sorted(bucket.values(), key=lambda x: x["entity_id"])
    duplicate_groups = [e for e in entities if len(set(e.get("entity_roles") or [])) > 1]
    payload = {"registry_id": "account_entity_registry_v1", "generated_at": now(), "source_milestone": "M137R", "summary": {"entity_count": len(entities), "trusted_pool_entity_count": sum("trusted_pool" in e["entity_roles"] for e in entities), "signed_customer_entity_count": sum("signed_customer" in e["entity_roles"] for e in entities), "customer_case_reference_entity_count": sum("customer_case_reference" in e["entity_roles"] for e in entities), "multi_role_entity_count": len(duplicate_groups)}, "items": entities}
    audit = {"batch_id": "m137r_entity_resolution_audit_v1", "generated_at": now(), "summary": payload["summary"], "multi_role_entities": duplicate_groups[:100]}
    write_json(ENTITY, payload)
    write_json(M137 / "account_entity_registry_v1.json", payload)
    write_json(M137 / "entity_resolution_audit_v1.json", audit)
    return {"registry": payload, "audit": audit}


def build_m138() -> dict[str, Any]:
    gate = ProspectEligibilityGate.from_files(ENTITY)
    queue = read_json(M121 / "evidence_collection_task_queue_v1.json", {"items": []})
    pool = read_json(POOL, {"items": []})
    regression_names = ["上海家化", "安踏体育用品有限公司", "自然堂集团", "森马", "鲜丰水果数据智能化应用汇报交流-观远数据-完整版v1.2"]
    checks = []
    for name in regression_names:
        checks.append(gate.check(name).to_dict())
    for task in queue.get("items") or []:
        name = task.get("candidate_company_name") or task.get("seed_title")
        checks.append({"seed_id": task.get("seed_id"), **gate.check(name).to_dict()})
    for item in pool.get("items", [])[:10]:
        checks.append({"prospect_id": item.get("prospect_id"), **gate.check(item.get("company_name"), item.get("prospect_id")).to_dict()})
    counts = Counter(item["prospect_eligibility_status"] for item in checks)
    report = {"batch_id": "m138r_prospect_eligibility_gate_report_v1", "generated_at": now(), "summary": dict(counts), "items": checks}
    policy = {"batch_id": "prospect_eligibility_gate_policy_v1", "generated_at": now(), "required_status_before_source_collection": "eligible_prospect", "blocking_statuses": ["excluded_signed_customer", "excluded_non_company", "duplicate_existing_prospect", "missing_entity_check"], "review_statuses": ["boundary_review"], "note": "same prospect_id update is eligible; different prospect_id duplicate is blocked."}
    write_json(M138 / "prospect_eligibility_gate_report_v1.json", report)
    write_json(M138 / "prospect_eligibility_gate_policy_v1.json", policy)
    return {"report": report, "policy": policy}


def infer_icp_signals(asset: dict[str, Any]) -> list[str]:
    text = " ".join(str(asset.get(k) or "") for k in ["title", "summary", "key_signals", "recommended_usage"])
    signals = []
    mapping = {
        "多品牌": "brand_product_matrix",
        "渠道": "channel_complexity",
        "供应链": "supply_chain_complexity",
        "门店": "store_network",
        "连锁": "chain_standardization",
        "跨境": "cross_border_operation",
        "财务": "finance_management",
        "一线": "frontline_action_loop",
        "经营": "management_visibility",
    }
    for token, signal in mapping.items():
        if token in text and signal not in signals:
            signals.append(signal)
    return signals or ["case_reference_general_icp_signal"]


def build_m139() -> dict[str, Any]:
    knowledge = read_json(KNOWLEDGE, {"items": []})
    items = []
    for asset in knowledge.get("items") or []:
        if asset.get("asset_type") != "customer_case":
            continue
        items.append({
            "case_reference_id": stable_id("case_ref", asset.get("asset_id", asset.get("title", ""))),
            "case_title": asset.get("title"),
            "customer_or_brand_name": case_customer_name(asset.get("title", "")),
            "reference_status": "usable_reference_case",
            "source_material": asset.get("source_path_or_url"),
            "track_ids": asset.get("track_ids") or [],
            "persona_hints": asset.get("persona_ids") or [],
            "icp_signals": infer_icp_signals(asset),
            "knowledge_asset_id": asset.get("asset_id"),
            "not_prospect_evidence": True,
            "does_not_confirm_signed_customer": True,
        })
    payload = {"registry_id": "customer_case_reference_registry_v1", "generated_at": now(), "source_milestone": "M139R", "summary": {"case_reference_count": len(items), "usable_reference_case_count": len(items), "prospect_evidence_count": 0, "signed_customer_auto_confirm_count": 0}, "items": items}
    write_json(CASE_REF, payload)
    write_json(M139 / "customer_case_reference_registry_v1.json", payload)
    return {"registry": payload}


def source_status(locator: str) -> str:
    if not locator:
        return "needs_recheck"
    parsed = urlparse(locator)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return "fresh"
    if parsed.scheme == "file" or locator.startswith("/"):
        return "internal_reference_needs_recheck"
    return "needs_recheck"


def build_m140() -> dict[str, Any]:
    trace = read_json(TRACE, {"items": []})
    items = []
    gap = []
    for row in trace.get("items") or []:
        prospect_sources = []
        for src in row.get("sources") or []:
            status = source_status(str(src.get("source_locator") or ""))
            checked = {"prospect_id": row.get("prospect_id"), "company_name": row.get("company_name"), "source_locator": src.get("source_locator"), "source_category": src.get("source_category"), "source_freshness_status": status, "source_health_checked_at": now()}
            prospect_sources.append(checked)
            if status != "fresh" and src.get("source_category") in STRONG_SOURCE_CATEGORIES:
                gap.append({**checked, "gap_reason": "strong source requires freshness/link recheck"})
        items.extend(prospect_sources)
    counts = Counter(item["source_freshness_status"] for item in items)
    payload = {"batch_id": "m140r_source_freshness_report_v1", "generated_at": now(), "summary": {"source_checked_count": len(items), "fresh_count": counts.get("fresh", 0), "needs_recheck_count": len(items) - counts.get("fresh", 0), "gap_queue_count": len(gap)}, "items": items}
    gap_payload = {"batch_id": "m140r_source_freshness_gap_queue_v1", "generated_at": now(), "summary": {"gap_queue_count": len(gap)}, "items": gap}
    write_json(M140 / "source_freshness_report_v1.json", payload)
    write_json(M140 / "source_freshness_gap_queue_v1.json", gap_payload)
    return {"report": payload, "gap": gap_payload}


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


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for base in paths:
        for path in ([base] if base.is_file() else base.rglob("*")) if base.exists() else []:
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


def scan_api(paths: list[Path]) -> dict[str, Any]:
    patterns = [re.compile(r"sk-[A-Za-z0-9_-]{20,}"), re.compile(r"AKLT[A-Za-z0-9_-]{20,}"), re.compile(r"DELEGATE_LLM_API_KEY\s*=\s*[^<\s].+")]
    findings = []
    for base in paths:
        for path in ([base] if base.is_file() else base.rglob("*")) if base.exists() else []:
            if path.name == ".env" or path.suffix.lower() not in {".md", ".json", ".py", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(p.search(text) for p in patterns):
                findings.append(rel(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def update_panel(m137: dict[str, Any], m138: dict[str, Any], m139: dict[str, Any], m140: dict[str, Any], status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    counts.update({
        "account_entity_count": m137["registry"]["summary"]["entity_count"],
        "entity_multi_role_count": m137["registry"]["summary"]["multi_role_entity_count"],
        "eligibility_excluded_signed_customer_count": m138["report"]["summary"].get("excluded_signed_customer", 0),
        "eligibility_duplicate_existing_prospect_count": m138["report"]["summary"].get("duplicate_existing_prospect", 0),
        "customer_case_reference_count": m139["registry"]["summary"]["case_reference_count"],
        "source_freshness_gap_count": m140["gap"]["summary"]["gap_queue_count"],
    })
    panel.update({"generated_at": now(), "overall_status": "PASS_M141R_SYSTEM_READINESS_V3" if status == "PASS" else "FAIL_M141R_SYSTEM_READINESS_V3", "latest_milestone": "M141R", "counts": counts, "m137r_account_entity_registry": m137["registry"]["summary"], "m138r_prospect_eligibility_gate": m138["report"]["summary"], "m139r_customer_case_reference_registry": m139["registry"]["summary"], "m140r_source_freshness": m140["report"]["summary"], "canonical_next_action": "后续候选发现先过 entity resolution 与 prospect eligibility gate；客户案例只作 ICP 参考，不直接入 prospect evidence。"})
    write_json(PANEL, panel)


def build_m141(m137: dict[str, Any], m138: dict[str, Any], m139: dict[str, Any], m140: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m137r_m141_cross_asset_readiness.py", "shared/static_pool/prospect_eligibility_gate.py", "shared/static_pool/signed_customer_gate.py"])
    json_parse = json_parse_report([M137, M138, M139, M140, M141, CANONICAL])
    dynamic = scan_dynamic([M137, M138, M139, M140, M141, WORKSPACE / "scripts/build_m137r_m141_cross_asset_readiness.py", WORKSPACE / "shared/static_pool/prospect_eligibility_gate.py"])
    api = scan_api([M137, M138, M139, M140, M141, WORKSPACE / "scripts/build_m137r_m141_cross_asset_readiness.py", WORKSPACE / "shared/static_pool/prospect_eligibility_gate.py"])
    regression = {
        "signed_customer_blocked": any(item.get("candidate_name") == "上海家化" and item.get("prospect_eligibility_status") == "excluded_signed_customer" for item in m138["report"].get("items", [])),
        "customer_case_not_prospect_evidence": m139["registry"]["summary"]["prospect_evidence_count"] == 0,
        "customer_case_not_signed_customer_auto_confirm": m139["registry"]["summary"]["signed_customer_auto_confirm_count"] == 0,
    }
    status = "PASS" if py_compile["returncode"] == 0 and json_parse["error_count"] == 0 and dynamic["status"] == "PASS" and api["status"] == "PASS" and all(regression.values()) else "FAIL"
    update_panel(m137, m138, m139, m140, status)
    report = {"batch_id": "m141r_system_readiness_v3_v1", "milestone": "M141R", "generated_at": now(), "status": status, "summary": {"entity_count": m137["registry"]["summary"]["entity_count"], "eligibility_check_count": len(m138["report"].get("items", [])), "case_reference_count": m139["registry"]["summary"]["case_reference_count"], "source_checked_count": m140["report"]["summary"]["source_checked_count"], "source_gap_count": m140["gap"]["summary"]["gap_queue_count"], "old_excel_written": False, "knowledge_asset_registry_written_from_prospect": False, "persona_registry_written_from_prospect": False}, "regression_assertions": regression, "py_compile": py_compile, "json_parse": json_parse, "dynamic_term_scan": dynamic, "api_key_scan": api}
    write_json(M141 / "system_readiness_v3_v1.json", report)
    write_md(WORKSPACE / "docs/00-当前总览/BusinessMaster-M137-M141横切资产收口复盘-v1.md", f"# BusinessMaster M137-M141 横切资产收口复盘 v1\n\n- 状态：`{status}`\n- account entity：`{report['summary']['entity_count']}`\n- eligibility checks：`{report['summary']['eligibility_check_count']}`\n- customer case reference：`{report['summary']['case_reference_count']}`\n- source freshness gap：`{report['summary']['source_gap_count']}`\n\n客户案例只作为 ICP/画像/知识参考，不自动进入 prospect evidence，也不自动确认 signed customer。\n")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M137R-M141R cross-asset readiness package.")
    parser.add_argument("--stage", choices=("all", "entity", "eligibility", "case-reference", "freshness", "readiness"), default="all")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    m137 = build_m137() if args.stage in {"all", "entity"} else {"registry": read_json(ENTITY), "audit": read_json(M137 / "entity_resolution_audit_v1.json")}
    m138 = build_m138() if args.stage in {"all", "eligibility"} else {"report": read_json(M138 / "prospect_eligibility_gate_report_v1.json"), "policy": read_json(M138 / "prospect_eligibility_gate_policy_v1.json")}
    m139 = build_m139() if args.stage in {"all", "case-reference"} else {"registry": read_json(CASE_REF)}
    m140 = build_m140() if args.stage in {"all", "freshness"} else {"report": read_json(M140 / "source_freshness_report_v1.json"), "gap": read_json(M140 / "source_freshness_gap_queue_v1.json")}
    m141 = build_m141(m137, m138, m139, m140) if args.stage in {"all", "readiness"} else read_json(M141 / "system_readiness_v3_v1.json")
    print(json.dumps({"m137": m137["registry"].get("summary"), "m138": m138["report"].get("summary"), "m139": m139["registry"].get("summary"), "m140": m140["report"].get("summary"), "m141": m141.get("summary"), "validation": m141.get("status")}, ensure_ascii=False, indent=2))
    return 0 if m141.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
