from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a handoff snapshot for another coding agent.")
    parser.add_argument("--output-json", help="Output JSON path.")
    parser.add_argument("--output-md", help="Output Markdown path.")
    parser.add_argument("--milestone-limit", type=int, default=12, help="Max number of recent milestone artifacts.")
    parser.add_argument("--changed-file-limit", type=int, default=200, help="Max number of changed files in git status.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run_git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=WORKSPACE, capture_output=True, text=True)
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def _git_info(changed_file_limit: int) -> dict[str, Any]:
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    commit = _run_git(["rev-parse", "HEAD"])
    short_commit = _run_git(["rev-parse", "--short", "HEAD"])
    status_text = _run_git(["status", "--porcelain"])
    status_lines = [line for line in status_text.splitlines() if line.strip()]
    changed_files = []
    for line in status_lines[:changed_file_limit]:
        # porcelain format: XY <path>
        changed_files.append({"status": _clean(line[:2]), "path": _clean(line[3:])})
    return {
        "branch": branch,
        "commit": commit,
        "short_commit": short_commit,
        "dirty": bool(status_lines),
        "changed_file_count": len(status_lines),
        "changed_files": changed_files,
    }


def _recent_files(base: Path, pattern: str, limit: int) -> list[dict[str, Any]]:
    files = [path for path in base.glob(pattern) if path.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    rows: list[dict[str, Any]] = []
    for path in files[:limit]:
        st = path.stat()
        rows.append(
            {
                "path": str(path.relative_to(WORKSPACE)),
                "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                "size_bytes": st.st_size,
            }
        )
    return rows


def _load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _latest_run_summary(milestone_limit: int) -> list[dict[str, Any]]:
    base = WORKSPACE / "deliveries/archive/milestones"
    if not base.exists():
        return []
    files = list(base.glob("**/*run_summary*.json"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    rows: list[dict[str, Any]] = []
    for path in files[:milestone_limit]:
        payload = _load_json(path)
        summary = payload.get("summary") if isinstance(payload, dict) else {}
        rows.append(
            {
                "path": str(path.relative_to(WORKSPACE)),
                "status": _clean(payload.get("status")) if isinstance(payload, dict) else "",
                "mode": _clean(payload.get("mode")) if isinstance(payload, dict) else "",
                "allow": summary.get("allow") if isinstance(summary, dict) else None,
                "warn": summary.get("warn") if isinstance(summary, dict) else None,
                "block": summary.get("block") if isinstance(summary, dict) else None,
                "workbook_lock_acquired": summary.get("workbook_lock_acquired") if isinstance(summary, dict) else None,
            }
        )
    return rows


def _key_configs() -> list[dict[str, Any]]:
    roots = [
        WORKSPACE / "configs/execution_batches",
        WORKSPACE / "configs/enrich_batches",
        WORKSPACE / "configs/promote_batches",
    ]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend([p for p in root.glob("*.json") if p.is_file()])
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    rows: list[dict[str, Any]] = []
    for path in files[:36]:
        payload = _load_json(path)
        rows.append(
            {
                "path": str(path.relative_to(WORKSPACE)),
                "batch_id": _clean(payload.get("batch_id")) if isinstance(payload, dict) else "",
                "milestone_id": _clean(payload.get("milestone_id")) if isinstance(payload, dict) else "",
                "goal": _clean(payload.get("goal")) if isinstance(payload, dict) else "",
            }
        )
    return rows


def _repairs_snapshot() -> dict[str, Any]:
    repairs_dir = WORKSPACE / "deliveries/archive/repairs"
    if not repairs_dir.exists():
        return {"files": [], "main_id_repair": {}, "integrity_report": {}}
    files = _recent_files(repairs_dir, "*.json", limit=20)
    main_id_payload = _load_json(repairs_dir / "main_id_repair_v1.json")
    integrity_payload = _load_json(repairs_dir / "workbook_integrity_report_v1.json")
    return {
        "files": files,
        "main_id_repair": (main_id_payload or {}).get("summary", {}) if isinstance(main_id_payload, dict) else {},
        "integrity_report": (integrity_payload or {}).get("report", {}) if isinstance(integrity_payload, dict) else {},
    }


def _default_outputs(now: datetime) -> tuple[Path, Path]:
    base = WORKSPACE / "deliveries/archive/handoffs"
    base.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    return base / f"handoff_snapshot_{stamp}.json", base / f"handoff_snapshot_{stamp}.md"


def _render_markdown(payload: dict[str, Any]) -> str:
    git_info = payload.get("git") or {}
    repairs = payload.get("repairs") or {}
    run_summaries = payload.get("recent_run_summaries") or []
    key_configs = payload.get("key_configs") or []
    lines = [
        "# 交接快照",
        "",
        f"- 生成时间(UTC): `{_clean(payload.get('generated_at'))}`",
        f"- 分支: `{_clean(git_info.get('branch'))}`",
        f"- 提交: `{_clean(git_info.get('short_commit'))}`",
        f"- 工作区是否干净: `{'no' if git_info.get('dirty') else 'yes'}`",
        "",
        "## 修复基线",
        "",
        f"- main_id_repair coverage: `{(repairs.get('main_id_repair') or {}).get('coverage_ratio')}`",
        f"- main_id_repair generated_rows: `{(repairs.get('main_id_repair') or {}).get('generated_rows')}`",
        f"- workbook_integrity ok: `{(repairs.get('integrity_report') or {}).get('ok')}`",
        "",
        "## 最近执行摘要",
        "",
    ]
    for item in run_summaries[:8]:
        lines.append(
            f"- `{_clean(item.get('path'))}` | status=`{_clean(item.get('status'))}` mode=`{_clean(item.get('mode'))}` "
            f"allow/warn/block=`{item.get('allow')}/{item.get('warn')}/{item.get('block')}` "
            f"lock=`{item.get('workbook_lock_acquired')}`"
        )
    lines.extend(["", "## 关键配置(最近)", ""])
    for item in key_configs[:12]:
        lines.append(f"- `{_clean(item.get('path'))}` | milestone=`{_clean(item.get('milestone_id'))}` batch=`{_clean(item.get('batch_id'))}`")
    lines.extend(
        [
            "",
            "## 接力建议",
            "",
            "- 先执行 `git pull` 并确认分支与本快照一致。",
            "- 统一从 `configs/*` 驱动执行，避免手工拼命令。",
            "- 保持 `report_only -> write_back` 顺序，并启用 `--require-report-baseline`。",
            "- 写回前后各跑一次完整性检查。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = build_parser().parse_args()
    now = _now()
    default_json, default_md = _default_outputs(now)
    output_json = Path(args.output_json) if args.output_json else default_json
    output_md = Path(args.output_md) if args.output_md else default_md

    payload: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "workspace": str(WORKSPACE),
        "git": _git_info(args.changed_file_limit),
        "repairs": _repairs_snapshot(),
        "recent_run_summaries": _latest_run_summary(args.milestone_limit),
        "key_configs": _key_configs(),
        "recent_docs": _recent_files(WORKSPACE / "docs/03-执行与校验", "*.md", limit=20),
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(_render_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "output_json": str(output_json),
                "output_md": str(output_md),
                "branch": payload["git"].get("branch"),
                "commit": payload["git"].get("short_commit"),
                "dirty": payload["git"].get("dirty"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
