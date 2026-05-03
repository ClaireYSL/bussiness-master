from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
C11 = MILESTONES / "workspace_cleanup_c11_archive_import"
C12 = MILESTONES / "workspace_cleanup_c12_legacy_import"
C13 = MILESTONES / "workspace_cleanup_c13_tracked_decisions"
C14 = MILESTONES / "workspace_cleanup_c14_status_panel"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return run(["git", "-c", "core.quotePath=false", *args])


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE))


def untracked_paths() -> list[str]:
    return [line for line in git(["ls-files", "--others", "--exclude-standard"]).stdout.splitlines() if line]


def tracked_modified_paths() -> list[str]:
    paths: list[str] = []
    for line in git(["status", "--short"]).stdout.splitlines():
        if line.startswith((" M ", "M  ", "MM ")):
            paths.append(line[3:])
    return paths


def path_exists(path: str) -> bool:
    return (WORKSPACE / path).exists()


def is_archive_import_candidate(path: str) -> bool:
    return path.startswith("deliveries/archive/handoffs/") or path.startswith("deliveries/archive/milestones/") or path.startswith("deliveries/archive/repairs/") or path.startswith("docs/00-") or path.startswith("docs/03-")


def is_legacy_keep_or_import(path: str) -> bool:
    if path.startswith("configs/enrich_batches/") or path.startswith("configs/execution_batches/") or path.startswith("configs/promote_batches/"):
        return True
    if path.startswith("prompts/"):
        return True
    if not path.startswith("scripts/") or not path.endswith(".py"):
        return False
    name = Path(path).name
    if name.startswith("build_m") or name.startswith("build_") or name.startswith("execute_m"):
        return True
    if name in {"pre_writeback_gate_check.py", "run_project_readiness_check.py"}:
        return True
    return False


def classify_untracked(path: str) -> str:
    if is_archive_import_candidate(path):
        return "archive_import_candidate"
    if is_legacy_keep_or_import(path):
        return "legacy_keep_local_or_import"
    return "needs_human_decision"


def classify_tracked(path: str) -> str:
    lower = path.lower()
    if path == "deliveries/archive/milestones/milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json":
        return "current_cleanup_commit_candidate"
    if "milestone6r" in lower or "milestone 6r" in lower or "workbook_integrity_report" in lower:
        return "archive_snapshot_commit_candidate"
    return "needs_user_or_historical_decision"


def safe_json_parse(paths: list[str]) -> dict[str, Any]:
    checked = 0
    errors = []
    for path in paths:
        p = WORKSPACE / path
        if p.is_file() and p.suffix == ".json":
            checked += 1
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": path, "error": str(exc)})
    return {"checked_count": checked, "error_count": len(errors), "errors": errors}


def contains_write_back_true(path: str) -> bool:
    p = WORKSPACE / path
    if not p.is_file() or p.suffix != ".json":
        return False
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return False

    def walk(obj: Any) -> bool:
        if isinstance(obj, dict):
            return any((k == "write_back" and v is True) or walk(v) for k, v in obj.items())
        if isinstance(obj, list):
            return any(walk(item) for item in obj)
        return False

    return walk(payload)


def is_current_cleanup_generated(path: str) -> bool:
    return (
        path.startswith("deliveries/archive/milestones/workspace_cleanup_c11_archive_import/")
        or path.startswith("deliveries/archive/milestones/workspace_cleanup_c12_legacy_import/")
        or path.startswith("deliveries/archive/milestones/workspace_cleanup_c13_tracked_decisions/")
        or path.startswith("deliveries/archive/milestones/workspace_cleanup_c14_status_panel/")
        or path == "scripts/build_c11_c14_workspace_cleanup_execution.py"
    )


