from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import check_workbook_integrity, resolve_static_pool_paths, workbook_write_lock, WorkbookLockError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pre-write-back gate checks for execution batches.")
    parser.add_argument("--candidate-file", required=True, help="Candidate JSON file used in report_only run.")
    parser.add_argument("--baseline-file", required=True, help="Report baseline JSON file.")
    parser.add_argument("--run-summary-file", required=True, help="Execution run summary JSON file.")
    parser.add_argument("--promote-file", required=True, help="Promote result JSON file.")
    parser.add_argument("--output-json", required=True, help="Where to write gate check JSON.")
    parser.add_argument("--output-md", required=True, help="Where to write gate checklist markdown.")
    parser.add_argument("--sample-per-track", type=int, default=1, help="Sample size per track for block reason review.")
    parser.add_argument("--main-file", help="Override main workbook path.")
    parser.add_argument("--profile-file", help="Override profile workbook path.")
    parser.add_argument("--governance-file", help="Override governance workbook path.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_signature(accounts: list[dict[str, Any]]) -> list[dict[str, str]]:
    pairs = sorted(
        [
            {
                "account_id": _clean(item.get("account_id")),
                "target_level": _clean(item.get("target_level")),
            }
            for item in accounts
            if _clean(item.get("account_id")) and _clean(item.get("target_level"))
        ],
        key=lambda item: (item["account_id"], item["target_level"]),
    )
    return pairs


def _check_signature(candidate_payload: dict[str, Any], baseline_payload: dict[str, Any]) -> dict[str, Any]:
    accounts = candidate_payload.get("accounts")
    if not isinstance(accounts, list):
        return {
            "ok": False,
            "message": "candidate file missing accounts list",
            "candidate_signature_count": 0,
            "baseline_signature_count": 0,
        }
    candidate_sig = _candidate_signature(accounts)
    baseline_sig = baseline_payload.get("candidate_signature")
    if not isinstance(baseline_sig, list):
        baseline_sig = []
    return {
        "ok": candidate_sig == baseline_sig,
        "message": "candidate signature matched baseline" if candidate_sig == baseline_sig else "candidate signature mismatch",
        "candidate_signature_count": len(candidate_sig),
        "baseline_signature_count": len(baseline_sig),
    }


def _check_run_consistency(run_summary: dict[str, Any], promote_payload: dict[str, Any]) -> dict[str, Any]:
    run_status_ok = _clean(run_summary.get("status")) == "success"
    run_mode_ok = _clean(run_summary.get("mode")) == "report_only"
    enrich_count = int((run_summary.get("enrich") or {}).get("result_count") or 0)
    promote_count = int((run_summary.get("promote") or {}).get("result_count") or 0)
    promote_results = promote_payload.get("results")
    promote_results_count = len(promote_results) if isinstance(promote_results, list) else 0
    count_ok = enrich_count == promote_count == promote_results_count
    return {
        "ok": run_status_ok and run_mode_ok and count_ok,
        "message": "run summary and promote result counts are consistent"
        if run_status_ok and run_mode_ok and count_ok
        else "run summary and promote result counts are inconsistent",
        "run_status": _clean(run_summary.get("status")),
        "run_mode": _clean(run_summary.get("mode")),
        "enrich_result_count": enrich_count,
        "promote_result_count": promote_count,
        "promote_results_count": promote_results_count,
    }


def _check_integrity(main_file: Path, profile_file: Path, governance_file: Path) -> dict[str, Any]:
    report = check_workbook_integrity([main_file, profile_file, governance_file], deep_scan=True)
    return {
        "ok": bool(report.get("ok")),
        "message": "workbook integrity ok" if report.get("ok") else "workbook integrity failed",
        "report": report,
    }


def _check_serial_writeback() -> dict[str, Any]:
    try:
        with workbook_write_lock(timeout_seconds=0.0) as lock_meta:
            return {
                "ok": bool(lock_meta.get("acquired")),
                "message": "write-back lock is available",
                "lock_meta": lock_meta,
            }
    except WorkbookLockError as exc:
        return {
            "ok": False,
            "message": str(exc),
            "lock_meta": {},
        }


def _extract_issue_messages(gate: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for issue in gate.get("blocking_issues") or []:
        msg = _clean(issue.get("message"))
        code = _clean(issue.get("code"))
        if msg and code:
            messages.append(f"{code}: {msg}")
        elif msg:
            messages.append(msg)
        elif code:
            messages.append(code)
    return messages


def _check_decision_samples(
    candidate_payload: dict[str, Any],
    promote_payload: dict[str, Any],
    *,
    sample_per_track: int,
) -> dict[str, Any]:
    accounts = candidate_payload.get("accounts")
    promote_results = promote_payload.get("results")
    if not isinstance(accounts, list) or not isinstance(promote_results, list):
        return {
            "ok": False,
            "message": "candidate/promote payload is incomplete",
            "tracks_covered": 0,
            "samples": [],
        }
    result_by_id = {_clean(item.get("account_id")): item for item in promote_results if _clean(item.get("account_id"))}
    track_map: dict[str, list[dict[str, Any]]] = {}
    for item in accounts:
        account_id = _clean(item.get("account_id"))
        track = _clean(item.get("track"))
        if account_id and track:
            track_map.setdefault(track, []).append(item)

    samples: list[dict[str, Any]] = []
    valid_tracks = 0
    for track, items in sorted(track_map.items()):
        picked = sorted(items, key=lambda row: _clean(row.get("account_id")))[: max(1, sample_per_track)]
        track_ok = True
        for cand in picked:
            account_id = _clean(cand.get("account_id"))
            result = result_by_id.get(account_id) or {}
            gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
            decision = _clean(gate.get("decision"))
            blocking_issues = _extract_issue_messages(gate)
            sample_ok = decision in {"allow", "warn", "block"} and (decision != "block" or bool(blocking_issues))
            if not sample_ok:
                track_ok = False
            samples.append(
                {
                    "track": track,
                    "account_id": account_id,
                    "decision": decision,
                    "ok": sample_ok,
                    "blocking_issues": blocking_issues,
                    "summary": _clean(gate.get("summary")),
                }
            )
        if track_ok and picked:
            valid_tracks += 1

    required_tracks = min(3, len(track_map))
    ok = valid_tracks >= required_tracks
    return {
        "ok": ok,
        "message": f"decision sample review covered {valid_tracks}/{required_tracks} required tracks"
        if ok
        else f"decision sample review covered {valid_tracks}/{required_tracks} required tracks",
        "tracks_covered": valid_tracks,
        "required_tracks": required_tracks,
        "samples": samples,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    gates = payload.get("gates") or {}
    lines = [
        "# 写回前闸门检查清单-v1",
        "",
        "## 总览",
        "",
        f"- 检查时间：`{_clean(payload.get('checked_at'))}`",
        f"- 批次：`{_clean(payload.get('batch_id'))}`",
        f"- 总结论：`{'PASS' if payload.get('ok') else 'FAIL'}`",
        "",
        "## 闸门结果",
        "",
    ]
    for key in ["signature_match", "run_consistency", "workbook_integrity", "decision_sample_review", "serial_execution_lock"]:
        item = gates.get(key) or {}
        lines.append(f"- {key}：`{'PASS' if item.get('ok') else 'FAIL'}`，{_clean(item.get('message'))}")
    samples = (gates.get("block_sample_review") or {}).get("samples") or []
    if samples:
        lines.extend(["", "## 决策抽样", ""])
        for sample in samples:
            issues = sample.get("blocking_issues") or []
            issue_text = " | ".join(issues) if issues else "无"
            lines.append(
                f"- `{_clean(sample.get('track'))}` / `{_clean(sample.get('account_id'))}` / decision=`{_clean(sample.get('decision'))}` / ok=`{sample.get('ok')}` / issues={issue_text}"
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    candidate_payload = _load_json(Path(args.candidate_file))
    baseline_payload = _load_json(Path(args.baseline_file))
    run_summary = _load_json(Path(args.run_summary_file))
    promote_payload = _load_json(Path(args.promote_file))

    pool = resolve_static_pool_paths()
    main_file = Path(args.main_file) if args.main_file else pool["main"]
    profile_file = Path(args.profile_file) if args.profile_file else pool["profile"]
    governance_file = Path(args.governance_file) if args.governance_file else pool["governance"]

    gates = {
        "signature_match": _check_signature(candidate_payload, baseline_payload),
        "run_consistency": _check_run_consistency(run_summary, promote_payload),
        "workbook_integrity": _check_integrity(main_file, profile_file, governance_file),
        "decision_sample_review": _check_decision_samples(candidate_payload, promote_payload, sample_per_track=max(1, args.sample_per_track)),
        "serial_execution_lock": _check_serial_writeback(),
    }
    overall_ok = all(bool(item.get("ok")) for item in gates.values())

    payload = {
        "checked_at": _now(),
        "batch_id": _clean(candidate_payload.get("batch_id")) or _clean(run_summary.get("batch_id")),
        "ok": overall_ok,
        "inputs": {
            "candidate_file": args.candidate_file,
            "baseline_file": args.baseline_file,
            "run_summary_file": args.run_summary_file,
            "promote_file": args.promote_file,
            "main_file": str(main_file),
            "profile_file": str(profile_file),
            "governance_file": str(governance_file),
        },
        "gates": gates,
    }

    json_path = Path(args.output_json)
    md_path = Path(args.output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(json_path),
                "output_md": str(md_path),
                "ok": overall_ok,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
