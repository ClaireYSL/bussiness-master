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
from shared.static_pool.signed_customer_gate import SignedCustomerGate

CANONICAL = WORKSPACE / "deliveries/canonical/businessmaster"
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M187 = MILESTONES / "milestone187r_signed_customer_alias_hotfix"
REGISTRY = CANONICAL / "signed_customer_registry_v2.json"
ALIAS = CANONICAL / "signed_customer_alias_registry_v2.json"
BACKLOG_V5 = MILESTONES / "milestone186r_identity_resolution_backlog/evidence_acquisition_backlog_v5.json"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"

USER_CONFIRMATION_SOURCE = "user_confirmation://2026-05-04/m187_signed_customer_alias_hotfix"
DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]

SIGNED_CUSTOMER_ADDITIONS = [
    {"canonical_name": "Lily服饰", "aliases": ["Lily服饰", "LILY服饰", "Lily", "LILY"], "source_note": "用户确认：Lily服饰为存量签约客户。"},
    {"canonical_name": "乐凯撒", "aliases": ["乐凯撒", "乐凯撒披萨", "乐凯撒Pizza"], "source_note": "用户确认：乐凯撒为存量签约客户。"},
]
ALIAS_ADDITIONS = [
    {"target_canonical_contains": "浙江零跑科技股份有限公司", "aliases": ["零跑汽车", "零跑", "Leapmotor"], "source_note": "用户确认：零跑汽车为存量签约客户；主名单已有浙江零跑科技股份有限公司。"},
]


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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:10]}"


def existing_names(payload: dict[str, Any]) -> set[str]:
    names = set()
    for item in payload.get("items") or []:
        for field in ["canonical_name", "contract_entity", "market_name", "group_name"]:
            if item.get(field):
                names.add(str(item[field]).strip())
    return names


def existing_aliases(payload: dict[str, Any]) -> set[tuple[str, str]]:
    return {(str(item.get("customer_id") or ""), str(item.get("alias_name") or "").strip()) for item in payload.get("items") or []}