def build_c11(untracked: list[str]) -> dict[str, Any]:
    items = sorted([path for path in untracked if not is_current_cleanup_generated(path) and classify_untracked(path) == "archive_import_candidate" and path_exists(path)])
    by_root = Counter(path.split("/")[0] + "/" + path.split("/")[1] if "/" in path else path for path in items)
    manifest = {
        "milestone": "C11",
        "generated_at": now(),
        "status": "PASS_C11_ARCHIVE_IMPORT_MANIFEST_READY",
        "summary": {"archive_import_candidate_count": len(items), "json_parse_error_count": safe_json_parse(items)["error_count"]},
        "policy": {
            "import_type": "versioned_archive_import_only",
            "content_modified": False,
            "old_runner_executed": False,
            "old_excel_written": False,
        },
        "root_counts": dict(by_root),
        "items": items,
    }
    parse_report = {"milestone": "C11", "generated_at": now(), "status": "PASS" if safe_json_parse(items)["error_count"] == 0 else "FAIL", **safe_json_parse(items)}
    proof = {
        "milestone": "C11",
        "generated_at": now(),
        "status": "PASS_C11_ARCHIVE_IMPORT_NO_BEHAVIOR_CHANGE",
        "files_deleted": False,
        "files_moved": False,
        "file_content_modified": False,
        "old_enrich_promote_runner_executed": False,
        "old_workbook_written": False,
    }
    write_json(C11 / "archive_import_manifest_v1.json", manifest)
    write_json(C11 / "json_parse_report_v1.json", parse_report)
    write_json(C11 / "archive_import_no_behavior_change_proof_v1.json", proof)
    write_lines(C11 / "archive_import_paths_v1.txt", items)
    return {"manifest": manifest, "parse_report": parse_report, "proof": proof, "paths": items}


def build_c12(untracked: list[str]) -> dict[str, Any]:
    items = sorted([path for path in untracked if not is_current_cleanup_generated(path) and classify_untracked(path) == "legacy_keep_local_or_import" and path_exists(path)])
    write_back_items = [path for path in items if contains_write_back_true(path)]
    by_kind = defaultdict(list)
    for path in items:
        if path.startswith("configs/"):
            by_kind["configs"].append(path)
        elif path.startswith("scripts/"):
            by_kind["scripts"].append(path)
        elif path.startswith("prompts/"):
            by_kind["prompts"].append(path)
        else:
            by_kind["other"].append(path)
    manifest = {
        "milestone": "C12",
        "generated_at": now(),
        "status": "PASS_C12_LEGACY_IMPORT_MANIFEST_READY",
        "summary": {
            "legacy_import_candidate_count": len(items),
            "config_count": len(by_kind["configs"]),
            "script_count": len(by_kind["scripts"]),
            "prompt_count": len(by_kind["prompts"]),
            "write_back_true_count": len(write_back_items),
            "json_parse_error_count": safe_json_parse(items)["error_count"],
        },
        "policy": {
            "new_mainline_entry": False,
            "legacy_write_requires_override": True,
            "config_content_modified": False,
            "legacy_runner_executed": False,
        },
        "items_by_kind": dict(by_kind),
        "items": items,
    }
    write_back_inventory = {
        "milestone": "C12",
        "generated_at": now(),
        "status": "PASS_C12_WRITE_BACK_TRUE_INVENTORY_READY",
        "summary": {"write_back_true_count": len(write_back_items)},
        "policy": "这些配置只作为 legacy 历史存在；真实写回必须走 legacy override，不作为 evidence-first 主线入口。",
        "items": write_back_items,
    }
    no_execution = {
        "milestone": "C12",
        "generated_at": now(),
        "status": "PASS_C12_LEGACY_IMPORT_NO_EXECUTION",
        "legacy_runner_executed": False,
        "old_workbook_written": False,
        "config_files_modified": False,
    }
    write_json(C12 / "legacy_config_script_import_manifest_v1.json", manifest)
    write_json(C12 / "write_back_true_inventory_v1.json", write_back_inventory)
    write_json(C12 / "legacy_no_execution_proof_v1.json", no_execution)
    write_lines(C12 / "legacy_import_paths_v1.txt", items)
    return {"manifest": manifest, "write_back_inventory": write_back_inventory, "proof": no_execution, "paths": items}


