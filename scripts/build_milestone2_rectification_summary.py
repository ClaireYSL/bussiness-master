from __future__ import annotations

import argparse
import json
from pathlib import Path


WRITEBACK_TARGETS = [
    "潜客档案库.xlsx",
    "内部运营-静态潜客池-共享版.xlsx",
    "治理与证据.xlsx",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build milestone 2 cross-track rectification summary package.")
    parser.add_argument("--config-file", required=True, help="Milestone config JSON.")
    parser.add_argument("--enrich-result-file", required=True, help="Current enrich result JSON.")
    parser.add_argument("--promote-result-file", required=True, help="Current promote result JSON.")
    parser.add_argument("--output-file", required=True, help="Summary output JSON.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_enrich_lookup(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {_clean(item.get("account_id")): item for item in payload.get("results") or [] if _clean(item.get("account_id"))}


def build_promote_lookup(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for item in payload.get("results") or []:
        account_id = _clean(item.get("account_id"))
        if account_id:
            result[account_id] = item
    return result


def main() -> int:
    args = build_parser().parse_args()
    config = load_json(args.config_file)
    current_enrich = load_json(args.enrich_result_file)
    current_promote = load_json(args.promote_result_file)
    baseline_enrich = load_json(config["baseline_enrich_file"])
    baseline_promote = load_json(config["baseline_promote_file"])

    current_enrich_by_id = build_enrich_lookup(current_enrich)
    baseline_enrich_by_id = build_enrich_lookup(baseline_enrich)
    current_promote_by_id = build_promote_lookup(current_promote)
    baseline_promote_by_id = build_promote_lookup(baseline_promote)

    accounts_cfg = config.get("accounts") or {}
    items: list[dict[str, object]] = []
    summary = {
        "account_count": 0,
        "observation_kept": 0,
        "observation_promoted_to_formal": 0,
        "control_to_allow": 0,
        "control_kept_warn": 0,
        "control_downgraded": 0,
        "official_source_repaired": 0,
        "persona_resolved": 0,
    }

    for account_id in config.get("account_ids") or []:
        account_meta = accounts_cfg.get(account_id) or {}
        before_enrich = baseline_enrich_by_id.get(account_id, {})
        after_enrich = current_enrich_by_id.get(account_id, {})
        before_promote = (baseline_promote_by_id.get(account_id) or {}).get("promotion_gate") or {}
        after_promote = (current_promote_by_id.get(account_id) or {}).get("promotion_gate") or {}

        before_candidate_type = _clean(before_enrich.get("candidate_type"))
        after_candidate_type = _clean(after_enrich.get("candidate_type"))
        before_minimum_fact = _clean(before_enrich.get("minimum_fact_status"))
        after_minimum_fact = _clean(after_enrich.get("minimum_fact_status"))
        before_decision = _clean(before_promote.get("decision"))
        after_decision = _clean(after_promote.get("decision"))
        official_source_repaired = (
            _clean(before_enrich.get("official_source_status")) == "missing"
            and _clean(after_enrich.get("official_source_status")) == "available"
        )
        persona_resolved = not _clean(before_enrich.get("persona_tag")) and bool(_clean(after_enrich.get("persona_tag")))
        remaining_gaps = [
            item
            for item in [
                _clean(after_enrich.get("validation_gap")),
                *[_clean(issue.get("message")) for issue in (after_promote.get("blocking_issues") or []) if _clean(issue.get("message"))],
                *[_clean(issue.get("message")) for issue in (after_promote.get("warning_issues") or []) if _clean(issue.get("message"))],
            ]
            if item
        ]

        item = {
            "account_id": account_id,
            "account_name": _clean(after_enrich.get("account_canonical_name") or before_enrich.get("account_canonical_name")),
            "track": _clean(account_meta.get("track")),
            "role": _clean(account_meta.get("role")),
            "before_candidate_type": before_candidate_type,
            "after_candidate_type": after_candidate_type,
            "before_minimum_fact_status": before_minimum_fact,
            "after_minimum_fact_status": after_minimum_fact,
            "before_promote_decision": before_decision,
            "after_promote_decision": after_decision,
            "official_source_repaired": official_source_repaired,
            "persona_resolved": persona_resolved,
            "writeback_targets": WRITEBACK_TARGETS,
            "remaining_gaps": remaining_gaps,
            "after_persona_tag": after_enrich.get("persona_tag"),
            "after_secondary_persona_tags": after_enrich.get("secondary_persona_tags") or [],
            "after_review_status": after_enrich.get("review_status"),
            "after_required_queue_type": after_enrich.get("required_queue_type"),
            "promote_summary": _clean(after_promote.get("summary")),
            "enrich_summary": _clean(after_enrich.get("summary")),
        }
        items.append(item)
        summary["account_count"] += 1
        if official_source_repaired:
            summary["official_source_repaired"] += 1
        if persona_resolved:
            summary["persona_resolved"] += 1

        if item["role"] == "observation":
            if after_candidate_type == "formal_candidate":
                summary["observation_promoted_to_formal"] += 1
            else:
                summary["observation_kept"] += 1
        else:
            if after_decision == "allow":
                summary["control_to_allow"] += 1
            elif after_decision == "warn":
                summary["control_kept_warn"] += 1
            else:
                summary["control_downgraded"] += 1

    payload = {
        "batch_id": _clean(config.get("batch_id")),
        "goal": _clean(config.get("goal")),
        "summary": summary,
        "enrich_summary": current_enrich.get("summary") or {},
        "promote_summary": current_promote.get("batch_summary") or {},
        "write_back": current_enrich.get("write_back") or {},
        "items": items,
    }
    Path(args.output_file).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_file": args.output_file, "summary": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
