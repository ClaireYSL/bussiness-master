from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an execution batch: enrich -> promote -> run summary/review.")
    parser.add_argument("--config-file", required=True, help="Execution batch config JSON.")
    parser.add_argument("--report-only", action="store_true", help="Force report-only mode for this run.")
    parser.add_argument("--write-back", action="store_true", help="Force write-back mode for this run.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_mode(config: dict[str, object], args: argparse.Namespace) -> str:
    if args.report_only and args.write_back:
        raise ValueError("`--report-only` and `--write-back` cannot be used together.")
    if args.report_only:
        return "report_only"
    if args.write_back:
        return "write_back"
    mode = _clean(config.get("mode")) or "report_only"
    if mode not in {"report_only", "write_back"}:
        raise ValueError("mode must be `report_only` or `write_back`.")
    return mode


def _default_run_summary_path(batch_id: str) -> Path:
    base = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{batch_id}_execution_summary.json"


def _default_run_review_path(batch_id: str) -> Path:
    base = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{batch_id}_execution_review.md"


def _parse_stdout_json(stdout: str) -> dict[str, object]:
    text = stdout.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
    return {}


def _build_stage_config(
    *,
    base_config_path: Path,
    stage: dict[str, object],
    stage_kind: str,
) -> Path:
    payload = _load_json(base_config_path)
    output = payload.get("output")
    if not isinstance(output, dict):
        output = {}
    if stage_kind == "enrich":
        if _clean(stage.get("output_file")):
            output["enrich_file"] = _clean(stage.get("output_file"))
    if stage_kind == "promote":
        if _clean(stage.get("output_file")):
            output["promote_file"] = _clean(stage.get("output_file"))
    if _clean(stage.get("summary_file")):
        output["summary_file"] = _clean(stage.get("summary_file"))
    if _clean(stage.get("review_file")):
        output["review_file"] = _clean(stage.get("review_file"))
    payload["output"] = output
    if stage_kind == "promote" and _clean(stage.get("enrich_result_file")):
        payload["enrich_result_file"] = _clean(stage.get("enrich_result_file"))

    temp_dir = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{_clean(payload.get('batch_id') or base_config_path.stem)}_{stage_kind}_run_config.json"
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return temp_path


def _run_stage(command: list[str]) -> tuple[int, dict[str, object], str, str]:
    proc = subprocess.run(command, cwd=WORKSPACE, capture_output=True, text=True)
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    output = _parse_stdout_json(stdout)
    return proc.returncode, output, stdout, stderr


def _render_execution_review(payload: dict[str, object]) -> str:
    summary = payload.get("summary") or {}
    enrich = payload.get("enrich") or {}
    promote = payload.get("promote") or {}
    lines = [
        f"# {_clean(payload.get('batch_id'))} execution复盘-v1",
        "",
        "## 批次概览",
        "",
        f"- 目标：`{_clean(payload.get('goal'))}`",
        f"- 模式：`{_clean(payload.get('mode'))}`",
        f"- 状态：`{_clean(payload.get('status'))}`",
        f"- 开始：`{_clean(payload.get('started_at'))}`",
        f"- 结束：`{_clean(payload.get('finished_at'))}`",
        "",
        "## 阶段结果",
        "",
        f"- enrich：`status={_clean(enrich.get('status'))}`，`result_count={enrich.get('result_count', 0)}`，`output={_clean(enrich.get('output_file'))}`",
        f"- promote：`status={_clean(promote.get('status'))}`，`result_count={promote.get('result_count', 0)}`，`output={_clean(promote.get('output_file'))}`",
        "",
        "## 执行摘要",
        "",
        f"- promote 判定：`allow={summary.get('allow', 0)} / warn={summary.get('warn', 0)} / block={summary.get('block', 0)}`",
        f"- 写回：`enrich_enabled={summary.get('enrich_write_back_enabled')} / promote_enabled={summary.get('promote_write_back_enabled')}`",
        f"- run summary：`{_clean(payload.get('run_summary_file'))}`",
        f"- enrich summary/review：`{_clean(enrich.get('summary_file'))}` / `{_clean(enrich.get('review_file'))}`",
        f"- promote summary/review：`{_clean(promote.get('summary_file'))}` / `{_clean(promote.get('review_file'))}`",
    ]
    if _clean(payload.get("error_stage")):
        lines.extend(["", "## 失败信息", "", f"- error_stage：`{_clean(payload.get('error_stage'))}`", f"- error_message：{_clean(payload.get('error_message'))}"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    config_path = Path(args.config_file)
    config = _load_json(config_path)
    mode = _resolve_mode(config, args)
    batch_id = _clean(config.get("batch_id")) or config_path.stem
    goal = _clean(config.get("goal"))
    started_at = _now()

    enrich_cfg = config.get("enrich")
    promote_cfg = config.get("promote")
    if not isinstance(enrich_cfg, dict) or not _clean(enrich_cfg.get("config_file")):
        raise ValueError("execution batch config must provide enrich.config_file")
    if not isinstance(promote_cfg, dict) or not _clean(promote_cfg.get("config_file")):
        raise ValueError("execution batch config must provide promote.config_file")

    run_output = config.get("run_output") if isinstance(config.get("run_output"), dict) else {}
    run_summary_path = Path(_clean(run_output.get("summary_file"))) if _clean(run_output.get("summary_file")) else _default_run_summary_path(batch_id)
    run_review_path = Path(_clean(run_output.get("review_file"))) if _clean(run_output.get("review_file")) else _default_run_review_path(batch_id)
    run_summary_path.parent.mkdir(parents=True, exist_ok=True)
    run_review_path.parent.mkdir(parents=True, exist_ok=True)

    enrich_temp_cfg = _build_stage_config(
        base_config_path=Path(_clean(enrich_cfg.get("config_file"))),
        stage=enrich_cfg,
        stage_kind="enrich",
    )
    enrich_cmd = ["python3", "scripts/enrich_static_pool.py", "--config-file", str(enrich_temp_cfg)]
    if mode == "report_only":
        enrich_cmd.append("--report-only")
    if mode == "write_back":
        enrich_cmd.append("--write-back")

    enrich_code, enrich_output, enrich_stdout, enrich_stderr = _run_stage(enrich_cmd)
    enrich_status = "success" if enrich_code == 0 else "failed"
    enrich_result_file = _clean(enrich_output.get("output_file")) or _clean(enrich_cfg.get("output_file"))
    enrich_summary_file = _clean(enrich_output.get("summary_file")) or _clean(enrich_cfg.get("summary_file"))
    enrich_review_file = _clean(enrich_output.get("review_file")) or _clean(enrich_cfg.get("review_file"))

    promote_status = "skipped"
    promote_code = 0
    promote_output: dict[str, object] = {}
    promote_stdout = ""
    promote_stderr = ""
    promote_result_file = ""
    promote_summary_file = ""
    promote_review_file = ""
    error_stage = ""
    error_message = ""

    if enrich_code == 0:
        enrich_result_source = _clean(promote_cfg.get("enrich_result_source")) or "from_current_enrich"
        promote_cfg_with_override = dict(promote_cfg)
        if enrich_result_source == "from_current_enrich":
            promote_cfg_with_override["enrich_result_file"] = enrich_result_file
        promote_temp_cfg = _build_stage_config(
            base_config_path=Path(_clean(promote_cfg.get("config_file"))),
            stage=promote_cfg_with_override,
            stage_kind="promote",
        )
        promote_cmd = ["python3", "scripts/promote_static_pool.py", "--config-file", str(promote_temp_cfg)]
        if _clean(promote_cfg_with_override.get("enrich_result_file")):
            promote_cmd.extend(["--enrich-result-file", _clean(promote_cfg_with_override.get("enrich_result_file"))])
        if mode == "report_only":
            promote_cmd.append("--report-only")
        if mode == "write_back":
            promote_cmd.append("--write-back")
        promote_code, promote_output, promote_stdout, promote_stderr = _run_stage(promote_cmd)
        promote_status = "success" if promote_code == 0 else "failed"
        promote_result_file = _clean(promote_output.get("output_file")) or _clean(promote_cfg.get("output_file"))
        promote_summary_file = _clean(promote_output.get("summary_file")) or _clean(promote_cfg.get("summary_file"))
        promote_review_file = _clean(promote_output.get("review_file")) or _clean(promote_cfg.get("review_file"))
        if promote_code != 0:
            error_stage = "promote"
            error_message = _clean(promote_stderr) or _clean(promote_stdout) or "promote stage failed"
    else:
        error_stage = "enrich"
        error_message = _clean(enrich_stderr) or _clean(enrich_stdout) or "enrich stage failed"

    status = "success"
    if enrich_code != 0 or promote_code != 0:
        status = "fail"

    promote_batch_summary = promote_output.get("batch_summary") if isinstance(promote_output, dict) else {}
    if not isinstance(promote_batch_summary, dict):
        promote_batch_summary = {}

    payload = {
        "batch_id": batch_id,
        "goal": goal,
        "mode": mode,
        "status": status,
        "started_at": started_at,
        "finished_at": _now(),
        "error_stage": error_stage,
        "error_message": error_message,
        "run_summary_file": str(run_summary_path),
        "run_review_file": str(run_review_path),
        "enrich": {
            "status": enrich_status,
            "return_code": enrich_code,
            "config_file": _clean(enrich_cfg.get("config_file")),
            "output_file": enrich_result_file,
            "summary_file": enrich_summary_file,
            "review_file": enrich_review_file,
            "result_count": int((enrich_output.get("summary") or {}).get("result_count") or 0) if isinstance(enrich_output.get("summary"), dict) else 0,
            "write_back": enrich_output.get("write_back") or {},
        },
        "promote": {
            "status": promote_status,
            "return_code": promote_code,
            "config_file": _clean(promote_cfg.get("config_file")),
            "output_file": promote_result_file,
            "summary_file": promote_summary_file,
            "review_file": promote_review_file,
            "result_count": int(promote_output.get("result_count") or 0) if isinstance(promote_output, dict) else 0,
            "write_back": promote_output.get("write_back") or {},
            "batch_summary": promote_batch_summary,
        },
        "summary": {
            "allow": int(promote_batch_summary.get("allow") or 0),
            "warn": int(promote_batch_summary.get("warn") or 0),
            "block": int(promote_batch_summary.get("block") or 0),
            "enrich_write_back_enabled": bool((enrich_output.get("write_back") or {}).get("enabled")),
            "promote_write_back_enabled": bool((promote_output.get("write_back") or {}).get("enabled")),
        },
    }

    run_summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    run_review_path.write_text(_render_execution_review(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "batch_id": batch_id,
                "status": status,
                "mode": mode,
                "run_summary_file": str(run_summary_path),
                "run_review_file": str(run_review_path),
                "enrich_output_file": enrich_result_file,
                "promote_output_file": promote_result_file,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
