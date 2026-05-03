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
DEFAULT_SOURCE_TRACE = "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json"
DEFAULT_OUTPUT = "deliveries/archive/runtime/trusted_pool_runner/trusted_pool_static_promote_report_v1.json"
DEFAULT_GAP_QUEUE = "deliveries/archive/runtime/trusted_pool_runner/static_gap_queue_v1.json"
DEFAULT_BASELINE = "deliveries/archive/runtime/trusted_pool_runner/trusted_pool_runner_baseline_v1.json"
DEFAULT_SOURCE_TRACE_OUTPUT = "deliveries/archive/runtime/trusted_pool_runner/source_trace_normalized_v1.json"
DEFAULT_NO_WRITE_PROOF = "deliveries/archive/runtime/trusted_pool_runner/no_write_proof_v1.json"
DEFAULT_POOL_DIFF = "deliveries/archive/runtime/trusted_pool_runner/pool_diff_report_v1.json"
DEFAULT_VALIDATION = "deliveries/archive/runtime/trusted_pool_runner/validation_report_v1.json"
DEFAULT_VAULT_PREVIEW = "deliveries/archive/runtime/trusted_pool_runner/vault_output_preview"
DEFAULT_VAULT_ROOT = "/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案"


STATIC_UPDATE_FIELDS = (
    "level",
    "trusted_status",
    "static_promotion_summary",
    "static_gap_count",
    "static_evidence_count",
    "static_strong_evidence_count",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evidence-first trusted pool runner for static L1-L5 promotion.")
    parser.add_argument(
        "--mode",
        choices=("report_only", "validate_only", "update_trusted_pool", "generate_vault_preview", "write_vault_regular"),
        default="report_only",
    )
    parser.add_argument("--trusted-pool", default=DEFAULT_TRUSTED_POOL)
    parser.add_argument("--source-trace", default=DEFAULT_SOURCE_TRACE)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT)
    parser.add_argument("--gap-queue-file", default=DEFAULT_GAP_QUEUE)
    parser.add_argument("--baseline-file", default=DEFAULT_BASELINE)
    parser.add_argument("--source-trace-output", default=DEFAULT_SOURCE_TRACE_OUTPUT)
    parser.add_argument("--no-write-proof-file", default=DEFAULT_NO_WRITE_PROOF)
    parser.add_argument("--pool-diff-file", default=DEFAULT_POOL_DIFF)
    parser.add_argument("--validation-report-file", default=DEFAULT_VALIDATION)
    parser.add_argument("--vault-preview-dir", default=DEFAULT_VAULT_PREVIEW)
    parser.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--require-baseline", action="store_true", help="Fail if the current batch signature differs from --baseline-file.")
    parser.add_argument("--write-baseline", action="store_true", help="Write the current batch baseline/signature.")
    parser.add_argument("--allow-trusted-pool-update", action="store_true", help="Required with --mode update_trusted_pool.")
    parser.add_argument("--update-trusted-pool", action="store_true", help="Persist suggested levels back to trusted_prospect_pool_v1 JSON.")
    parser.add_argument("--allow-vault-regular-write", action="store_true", help="Required with --mode write_vault_regular.")
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


def _safe_filename(value: str) -> str:
    keep = []
    for char in value.strip():
        if char in {"/", "\\", ":", "*", "?", '"', "<", ">", "|"}:
            keep.append("_")
        else:
            keep.append(char)
    return "".join(keep) or "unknown_prospect"


def _vault_regular_dir(vault_root: str | Path, level: str) -> Path | None:
    root = Path(vault_root)
    return {
        "L1": root / "01-L1 ICP强匹配档案",
        "L2": root / "02-L2正式潜客档案",
        "L3": root / "03-L3可信摘要卡",
    }.get(level)


def _static_patch_for_decision(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "level": decision["suggested_level"],
        "trusted_status": _status_for_level(decision["suggested_level"]),
        "static_promotion_summary": decision["summary"],
        "static_gap_count": len(decision["gap_queue"]),
        "static_evidence_count": decision["evidence_count"],
        "static_strong_evidence_count": decision["strong_evidence_count"],
    }


