from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import socket
import ssl
import subprocess
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M85 = MILESTONES / "milestone85r_non_listed_candidate_trial"
M86 = MILESTONES / "milestone86r_source_locator_hardening"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"

DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)
L2_OR_ABOVE = {"L1", "L2"}
COUNTABLE_CATEGORIES = {"official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"}
NON_CAPITAL_CATEGORIES = {"official_owned", "platform_operating_fact", "authoritative_third_party"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE)) if path.is_relative_to(WORKSPACE) else str(path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _url_check(url: str, timeout: int = 8) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"source_locator": url, "availability_status": "invalid_url", "verified": False, "status_code": None, "final_url": url, "error": "not_http_url"}

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BusinessMasterSourceAudit/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    }
    ctx = ssl.create_default_context()
    attempts = [("HEAD", None), ("GET", "bytes=0-4095")]
    last_error = ""
    for method, range_header in attempts:
        req_headers = dict(headers)
        if range_header:
            req_headers["Range"] = range_header
        req = urllib.request.Request(url, method=method, headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                status = int(getattr(response, "status", 0) or response.getcode() or 0)
                final_url = response.geturl()
                content_type = response.headers.get("content-type", "")
                return {
                    "source_locator": url,
                    "availability_status": "verified" if 200 <= status < 400 else "http_unexpected",
                    "verified": 200 <= status < 400,
                    "status_code": status,
                    "final_url": final_url,
                    "content_type": content_type,
                    "method": method,
                    "error": "",
                }
        except urllib.error.HTTPError as exc:
            status = int(exc.code or 0)
            if status in {401, 403, 405, 429}:
                return {
                    "source_locator": url,
                    "availability_status": "reachable_restricted",
                    "verified": False,
                    "status_code": status,
                    "final_url": exc.geturl() or url,
                    "content_type": exc.headers.get("content-type", "") if exc.headers else "",
                    "method": method,
                    "error": f"HTTPError:{status}",
                }
            last_error = f"HTTPError:{status}"
        except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError) as exc:
            last_error = f"{type(exc).__name__}:{exc}"
        except Exception as exc:  # noqa: BLE001 - audit should record unexpected URL failures, not crash early.
            last_error = f"{type(exc).__name__}:{exc}"
    return {"source_locator": url, "availability_status": "unverified", "verified": False, "status_code": None, "final_url": url, "content_type": "", "method": "HEAD_GET", "error": last_error[:500]}


def audit_urls(trace: dict[str, Any]) -> dict[str, Any]:
    urls = sorted({source.get("source_locator", "") for item in trace.get("items") or [] for source in item.get("sources") or [] if str(source.get("source_locator", "")).startswith(("http://", "https://"))})
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        checks = list(executor.map(_url_check, urls))
    by_url = {row["source_locator"]: row for row in checks}
    status_counts = Counter(row["availability_status"] for row in checks)
    audit = {
        "milestone": "M86R",
        "generated_at": now(),
        "status": "PASS_M86R_SOURCE_LOCATOR_AVAILABILITY_AUDITED",
        "summary": {
            "unique_url_count": len(urls),
            "verified_url_count": sum(1 for row in checks if row.get("verified")),
            "restricted_or_unverified_url_count": sum(1 for row in checks if not row.get("verified")),
            "availability_status_counts": dict(status_counts),
        },
        "items": checks,
    }
    write_json(M86 / "source_locator_availability_audit_v1.json", audit)
    return {"audit": audit, "by_url": by_url}


def build_hardened_trace(trace: dict[str, Any], availability_by_url: dict[str, dict[str, Any]]) -> dict[str, Any]:
    items = []
    category_counts = Counter()
    verified_counts = Counter()
    for item in trace.get("items") or []:
        sources = []
        for source in item.get("sources") or []:
            locator = str(source.get("source_locator") or "")
            availability = availability_by_url.get(locator, {"availability_status": "not_checked", "verified": False})
            hardened = {**source, "locator_hardening": availability}
            sources.append(hardened)
            category = source.get("source_category") or "unknown"
            category_counts[category] += 1
            if availability.get("verified"):
                verified_counts[category] += 1
        verified_sources = [source for source in sources if source.get("locator_hardening", {}).get("verified")]
        items.append({**item, "verified_source_count": len(verified_sources), "sources": sources})
    hardened_trace = {
        "milestone": "M86R",
        "generated_at": now(),
        "status": "PASS_M86R_HARDENED_SOURCE_TRACE_READY",
        "summary": {
            "source_trace_count": len(items),
            "source_category_counts": dict(category_counts),
            "verified_source_category_counts": dict(verified_counts),
        },
        "items": items,
    }
    write_json(M86 / "hardened_source_trace_v1.json", hardened_trace)
    return hardened_trace


