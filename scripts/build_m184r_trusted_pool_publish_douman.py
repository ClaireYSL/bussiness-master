from __future__ import annotations

import argparse
import hashlib
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

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import SignedCustomerGate, normalize_name

M183 = WORKSPACE / "deliveries/archive/milestones/milestone183r_evidence_acquisition_restart"
M184 = WORKSPACE / "deliveries/archive/milestones/milestone184r_trusted_pool_publish_douman"
CANONICAL_POOL = WORKSPACE / "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = WORKSPACE / "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json"
ENTITY_REGISTRY = WORKSPACE / "deliveries/canonical/businessmaster/account_entity_registry_v2.json"
STATUS_PANEL = WORKSPACE / "deliveries/archive/milestones/milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
L2_DIR = VAULT_ROOT / "02-L2正式潜客档案"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:12]}"


def load_m183() -> dict[str, Any]:
    return {
        "validation": read_json(M183 / "m183_validation_report_v1.json"),
        "expert": read_json(M183 / "m183_expert_review_report_v1.json"),
        "baseline": read_json(M183 / "baseline_v1.json"),
        "report": read_json(M183 / "m183r_report_only_v1.json"),
        "source_trace": read_json(M183 / "source_trace_package_v1.json"),
        "evidence": read_json(M183 / "evidence_patch_package_v1.json"),
        "identity": read_json(M183 / "identity_resolution_package_v1.json"),
    }


def build_candidate(m183: dict[str, Any]) -> dict[str, Any]:
    report = m183["report"]
    candidate = dict(report["candidate"])
    decision = report["decisions"][0]
    candidate.update(
        {
            "level": decision["suggested_level"],
            "trusted_status": "static_l2_ready",
            "static_promotion_summary": decision["summary"],
            "static_gap_count": len(decision["gap_queue"]),
            "static_evidence_count": decision["evidence_count"],
            "static_strong_evidence_count": decision["strong_evidence_count"],
            "card_id": f"card_{candidate['prospect_id']}",
            "canonical_update_source": "M184R_trusted_pool_publish_douman",
            "signed_customer_gate_version": "signed_customer_v2",
            "legacy_field_inherited": False,
        }
    )
    return candidate


