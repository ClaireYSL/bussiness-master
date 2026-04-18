from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import build_promote_summary_payload, render_promote_review_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an execution batch: enrich -> promote -> run summary/review.")
    parser.add_argument("--config-file", required=True, help="Execution batch config JSON.")
    parser.add_argument("--report-only", action="store_true", help="Force report-only mode for this run.")
    parser.add_argument("--write-back", action="store_true", help="Force write-back mode for this run.")
    parser.add_argument(
        "--phase",
        choices=["report_only", "write_back", "both"],
        help="Execution phase. `both` means report_only first, then write_back.",
    )
    parser.add_argument("--candidate-file", help="Optional candidate list JSON.")
    parser.add_argument(
        "--require-report-baseline",
        action="store_true",
        help="Require report baseline and candidate signature match before write_back.",
    )
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
    if args.phase and (args.report_only or args.write_back):
        raise ValueError("`--phase` cannot be used with legacy `--report-only/--write-back`.")
    if args.report_only:
        return "report_only"
    if args.write_back:
        return "write_back"
    if args.phase:
        return args.phase
    mode_policy = config.get("mode_policy") if isinstance(config.get("mode_policy"), dict) else {}
    policy_phase = _clean(mode_policy.get("default_phase"))
    if policy_phase in {"report_only", "write_back", "both"}:
        return policy_phase
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


def _default_report_baseline_path(batch_id: str) -> Path:
    base = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{batch_id}_report_baseline.json"


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


def _with_phase_suffix(path: str, phase: str, *, enabled: bool) -> str:
    if not path or not enabled:
        return path
    src = Path(path)
    return str(src.with_name(f"{src.stem}_{phase}{src.suffix}"))


