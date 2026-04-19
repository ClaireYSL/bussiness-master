from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import (
    attach_account_ids,
    evaluate_promotion_batch,
    load_main_rows,
    load_sheet_rows,
    resolve_static_pool_paths,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Select milestone execution candidates from main/profile/governance sources.")
    parser.add_argument("--config-file", required=True, help="Execution registry config JSON.")
    parser.add_argument("--output-file", required=True, help="Output candidate JSON file.")
    parser.add_argument("--strict", action="store_true", help="Fail when candidate mix constraints are not met.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _candidate_type(main_row: dict[str, object]) -> str:
    review_status = _clean(main_row.get("review_status")).lower()
    if review_status in {"observation", "queued", "pending_review", "boundary_review"}:
        return "observation"
    return "formal_candidate"


def _collect_queue_types(queue_rows: list[dict[str, object]], account_id: str) -> list[str]:
    values = sorted(
        {
            _clean(row.get("queue_type"))
            for row in queue_rows
            if _clean(row.get("account_id")) == account_id and _clean(row.get("status")) in {"", "open", "in_progress"}
        }
    )
    return [value for value in values if value]


def _build_selection_reason(decision: str, from_level: str, target_level: str, track: str) -> str:
    return f"{track} {from_level}->{target_level} 候选；latest_promote_decision={decision}"


def _pick_group(
    rows: list[dict[str, object]],
    *,
    required_count: int,
    prefer_allow: bool = True,
) -> list[dict[str, object]]:
    allow_rows = [row for row in rows if _clean(row.get("latest_promote_decision")) == "allow"]
    conservative_rows = [row for row in rows if _clean(row.get("latest_promote_decision")) in {"warn", "block"}]
    picked: list[dict[str, object]] = []
    if prefer_allow:
        for row in allow_rows:
            if len(picked) >= required_count:
                break
            picked.append(row)
        for row in conservative_rows:
            if len(picked) >= required_count:
                break
            if row not in picked:
                picked.append(row)
    else:
        for row in rows:
            if len(picked) >= required_count:
                break
            picked.append(row)
    return picked


def _default_source_paths() -> dict[str, str]:
    pool = resolve_static_pool_paths()
    return {
        "main_file": str(pool["main"]),
        "main_sheet": "accounts_main",
        "profile_file": str(pool["profile"]),
        "profile_sheet": "account_profiles",
        "governance_file": str(pool["governance"]),
        "queue_sheet": "review_queue",
        "evidence_sheet": "evidence_log",
    }


def main() -> int:
    args = build_parser().parse_args()
    config = json.loads(Path(args.config_file).read_text(encoding="utf-8"))
    source_paths = _default_source_paths()
    source_paths.update(config.get("source_paths") or {})
    main_rows = load_main_rows(Path(source_paths["main_file"]), source_paths["main_sheet"])
    _headers, profile_rows = load_sheet_rows(Path(source_paths["profile_file"]), source_paths["profile_sheet"])
    _headers, queue_rows = load_sheet_rows(Path(source_paths["governance_file"]), source_paths["queue_sheet"])
    _headers, evidence_rows = load_sheet_rows(Path(source_paths["governance_file"]), source_paths["evidence_sheet"])
    main_rows = attach_account_ids(main_rows, profile_rows)

    track_mix = config.get("track_mix") or {}
    promotion_mix = config.get("promotion_mix") or {}
    tracks = list(track_mix.get("tracks") or ["零售消费", "跨境电商", "先进制造"])
    route_targets = list(promotion_mix.get("routes") or [])
    if not route_targets:
        route_targets = [
            {"from_level": "L4", "target_level": "L3", "per_track": 6},
            {"from_level": "L3", "target_level": "L2", "per_track": 2},
        ]

    by_account = {(_clean(row.get("account_id"))): row for row in main_rows if _clean(row.get("account_id"))}
    draft_candidates: list[dict[str, object]] = []
    shortages: list[dict[str, object]] = []
    selection_detail: list[dict[str, object]] = []

    for track in tracks:
        for route in route_targets:
            from_level = _clean(route.get("from_level"))
            target_level = _clean(route.get("target_level"))
            per_track = int(route.get("per_track") or 0)
            if not from_level or not target_level or per_track <= 0:
                continue
            eval_payload = evaluate_promotion_batch(
                main_rows,
                profile_rows,
                evidence_rows,
                queue_rows,
                from_level=from_level,
                target_level=target_level,
                track=track,
                limit=9999,
            )
            grouped_rows: list[dict[str, object]] = []
            for item in eval_payload.get("results") or []:
                account_id = _clean(item.get("account_id"))
                if not account_id:
                    continue
                main_row = by_account.get(account_id) or {}
                gate = item.get("promotion_gate") or {}
                required_queue_types = _collect_queue_types(queue_rows, account_id)
                suggested_queue_type = _clean(gate.get("suggested_queue_type"))
                if suggested_queue_type and suggested_queue_type not in required_queue_types:
                    required_queue_types.append(suggested_queue_type)
                grouped_rows.append(
                    {
                        "account_id": account_id,
                        "track": track,
                        "current_level": from_level,
                        "target_level": target_level,
                        "candidate_type": _candidate_type(main_row),
                        "latest_promote_decision": _clean(gate.get("decision")),
                        "required_queue_types": sorted(required_queue_types),
                        "selection_reason": _build_selection_reason(_clean(gate.get("decision")), from_level, target_level, track),
                    }
                )
            picked = _pick_group(grouped_rows, required_count=per_track, prefer_allow=True)
            selection_detail.append(
                {
                    "track": track,
                    "from_level": from_level,
                    "target_level": target_level,
                    "required": per_track,
                    "available": len(grouped_rows),
                    "picked": len(picked),
                    "decision_counts": dict(Counter(_clean(item.get("latest_promote_decision")) for item in grouped_rows)),
                }
            )
            draft_candidates.extend(picked)
            if len(picked) < per_track:
                shortages.append(
                    {
                        "track": track,
                        "from_level": from_level,
                        "target_level": target_level,
                        "required": per_track,
                        "available": len(grouped_rows),
                        "picked": len(picked),
                    }
                )

    unique: dict[tuple[str, str], dict[str, object]] = {}
    for item in draft_candidates:
        key = (_clean(item.get("account_id")), _clean(item.get("target_level")))
        if key[0] and key[1]:
            unique[key] = item
    final_candidates = sorted(unique.values(), key=lambda item: (_clean(item.get("track")), _clean(item.get("target_level")), _clean(item.get("account_id"))))

    payload: dict[str, Any] = {
        "batch_id": _clean(config.get("batch_id")) or "milestone5_execution_batch_v1",
        "generated_at": _now(),
        "goal": _clean(config.get("goal")),
        "candidate_policy": {
            "tracks": tracks,
            "routes": route_targets,
            "strict_mode": bool(args.strict),
        },
        "selection_summary": {
            "required_total": sum(int(item.get("per_track") or 0) for item in route_targets) * len(tracks),
            "picked_total": len(final_candidates),
            "shortage_count": len(shortages),
            "shortages": shortages,
            "detail": selection_detail,
        },
        "accounts": final_candidates,
    }
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_file": str(output_path), "picked_total": len(final_candidates), "shortage_count": len(shortages)}, ensure_ascii=False, indent=2))
    if args.strict and shortages:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