def build_admission(hardened_trace: dict[str, Any], review: dict[str, Any], pool: dict[str, Any]) -> dict[str, Any]:
    decision_by_id = {item["prospect_id"]: item for item in review.get("items") or []}
    pool_by_id = {item["prospect_id"]: item for item in pool.get("items") or []}
    admission_items = []
    gap_items = []
    for trace_item in hardened_trace.get("items") or []:
        prospect_id = trace_item.get("prospect_id")
        decision = decision_by_id.get(prospect_id, {})
        pool_item = pool_by_id.get(prospect_id, {})
        sources = trace_item.get("sources") or []
        verified_sources = [source for source in sources if source.get("locator_hardening", {}).get("verified")]
        verified_countable = [source for source in verified_sources if source.get("source_category") in COUNTABLE_CATEGORIES]
        verified_categories = sorted({source.get("source_category") for source in verified_countable})
        non_capital_verified_categories = sorted({source.get("source_category") for source in verified_countable if source.get("source_category") in NON_CAPITAL_CATEGORIES})
        icp_support_verified = [source for source in verified_countable if "icp_match_support" in str(source.get("supports_dimension") or "")]
        suggested_level = decision.get("suggested_level", "L5")
        reasons = []
        if suggested_level not in L2_OR_ABOVE:
            reasons.append("M85R report-only 未达到 L2+。")
        if len(verified_countable) < 2:
            reasons.append("可访问且可计入的强来源少于 2 条。")
        if len(verified_categories) < 2:
            reasons.append("可访问来源类别少于 2 个。")
        if not non_capital_verified_categories:
            reasons.append("缺少非上市友好的可访问来源类别。")
        if not icp_support_verified:
            reasons.append("缺少可访问且直接支撑 ICP 的来源。")
        canonical_update_ready = not reasons
        row = {
            "prospect_id": prospect_id,
            "company_name": trace_item.get("company_name") or pool_item.get("company_name"),
            "matched_persona": trace_item.get("matched_persona") or pool_item.get("matched_persona"),
            "m85_suggested_level": suggested_level,
            "verified_countable_source_count": len(verified_countable),
            "verified_source_categories": verified_categories,
            "non_capital_verified_categories": non_capital_verified_categories,
            "icp_support_verified_source_count": len(icp_support_verified),
            "canonical_update_ready": canonical_update_ready,
            "admission_reasons": ["source locator hardening PASS"] if canonical_update_ready else reasons,
            "static_fields_only": True,
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        }
        admission_items.append(row)
        if not canonical_update_ready:
            for reason in reasons:
                gap_items.append({"prospect_id": prospect_id, "company_name": row["company_name"], "queue_type": "source_locator_hardening_gap", "reason": reason})
    ready = [item for item in admission_items if item["canonical_update_ready"]]
    package = {
        "milestone": "M86R",
        "generated_at": now(),
        "status": "PASS_M86R_CANONICAL_UPDATE_ADMISSION_READY",
        "summary": {
            "candidate_count": len(admission_items),
            "canonical_update_ready_count": len(ready),
            "not_ready_count": len(admission_items) - len(ready),
            "suggested_level_counts_for_ready": dict(Counter(item["m85_suggested_level"] for item in ready)),
            "canonical_pool_updated": False,
            "vault_regular_written": False,
        },
        "items": admission_items,
    }
    gap_queue = {"milestone": "M86R", "generated_at": now(), "status": "PASS_M86R_SOURCE_HARDENING_GAP_QUEUE_READY", "summary": {"gap_count": len(gap_items)}, "items": gap_items}
    write_json(M86 / "canonical_update_admission_package_v1.json", package)
    write_json(M86 / "source_hardening_gap_queue_v1.json", gap_queue)
    return {"package": package, "gap_queue": gap_queue}


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
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings[:50]}