def _candidate_signature(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    pairs = sorted(
        [
            {
                "account_id": _clean(item.get("account_id")),
                "target_level": _clean(item.get("target_level")),
            }
            for item in candidates
            if _clean(item.get("account_id")) and _clean(item.get("target_level"))
        ],
        key=lambda item: (item["account_id"], item["target_level"]),
    )
    return pairs


def _load_candidates(config: dict[str, object], cli_candidate_file: str | None) -> list[dict[str, str]]:
    candidate_file = cli_candidate_file or _clean(config.get("candidate_file"))
    payload: dict[str, Any] = {}
    if candidate_file:
        payload = _load_json(Path(candidate_file))
    else:
        payload = config
    raw_accounts = payload.get("accounts")
    if not isinstance(raw_accounts, list):
        raise ValueError("candidate file must provide `accounts` list.")
    candidates: list[dict[str, str]] = []
    for item in raw_accounts:
        if isinstance(item, str):
            account_id = _clean(item)
            if account_id:
                candidates.append({"account_id": account_id, "target_level": "", "from_level": "", "track": ""})
            continue
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        if not account_id:
            continue
        target_level = _clean(item.get("target_level"))
        if not target_level:
            raise ValueError(f"candidate `{account_id}` missing target_level.")
        from_level = _clean(item.get("current_level") or item.get("from_level"))
        if not from_level:
            raise ValueError(f"candidate `{account_id}` missing current_level/from_level.")
        candidates.append(
            {
                "account_id": account_id,
                "target_level": target_level,
                "from_level": from_level,
                "track": _clean(item.get("track")),
            }
        )
    if not candidates:
        raise ValueError("no valid candidates found for execution batch.")
    return candidates


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
    if stage.get("account_ids"):
        payload["account_ids"] = list(stage.get("account_ids") or [])
    if _clean(stage.get("from_level")):
        payload["from_level"] = _clean(stage.get("from_level"))
    if _clean(stage.get("target_level")):
        payload["target_level"] = _clean(stage.get("target_level"))
    if _clean(stage.get("promote_target_level")):
        payload["promote_target_level"] = _clean(stage.get("promote_target_level"))
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


def _run_enrich_stage(
    enrich_cfg: dict[str, object],
    *,
    account_ids: list[str],
    mode: str,
    phase_label: str,
    phase_suffix_enabled: bool,
) -> tuple[int, dict[str, object], str, str]:
    stage = dict(enrich_cfg)
    stage["account_ids"] = account_ids
    stage["output_file"] = _with_phase_suffix(_clean(stage.get("output_file")), phase_label, enabled=phase_suffix_enabled)
    stage["summary_file"] = _with_phase_suffix(_clean(stage.get("summary_file")), phase_label, enabled=phase_suffix_enabled)
    stage["review_file"] = _with_phase_suffix(_clean(stage.get("review_file")), phase_label, enabled=phase_suffix_enabled)
    enrich_temp_cfg = _build_stage_config(
        base_config_path=Path(_clean(enrich_cfg.get("config_file"))),
        stage=stage,
        stage_kind="enrich",
    )
    cmd = ["python3", "scripts/enrich_static_pool.py", "--config-file", str(enrich_temp_cfg)]
    if mode == "report_only":
        cmd.append("--report-only")
    if mode == "write_back":
        cmd.append("--write-back")
    return _run_stage(cmd)


def _merge_promote_payloads(batch_id: str, goal: str, payloads: list[dict[str, object]], *, enrich_result_file: str, account_ids: list[str]) -> dict[str, object]:
    results: list[dict[str, object]] = []
    summary = {"allow": 0, "warn": 0, "block": 0}
    merged_writeback: dict[str, object] = {
        "enabled": False,
        "promoted": 0,
        "skipped": 0,
        "profile_updates": 0,
        "main_updates": 0,
        "main_shared_updates": 0,
        "coverage_updates": 0,
        "evidence_created": 0,
        "promotion_review_resolved": 0,
        "samples": [],
    }
    for payload in payloads:
        results.extend(payload.get("results") or [])
        ps = payload.get("batch_summary") if isinstance(payload.get("batch_summary"), dict) else {}
        summary["allow"] += int(ps.get("allow") or 0)
        summary["warn"] += int(ps.get("warn") or 0)
        summary["block"] += int(ps.get("block") or 0)
        wb = payload.get("write_back") if isinstance(payload.get("write_back"), dict) else {}
        if wb:
            merged_writeback["enabled"] = bool(merged_writeback.get("enabled")) or bool(wb.get("enabled"))
            for key in [
                "promoted",
                "skipped",
                "profile_updates",
                "main_updates",
                "main_shared_updates",
                "coverage_updates",
                "evidence_created",
                "promotion_review_resolved",
            ]:
                merged_writeback[key] = int(merged_writeback.get(key) or 0) + int(wb.get(key) or 0)
            merged_writeback["samples"] = list(merged_writeback.get("samples") or []) + list(wb.get("samples") or [])
    return {
        "batch_id": batch_id,
        "goal": goal,
        "selection": {"account_ids": account_ids, "limit": len(account_ids)},
        "enrich_result_file": enrich_result_file,
        "result_count": len(results),
        "batch_summary": summary,
        "results": results,
        "write_back": merged_writeback,
    }


def _run_promote_stage(
    *,
    batch_id: str,
    goal: str,
    promote_cfg: dict[str, object],
    candidates: list[dict[str, str]],
    mode: str,
    phase_label: str,
    phase_suffix_enabled: bool,
    enrich_result_file: str,
) -> tuple[int, dict[str, object], str, str]:
    grouped: dict[tuple[str, str], list[str]] = {}
    for item in candidates:
        target = _clean(item.get("target_level"))
        from_level = _clean(item.get("from_level"))
        if not target:
            continue
        grouped.setdefault((from_level, target), []).append(_clean(item.get("account_id")))
    if not grouped:
        return 1, {}, "", "no promote candidates with target_level"

    payloads: list[dict[str, object]] = []
    stdouts: list[str] = []
    stderrs: list[str] = []
    all_account_ids: list[str] = []
    for idx, ((from_level, target_level), account_ids) in enumerate(sorted(grouped.items()), start=1):
        all_account_ids.extend(account_ids)
        stage = dict(promote_cfg)
        stage["account_ids"] = account_ids
        stage["from_level"] = from_level
        stage["target_level"] = target_level
        base_output_file = _clean(stage.get("output_file"))
        if base_output_file:
            # Promote is executed by route groups; each route must write a unique
            # file, otherwise later groups overwrite earlier outputs.
            stage["output_file"] = _with_phase_suffix(base_output_file, f"{phase_label}_{target_level}_{idx}", enabled=True)
        else:
            temp = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
            temp.mkdir(parents=True, exist_ok=True)
            stage["output_file"] = str(temp / f"{batch_id}_{phase_label}_{target_level}_{idx}_promote.json")
        stage["summary_file"] = ""
        stage["review_file"] = ""
        stage["enrich_result_file"] = enrich_result_file
        promote_temp_cfg = _build_stage_config(
            base_config_path=Path(_clean(promote_cfg.get("config_file"))),
            stage=stage,
            stage_kind="promote",
        )
        cmd = ["python3", "scripts/promote_static_pool.py", "--config-file", str(promote_temp_cfg)]
        if enrich_result_file:
            cmd.extend(["--enrich-result-file", enrich_result_file])
        if mode == "report_only":
            cmd.append("--report-only")
        if mode == "write_back":
            cmd.append("--write-back")
        code, output, stdout, stderr = _run_stage(cmd)
        stdouts.append(stdout)
        stderrs.append(stderr)
        if code != 0:
            return code, output, "\n".join(stdouts), "\n".join(stderrs)
        result_file = _clean(output.get("output_file")) or _clean(stage.get("output_file"))
        payloads.append(_load_json(Path(result_file)))

    merged = _merge_promote_payloads(
        batch_id=batch_id,
        goal=goal,
        payloads=payloads,
        enrich_result_file=enrich_result_file,
        account_ids=all_account_ids,
    )
    promote_output_file = _with_phase_suffix(_clean(promote_cfg.get("output_file")), phase_label, enabled=phase_suffix_enabled)
    if not promote_output_file:
        temp = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
        temp.mkdir(parents=True, exist_ok=True)
        promote_output_file = str(temp / f"{batch_id}_{phase_label}_promote_merged.json")
    Path(promote_output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(promote_output_file).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    promote_summary_file = _with_phase_suffix(_clean(promote_cfg.get("summary_file")), phase_label, enabled=phase_suffix_enabled)
    promote_review_file = _with_phase_suffix(_clean(promote_cfg.get("review_file")), phase_label, enabled=phase_suffix_enabled)
    if promote_summary_file:
        summary_payload = build_promote_summary_payload(
            {},
            merged,
            config_path=_clean(promote_cfg.get("config_file")),
            promote_result_path=promote_output_file,
        )
        Path(promote_summary_file).parent.mkdir(parents=True, exist_ok=True)
        Path(promote_summary_file).write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if promote_review_file:
            Path(promote_review_file).parent.mkdir(parents=True, exist_ok=True)
            Path(promote_review_file).write_text(render_promote_review_markdown(summary_payload), encoding="utf-8")

    stdout_payload = {
        "output_file": promote_output_file,
        "result_count": len(merged.get("results") or []),
        "batch_summary": merged.get("batch_summary") or {},
        "summary_file": promote_summary_file,
        "review_file": promote_review_file,
        "write_back": merged.get("write_back") or {},
    }
    return 0, stdout_payload, json.dumps(stdout_payload, ensure_ascii=False, indent=2), "\n".join(stderrs)


def _execute_single_phase(
    *,
    batch_id: str,
    goal: str,
    config: dict[str, object],
    candidates: list[dict[str, str]],
    mode: str,
    phase_label: str,
    phase_suffix_enabled: bool,
) -> dict[str, object]:
    started_at = _now()
    enrich_cfg = config.get("enrich")
    promote_cfg = config.get("promote")
    if not isinstance(enrich_cfg, dict) or not _clean(enrich_cfg.get("config_file")):
        raise ValueError("execution batch config must provide enrich.config_file")
    if not isinstance(promote_cfg, dict) or not _clean(promote_cfg.get("config_file")):
        raise ValueError("execution batch config must provide promote.config_file")

    account_ids = sorted({_clean(item.get("account_id")) for item in candidates if _clean(item.get("account_id"))})
    enrich_code, enrich_output, enrich_stdout, enrich_stderr = _run_enrich_stage(
        enrich_cfg,
        account_ids=account_ids,
        mode=mode,
        phase_label=phase_label,
        phase_suffix_enabled=phase_suffix_enabled,
    )
    enrich_status = "success" if enrich_code == 0 else "failed"
    enrich_result_file = _clean(enrich_output.get("output_file")) or _with_phase_suffix(_clean(enrich_cfg.get("output_file")), phase_label, enabled=phase_suffix_enabled)
    enrich_summary_file = _clean(enrich_output.get("summary_file")) or _with_phase_suffix(_clean(enrich_cfg.get("summary_file")), phase_label, enabled=phase_suffix_enabled)
    enrich_review_file = _clean(enrich_output.get("review_file")) or _with_phase_suffix(_clean(enrich_cfg.get("review_file")), phase_label, enabled=phase_suffix_enabled)

    promote_status = "skipped"
    promote_code = 0
    promote_output: dict[str, object] = {}
    promote_stdout = ""
    promote_stderr = ""
    error_stage = ""
    error_message = ""
    if enrich_code == 0:
        promote_candidates = [item for item in candidates if _clean(item.get("target_level"))]
        promote_code, promote_output, promote_stdout, promote_stderr = _run_promote_stage(
            batch_id=batch_id,
            goal=goal,
            promote_cfg=promote_cfg,
            candidates=promote_candidates,
            mode=mode,
            phase_label=phase_label,
            phase_suffix_enabled=phase_suffix_enabled,
            enrich_result_file=enrich_result_file,
        )
        promote_status = "success" if promote_code == 0 else "failed"
        if promote_code != 0:
            error_stage = "promote"
            error_message = _clean(promote_stderr) or _clean(promote_stdout) or "promote stage failed"
    else:
        error_stage = "enrich"
        error_message = _clean(enrich_stderr) or _clean(enrich_stdout) or "enrich stage failed"

    promote_batch_summary = promote_output.get("batch_summary") if isinstance(promote_output, dict) else {}
    if not isinstance(promote_batch_summary, dict):
        promote_batch_summary = {}
    status = "success" if enrich_code == 0 and promote_code == 0 else "fail"
    return {
        "batch_id": batch_id,
        "goal": goal,
        "mode": mode,
        "phase": phase_label,
        "status": status,
        "started_at": started_at,
        "finished_at": _now(),
        "error_stage": error_stage,
        "error_message": error_message,
        "candidate_signature": _candidate_signature(candidates),
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
            "output_file": _clean(promote_output.get("output_file")),
            "summary_file": _clean(promote_output.get("summary_file")),
            "review_file": _clean(promote_output.get("review_file")),
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


def _validate_baseline(required: bool, baseline_path: Path, candidates: list[dict[str, str]]) -> None:
    if not required:
        return
    if not baseline_path.exists():
        raise ValueError(f"report baseline missing: {baseline_path}")
    baseline = _load_json(baseline_path)
    baseline_sig = baseline.get("candidate_signature") or []
    if baseline_sig != _candidate_signature(candidates):
        raise ValueError("candidate signature mismatch between report baseline and write_back request.")


def main() -> int:
    args = build_parser().parse_args()
    config_path = Path(args.config_file)
    config = _load_json(config_path)
    mode = _resolve_mode(config, args)
    batch_id = _clean(config.get("batch_id")) or config_path.stem
    goal = _clean(config.get("goal"))
    candidates = _load_candidates(config, args.candidate_file)

    run_output = config.get("run_output") if isinstance(config.get("run_output"), dict) else {}
    run_summary_raw = _clean(run_output.get("summary_file"))
    run_review_raw = _clean(run_output.get("review_file"))
    run_summary_path = Path(run_summary_raw) if run_summary_raw else _default_run_summary_path(batch_id)
    run_review_path = Path(run_review_raw) if run_review_raw else _default_run_review_path(batch_id)
    report_baseline_raw = _clean(run_output.get("report_baseline_file"))
    baseline_path = Path(report_baseline_raw) if report_baseline_raw else _default_report_baseline_path(batch_id)
    require_baseline = bool(args.require_report_baseline or bool((config.get("mode_policy") or {}).get("require_report_baseline")))
    run_summary_path.parent.mkdir(parents=True, exist_ok=True)
    run_review_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)

    if mode == "report_only":
        payload = _execute_single_phase(
            batch_id=batch_id,
            goal=goal,
            config=config,
            candidates=candidates,
            mode="report_only",
            phase_label="report_only",
            phase_suffix_enabled=False,
        )
        payload["run_summary_file"] = str(run_summary_path)
        payload["run_review_file"] = str(run_review_path)
        run_summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        run_review_path.write_text(_render_execution_review(payload), encoding="utf-8")
        baseline_path.write_text(
            json.dumps(
                {
                    "batch_id": batch_id,
                    "goal": goal,
                    "phase": "report_only",
                    "generated_at": _now(),
                    "candidate_signature": payload.get("candidate_signature") or [],
                    "report_run_summary_file": str(run_summary_path),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "batch_id": batch_id,
                    "status": payload.get("status"),
                    "mode": mode,
                    "run_summary_file": str(run_summary_path),
                    "run_review_file": str(run_review_path),
                    "report_baseline_file": str(baseline_path),
                    "enrich_output_file": payload.get("enrich", {}).get("output_file"),
                    "promote_output_file": payload.get("promote", {}).get("output_file"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if payload.get("status") == "success" else 1

    if mode == "write_back":
        _validate_baseline(require_baseline, baseline_path, candidates)
        payload = _execute_single_phase(
            batch_id=batch_id,
            goal=goal,
            config=config,
            candidates=candidates,
            mode="write_back",
            phase_label="write_back",
            phase_suffix_enabled=False,
        )
        payload["run_summary_file"] = str(run_summary_path)
        payload["run_review_file"] = str(run_review_path)
        run_summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        run_review_path.write_text(_render_execution_review(payload), encoding="utf-8")
        print(
            json.dumps(
                {
                    "batch_id": batch_id,
                    "status": payload.get("status"),
                    "mode": mode,
                    "run_summary_file": str(run_summary_path),
                    "run_review_file": str(run_review_path),
                    "report_baseline_file": str(baseline_path),
                    "enrich_output_file": payload.get("enrich", {}).get("output_file"),
                    "promote_output_file": payload.get("promote", {}).get("output_file"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if payload.get("status") == "success" else 1

    report_payload = _execute_single_phase(
        batch_id=batch_id,
        goal=goal,
        config=config,
        candidates=candidates,
        mode="report_only",
        phase_label="report_only",
        phase_suffix_enabled=True,
    )
    report_summary_path = Path(_with_phase_suffix(str(run_summary_path), "report_only", enabled=True))
    report_review_path = Path(_with_phase_suffix(str(run_review_path), "report_only", enabled=True))
    report_summary_path.parent.mkdir(parents=True, exist_ok=True)
    report_review_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload["run_summary_file"] = str(report_summary_path)
    report_payload["run_review_file"] = str(report_review_path)
    report_summary_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report_review_path.write_text(_render_execution_review(report_payload), encoding="utf-8")
    baseline_path.write_text(
        json.dumps(
            {
                "batch_id": batch_id,
                "goal": goal,
                "phase": "report_only",
                "generated_at": _now(),
                "candidate_signature": report_payload.get("candidate_signature") or [],
                "report_run_summary_file": str(report_summary_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _validate_baseline(True, baseline_path, candidates)
    write_payload = _execute_single_phase(
        batch_id=batch_id,
        goal=goal,
        config=config,
        candidates=candidates,
        mode="write_back",
        phase_label="write_back",
        phase_suffix_enabled=False,
    )
    write_payload["run_summary_file"] = str(run_summary_path)
    write_payload["run_review_file"] = str(run_review_path)
    write_payload["report_baseline_file"] = str(baseline_path)
    write_payload["report_phase_summary_file"] = str(report_summary_path)
    run_summary_path.write_text(json.dumps(write_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    run_review_path.write_text(_render_execution_review(write_payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "batch_id": batch_id,
                "status": write_payload.get("status"),
                "mode": mode,
                "run_summary_file": str(run_summary_path),
                "run_review_file": str(run_review_path),
                "report_baseline_file": str(baseline_path),
                "report_phase_summary_file": str(report_summary_path),
                "enrich_output_file": write_payload.get("enrich", {}).get("output_file"),
                "promote_output_file": write_payload.get("promote", {}).get("output_file"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if write_payload.get("status") == "success" and report_payload.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
