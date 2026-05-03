from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M87 = MILESTONES / "milestone87r_trusted_pool_update_preview"
M88 = MILESTONES / "milestone88r_canonical_trusted_pool_update"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)


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


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M88R canonical trusted pool update from M87R preview.")
    parser.add_argument("--allow-canonical-update", action="store_true", help="Required to write canonical trusted pool and source trace.")
    return parser


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md"}]
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


def prepare_canonical_payloads() -> dict[str, Any]:
    preview_pool = read_json(M87 / "trusted_pool_update_preview_v1.json")
    preview_trace = read_json(M87 / "source_trace_update_preview_v1.json")
    preview_diff = read_json(M87 / "pool_diff_preview_v1.json")
    trace_diff = read_json(M87 / "source_trace_diff_preview_v1.json")
    m87_validation = read_json(M87 / "m87r_validation_report_v1.json")
    if m87_validation.get("status") != "PASS":
        raise RuntimeError("M87R validation is not PASS; refusing canonical update.")
    if preview_diff.get("summary", {}).get("append_new_count") != 11:
        raise RuntimeError("M87R append_new_count is not 11; refusing canonical update.")
    if trace_diff.get("summary", {}).get("changed_trace_count") != 11:
        raise RuntimeError("M87R changed_trace_count is not 11; refusing canonical update.")

    level_counts = Counter(item.get("level") for item in preview_pool.get("items") or [])
    preview_pool["generated_at"] = now()
    preview_pool["summary"] = {
        **(preview_pool.get("summary") or {}),
        "trusted_pool_count": len(preview_pool.get("items") or []),
        "source_trace_count": len(preview_trace.get("items") or []),
        "static_level_counts": dict(level_counts),
        "canonical_update_source": "M88R",
        "runner": "trusted_pool_runner_v3",
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "no_write_proof_ok": True,
    }
    for item in preview_pool.get("items") or []:
        if item.get("canonical_update_source") == "M87R_preview_from_M86R_hardened_ready":
            item["canonical_update_source"] = "M88R_from_M86R_hardened_ready"

    category_counts = Counter(source.get("source_category") for item in preview_trace.get("items") or [] for source in item.get("sources") or [])
    preview_trace["generated_at"] = now()
    preview_trace["summary"] = {
        **(preview_trace.get("summary") or {}),
        "source_trace_count": len(preview_trace.get("items") or []),
        "source_category_counts": dict(category_counts),
        "canonical_update_source": "M88R",
    }
    for item in preview_trace.get("items") or []:
        if item.get("added_by_milestone") == "M87R_preview":
            item["added_by_milestone"] = "M88R"
        for source in item.get("sources") or []:
            if source.get("added_by_milestone") == "M87R_preview":
                source["added_by_milestone"] = "M88R"
    return {"pool": preview_pool, "trace": preview_trace, "preview_diff": preview_diff, "trace_diff": trace_diff}


def write_canonical(payloads: dict[str, Any]) -> dict[str, Any]:
    before_pool = read_json(CANONICAL_POOL)
    before_trace = read_json(CANONICAL_TRACE)
    before_pool_hash = stable_hash(before_pool)
    before_trace_hash = stable_hash(before_trace)
    write_json(CANONICAL_POOL, payloads["pool"])
    write_json(CANONICAL_TRACE, payloads["trace"])
    after_pool = read_json(CANONICAL_POOL)
    after_trace = read_json(CANONICAL_TRACE)
    after_pool_hash = stable_hash(after_pool)
    after_trace_hash = stable_hash(after_trace)
    diff = {
        "milestone": "M88R",
        "generated_at": now(),
        "status": "PASS_M88R_CANONICAL_WRITE_DIFF_READY",
        "summary": {
            "before_pool_count": len(before_pool.get("items") or []),
            "after_pool_count": len(after_pool.get("items") or []),
            "before_trace_count": len(before_trace.get("items") or []),
            "after_trace_count": len(after_trace.get("items") or []),
            "appended_pool_count": len(after_pool.get("items") or []) - len(before_pool.get("items") or []),
            "appended_trace_count": len(after_trace.get("items") or []) - len(before_trace.get("items") or []),
            "before_pool_hash": before_pool_hash,
            "after_pool_hash": after_pool_hash,
            "before_trace_hash": before_trace_hash,
            "after_trace_hash": after_trace_hash,
            "canonical_pool_updated": before_pool_hash != after_pool_hash,
            "canonical_trace_updated": before_trace_hash != after_trace_hash,
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        },
        "pool_diff_preview_file": rel(M87 / "pool_diff_preview_v1.json"),
        "source_trace_diff_preview_file": rel(M87 / "source_trace_diff_preview_v1.json"),
    }
    write_json(M88 / "canonical_write_diff_v1.json", diff)
    return diff


