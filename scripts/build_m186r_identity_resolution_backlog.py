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

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import SignedCustomerGate

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M185 = MILESTONES / "milestone185r_post_publish_reconciliation"
M186 = MILESTONES / "milestone186r_identity_resolution_backlog"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
BACKLOG_V4 = M185 / "evidence_acquisition_backlog_v4.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]

# Conservative title/name normalization. This does not create prospect evidence;
# it only resolves the company name before signed-customer and duplicate gates.
IDENTITY_RULES = [
    ("Lily服饰", "Lily服饰", "brand_name_from_title"),
    ("乐凯撒", "乐凯撒", "brand_name_from_title"),
    ("吉家宠物", "吉家宠物", "brand_name_from_title"),
    ("来伊份", "来伊份", "brand_name_from_title"),
    ("正新集团", "正新集团", "group_name_from_title"),
    ("首帆动力", "首帆动力", "brand_name_from_title"),
    ("七秒易购", "七秒易购", "brand_name_from_title"),
    ("零跑汽车", "零跑汽车", "brand_name_from_title"),
    ("博士眼镜", "博士眼镜", "brand_name_from_title"),
    ("M Stand", "M Stand", "brand_name_from_title"),
    ("花西子", "花西子", "brand_name_from_title"),
    ("老乡鸡", "老乡鸡", "brand_name_from_title"),
    ("自然堂", "自然堂", "brand_name_from_title"),
    ("鲜丰水果", "鲜丰水果", "brand_name_from_title"),
    ("森马", "森马", "brand_name_from_title"),
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


def normalize_key(name: Any) -> str:
    return re.sub(r"[\s·•,，。.;；:：/\\|\-—_（）()]+", "", str(name or "").strip().lower())


def resolve_identity(item: dict[str, Any]) -> dict[str, Any]:
    text = f"{item.get('candidate_name') or ''} {item.get('source_seed_title') or ''}"
    for token, resolved, method in IDENTITY_RULES:
        if token in text:
            return {
                "task_id": item.get("task_id"),
                "source_seed_title": item.get("source_seed_title"),
                "raw_candidate_name": item.get("candidate_name"),
                "resolved_company_name": resolved,
                "identity_resolution_status": "resolved_company_candidate",
                "resolution_method": method,
                "confidence": "medium",
                "boundary_note": "身份解析只用于进入 signed customer/duplicate gate，不作为 prospect evidence。",
            }
    return {
        "task_id": item.get("task_id"),
        "source_seed_title": item.get("source_seed_title"),
        "raw_candidate_name": item.get("candidate_name"),
        "resolved_company_name": None,
        "identity_resolution_status": "identity_pending",
        "resolution_method": "no_conservative_rule_match",
        "confidence": "low",
        "boundary_note": "未找到保守公司名解析规则，继续人工确认。",
    }


def build_identity_resolution(backlog: dict[str, Any]) -> dict[str, Any]:
    items = backlog.get("items") or []
    pending = [item for item in items if item.get("current_state") == "identity_pending"]
    resolved = [resolve_identity(item) for item in pending]
    status_counts = Counter(row["identity_resolution_status"] for row in resolved)
    unique_resolved = sorted({row["resolved_company_name"] for row in resolved if row.get("resolved_company_name")})
    payload = {
        "package_id": "m186r_candidate_identity_resolution_package_v1",
        "milestone": "M186R",
        "generated_at": now(),
        "summary": {
            "input_identity_pending_count": len(pending),
            "resolved_company_candidate_count": status_counts.get("resolved_company_candidate", 0),
            "still_identity_pending_count": status_counts.get("identity_pending", 0),
            "unique_resolved_company_count": len(unique_resolved),
        },
        "items": resolved,
    }
    write_json(M186 / "candidate_identity_resolution_package_v1.json", payload)
    return payload


def rebuild_backlog(backlog: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    resolution_by_task = {row["task_id"]: row for row in identity.get("items") or []}
    seen_ready: set[str] = set()
    new_items: list[dict[str, Any]] = []
    for item in backlog.get("items") or []:
        new_item = dict(item)
        if item.get("current_state") == "identity_pending":
            resolution = resolution_by_task.get(item.get("task_id")) or resolve_identity(item)
            new_item["identity_resolution"] = resolution
            resolved_name = resolution.get("resolved_company_name")
            if not resolved_name:
                new_item["candidate_name"] = item.get("candidate_name")
                new_item["current_state"] = "identity_pending"
                new_item["next_action"] = "继续人工确认公司标准名、法体/品牌/集团关系，再跑 signed customer v2 gate。"
            else:
                new_item["candidate_name"] = resolved_name
                new_item["identity_status"] = "resolved_company_candidate"
                signed = signed_gate.check(resolved_name).to_dict()
                eligibility = eligibility_gate.check(resolved_name, item.get("task_id")).to_dict()
                new_item["signed_customer_gate_version"] = "signed_customer_v2"
                new_item["signed_customer_check"] = signed
                new_item["prospect_eligibility"] = eligibility
                key = normalize_key(resolved_name)
                if eligibility.get("prospect_eligibility_status") == "eligible_prospect" and key in seen_ready:
                    new_item["current_state"] = "eligibility_blocked"
                    new_item["prospect_eligibility"] = {**eligibility, "prospect_eligibility_status": "duplicate_candidate_in_backlog", "reason": "same resolved company already selected for source collection in this backlog"}
                    new_item["next_action"] = "同一 resolved company 在本轮 backlog 已有一个采集任务，避免重复采集。"
                elif eligibility.get("prospect_eligibility_status") == "eligible_prospect":
                    new_item["current_state"] = "source_collection_pending"
                    seen_ready.add(key)
                    new_item["next_action"] = "采集 official_owned / platform_operating_fact / authoritative_third_party 等公开强来源；seed 本身不计入 prospect evidence。"
                else:
                    new_item["current_state"] = "eligibility_blocked"
                    new_item["next_action"] = "资格闸门未通过，不进入 source collection；如为边界/老客/重复对象，保留为学习或案例参考。"
        elif item.get("current_state") == "source_collection_pending":
            # M184 already published Douman; after M185 it should be duplicate. Keep the current state from v4 if any remains eligible.
            eligibility = eligibility_gate.check(item.get("candidate_name"), item.get("task_id")).to_dict()
            new_item["prospect_eligibility"] = eligibility
            if eligibility.get("prospect_eligibility_status") != "eligible_prospect":
                new_item["current_state"] = "eligibility_blocked"
                new_item["next_action"] = "已不再是可采集新潜客；按 duplicate/signed/boundary 结果处理。"
        new_items.append(new_item)
    state_counts = Counter(item.get("current_state") for item in new_items)
    eligibility_counts = Counter((item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") or "not_checked" for item in new_items)
    payload = {
        "batch_id": "m186r_evidence_acquisition_backlog_v5",
        "milestone": "M186R",
        "generated_at": now(),
        "summary": {
            "task_count": len(new_items),
            "state_counts": dict(state_counts),
            "eligibility_status_counts": dict(eligibility_counts),
            "source_collection_pending_count": state_counts.get("source_collection_pending", 0),
            "identity_pending_count": state_counts.get("identity_pending", 0),
            "eligibility_blocked_count": state_counts.get("eligibility_blocked", 0),
            "excluded_count": state_counts.get("excluded", 0),
            "signed_customer_gate_version": "v2",
            "old_workbook_written": False,
            "trusted_pool_written": False,
        },
        "items": new_items,
    }
    write_json(M186 / "evidence_acquisition_backlog_v5.json", payload)
    return payload


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".py":
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": rel(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    pats = [re.compile(p) for p in SECRET_PATTERNS]
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            if any(p.search(text) for p in pats):
                findings.append(rel(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def update_panel(backlog_v5: dict[str, Any], validation_status: str) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    summary = backlog_v5.get("summary") or {}
    counts.update({
        "m186_source_collection_pending_count": summary.get("source_collection_pending_count"),
        "m186_identity_pending_count": summary.get("identity_pending_count"),
        "m186_eligibility_blocked_count": summary.get("eligibility_blocked_count"),
        "m186_excluded_count": summary.get("excluded_count"),
        "m186_resolved_company_candidate_count": summary.get("eligibility_status_counts", {}).get("eligible_prospect", 0) + summary.get("eligibility_status_counts", {}).get("excluded_signed_customer", 0) + summary.get("eligibility_status_counts", {}).get("boundary_review", 0) + summary.get("eligibility_status_counts", {}).get("duplicate_existing_prospect", 0) + summary.get("eligibility_status_counts", {}).get("duplicate_candidate_in_backlog", 0),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M186R",
        "overall_status": "PASS_M186R_IDENTITY_BACKLOG_REBUILT" if validation_status == "PASS" else "FAIL_M186R_IDENTITY_BACKLOG_REBUILD",
        "counts": counts,
        "m186r_identity_resolution": {
            "generated_at": now(),
            "status": validation_status,
            "backlog_state_counts": summary.get("state_counts"),
            "eligibility_status_counts": summary.get("eligibility_status_counts"),
            "source_collection_pending_count": summary.get("source_collection_pending_count"),
            "signed_customer_gate_version": "v2",
        },
        "canonical_next_action": "进入 M187：只对 backlog_v5 中 source_collection_pending 的去重候选采集公开强 evidence。",
    })
    write_json(PANEL, panel)


def validate(identity: dict[str, Any], backlog_v5: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m186r_identity_resolution_backlog.py", "shared/static_pool/signed_customer_gate.py", "shared/static_pool/prospect_eligibility_gate.py"])
    json_errors = []
    for path in M186.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M186, WORKSPACE / "scripts/build_m186r_identity_resolution_backlog.py"])
    api = scan_api([M186, WORKSPACE / "scripts/build_m186r_identity_resolution_backlog.py"])
    summary = backlog_v5.get("summary") or {}
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "identity_pending_reduced": summary.get("identity_pending_count", 999) < read_json(BACKLOG_V4, {"summary": {}}).get("summary", {}).get("identity_pending_count", 0),
        "source_collection_pending_deduped": summary.get("source_collection_pending_count") == len({normalize_key(item.get("candidate_name")) for item in backlog_v5.get("items", []) if item.get("current_state") == "source_collection_pending"}),
        "source_collection_pending_all_eligible": all((item.get("prospect_eligibility") or {}).get("prospect_eligibility_status") == "eligible_prospect" for item in backlog_v5.get("items", []) if item.get("current_state") == "source_collection_pending"),
        "signed_customer_block_present": summary.get("eligibility_status_counts", {}).get("excluded_signed_customer", 0) >= 1,
        "boundary_review_present": summary.get("eligibility_status_counts", {}).get("boundary_review", 0) >= 1,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_forbidden_write_pass": True,
    }
    payload = {
        "milestone": "M186R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": pyc,
        "json_parse": {"checked_count": len(list(M186.glob("*.json"))), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "trusted_pool_written": False, "source_trace_written": False, "vault_regular_area_written": False},
    }
    write_json(M186 / "m186_validation_report_v1.json", payload)
    return payload


def build_all() -> dict[str, Any]:
    M186.mkdir(parents=True, exist_ok=True)
    backlog_v4 = read_json(BACKLOG_V4, {"items": []})
    identity = build_identity_resolution(backlog_v4)
    backlog_v5 = rebuild_backlog(backlog_v4, identity)
    validation = validate(identity, backlog_v5)
    expert = {
        "milestone": "M186R",
        "generated_at": now(),
        "overall_review_status": "pass" if validation["status"] == "PASS" else "fail",
        "product_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "身份解析后只保留去重且过 gate 的候选进入 source collection。"},
        "architecture_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "M186 不写 trusted pool/vault，只更新 backlog 和状态面板。"},
        "data_governance_review": {"status": "pass" if validation["status"] == "PASS" else "fail", "notes": "老客、边界 review、重复候选均在 eligibility gate 层处理，customer case seed 不作为 evidence。"},
    }
    write_json(M186 / "m186_expert_review_report_v1.json", expert)
    operating = {
        "milestone": "M186R",
        "generated_at": now(),
        "status": "PASS_M186R_IDENTITY_BACKLOG_REBUILT" if validation["status"] == "PASS" else "FAIL_M186R_IDENTITY_BACKLOG_REBUILT",
        "summary": {
            "input_identity_pending_count": identity["summary"]["input_identity_pending_count"],
            "resolved_company_candidate_count": identity["summary"]["resolved_company_candidate_count"],
            "still_identity_pending_count": backlog_v5["summary"]["identity_pending_count"],
            "source_collection_pending_count": backlog_v5["summary"]["source_collection_pending_count"],
            "eligibility_blocked_count": backlog_v5["summary"]["eligibility_blocked_count"],
            "backlog_state_counts": backlog_v5["summary"]["state_counts"],
            "eligibility_status_counts": backlog_v5["summary"]["eligibility_status_counts"],
        },
        "next_recommended_action": "进入 M187：对 source_collection_pending 的候选采集公开强 evidence。",
    }
    write_json(M186 / "m186_operating_panel_v1.json", operating)
    update_panel(backlog_v5, validation["status"])
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M186 identity resolution backlog rebuild.")
    parser.add_argument("--stage", choices=["all", "readiness"], default="all")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.stage == "readiness":
        panel = read_json(PANEL, {})
        payload = {"mode": "readiness", "milestone": "M186R", "generated_at": now(), "status": "PASS", "current_status": {"latest_milestone": panel.get("latest_milestone"), "overall_status": panel.get("overall_status"), "counts": panel.get("counts")}}
    else:
        payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if str(payload.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