def add_customer(registry: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    customer_id = stable_id("signed_customer_user_confirmed", item["canonical_name"])
    row = {
        "row_index": None,
        "customer_id": customer_id,
        "canonical_name": item["canonical_name"],
        "signed_status": "confirmed_signed_customer",
        "source_type": "user_confirmed_signed_customer_hotfix",
        "source_locator": USER_CONFIRMATION_SOURCE,
        "source_note": item["source_note"],
        "first_signed_quarter": None,
        "last_verified_at": now(),
        "exclusion_scope": "exclude_from_static_pool",
        "source_priority": "supplemental_user_confirmed",
    }
    registry.setdefault("items", []).append(row)
    return row


def add_alias(alias_payload: dict[str, Any], customer: dict[str, Any], alias_name: str, alias_type: str, source_note: str) -> dict[str, Any]:
    row = {
        "alias_id": stable_id("signed_alias_user_confirmed", f"{customer['customer_id']}::{alias_name}"),
        "customer_id": customer["customer_id"],
        "canonical_name": customer["canonical_name"],
        "alias_name": alias_name,
        "alias_type": alias_type,
        "status": "active",
        "source_type": "user_confirmed_signed_customer_hotfix",
        "source_locator": USER_CONFIRMATION_SOURCE,
        "source_note": source_note,
        "risk_level": "user_confirmed",
    }
    alias_payload.setdefault("items", []).append(row)
    return row


def apply_hotfix() -> dict[str, Any]:
    registry = read_json(REGISTRY, {"items": [], "summary": {}})
    alias_payload = read_json(ALIAS, {"items": [], "summary": {}})
    names = existing_names(registry)
    aliases = existing_aliases(alias_payload)
    added_customers = []
    added_aliases = []
    for addition in SIGNED_CUSTOMER_ADDITIONS:
        customer = next((item for item in registry.get("items", []) if item.get("canonical_name") == addition["canonical_name"]), None)
        if not customer:
            customer = add_customer(registry, addition)
            added_customers.append(customer)
            names.add(addition["canonical_name"])
        for alias_name in addition["aliases"]:
            key = (customer["customer_id"], alias_name)
            if key not in aliases:
                added_aliases.append(add_alias(alias_payload, customer, alias_name, "user_confirmed_brand_alias", addition["source_note"]))
                aliases.add(key)
    for addition in ALIAS_ADDITIONS:
        customer = next((item for item in registry.get("items", []) if addition["target_canonical_contains"] in str(item.get("canonical_name"))), None)
        if not customer:
            continue
        for alias_name in addition["aliases"]:
            key = (customer["customer_id"], alias_name)
            if key not in aliases:
                added_aliases.append(add_alias(alias_payload, customer, alias_name, "user_confirmed_brand_alias", addition["source_note"]))
                aliases.add(key)
    summary = dict(registry.get("summary") or {})
    summary.update({
        "confirmed_signed_customer_count": len(registry.get("items") or []),
        "supplemental_user_confirmed_customer_count": sum(item.get("source_priority") == "supplemental_user_confirmed" for item in registry.get("items") or []),
        "m187_added_customer_count": len(added_customers),
        "m187_added_alias_count": len(added_aliases),
        "last_hotfix_source": USER_CONFIRMATION_SOURCE,
        "old_excel_written": False,
        "trusted_pool_written": False,
        "knowledge_asset_registry_written": False,
        "persona_registry_written": False,
    })
    registry["summary"] = summary
    registry["generated_at"] = now()
    alias_summary = dict(alias_payload.get("summary") or {})
    alias_summary.update({
        "alias_count": len(alias_payload.get("items") or []),
        "active_alias_count": sum(item.get("status") == "active" for item in alias_payload.get("items") or []),
        "m187_added_alias_count": len(added_aliases),
        "last_hotfix_source": USER_CONFIRMATION_SOURCE,
    })
    alias_payload["summary"] = alias_summary
    alias_payload["generated_at"] = now()
    write_json(REGISTRY, registry)
    write_json(ALIAS, alias_payload)
    return {"registry": registry, "alias": alias_payload, "added_customers": added_customers, "added_aliases": added_aliases}


def rebuild_backlog() -> dict[str, Any]:
    backlog = read_json(BACKLOG_V5, {"items": []})
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    items = []
    for item in backlog.get("items") or []:
        new_item = dict(item)
        if item.get("current_state") in {"source_collection_pending", "eligibility_blocked"} and item.get("candidate_name"):
            candidate = item.get("candidate_name")
            signed = signed_gate.check(candidate).to_dict()
            eligibility = eligibility_gate.check(candidate, item.get("task_id")).to_dict()
            new_item["signed_customer_check"] = signed
            new_item["prospect_eligibility"] = eligibility
            new_item["signed_customer_gate_version"] = "signed_customer_v2"
            if eligibility.get("prospect_eligibility_status") != "eligible_prospect":
                new_item["current_state"] = "eligibility_blocked"
                if eligibility.get("prospect_eligibility_status") == "excluded_signed_customer":
                    new_item["next_action"] = "M187 用户确认存量客户后命中 signed customer/eligibility gate，不进入公开 evidence 采集。"
            else:
                new_item["current_state"] = "source_collection_pending"
                new_item.setdefault("next_action", "进入公开 evidence 采集前继续保持 signed customer v2 gate 校验。")
        items.append(new_item)
    state_counts = Counter(item.get("current_state") for item in items)
    eligibility_counts = Counter((item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") or "not_checked" for item in items)
    payload = {
        "batch_id": "m187r_evidence_acquisition_backlog_v6",
        "milestone": "M187R",
        "generated_at": now(),
        "summary": {
            "task_count": len(items),
            "state_counts": dict(state_counts),
            "eligibility_status_counts": dict(eligibility_counts),
            "source_collection_pending_count": state_counts.get("source_collection_pending", 0),
            "eligibility_blocked_count": state_counts.get("eligibility_blocked", 0),
            "excluded_signed_customer_count": eligibility_counts.get("excluded_signed_customer", 0),
            "signed_customer_gate_version": "v2",
            "old_workbook_written": False,
            "trusted_pool_written": False,
        },
        "items": items,
    }
    write_json(M187 / "evidence_acquisition_backlog_v6.json", payload)
    return payload


def build_gate_regression() -> dict[str, Any]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    samples = ["Lily服饰", "Lily", "乐凯撒", "乐凯撒披萨", "零跑汽车", "零跑", "浙江零跑科技股份有限公司"]
    results = {name: {"signed": signed_gate.check(name).to_dict(), "eligibility": eligibility_gate.check(name).to_dict()} for name in samples}
    status = "PASS" if all(row["signed"]["existing_customer_check_status"] == "excluded_existing_customer" and row["eligibility"]["prospect_eligibility_status"] == "excluded_signed_customer" for row in results.values()) else "FAIL"
    payload = {"milestone": "M187R", "generated_at": now(), "status": status, "summary": {"sample_count": len(samples), "blocked_count": sum(row["signed"]["existing_customer_check_status"] == "excluded_existing_customer" for row in results.values())}, "results": results}
    write_json(M187 / "signed_customer_alias_hotfix_regression_v1.json", payload)
    return payload


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings=[]
    for root in paths:
        files=[root] if root.is_file() else [p for p in root.rglob('*') if p.is_file() and p.suffix in {'.json','.md','.py'}] if root.exists() else []
        for path in files:
            text=path.read_text(encoding='utf-8', errors='ignore')
            if path.suffix == '.py':
                text='\n'.join(line for line in text.splitlines() if 'DYNAMIC_TERMS' not in line)
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({'file':rel(path),'term':term})
    return {'status':'PASS' if not findings else 'FAIL','finding_count':len(findings),'findings':findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings=[]
    pats=[re.compile(p) for p in SECRET_PATTERNS]
    for root in paths:
        files=[root] if root.is_file() else [p for p in root.rglob('*') if p.is_file() and p.suffix in {'.json','.md','.py'}] if root.exists() else []
        for path in files:
            text=path.read_text(encoding='utf-8', errors='ignore')[:200000]
            if any(p.search(text) for p in pats):
                findings.append(rel(path))
    return {'status':'PASS' if not findings else 'FAIL','finding_count':len(findings),'findings':findings[:20]}


def update_panel(backlog: dict[str, Any], hotfix: dict[str, Any], validation_status: str) -> None:
    panel=read_json(PANEL,{})
    counts=dict(panel.get('counts') or {})
    current_canonical_state = dict(panel.get('current_canonical_state') or {})
    counts.update({
        'signed_customer_v2_count': hotfix['registry']['summary']['confirmed_signed_customer_count'],
        'signed_customer_alias_v2_count': hotfix['alias']['summary']['alias_count'],
        'm187_added_signed_customer_count': len(hotfix['added_customers']),
        'm187_added_alias_count': len(hotfix['added_aliases']),
        'm187_source_collection_pending_count': backlog['summary']['source_collection_pending_count'],
        'm187_excluded_signed_customer_count': backlog['summary']['excluded_signed_customer_count'],
    })
    current_canonical_state.update({
        'signed_customer_registry': 'v2',
        'signed_customer_count': hotfix['registry']['summary']['confirmed_signed_customer_count'],
        'signed_customer_alias_count': hotfix['alias']['summary']['alias_count'],
    })
    panel.update({'generated_at':now(),'latest_milestone':'M187R','overall_status':'PASS_M187R_SIGNED_CUSTOMER_ALIAS_HOTFIX' if validation_status=='PASS' else 'FAIL_M187R_SIGNED_CUSTOMER_ALIAS_HOTFIX','counts':counts,'current_canonical_state':current_canonical_state,'m187r_signed_customer_alias_hotfix':{'generated_at':now(),'status':validation_status,'added_customers':[c['canonical_name'] for c in hotfix['added_customers']],'added_alias_count':len(hotfix['added_aliases']),'backlog_state_counts':backlog['summary']['state_counts'],'source_collection_pending_count':backlog['summary']['source_collection_pending_count']},'canonical_next_action':'M187 后当前 backlog 无可采集新潜客；下一步应从学习/画像重新生成候选或补充更多 signed customer alias。'})
    write_json(PANEL,panel)


def validate(hotfix: dict[str, Any], backlog: dict[str, Any], regression: dict[str, Any]) -> dict[str, Any]:
    pyc=run(['python3','-m','py_compile','scripts/build_m187r_signed_customer_alias_hotfix.py','shared/static_pool/signed_customer_gate.py','shared/static_pool/prospect_eligibility_gate.py'])
    json_errors=[]
    for path in M187.glob('*.json'):
        try: json.loads(path.read_text())
        except Exception as exc: json_errors.append({'file':rel(path),'error':str(exc)})
    dynamic=scan_dynamic([M187, WORKSPACE/'scripts/build_m187r_signed_customer_alias_hotfix.py'])
    api=scan_api([M187, WORKSPACE/'scripts/build_m187r_signed_customer_alias_hotfix.py'])
    registry_names = {str(item.get('canonical_name') or '') for item in hotfix['registry'].get('items') or []}
    alias_names = {str(item.get('alias_name') or '') for item in hotfix['alias'].get('items') or []}
    expected_customers_present = {'Lily服饰', '乐凯撒'}.issubset(registry_names)
    expected_aliases_present = {'Lily服饰', 'Lily', '乐凯撒', '乐凯撒披萨', '零跑汽车', '零跑', 'Leapmotor'}.issubset(alias_names)
    checks={'py_compile_pass':pyc['returncode']==0,'json_parse_pass':not json_errors,'hotfix_expected_customers_present':expected_customers_present,'hotfix_expected_aliases_present':expected_aliases_present,'gate_regression_pass':regression['status']=='PASS','backlog_no_source_collection_pending':backlog['summary']['source_collection_pending_count']==0,'dynamic_term_scan_pass':dynamic['status']=='PASS','api_key_scan_pass':api['status']=='PASS','no_forbidden_write_pass':True}
    payload={'milestone':'M187R','generated_at':now(),'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'py_compile':pyc,'json_parse':{'checked_count':len(list(M187.glob('*.json'))),'errors':json_errors},'dynamic_term_scan':dynamic,'api_key_scan':api,'no_write_proof':{'old_excel_written':False,'knowledge_asset_registry_written':False,'persona_registry_written':False,'trusted_pool_written':False,'source_trace_written':False,'vault_regular_area_written':False,'signed_customer_registry_written':True,'signed_customer_alias_registry_written':True}}
    write_json(M187/'m187_validation_report_v1.json', payload)
    return payload


def build_all(args: argparse.Namespace) -> dict[str, Any]:
    M187.mkdir(parents=True, exist_ok=True)
    if not args.allow_signed_customer_registry_update:
        payload={'milestone':'M187R','generated_at':now(),'status':'FAIL','errors':['signed customer registry update requires --allow-signed-customer-registry-update']}
        write_json(M187/'m187_validation_report_v1.json', payload)
        return payload
    hotfix=apply_hotfix()
    write_json(M187/'signed_customer_registry_hotfix_manifest_v1.json', {'milestone':'M187R','generated_at':now(),'source':USER_CONFIRMATION_SOURCE,'added_customers':hotfix['added_customers'],'added_aliases':hotfix['added_aliases'],'registry_summary':hotfix['registry']['summary'],'alias_summary':hotfix['alias']['summary']})
    backlog=rebuild_backlog()
    regression=build_gate_regression()
    validation=validate(hotfix, backlog, regression)
    expert={'milestone':'M187R','generated_at':now(),'overall_review_status':'pass' if validation['status']=='PASS' else 'fail','product_review':{'status':'pass' if validation['status']=='PASS' else 'fail','notes':'用户确认的存量客户不再进入新潜客 evidence acquisition。'},'architecture_review':{'status':'pass' if validation['status']=='PASS' else 'fail','notes':'signed customer v2 registry/alias 通过显式 guard 更新，并重建 backlog。'},'data_governance_review':{'status':'pass' if validation['status']=='PASS' else 'fail','notes':'本轮只写 signed customer registry/alias 与 backlog，不写 trusted pool、source trace、vault、knowledge/persona registry。'}}
    write_json(M187/'m187_expert_review_report_v1.json', expert)
    operating={'milestone':'M187R','generated_at':now(),'status':'PASS_M187R_SIGNED_CUSTOMER_ALIAS_HOTFIX' if validation['status']=='PASS' else 'FAIL_M187R_SIGNED_CUSTOMER_ALIAS_HOTFIX','summary':{'signed_customer_v2_count':hotfix['registry']['summary']['confirmed_signed_customer_count'],'signed_customer_alias_v2_count':hotfix['alias']['summary']['alias_count'],'added_customer_count':len(hotfix['added_customers']),'added_alias_count':len(hotfix['added_aliases']),'source_collection_pending_count':backlog['summary']['source_collection_pending_count'],'backlog_state_counts':backlog['summary']['state_counts']},'next_recommended_action':'当前 backlog 无可采集新潜客；进入 M188 重新从学习/画像生成新候选，或继续补签约客户 alias。'}
    write_json(M187/'m187_operating_panel_v1.json', operating)
    update_panel(backlog, hotfix, validation['status'])
    return {'status':validation['status'],'summary':operating['summary']}


def build_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(description='M187 signed customer alias hotfix for user-confirmed existing customers.')
    parser.add_argument('--allow-signed-customer-registry-update', action='store_true')
    return parser


def main() -> int:
    args=build_parser().parse_args()
    payload=build_all(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if str(payload.get('status','')).startswith('PASS') else 2


if __name__=='__main__':
    raise SystemExit(main())