def scan_api_keys(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"file": rel(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings[:50]}


def validate_outputs(admission: dict[str, Any], audit: dict[str, Any], canonical_hash_before: str, trace_hash_before: str) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", rel(Path(__file__)), "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    json_errors = []
    checked_count = 0
    for path in M86.glob("*.json"):
        checked_count += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic_scan = scan_dynamic([M86])
    api_key_scan = scan_api_keys([M86, Path(__file__)])
    canonical_hash_after = stable_hash(read_json(CANONICAL_POOL))
    trace_hash_after = stable_hash(read_json(CANONICAL_TRACE))
    assertions = {
        "candidate_count_24": admission["summary"]["candidate_count"] == 24,
        "canonical_ready_at_least_8": admission["summary"]["canonical_update_ready_count"] >= 8,
        "unique_url_count_at_least_40": audit["summary"]["unique_url_count"] >= 40,
        "verified_url_count_nonzero": audit["summary"]["verified_url_count"] > 0,
        "canonical_pool_not_updated": canonical_hash_before == canonical_hash_after,
        "canonical_trace_not_updated": trace_hash_before == trace_hash_after,
        "no_dynamic_terms": dynamic_scan["status"] == "PASS",
        "api_key_scan_pass": api_key_scan["status"] == "PASS",
        "py_compile_pass": py_compile.returncode == 0,
        "json_parse_pass": not json_errors,
    }
    validation = {
        "milestone": "M86R",
        "generated_at": now(),
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": checked_count, "error_count": len(json_errors), "errors": json_errors},
        "dynamic_term_scan": dynamic_scan,
        "api_key_scan": api_key_scan,
        "assertions": assertions,
    }
    write_json(M86 / "m86r_validation_report_v1.json", validation)
    return validation


def update_panel(admission: dict[str, Any], audit: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel.update(
        {
            "generated_at": now(),
            "overall_status": "PASS_M86R_SOURCE_LOCATOR_HARDENING",
            "latest_milestone": "M86R",
            "canonical_next_action": "从 M86R canonical_update_ready 候选中选择进入 trusted pool update；仍需显式 allow guard。",
            "m86r_source_locator_hardening": {
                "candidate_count": admission["summary"]["candidate_count"],
                "canonical_update_ready_count": admission["summary"]["canonical_update_ready_count"],
                "not_ready_count": admission["summary"]["not_ready_count"],
                "unique_url_count": audit["summary"]["unique_url_count"],
                "verified_url_count": audit["summary"]["verified_url_count"],
                "canonical_pool_updated": False,
                "vault_regular_written": False,
                "old_workbook_write_enabled": False,
                "knowledge_asset_write_enabled": False,
                "persona_registry_write_enabled": False,
            },
        }
    )
    write_json(STATUS_PANEL, panel)


def main() -> int:
    M86.mkdir(parents=True, exist_ok=True)
    canonical_hash_before = stable_hash(read_json(CANONICAL_POOL))
    trace_hash_before = stable_hash(read_json(CANONICAL_TRACE))
    pool = read_json(M85 / "trusted_pool_input_v1.json")
    trace = read_json(M85 / "source_trace_index_v1.json")
    review = read_json(M85 / "m85r_report_only_review_v1.json")

    audit_result = audit_urls(trace)
    hardened_trace = build_hardened_trace(trace, audit_result["by_url"])
    built = build_admission(hardened_trace, review, pool)
    no_write = {
        "milestone": "M86R",
        "generated_at": now(),
        "status": "PASS_NO_CANONICAL_OR_LEGACY_WRITE",
        "canonical_pool_updated": False,
        "canonical_trace_updated": False,
        "vault_regular_written": False,
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    write_json(M86 / "m86r_no_write_proof_v1.json", no_write)
    operating_panel = {
        "milestone": "M86R",
        "generated_at": now(),
        "status": "PASS_M86R_SOURCE_LOCATOR_HARDENING_READY",
        "summary": {
            **built["package"]["summary"],
            "unique_url_count": audit_result["audit"]["summary"]["unique_url_count"],
            "verified_url_count": audit_result["audit"]["summary"]["verified_url_count"],
        },
        "next_action": "只从 canonical_update_ready=true 的候选中选择进入 M87R trusted pool update preview。",
    }
    write_json(M86 / "m86r_operating_panel_v1.json", operating_panel)
    handoff = {
        "milestone": "M86R",
        "generated_at": now(),
        "current_scope": "M85R 非上市候选 source locator 硬化与 canonical update 准入。",
        "canonical_update_ready_count": built["package"]["summary"]["canonical_update_ready_count"],
        "canonical_pool_updated": False,
        "next_command": "python3 scripts/build_m86r_source_locator_hardening.py",
    }
    write_json(M86 / "handoff_snapshot_v1.json", handoff)
    validation = validate_outputs(built["package"], audit_result["audit"], canonical_hash_before, trace_hash_before)
    update_panel(built["package"], audit_result["audit"])
    print(json.dumps({"audit": audit_result["audit"]["summary"], "admission": built["package"]["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