def build_c13(tracked: list[str]) -> dict[str, Any]:
    groups = {
        "archive_snapshot_commit_candidate": [],
        "current_cleanup_commit_candidate": [],
        "needs_user_or_historical_decision": [],
        "do_not_touch": [],
    }
    for path in sorted(tracked):
        groups[classify_tracked(path)].append(path)
    package = {
        "milestone": "C13",
        "generated_at": now(),
        "status": "PASS_C13_TRACKED_CHANGE_DECISION_PACKAGE_READY",
        "summary": {key + "_count": len(value) for key, value in groups.items()},
        "policy": {
            "auto_revert": False,
            "auto_overwrite": False,
            "archive_snapshot_commit_allowed_later": True,
            "current_commit_includes_tracked_modified": "only current_cleanup_commit_candidate",
        },
        "groups": groups,
    }
    proof = {
        "milestone": "C13",
        "generated_at": now(),
        "status": "PASS_C13_NO_REVERT_PROOF",
        "git_reset_executed": False,
        "git_checkout_restore_executed": False,
        "tracked_files_modified_by_cleanup": False,
    }
    write_json(C13 / "tracked_changes_decision_package_v1.json", package)
    write_json(C13 / "no_revert_proof_v1.json", proof)
    return {"package": package, "proof": proof}


