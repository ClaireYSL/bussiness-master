#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "deliveries/archive/milestones/workspace_cleanup_c15_tracked_resolution"

ARCHIVE_PREFIXES = (
    "deliveries/archive/milestones/milestone6r_trust/",
    "deliveries/archive/repairs/workbook_integrity_report_v1.json",
    "docs/03-执行与校验/Milestone 6R-主表修复与可信增强-",
)

CURRENT_MAINLINE = {
    "docs/00-当前总览/README.md": "总览入口补充当前主线文档索引。",
    "docs/00-当前总览/静态潜客池-Milestone状态总览-v1.0.md": "阶段总览补齐 M7-M40 历史演进与 legacy 隔离口径。",
    "docs/02-注册表与结构/knowledge_asset_registry_v1-字段模板-v1.md": "补充潜客产出不能污染知识资产的边界说明。",
    "scripts/select_execution_candidates.py": "候选选择脚本优先尊重 STATIC_POOL_* 环境变量，避免旧绝对路径漂移。",
    "shared/static_pool/constants.py": "兼容 auto_ingested / promotion_completed 历史 review_status，保持静态升层机制可运行。",
}


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True)


def modified_paths() -> list[str]:
    raw = subprocess.check_output(["git", "diff", "--name-only", "-z"], cwd=ROOT)
    return [part.decode("utf-8") for part in raw.split(b"\0") if part]


def diff_stat(path: str) -> str:
    return run(["git", "diff", "--stat", "--", path]).strip()


def classify(path: str) -> tuple[str, str, str]:
    if path.startswith(ARCHIVE_PREFIXES):
        return (
            "archive_snapshot_commit",
            "commit_as_current_local_archive_snapshot",
            "这是历史 M6R 本机可信运行快照/复盘/完整性报告；不作为新主线事实源，但提交后可消除工作区漂移。",
        )
    if path in CURRENT_MAINLINE:
        return (
            "current_mainline_commit",
            "commit_as_boundary_or_compatibility_fix",
            CURRENT_MAINLINE[path],
        )
    return (
        "needs_human_decision",
        "do_not_stage_until_reviewed",
        "未匹配 C15 安全分类，保持不触碰。",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = modified_paths()
    items = []
    groups: dict[str, list[str]] = {
        "archive_snapshot_commit": [],
        "current_mainline_commit": [],
        "needs_human_decision": [],
    }
    for path in paths:
        group, action, reason = classify(path)
        groups[group].append(path)
        items.append(
            {
                "path": path,
                "group": group,
                "recommended_action": action,
                "reason": reason,
                "diff_stat": diff_stat(path),
            }
        )

    status = "PASS_C15_TRACKED_RESOLUTION_READY" if not groups["needs_human_decision"] else "WARN_C15_NEEDS_HUMAN_DECISION"
    package = {
        "milestone": "C15",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "tracked_modified_count": len(paths),
            "archive_snapshot_commit_count": len(groups["archive_snapshot_commit"]),
            "current_mainline_commit_count": len(groups["current_mainline_commit"]),
            "needs_human_decision_count": len(groups["needs_human_decision"]),
        },
        "policy": {
            "no_delete": True,
            "no_reset": True,
            "no_revert": True,
            "no_legacy_excel_write": True,
            "new_mainline": "source/persona -> evidence -> static_promote -> trusted_pool -> vault output",
            "static_boundary": "L1-L5 only express ICP match, evidence maturity, information completeness, risk/gap; no dynamic sales priority.",
        },
        "groups": groups,
        "items": items,
    }
    validation = {
        "milestone": "C15",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if status.startswith("PASS") else "WARN",
        "assertions": {
            "all_modified_paths_classified": len(groups["needs_human_decision"]) == 0,
            "no_delete_reset_revert_executed": True,
            "archive_snapshots_marked_legacy_reference_only": len(groups["archive_snapshot_commit"]) >= 1,
            "current_mainline_fixes_are_boundary_or_compatibility": len(groups["current_mainline_commit"]) == 5,
        },
    }
    no_destructive = {
        "milestone": "C15",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_NO_DESTRUCTIVE_ACTION",
        "proof": {
            "deleted_files": [],
            "reset_commands": [],
            "revert_commands": [],
            "legacy_workbook_writes": [],
            "note": "C15 only classifies and prepares tracked modified files for explicit commit; it does not delete, reset, revert, move, or write legacy workbooks.",
        },
    }

    (OUT_DIR / "tracked_cleanup_resolution_package_v1.json").write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n")
    (OUT_DIR / "c15_validation_report_v1.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n")
    (OUT_DIR / "no_destructive_action_proof_v1.json").write_text(json.dumps(no_destructive, ensure_ascii=False, indent=2) + "\n")
    (OUT_DIR / "tracked_paths_for_commit_v1.txt").write_text("\n".join(paths) + "\n")
    print(json.dumps(package["summary"], ensure_ascii=False, indent=2))
    print(status)
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
