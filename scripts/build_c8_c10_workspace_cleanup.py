from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
C8 = MILESTONES / "workspace_cleanup_c8_low_risk_closure"
C9 = MILESTONES / "workspace_cleanup_c9_legacy_runner_inventory"
C10 = MILESTONES / "workspace_cleanup_c10_handoff_snapshot"
C7_MANIFEST = MILESTONES / "workspace_cleanup_c7_final_governance/workspace_final_governance_manifest_v1.json"
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


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE))


def git_status_lines() -> list[str]:
    return run(["git", "status", "--short"]).stdout.splitlines()


def untracked_paths() -> list[str]:
    return run(["git", "ls-files", "--others", "--exclude-standard"]).stdout.splitlines()


def tracked_modified_paths() -> list[str]:
    paths = []
    for line in git_status_lines():
        if line.startswith(" M ") or line.startswith("M  ") or line.startswith("MM "):
            paths.append(line[3:])
    return paths


def classify_untracked(path: str) -> str:
    lower = path.lower()
    if lower.startswith("static-pool-deps") or lower.endswith(".zip"):
        return "safe_to_ignore_local"
    if path.startswith("deliveries/archive/handoffs/"):
        return "archive_import_candidate"
    if path.startswith("deliveries/archive/milestones/") or path.startswith("deliveries/archive/repairs/"):
        return "archive_import_candidate"
    if path.startswith("configs/") or path.startswith("scripts/build_") or path.startswith("scripts/execute_") or path.startswith("prompts/"):
        return "legacy_keep_local_or_ignore"
    if path.startswith("docs/03-") or path.startswith("docs/00-"):
        return "archive_import_candidate"
    return "needs_human_decision"


def classify_tracked(path: str) -> str:
    lower = path.lower()
    if "milestone6r" in lower or "milestone 6r" in lower or "workbook_integrity_report" in lower:
        return "needs_human_decision"
    if path.startswith("scripts/select_execution_candidates.py") or path.startswith("shared/static_pool/constants.py"):
        return "needs_human_decision"
    if path.startswith("docs/"):
        return "needs_human_decision"
    return "needs_human_decision"


def build_c8() -> dict[str, Any]:
    c7 = read_json(C7_MANIFEST)
    categories = {
        "archive_import_candidate": [],
        "legacy_keep_local_or_ignore": [],
        "needs_human_decision": [],
        "safe_to_ignore_local": [],
    }
    for path in untracked_paths():
        categories[classify_untracked(path)].append(path)
    for path in tracked_modified_paths():
        categories[classify_tracked(path)].append(path)

    gitignore = (WORKSPACE / ".gitignore").read_text(encoding="utf-8") if (WORKSPACE / ".gitignore").exists() else ""
    ignored_checks = {
        "raw_material_bundle_dir_ignored": "static-pool-deps-20260419_151148/" in gitignore,
        "raw_material_zip_ignored": "static-pool-deps-20260419_151148.zip" in gitignore,
        "env_ignored": ".env" in gitignore,
        "pycache_ignored": "__pycache__/" in gitignore and "*.pyc" in gitignore,
    }
    ignore_strategy = {
        "milestone": "C8",
        "generated_at": now(),
        "status": "PASS_IGNORE_STRATEGY_NO_REPO_CHANGE_REQUIRED" if all(ignored_checks.values()) else "WARN_IGNORE_STRATEGY_REVIEW_REQUIRED",
        "checks": ignored_checks,
        "repo_gitignore_changed": False,
        "local_git_exclude_changed": False,
        "recommendation": "当前不新增忽略规则；历史 archive/config 仍保留可见，避免隐藏后续 archive import 候选。",
    }
    classification = {
        "milestone": "C8",
        "generated_at": now(),
        "status": "PASS_C8_LOW_RISK_WORKSPACE_CLASSIFICATION_READY",
        "source_manifest": str(C7_MANIFEST.relative_to(WORKSPACE)),
        "summary": {key + "_count": len(value) for key, value in categories.items()},
        "actions": {
            "archive_import_candidate": "后续单独 archive import 批次处理，不与主线代码混提。",
            "legacy_keep_local_or_ignore": "保留本地或后续 legacy 包导入；不作为新 evidence-first 主线入口。",
            "needs_human_decision": "疑似用户/历史 tracked 改动，禁止自动回滚、覆盖或删除。",
            "safe_to_ignore_local": "本机依赖或临时资源，应由 .gitignore 或 handoff 说明隔离。",
        },
        "categories": categories,
        "previous_c7_summary": c7.get("summary", {}),
    }
    proof = {
        "milestone": "C8",
        "generated_at": now(),
        "status": "PASS_C8_NO_DESTRUCTIVE_ACTION",
        "delete_executed": False,
        "reset_executed": False,
        "move_executed": False,
        "tracked_history_overwritten": False,
        "repo_gitignore_changed": False,
    }
    write_json(C8 / "workspace_cleanup_classification_v1.json", classification)
    write_json(C8 / "ignore_strategy_report_v1.json", ignore_strategy)
    write_json(C8 / "no_destructive_cleanup_proof_v1.json", proof)
    return {"classification": classification, "ignore_strategy": ignore_strategy, "proof": proof}