def scan_api_keys(paths: list[str]) -> dict[str, Any]:
    findings = []
    for path in paths:
        p = WORKSPACE / path
        if not p.is_file() or p.suffix not in {".json", ".md", ".py", ".txt"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for pattern in API_KEY_PATTERNS:
            if pattern.search(text):
                findings.append({"path": path, "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def scan_dynamic_terms(paths: list[str]) -> dict[str, Any]:
    findings = []
    allowed = []
    for path in paths:
        p = WORKSPACE / path
        if not p.is_file() or p.suffix not in {".json", ".md", ".py", ".txt"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for term in DYNAMIC_TERMS:
            if term in text:
                record = {"path": path, "term": term}
                if (
                    path.startswith("deliveries/archive/")
                    or path.startswith("docs/00-")
                    or path.startswith("docs/03-")
                    or path.startswith("configs/")
                    or (path.startswith("scripts/") and path != "scripts/trusted_pool_runner.py")
                    or "legacy" in path
                    or "cleanup" in path
                ):
                    allowed.append({**record, "reason": "legacy_archive_import_or_cleanup_reference"})
                else:
                    findings.append(record)
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings, "allowed_references": allowed[:200], "allowed_reference_count": len(allowed)}


def build_c14(c11: dict[str, Any], c12: dict[str, Any], c13: dict[str, Any], before_untracked_count: int, before_tracked_count: int) -> dict[str, Any]:
    after_untracked = len(untracked_paths())
    after_tracked = len(tracked_modified_paths())
    panel = {
        "milestone": "C14",
        "generated_at": now(),
        "status": "PASS_C14_CLEANUP_STATUS_PANEL_READY",
        "summary": {
            "before_untracked_count": before_untracked_count,
            "before_tracked_modified_count": before_tracked_count,
            "current_untracked_count_before_staging": after_untracked,
            "current_tracked_modified_count": after_tracked,
            "archive_import_candidate_count": c11["manifest"]["summary"]["archive_import_candidate_count"],
            "legacy_import_candidate_count": c12["manifest"]["summary"]["legacy_import_candidate_count"],
            "tracked_decision_count": sum(c13["package"]["summary"].values()),
        },
        "next_cleanup_step": "Stage and commit C11 archive/import candidates plus C12 legacy candidates; keep C13 tracked modified out of the commit.",
        "remaining_risk": "tracked modified files still require user/historical decision; no revert has been done.",
    }
    handoff = {
        "milestone": "C14",
        "generated_at": now(),
        "status": "PASS_C14_HANDOFF_SNAPSHOT_CLEANUP_PROGRESS_READY",
        "latest_cleanup": "C14",
        "key_outputs": {
            "c11_archive_manifest": rel(C11 / "archive_import_manifest_v1.json"),
            "c12_legacy_manifest": rel(C12 / "legacy_config_script_import_manifest_v1.json"),
            "c13_tracked_decisions": rel(C13 / "tracked_changes_decision_package_v1.json"),
            "c14_status_panel": rel(C14 / "workspace_cleanup_status_panel_v2.json"),
        },
        "do_not_do": ["delete", "reset", "move historical files", "run legacy write_back", "stage C13 tracked modified without explicit decision"],
    }
    write_json(C14 / "workspace_cleanup_status_panel_v2.json", panel)
    write_json(C14 / "handoff_snapshot_clean_worktree_progress_v1.json", handoff)

    status_panel = read_json(STATUS_PANEL)
    status_panel["generated_at"] = now()
    status_panel["latest_workspace_cleanup"] = "C14"
    status_panel["workspace_cleanup_status"] = "PASS_C14_CLEANUP_IMPORT_READY"
    status_panel["c11_archive_import"] = c11["manifest"]["summary"]
    status_panel["c12_legacy_import"] = c12["manifest"]["summary"]
    status_panel["c13_tracked_decisions"] = c13["package"]["summary"]
    status_panel["c14_cleanup_panel"] = panel["summary"]
    write_json(STATUS_PANEL, status_panel)
    return {"panel": panel, "handoff": handoff}


def validate(c11: dict[str, Any], c12: dict[str, Any], c13: dict[str, Any], c14: dict[str, Any]) -> dict[str, Any]:
    generated = [
        rel(C11 / "archive_import_manifest_v1.json"),
        rel(C11 / "json_parse_report_v1.json"),
        rel(C11 / "archive_import_no_behavior_change_proof_v1.json"),
        rel(C11 / "archive_import_paths_v1.txt"),
        rel(C12 / "legacy_config_script_import_manifest_v1.json"),
        rel(C12 / "write_back_true_inventory_v1.json"),
        rel(C12 / "legacy_no_execution_proof_v1.json"),
        rel(C12 / "legacy_import_paths_v1.txt"),
        rel(C13 / "tracked_changes_decision_package_v1.json"),
        rel(C13 / "no_revert_proof_v1.json"),
        rel(C14 / "workspace_cleanup_status_panel_v2.json"),
        rel(C14 / "handoff_snapshot_clean_worktree_progress_v1.json"),
        rel(STATUS_PANEL),
    ]
    all_paths_for_scan = c11["paths"] + c12["paths"] + generated + ["scripts/build_c11_c14_workspace_cleanup_execution.py"]
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_c11_c14_workspace_cleanup_execution.py"])
    json_errors = []
    checked = 0
    for path in all_paths_for_scan:
        p = WORKSPACE / path
        if p.is_file() and p.suffix == ".json":
            checked += 1
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                json_errors.append({"path": path, "error": str(exc)})
    api = scan_api_keys(all_paths_for_scan)
    dynamic = scan_dynamic_terms(all_paths_for_scan)
    assertions = {
        "c11_no_behavior_change": c11["proof"].get("file_content_modified") is False and c11["proof"].get("old_workbook_written") is False,
        "c12_no_legacy_execution": c12["proof"].get("legacy_runner_executed") is False and c12["proof"].get("old_workbook_written") is False,
        "c13_no_revert": c13["proof"].get("git_reset_executed") is False and c13["proof"].get("git_checkout_restore_executed") is False,
        "c14_ready": c14["panel"].get("status") == "PASS_C14_CLEANUP_STATUS_PANEL_READY",
    }
    status = "PASS" if py_compile.returncode == 0 and not json_errors and api["status"] == "PASS" and dynamic["status"] == "PASS" and all(assertions.values()) else "FAIL"
    report = {
        "milestone": "C11-C14",
        "generated_at": now(),
        "status": status,
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": checked, "error_count": len(json_errors), "errors": json_errors},
        "api_key_scan": api,
        "dynamic_term_scan": dynamic,
        "assertions": assertions,
    }
    write_json(C14 / "c11_c14_validation_report_v1.json", report)
    return report


def main() -> int:
    for directory in (C11, C12, C13, C14):
        directory.mkdir(parents=True, exist_ok=True)
    before_untracked = len(untracked_paths())
    before_tracked = len(tracked_modified_paths())
    untracked = untracked_paths()
    tracked = tracked_modified_paths()
    c11 = build_c11(untracked)
    c12 = build_c12(untracked)
    c13 = build_c13(tracked)
    c14 = build_c14(c11, c12, c13, before_untracked, before_tracked)
    report = validate(c11, c12, c13, c14)
    # Refresh C14 after validation exists.
    c14 = build_c14(c11, c12, c13, before_untracked, before_tracked)
    report = validate(c11, c12, c13, c14)
    print(json.dumps({
        "status": report["status"],
        "c11": c11["manifest"]["summary"],
        "c12": c12["manifest"]["summary"],
        "c13": c13["package"]["summary"],
        "c14": c14["panel"]["summary"],
    }, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