def _build_pool_diff(items: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {decision["prospect_id"]: decision for decision in decisions}
    changes = []
    for item in items:
        prospect_id = str(item.get("prospect_id") or "").strip()
        decision = by_id.get(prospect_id)
        if not decision:
            continue
        patch = _static_patch_for_decision(decision)
        field_changes = []
        for field, new_value in patch.items():
            old_value = item.get(field)
            if old_value != new_value:
                field_changes.append({"field": field, "old": old_value, "new": new_value})
        changes.append(
            {
                "prospect_id": prospect_id,
                "company_name": decision["company_name"],
                "changed": bool(field_changes),
                "field_changes": field_changes,
            }
        )
    return {
        "generated_at": _now(),
        "changed_count": sum(1 for change in changes if change["changed"]),
        "items": changes,
    }


def _write_vault_preview(preview_dir: str | Path, items: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[dict[str, str]]:
    out_dir = Path(preview_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    by_id = {str(item.get("prospect_id") or "").strip(): item for item in items}
    outputs = []
    for decision in decisions:
        item = by_id.get(decision["prospect_id"], {})
        filename = _safe_filename(decision["company_name"]) + ".md"
        path = out_dir / filename
        gaps = "\n".join(f"- {gap.get('reason', '')}" for gap in decision["gap_queue"]) or "- 暂无结构化缺口。"
        text = f"""---
prospect_id: {decision['prospect_id']}
static_level: {decision['suggested_level']}
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
---

# {decision['company_name']}

## 静态等级

{decision['suggested_level']}

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键来源

- {item.get('source_locator', '')}

## 风险与待补点

{item.get('risk_or_gap', '')}

## 升层缺口

{gaps}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""
        path.write_text(text, encoding="utf-8")
        outputs.append({"prospect_id": decision["prospect_id"], "company_name": decision["company_name"], "path": str(path)})
    return outputs


def _write_vault_regular(vault_root: str | Path, items: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_id = {str(item.get("prospect_id") or "").strip(): item for item in items}
    outputs = []
    for decision in decisions:
        level = decision["suggested_level"]
        target_dir = _vault_regular_dir(vault_root, level)
        if target_dir is None:
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        item = by_id.get(decision["prospect_id"], {})
        filename = _safe_filename(decision["company_name"]) + ".md"
        path = target_dir / filename
        gaps = "\n".join(f"- {gap.get('reason', '')}" for gap in decision["gap_queue"]) or "- 暂无结构化缺口。"
        text = f"""---
prospect_id: {decision['prospect_id']}
static_level: {level}
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
fact_source: trusted_prospect_pool_v1
---

# {decision['company_name']}

## 静态等级

{level}

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键来源

- {item.get('source_locator', '')}

## 风险与待补点

{item.get('risk_or_gap', '')}

## 升层缺口

{gaps}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""
        path.write_text(text, encoding="utf-8")
        outputs.append({"prospect_id": decision["prospect_id"], "company_name": decision["company_name"], "level": level, "path": str(path)})
    return outputs


def main() -> int:
    args = build_parser().parse_args()
    mode = "update_trusted_pool" if args.update_trusted_pool else args.mode
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

    pool_diff = _build_pool_diff(items, decisions)
    validation_errors: list[str] = []
    if mode == "update_trusted_pool" and not args.allow_trusted_pool_update:
        validation_errors.append("update_trusted_pool requires --allow-trusted-pool-update")
    if mode == "write_vault_regular" and not args.allow_vault_regular_write:
        validation_errors.append("write_vault_regular requires --allow-vault-regular-write")

    updated_pool_written = False
    if mode == "update_trusted_pool" and not validation_errors:
        by_id = {decision["prospect_id"]: decision for decision in decisions}
        for item in items:
            decision = by_id.get(str(item.get("prospect_id") or "").strip())
            if not decision:
                continue
            item.update(_static_patch_for_decision(decision))
        pool["generated_at"] = _now()
        pool["summary"] = {**(pool.get("summary") or {}), "static_level_counts": level_counts, "runner": "trusted_pool_runner_v3"}
        _write_json(pool_path, pool)
        updated_pool_written = True

    if validation_errors:
        validation_report = {
            "generated_at": _now(),
            "status": "FAIL_VALIDATION",
            "mode": mode,
            "errors": validation_errors,
        }
        _write_json(args.validation_report_file, validation_report)
        print("; ".join(validation_errors), file=sys.stderr)
        return 2

    vault_preview_outputs: list[dict[str, str]] = []
    if mode == "generate_vault_preview":
        vault_preview_outputs = _write_vault_preview(args.vault_preview_dir, items, decisions)
    vault_regular_outputs: list[dict[str, str]] = []
    if mode == "write_vault_regular":
        vault_regular_outputs = _write_vault_regular(args.vault_root, items, decisions)

    report = {
        "batch_id": Path(args.output_file).stem,
        "generated_at": _now(),
        "runner": "trusted_pool_runner_v3",
        "mode": mode,
        "trusted_pool_file": str(pool_path),
        "source_trace_file": str(args.source_trace),
        "baseline_file": str(args.baseline_file),
        "candidate_signature": signature["candidate_signature"],
        "summary": {
            "prospect_count": len(items),
            "level_counts": level_counts,
            "gap_queue_count": len(gap_queue),
            "updated_pool_written": updated_pool_written,
            "pool_diff_changed_count": pool_diff["changed_count"],
            "vault_preview_count": len(vault_preview_outputs),
            "vault_regular_write_count": len(vault_regular_outputs),
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
        "pool_diff_file": str(args.pool_diff_file),
        "vault_preview_outputs": vault_preview_outputs,
        "vault_regular_outputs": vault_regular_outputs,
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
        "vault_preview_written": bool(vault_preview_outputs),
        "vault_regular_area_written": bool(vault_regular_outputs),
    }
    validation_report = {
        "generated_at": _now(),
        "status": "PASS_VALIDATION",
        "mode": mode,
        "prospect_count": len(items),
        "candidate_signature": signature["candidate_signature"],
        "dynamic_static_boundary": "PASS_STATIC_ONLY",
        "old_workbook_write_enabled": False,
    }
    _write_json(args.output_file, report)
    _write_json(args.gap_queue_file, gap_queue_payload)
    _write_json(args.source_trace_output, source_trace_payload)
    _write_json(args.no_write_proof_file, no_write_proof)
    _write_json(args.pool_diff_file, pool_diff)
    _write_json(args.validation_report_file, validation_report)
    if args.write_baseline:
        _write_json(args.baseline_file, baseline)
    print(json.dumps({"output_file": args.output_file, "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