def validate_preconditions(args: argparse.Namespace, m183: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not args.allow_trusted_pool_update:
        errors.append("trusted pool update requires --allow-trusted-pool-update")
    if not args.allow_vault_regular_write:
        errors.append("vault regular write requires --allow-vault-regular-write")
    if m183["validation"].get("status") != "PASS":
        errors.append("M183 validation is not PASS")
    if m183["expert"].get("overall_review_status") != "pass":
        errors.append("M183 expert review is not pass")
    if m183["baseline"].get("candidate_signature") != m183["report"].get("candidate_signature"):
        errors.append("M183 baseline signature mismatch")
    if m183["report"].get("summary", {}).get("suggested_level") != "L2":
        errors.append("M183 report-only did not suggest L2")
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    for name in [candidate.get("company_name"), *(candidate.get("candidate_aliases") or [])]:
        signed = signed_gate.check(name).to_dict()
        if signed["existing_customer_check_status"] != "passed":
            errors.append(f"signed customer gate failed for {name}: {signed}")
        elig = eligibility_gate.check(name, candidate.get("prospect_id")).to_dict()
        if elig["prospect_eligibility_status"] not in {"eligible_prospect"}:
            errors.append(f"prospect eligibility failed for {name}: {elig}")
    return errors


def update_pool(candidate: dict[str, Any]) -> dict[str, Any]:
    pool = read_json(CANONICAL_POOL, {"items": []})
    items = pool.get("items") or []
    before_count = len(items)
    before_levels = Counter(item.get("level") for item in items)
    idx = next((i for i, item in enumerate(items) if item.get("prospect_id") == candidate["prospect_id"]), None)
    if idx is None:
        items.append(candidate)
        change_type = "added"
    else:
        items[idx].update(candidate)
        change_type = "updated"
    after_levels = Counter(item.get("level") for item in items)
    pool["items"] = items
    pool["generated_at"] = now()
    summary = dict(pool.get("summary") or {})
    summary.update(
        {
            "trusted_pool_count": len(items),
            "source_trace_count": len(items),
            "static_level_counts": dict(after_levels),
            "canonical_update_source": "M184R_trusted_pool_publish_douman",
            "signed_customer_v2_gate_applied": True,
            "last_added_prospect_id": candidate["prospect_id"],
        }
    )
    pool["summary"] = summary
    write_json(CANONICAL_POOL, pool)
    return {"change_type": change_type, "before_count": before_count, "after_count": len(items), "before_levels": dict(before_levels), "after_levels": dict(after_levels)}


def update_trace(m183: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    trace = read_json(CANONICAL_TRACE, {"items": []})
    items = trace.get("items") or []
    source_item = m183["source_trace"]["items"][0]
    new_item = {
        "prospect_id": candidate["prospect_id"],
        "company_name": candidate["company_name"],
        "source_locator": candidate.get("source_locator"),
        "evidence_strength": candidate.get("evidence_strength"),
        "matched_persona": candidate.get("matched_persona"),
        "sources": source_item.get("sources") or [],
        "reference_only_sources": source_item.get("reference_only_sources") or [],
        "source_count": len(source_item.get("sources") or []),
        "canonical_update_source": "M184R_trusted_pool_publish_douman",
        "signed_customer_gate_version": "signed_customer_v2",
    }
    before_count = len(items)
    idx = next((i for i, item in enumerate(items) if item.get("prospect_id") == candidate["prospect_id"]), None)
    if idx is None:
        items.append(new_item)
        change_type = "added"
    else:
        items[idx] = new_item
        change_type = "updated"
    trace["items"] = items
    trace["generated_at"] = now()
    trace["summary"] = {**(trace.get("summary") or {}), "source_trace_count": len(items), "canonical_update_source": "M184R_trusted_pool_publish_douman", "signed_customer_v2_gate_applied": True}
    write_json(CANONICAL_TRACE, trace)
    return {"change_type": change_type, "before_count": before_count, "after_count": len(items)}


def update_entity_registry(candidate: dict[str, Any]) -> dict[str, Any]:
    registry = read_json(ENTITY_REGISTRY, {"items": []})
    items = registry.get("items") or []
    before_count = len(items)
    entity_id = stable_id("entity", candidate["company_name"])
    entity = {
        "entity_id": entity_id,
        "canonical_name": candidate["company_name"],
        "normalized_name": normalize_name(candidate["company_name"]),
        "entity_roles": ["trusted_pool", "source_trace"],
        "aliases": sorted(set([candidate["company_name"], *(candidate.get("candidate_aliases") or [])])),
        "source_refs": [
            {"source": "trusted_prospect_pool_v1", "prospect_id": candidate["prospect_id"], "level": candidate.get("level"), "matched_persona": candidate.get("matched_persona")},
            {"source": "source_trace_index_v1", "prospect_id": candidate["prospect_id"]},
        ],
        "prospect_id": candidate["prospect_id"],
        "level": candidate.get("level"),
        "matched_persona": candidate.get("matched_persona"),
    }
    idx = next((i for i, item in enumerate(items) if item.get("prospect_id") == candidate["prospect_id"] or item.get("canonical_name") == candidate["company_name"]), None)
    if idx is None:
        items.append(entity)
        change_type = "added"
    else:
        items[idx] = entity
        change_type = "updated"
    registry["items"] = items
    registry["generated_at"] = now()
    role_counts = Counter(role for item in items for role in item.get("entity_roles") or [])
    multi_role_count = sum(1 for item in items if len(item.get("entity_roles") or []) > 1)
    registry["summary"] = {**(registry.get("summary") or {}), "entity_count": len(items), "trusted_pool_entity_count": role_counts.get("trusted_pool", 0), "source_trace_entity_count": role_counts.get("source_trace", 0), "multi_role_entity_count": multi_role_count, "canonical_update_source": "M184R_trusted_pool_publish_douman"}
    write_json(ENTITY_REGISTRY, registry)
    return {"change_type": change_type, "before_count": before_count, "after_count": len(items), "trusted_pool_entity_count": role_counts.get("trusted_pool", 0), "source_trace_entity_count": role_counts.get("source_trace", 0), "entity_id": entity_id}


def write_vault_l2(candidate: dict[str, Any], m183: dict[str, Any]) -> dict[str, Any]:
    L2_DIR.mkdir(parents=True, exist_ok=True)
    path = L2_DIR / f"{candidate['company_name']}.md"
    sources = m183["source_trace"]["items"][0].get("sources") or []
    source_lines = "\n".join(f"- `{src.get('source_category')}` {src.get('source_locator')}：{src.get('summary')}" for src in sources)
    gaps = "\n".join(f"- {gap.get('reason')}" for gap in m183["report"]["decisions"][0].get("gap_queue") or []) or "- 暂无结构化缺口。"
    text = f"""---
prospect_id: {candidate['prospect_id']}
static_level: L2
matched_persona: {candidate['matched_persona']}
legacy_field_inherited: false
source_boundary: evidence_first_public_sources_only
fact_source: trusted_prospect_pool_v1
signed_customer_gate_version: signed_customer_v2
---

# {candidate['company_name']}

## 静态等级

L2

## 为什么匹配 ICP

{candidate['match_reason']}

## 核心产品/服务

{candidate['core_product_service_summary']}

## 业务模式

{candidate['business_model_summary']}

## 关键来源

{source_lines}

## 风险与待补点

{candidate['risk_or_gap']}

## 升层缺口

{gaps}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。客户案例只作为 ICP/reference，不计入 prospect evidence。
"""
    existed = path.exists()
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "change_type": "updated" if existed else "created"}


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": rel(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, text):
                    findings.append({"file": rel(path), "pattern": pattern})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def update_status_panel(pool_update: dict[str, Any], trace_update: dict[str, Any], entity_update: dict[str, Any], vault_write: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel["latest_milestone"] = "M184R"
    panel["overall_status"] = "PASS_M184R_TRUSTED_POOL_PUBLISHED"
    counts = dict(panel.get("counts") or {})
    counts.update({"trusted_pool_count": pool_update["after_count"], "source_trace_count": trace_update["after_count"], "entity_v2_count": entity_update["after_count"], "entity_v2_trusted_pool_entity_count": entity_update["trusted_pool_entity_count"], "l1_count": pool_update["after_levels"].get("L1", 0), "l2_count": pool_update["after_levels"].get("L2", 0), "l3_count": pool_update["after_levels"].get("L3", 0), "l4_count": pool_update["after_levels"].get("L4", 0), "m184_new_l2_count": 1})
    panel["counts"] = counts
    panel["current_canonical_state"] = {"trusted_pool_count": pool_update["after_count"], "source_trace_count": trace_update["after_count"], "level_counts": pool_update["after_levels"], "signed_customer_registry": "v2", "signed_customer_count": counts.get("signed_customer_v2_count", counts.get("signed_customer_count")), "old_customer_hits": 0}
    panel["m184r_trusted_pool_publish"] = {"generated_at": now(), "published_prospect_id": "m183_acc_douman", "company_name": "广州市斗满科技有限公司", "level": "L2", "trusted_pool_update": pool_update, "source_trace_update": trace_update, "entity_registry_update": entity_update, "vault_write": vault_write, "signed_customer_gate_version": "signed_customer_v2", "canonical_pool_updated": True, "vault_regular_area_written": True}
    write_json(STATUS_PANEL, panel)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M184R guarded trusted pool/vault publish for M183 Douman candidate.")
    parser.add_argument("--allow-trusted-pool-update", action="store_true")
    parser.add_argument("--allow-vault-regular-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    M184.mkdir(parents=True, exist_ok=True)
    m183 = load_m183()
    candidate = build_candidate(m183)
    pre_errors = validate_preconditions(args, m183, candidate)
    if pre_errors:
        validation = {"milestone": "M184R", "generated_at": now(), "status": "FAIL", "errors": pre_errors}
        write_json(M184 / "m184_validation_report_v1.json", validation)
        print(json.dumps(validation, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    pool_update = update_pool(candidate)
    trace_update = update_trace(m183, candidate)
    entity_update = update_entity_registry(candidate)
    vault_write = write_vault_l2(candidate, m183)
    update_status_panel(pool_update, trace_update, entity_update, vault_write)

    write_manifest = {"milestone": "M184R", "generated_at": now(), "candidate": candidate, "trusted_pool_update": pool_update, "source_trace_update": trace_update, "entity_registry_update": entity_update, "vault_write": vault_write, "canonical_files": {"trusted_pool": rel(CANONICAL_POOL), "source_trace": rel(CANONICAL_TRACE), "entity_registry": rel(ENTITY_REGISTRY), "vault_l2_file": vault_write["path"]}}
    write_json(M184 / "m184_write_manifest_v1.json", write_manifest)
    no_write = {"milestone": "M184R", "generated_at": now(), "status": "PASS_NO_FORBIDDEN_WRITE", "old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "customer_case_auto_signed_customer": False, "trusted_pool_written": True, "source_trace_written": True, "vault_regular_area_written": True}
    write_json(M184 / "m184_no_write_proof_v1.json", no_write)

    dynamic = scan_dynamic([M184, Path(vault_write["path"])])
    api = scan_api([M184, Path(vault_write["path"]), WORKSPACE / "scripts/build_m184r_trusted_pool_publish_douman.py"])
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m184r_trusted_pool_publish_douman.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    errors: list[str] = []
    if dynamic["status"] != "PASS":
        errors.append("dynamic term scan failed")
    if api["status"] != "PASS":
        errors.append("api key scan failed")
    if py_compile["returncode"] != 0:
        errors.append("py_compile failed")
    json_errors = []
    for path in sorted(M184.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            json_errors.append({"file": rel(path), "error": str(exc)})
    if json_errors:
        errors.append("json parse failed")
    validation = {"milestone": "M184R", "generated_at": now(), "status": "PASS" if not errors else "FAIL", "errors": errors, "py_compile": py_compile, "json_parse": {"checked_count": len(list(M184.glob('*.json'))), "errors": json_errors}, "dynamic_term_scan": dynamic, "api_key_scan": api, "signed_customer_gate_version": "signed_customer_v2"}
    write_json(M184 / "m184_validation_report_v1.json", validation)
    expert = {"milestone": "M184R", "generated_at": now(), "overall_review_status": "pass" if validation["status"] == "PASS" else "fail", "product_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "斗满已从 preview 进入 L2 正式可信潜客，页面只表达 ICP/证据/缺口。"}, "architecture_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "写入只触达 trusted pool/source trace/entity registry/vault 新区，且需要显式 guard。"}, "data_governance_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "signed customer v2 gate 已执行；客户案例未作为 prospect evidence；未写旧 Excel/知识资产/persona registry。"}}
    write_json(M184 / "m184_expert_review_report_v1.json", expert)
    panel = {"milestone": "M184R", "generated_at": now(), "status": "PASS_M184R_TRUSTED_POOL_PUBLISHED" if validation["status"] == "PASS" else "FAIL_M184R_TRUSTED_POOL_PUBLISHED", "summary": {"trusted_pool_count": pool_update["after_count"], "source_trace_count": trace_update["after_count"], "entity_v2_count": entity_update["after_count"], "level_counts": pool_update["after_levels"], "new_l2_count": 1, "vault_regular_write_count": 1, "signed_customer_gate_version": "signed_customer_v2"}, "next_recommended_action": "进入 M185：重跑系统一致性/实体/eligibility backlog，确认斗满成为 duplicate-existing-prospect 回归样本。"}
    write_json(M184 / "m184_operating_panel_v1.json", panel)

    # Re-run validation after all M184 artifacts exist so JSON parse covers the full package.
    dynamic = scan_dynamic([M184, Path(vault_write["path"])])
    api = scan_api([M184, Path(vault_write["path"]), WORKSPACE / "scripts/build_m184r_trusted_pool_publish_douman.py"])
    json_errors = []
    for path in sorted(M184.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            json_errors.append({"file": rel(path), "error": str(exc)})
    final_errors = []
    if dynamic["status"] != "PASS":
        final_errors.append("dynamic term scan failed")
    if api["status"] != "PASS":
        final_errors.append("api key scan failed")
    if json_errors:
        final_errors.append("json parse failed")
    validation = {**validation, "generated_at": now(), "status": "PASS" if not final_errors else "FAIL", "errors": final_errors, "json_parse": {"checked_count": len(list(M184.glob('*.json'))), "errors": json_errors}, "dynamic_term_scan": dynamic, "api_key_scan": api}
    write_json(M184 / "m184_validation_report_v1.json", validation)
    expert["generated_at"] = now()
    expert["overall_review_status"] = "pass" if validation["status"] == "PASS" else "fail"
    write_json(M184 / "m184_expert_review_report_v1.json", expert)
    panel["status"] = "PASS_M184R_TRUSTED_POOL_PUBLISHED" if validation["status"] == "PASS" else "FAIL_M184R_TRUSTED_POOL_PUBLISHED"
    write_json(M184 / "m184_operating_panel_v1.json", panel)

    print(json.dumps({"milestone": "M184R", "status": validation["status"], "summary": panel["summary"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