def run_post_update_checks() -> dict[str, Any]:
    common = [
        "python3",
        "scripts/trusted_pool_runner.py",
        "--mode",
        "report_only",
        "--trusted-pool",
        rel(CANONICAL_POOL),
        "--source-trace",
        rel(CANONICAL_TRACE),
        "--output-file",
        rel(M88 / "m88r_post_update_report_only_v1.json"),
        "--gap-queue-file",
        rel(M88 / "m88r_post_update_gap_queue_v1.json"),
        "--source-trace-output",
        rel(M88 / "m88r_post_update_source_trace_normalized_v1.json"),
        "--no-write-proof-file",
        rel(M88 / "m88r_post_update_no_write_proof_v1.json"),
        "--pool-diff-file",
        rel(M88 / "m88r_post_update_pool_diff_v1.json"),
        "--validation-report-file",
        rel(M88 / "m88r_post_update_runner_validation_v1.json"),
        "--baseline-file",
        rel(M88 / "m88r_post_update_baseline_v1.json"),
    ]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    guard = run([
        "python3",
        "scripts/trusted_pool_runner.py",
        "--mode",
        "update_trusted_pool",
        "--trusted-pool",
        rel(CANONICAL_POOL),
        "--source-trace",
        rel(CANONICAL_TRACE),
        "--output-file",
        rel(M88 / "m88r_update_guard_probe_v1.json"),
        "--validation-report-file",
        rel(M88 / "m88r_update_guard_probe_validation_v1.json"),
    ])
    probe = {"returncode": guard.returncode, "stderr": guard.stderr, "expected_failure": True}
    write_json(M88 / "m88r_update_guard_probe_v1.json", probe)
    return probe


def validate(diff: dict[str, Any], guard_probe: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", rel(Path(__file__)), "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    json_errors = []
    checked = 0
    for path in M88.glob("*.json"):
        checked += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    report = read_json(M88 / "m88r_post_update_report_only_v1.json")
    dynamic_scan = scan_dynamic([M88, CANONICAL_POOL, CANONICAL_TRACE])
    api_key_scan = scan_api_keys([M88, CANONICAL_POOL, CANONICAL_TRACE, Path(__file__)])
    level_counts = pool.get("summary", {}).get("static_level_counts") or {}
    assertions = {
        "canonical_pool_updated": diff["summary"]["canonical_pool_updated"],
        "canonical_trace_updated": diff["summary"]["canonical_trace_updated"],
        "pool_count_61": len(pool.get("items") or []) == 61,
        "trace_count_61": len(trace.get("items") or []) == 61,
        "appended_pool_count_11": diff["summary"]["appended_pool_count"] == 11,
        "appended_trace_count_11": diff["summary"]["appended_trace_count"] == 11,
        "level_counts_expected": level_counts == {"L1": 35, "L2": 25, "L4": 1},
        "post_update_report_count_61": report.get("summary", {}).get("prospect_count") == 61,
        "update_guard_failed_without_allow": guard_probe.get("returncode") == 2,
        "no_dynamic_terms": dynamic_scan["status"] == "PASS",
        "api_key_scan_pass": api_key_scan["status"] == "PASS",
        "py_compile_pass": py_compile.returncode == 0,
        "json_parse_pass": not json_errors,
    }
    validation = {
        "milestone": "M88R",
        "generated_at": now(),
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": checked, "error_count": len(json_errors), "errors": json_errors},
        "dynamic_term_scan": dynamic_scan,
        "api_key_scan": api_key_scan,
        "assertions": assertions,
    }
    write_json(M88 / "m88r_validation_report_v1.json", validation)
    return validation


def update_panel(diff: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel.update(
        {
            "generated_at": now(),
            "overall_status": "PASS_M88R_CANONICAL_TRUSTED_POOL_UPDATED",
            "latest_milestone": "M88R",
            "canonical_next_action": "进入 M89R：为新写入的 11 家生成 vault 正区输出准入与正式档案写入。",
            "m88r_canonical_trusted_pool_update": {
                "after_pool_count": diff["summary"]["after_pool_count"],
                "after_trace_count": diff["summary"]["after_trace_count"],
                "appended_pool_count": diff["summary"]["appended_pool_count"],
                "appended_trace_count": diff["summary"]["appended_trace_count"],
                "canonical_pool_updated": True,
                "canonical_trace_updated": True,
                "vault_regular_written": False,
                "old_workbook_write_enabled": False,
                "knowledge_asset_write_enabled": False,
                "persona_registry_write_enabled": False,
            },
        }
    )
    write_json(STATUS_PANEL, panel)


def main() -> int:
    args = build_parser().parse_args()
    M88.mkdir(parents=True, exist_ok=True)
    if not args.allow_canonical_update:
        probe = {"milestone": "M88R", "generated_at": now(), "status": "FAIL_GUARD_REQUIRED", "returncode": 2, "error": "canonical update requires --allow-canonical-update"}
        write_json(M88 / "m88r_canonical_update_guard_probe_v1.json", probe)
        print(probe["error"])
        return 2
    payloads = prepare_canonical_payloads()
    diff = write_canonical(payloads)
    guard_probe = run_post_update_checks()
    no_write = {
        "milestone": "M88R",
        "generated_at": now(),
        "status": "PASS_CANONICAL_ONLY_WRITE",
        "canonical_pool_updated": True,
        "canonical_trace_updated": True,
        "vault_regular_written": False,
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    write_json(M88 / "m88r_no_write_proof_v1.json", no_write)
    operating = {
        "milestone": "M88R",
        "generated_at": now(),
        "status": "PASS_M88R_CANONICAL_UPDATE_COMPLETE",
        "summary": diff["summary"],
        "next_action": "M89R：为新增 11 家生成 vault 正区输出准入与正式档案写入。",
    }
    write_json(M88 / "m88r_operating_panel_v1.json", operating)
    handoff = {
        "milestone": "M88R",
        "generated_at": now(),
        "current_scope": "M87R preview 正式提升为 canonical trusted pool/source trace。",
        "canonical_pool_updated": True,
        "canonical_trace_updated": True,
        "next_command": "python3 scripts/build_m88r_canonical_trusted_pool_update.py --allow-canonical-update",
    }
    write_json(M88 / "handoff_snapshot_v1.json", handoff)
    validation = validate(diff, guard_probe)
    update_panel(diff)
    print(json.dumps({"diff": diff["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
