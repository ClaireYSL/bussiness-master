from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.static_promote import evaluate_static_promotion


DEFAULT_TRUSTED_POOL = "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
DEFAULT_SOURCE_TRACE = "deliveries/archive/milestones/milestone52r_second_evidence_patch/source_trace_index_v2.json"
DEFAULT_OUTPUT = "deliveries/archive/milestones/milestone59r_static_promotion_core/trusted_pool_static_promote_report_v1.json"
DEFAULT_GAP_QUEUE = "deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/static_gap_queue_v1.json"
DEFAULT_BASELINE = "deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/trusted_pool_runner_baseline_v1.json"
DEFAULT_SOURCE_TRACE_OUTPUT = "deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/source_trace_normalized_v1.json"
DEFAULT_NO_WRITE_PROOF = "deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/no_write_proof_v1.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-first trusted pool runner for static L1-L5 promotion.")
    parser.add_argument("--trusted-pool", default=DEFAULT_TRUSTED_POOL)
    parser.add_argument("--source-trace", default=DEFAULT_SOURCE_TRACE)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT)
    parser.add_argument("--gap-queue-file", default=DEFAULT_GAP_QUEUE)
    parser.add_argument("--baseline-file", default=DEFAULT_BASELINE)
    parser.add_argument("--source-trace-output", default=DEFAULT_SOURCE_TRACE_OUTPUT)
    parser.add_argument("--no-write-proof-file", default=DEFAULT_NO_WRITE_PROOF)
    parser.add_argument("--require-baseline", action="store_true", help="Fail if the current batch signature differs from --baseline-file.")
    parser.add_argument("--write-baseline", action="store_true", help="Write the current batch baseline/signature.")
    parser.add_argument("--update-trusted-pool", action="store_true", help="Persist suggested levels back to trusted_prospect_pool_v1 JSON.")
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _source_trace_by_prospect(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in payload.get("items") or []:
        prospect_id = str(item.get("prospect_id") or "").strip()
        if not prospect_id:
            continue
        sources = item.get("sources") or []
        grouped[prospect_id] = [source for source in sources if isinstance(source, dict)]
    return grouped


def _batch_signature(items: list[dict[str, Any]], source_trace: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    candidates = []
    for item in items:
        prospect_id = str(item.get("prospect_id") or "").strip()
        candidates.append(
            {
                "prospect_id": prospect_id,
                "company_name": str(item.get("company_name") or "").strip(),
                "matched_persona": str(item.get("matched_persona") or item.get("persona") or "").strip(),
                "source_locator": str(item.get("source_locator") or "").strip(),
                "source_count": len(source_trace.get(prospect_id, [])),
            }
        )
    candidates.sort(key=lambda row: row["prospect_id"])
    return {
        "candidate_count": len(candidates),
        "candidate_signature": _sha256(candidates),
        "candidates": candidates,
    }


def _normalized_source_trace(source_trace: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    items = []
    for prospect_id in sorted(source_trace):
        sources = source_trace[prospect_id]
        strong_sources = [
            source
            for source in sources
            if str(source.get("evidence_strength") or "").strip().lower()
            in {"official", "ir", "annual_report", "exchange_filing", "regulatory_annual_report", "cninfo", "announcement"}
        ]
        items.append(
            {
                "prospect_id": prospect_id,
                "source_count": len(sources),
                "strong_source_count": len(strong_sources),
                "sources": sources,
            }
        )
    return {
        "generated_at": _now(),
        "source_trace_count": len(items),
        "items": items,
    }


def _status_for_level(level: str) -> str:
    return {
        "L1": "static_l1_ready",
        "L2": "static_l2_ready",
        "L3": "trusted_summary_ready",
        "L4": "evidence_pending",
        "L5": "candidate_seed",
    }.get(level, "candidate_seed")


def main() -> int:
    args = build_parser().parse_args()
    pool_path = Path(args.trusted_pool)
    pool = _read_json(pool_path)
    source_trace = _source_trace_by_prospect(_read_json(args.source_trace))
    items = [item for item in pool.get("items") or [] if isinstance(item, dict)]
    signature = _batch_signature(items, source_trace)
    baseline = {
        "generated_at": _now(),
        "runner": "trusted_pool_runner",
        "trusted_pool_file": str(pool_path),
        "source_trace_file": str(args.source_trace),
        **{key: value for key, value in signature.items() if key != "candidates"},
    }
    if args.require_baseline:
        existing = _read_json(args.baseline_file)
        expected = existing.get("candidate_signature")
        if not expected:
            print(f"trusted_pool_runner baseline missing: {args.baseline_file}", file=sys.stderr)
            return 2
        if expected != signature["candidate_signature"]:
            print(
                "trusted_pool_runner baseline mismatch: "
                f"expected={expected} actual={signature['candidate_signature']}",
                file=sys.stderr,
            )
            return 2

    decisions = [evaluate_static_promotion(item, source_trace_by_prospect=source_trace).to_dict() for item in items]
    gap_queue = [
        {"prospect_id": decision["prospect_id"], "company_name": decision["company_name"], **gap}
        for decision in decisions
        for gap in decision["gap_queue"]
    ]
    level_counts: dict[str, int] = {}
    for decision in decisions:
        level_counts[decision["suggested_level"]] = level_counts.get(decision["suggested_level"], 0) + 1

    updated_pool_written = False
    if args.update_trusted_pool:
        by_id = {decision["prospect_id"]: decision for decision in decisions}
        for item in items:
            decision = by_id.get(str(item.get("prospect_id") or "").strip())
            if not decision:
                continue
            item["level"] = decision["suggested_level"]
            item["trusted_status"] = _status_for_level(decision["suggested_level"])
            item["static_promotion_summary"] = decision["summary"]
            item["static_gap_count"] = len(decision["gap_queue"])
        pool["generated_at"] = _now()
        pool["summary"] = {**(pool.get("summary") or {}), "static_level_counts": level_counts, "runner": "trusted_pool_runner"}
        _write_json(pool_path, pool)
        updated_pool_written = True

    report = {
        "batch_id": Path(args.output_file).stem,
        "generated_at": _now(),
        "runner": "trusted_pool_runner_v2",
        "mode": "update_trusted_pool" if args.update_trusted_pool else "report_only",
        "trusted_pool_file": str(pool_path),
        "source_trace_file": str(args.source_trace),
        "baseline_file": str(args.baseline_file),
        "candidate_signature": signature["candidate_signature"],
        "summary": {
            "prospect_count": len(items),
            "level_counts": level_counts,
            "gap_queue_count": len(gap_queue),
            "updated_pool_written": updated_pool_written,
            "old_workbook_write_enabled": False,
            "baseline_required": bool(args.require_baseline),
            "baseline_written": bool(args.write_baseline),
        },
        "decisions": decisions,
        "static_gap_queue": gap_queue,
        "no_write_proof": {
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
            "dynamic_followup_task_created": False,
        },
    }
    gap_queue_payload = {
        "generated_at": _now(),
        "candidate_signature": signature["candidate_signature"],
        "gap_queue_count": len(gap_queue),
        "items": gap_queue,
    }
    source_trace_payload = _normalized_source_trace(source_trace)
    no_write_proof = {
        "generated_at": _now(),
        "status": "PASS_NO_LEGACY_OR_DYNAMIC_WRITE",
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "dynamic_followup_task_created": False,
        "trusted_pool_updated": updated_pool_written,
    }
    _write_json(args.output_file, report)
    _write_json(args.gap_queue_file, gap_queue_payload)
    _write_json(args.source_trace_output, source_trace_payload)
    _write_json(args.no_write_proof_file, no_write_proof)
    if args.write_baseline:
        _write_json(args.baseline_file, baseline)
    print(json.dumps({"output_file": args.output_file, "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