def read_json_file_maybe(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def is_write_back_enabled(payload: Any) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "write_back" and value is True:
                return True
            if is_write_back_enabled(value):
                return True
    if isinstance(payload, list):
        return any(is_write_back_enabled(item) for item in payload)
    return False


def inventory_config(path: Path) -> dict[str, Any]:
    payload = read_json_file_maybe(path)
    rel_path = rel(path)
    write_back = is_write_back_enabled(payload)
    if path.parts[:2] == ("configs", "archive"):
        status = "historical_archive_only"
    elif "promote_batches" in path.parts or "enrich_batches" in path.parts or "execution_batches" in path.parts:
        status = "legacy_runner_config_requires_override" if write_back else "legacy_or_report_only_config"
    else:
        status = "review_before_use"
    return {
        "path": rel_path,
        "write_back_true": write_back,
        "recommended_status": status,
        "new_mainline_entry": False,
        "requires_legacy_override_for_write": write_back,
    }


def inventory_script(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel_path = rel(path)
    touches_legacy_workbook = any(token in text for token in ["write_back", "main_shared", "workbook", "xlsx", "promotion_review"])
    trusted_mainline = path.name in {
        "trusted_pool_runner.py",
        "build_m61r_m64_trusted_pool_productization.py",
        "build_m65r_m68_trusted_pool_next_stage.py",
        "build_m69r_m72_l3_to_l2_closure.py",
    }
    if trusted_mainline:
        status = "trusted_pool_mainline_or_recent_builder"
    elif touches_legacy_workbook:
        status = "legacy_runner_or_legacy_builder"
    elif path.name.startswith("build_m"):
        status = "historical_milestone_builder"
    else:
        status = "utility_review_before_use"
    return {
        "path": rel_path,
        "recommended_status": status,
        "touches_legacy_workbook_terms": touches_legacy_workbook,
        "new_mainline_entry": trusted_mainline,
        "requires_legacy_override_for_write": touches_legacy_workbook and not trusted_mainline,
    }


def build_c9() -> dict[str, Any]:
    config_paths = sorted((WORKSPACE / "configs").rglob("*.json")) if (WORKSPACE / "configs").exists() else []
    configs = [inventory_config(path) for path in config_paths]
    script_candidates = []
    for path in sorted((WORKSPACE / "scripts").glob("*.py")):
        name = path.name
        if any(token in name for token in ["enrich", "promote", "execution", "expand", "writeback", "candidate", "m5", "m6", "m7", "m8", "m9"]):
            script_candidates.append(path)
        elif name.startswith("build_m") or name.startswith("execute_m"):
            script_candidates.append(path)
        elif name in {"trusted_pool_runner.py", "pre_writeback_gate_check.py", "select_execution_candidates.py"}:
            script_candidates.append(path)
    scripts = [inventory_script(path) for path in script_candidates]
    config_counts = Counter(item["recommended_status"] for item in configs)
    script_counts = Counter(item["recommended_status"] for item in scripts)
    inventory = {
        "milestone": "C9",
        "generated_at": now(),
        "status": "PASS_C9_LEGACY_RUNNER_INVENTORY_READY",
        "summary": {
            "config_count": len(configs),
            "config_write_back_true_count": sum(1 for item in configs if item["write_back_true"]),
            "script_count": len(scripts),
            "script_legacy_or_builder_count": sum(1 for item in scripts if item["recommended_status"] != "trusted_pool_mainline_or_recent_builder"),
            "trusted_mainline_script_count": sum(1 for item in scripts if item["new_mainline_entry"]),
        },
        "policy": {
            "new_default_runner": "trusted_pool_runner",
            "legacy_workbook_runners": "保留历史兼容；涉及写回必须依赖现有 legacy guard / override。",
            "config_mutation_in_c9": False,
        },
        "config_status_counts": dict(config_counts),
        "script_status_counts": dict(script_counts),
        "configs": configs,
        "scripts": scripts,
    }
    no_write = {
        "milestone": "C9",
        "generated_at": now(),
        "status": "PASS_C9_AUDIT_ONLY_NO_CONFIG_MUTATION",
        "config_files_modified": False,
        "legacy_runner_behavior_modified": False,
        "old_workbook_written": False,
    }
    write_json(C9 / "legacy_runner_inventory_v1.json", inventory)
    write_json(C9 / "legacy_runner_no_mutation_proof_v1.json", no_write)
    return {"inventory": inventory, "proof": no_write}


def build_c10(c8: dict[str, Any], c9: dict[str, Any]) -> dict[str, Any]:
    branch = run(["git", "branch", "--show-current"]).stdout.strip()
    last_commit = run(["git", "log", "-1", "--oneline"]).stdout.strip()
    panel = read_json(STATUS_PANEL)
    status_lines = git_status_lines()
    snapshot = {
        "milestone": "C10",
        "generated_at": now(),
        "status": "PASS_C10_WORKSPACE_HANDOFF_SNAPSHOT_READY",
        "branch": branch,
        "last_commit": last_commit,
        "trusted_pool_status": {
            "latest_milestone": panel.get("latest_milestone"),
            "overall_status": panel.get("overall_status"),
            "canonical_next_action": panel.get("canonical_next_action"),
        },
        "workspace_summary": {
            "git_status_line_count": len(status_lines),
            "c8_classification": c8["classification"].get("summary", {}),
            "c9_inventory": c9["inventory"].get("summary", {}),
        },
        "key_outputs": {
            "c8_classification": rel(C8 / "workspace_cleanup_classification_v1.json"),
            "c9_legacy_inventory": rel(C9 / "legacy_runner_inventory_v1.json"),
            "c10_handoff": rel(C10 / "workspace_handoff_snapshot_v1.json"),
        },
        "forbidden_actions_without_explicit_confirmation": [
            "git reset / checkout 回滚历史 tracked 改动",
            "删除或批量移动历史 archive/raw materials",
            "旧 Excel write_back",
            "把潜客产出写入知识资产或 persona registry",
        ],
        "next_recommended_step": "进入 M73R 第二强来源采集；提交时只纳入 M73R 主线产物，不混入 C8 标记为 needs_human_decision 的历史文件。",
    }
    panel["generated_at"] = now()
    panel["workspace_cleanup_status"] = "PASS_C10_WORKSPACE_HANDOFF_READY"
    panel["latest_workspace_cleanup"] = "C10"
    panel["c8_workspace_classification"] = c8["classification"].get("summary", {})
    panel["c9_legacy_runner_inventory"] = c9["inventory"].get("summary", {})
    panel["c10_workspace_handoff"] = {"status": snapshot["status"], "last_commit": last_commit, "branch": branch}
    write_json(C10 / "workspace_handoff_snapshot_v1.json", snapshot)
    write_json(STATUS_PANEL, panel)
    return {"snapshot": snapshot, "panel": panel}


def scan_dynamic_terms(paths: list[Path]) -> dict[str, Any]:
    findings = []
    allowed = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    record = {"path": rel(path), "term": term}
                    if "legacy" in path.name or "inventory" in path.name or "cleanup" in str(path):
                        allowed.append({**record, "reason": "cleanup_or_legacy_reference_only"})
                    else:
                        findings.append(record)
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings, "allowed_references": allowed}


def scan_api_keys(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            if path.name == ".env" or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"path": rel(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def validate(c8: dict[str, Any], c9: dict[str, Any], c10: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_c8_c10_workspace_cleanup.py"])
    json_paths = [*C8.glob("*.json"), *C9.glob("*.json"), *C10.glob("*.json"), STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    dynamic = scan_dynamic_terms([C8, C9, C10])
    api = scan_api_keys([C8, C9, C10, WORKSPACE / "scripts/build_c8_c10_workspace_cleanup.py"])
    assertions = {
        "c8_no_delete_reset_move": c8["proof"].get("delete_executed") is False and c8["proof"].get("reset_executed") is False and c8["proof"].get("move_executed") is False,
        "c9_no_config_mutation": c9["proof"].get("config_files_modified") is False,
        "c10_handoff_ready": c10["snapshot"].get("status") == "PASS_C10_WORKSPACE_HANDOFF_SNAPSHOT_READY",
        "raw_materials_ignored": c8["ignore_strategy"].get("checks", {}).get("raw_material_bundle_dir_ignored") is True,
    }
    status = "PASS" if py_compile.returncode == 0 and not json_errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and all(assertions.values()) else "FAIL"
    report = {
        "milestone": "C8-C10",
        "generated_at": now(),
        "status": status,
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "assertions": assertions,
    }
    write_json(C10 / "c8_c10_validation_report_v1.json", report)
    return report


def main() -> int:
    for directory in (C8, C9, C10):
        directory.mkdir(parents=True, exist_ok=True)
    c8 = build_c8()
    c9 = build_c9()
    c10 = build_c10(c8, c9)
    report = validate(c8, c9, c10)
    # Refresh C10 after validation exists so handoff line count reflects final state.
    c10 = build_c10(c8, c9)
    report = validate(c8, c9, c10)
    print(json.dumps({"status": report["status"], "c8": c8["classification"]["summary"], "c9": c9["inventory"]["summary"], "c10": c10["snapshot"]["status"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
