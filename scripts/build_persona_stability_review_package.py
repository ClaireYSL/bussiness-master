from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import attach_account_ids, load_main_rows, load_sheet_rows, normalize_review_status, resolve_static_pool_paths

DEFAULT_PROMOTE_RESULT = "deliveries/archive/milestones/milestone11_warn_quality/milestone11_warn_quality_promote_v1_report_only_L2_1.json"
DEFAULT_OUTPUT = "deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_abstract_input_v1.json"
DEFAULT_REVIEW = "docs/03-执行与校验/Milestone 12-主画像稳定性复核草稿-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an abstracted persona stability review package for external LLM delegation.")
    parser.add_argument("--promote-result-file", default=DEFAULT_PROMOTE_RESULT)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT)
    parser.add_argument("--review-file", default=DEFAULT_REVIEW)
    parser.add_argument("--max-evidence-per-account", type=int, default=5)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _lookup_by_id(rows: list[dict[str, object]], key: str = "account_id") -> dict[str, dict[str, object]]:
    return {_clean(row.get(key)): row for row in rows if _clean(row.get(key))}


def _group_by_id(rows: list[dict[str, object]], key: str = "account_id") -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        account_id = _clean(row.get(key))
        if account_id:
            grouped.setdefault(account_id, []).append(row)
    return grouped


def _first_nonempty(*values: object) -> str:
    for value in values:
        clean = _clean(value)
        if clean:
            return clean
    return ""


def _issue_codes(gate: dict[str, object], key: str) -> list[str]:
    issues = gate.get(key) or []
    if not isinstance(issues, list):
        return []
    return [_clean(item.get("code")) for item in issues if isinstance(item, dict) and _clean(item.get("code"))]


def _evidence_abstract(row: dict[str, object]) -> dict[str, str]:
    return {
        "source_type": _first_nonempty(row.get("source_type"), row.get("来源类型")),
        "evidence_strength": _first_nonempty(row.get("evidence_strength"), row.get("strength"), row.get("证据强度")),
        "supports_dimension": _first_nonempty(row.get("supports_dimension"), row.get("支持维度")),
        "summary": _first_nonempty(row.get("evidence_summary"), row.get("summary"), row.get("证据摘要"), row.get("note")),
        "source_locator": _first_nonempty(row.get("source_locator"), row.get("source_ref"), row.get("来源定位")),
    }


def _queue_abstract(row: dict[str, object]) -> dict[str, str]:
    return {
        "queue_type": _clean(row.get("queue_type")),
        "status": _clean(row.get("status")),
        "priority": _clean(row.get("priority")),
        "note": _clean(row.get("note")),
    }


def _build_account_payload(
    result: dict[str, object],
    main_row: dict[str, object],
    profile_row: dict[str, object],
    evidence_rows: list[dict[str, object]],
    queue_rows: list[dict[str, object]],
    *,
    max_evidence: int,
) -> dict[str, object]:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    account_id = _clean(result.get("account_id"))
    review_status = normalize_review_status(_first_nonempty(main_row.get("review_status"), profile_row.get("review_status"), gate.get("suggested_review_status")))
    warning_codes = _issue_codes(gate, "warning_issues")
    blocking_codes = _issue_codes(gate, "blocking_issues")
    evidence = [_evidence_abstract(row) for row in evidence_rows[:max_evidence]]
    queues = [_queue_abstract(row) for row in queue_rows if _clean(row.get("status")) in {"", "open", "in_progress"}]
    return {
        "account_id": account_id,
        "account_name": _first_nonempty(result.get("account_canonical_name"), main_row.get("account_canonical_name"), profile_row.get("account_canonical_name")),
        "primary_track": _first_nonempty(result.get("primary_track"), main_row.get("primary_track"), profile_row.get("primary_track")),
        "current_persona": _first_nonempty(result.get("persona_tag"), main_row.get("persona_tag"), profile_row.get("persona_tag")),
        "secondary_personas": _first_nonempty(result.get("secondary_persona_tags"), main_row.get("secondary_persona_tags"), profile_row.get("secondary_persona_tags")),
        "current_review_status": review_status,
        "current_promotion_decision": _clean(gate.get("decision")),
        "warning_codes": warning_codes,
        "blocking_codes": blocking_codes,
        "product_service_summary": _first_nonempty(main_row.get("公司产品与服务概述"), profile_row.get("公司产品与服务概述"), profile_row.get("产品与服务长摘录")),
        "business_model_summary": _first_nonempty(main_row.get("商业模式概述"), profile_row.get("商业模式概述"), profile_row.get("商业模式长摘录")),
        "admission_reason_summary": _first_nonempty(main_row.get("admission_reason_summary"), profile_row.get("admission_reason_summary"), profile_row.get("一话入池理由")),
        "validation_gap": _first_nonempty(main_row.get("validation_gap"), profile_row.get("validation_gap"), profile_row.get("待验证项")),
        "knowledge_asset_refs": _first_nonempty(main_row.get("knowledge_asset_refs"), profile_row.get("knowledge_asset_refs")),
        "talk_track_refs": _first_nonempty(main_row.get("talk_track_refs"), profile_row.get("talk_track_refs")),
        "evidence_summaries": evidence,
        "open_review_queue": queues,
        "local_gate_summary": _clean(gate.get("summary")),
        "expected_review_question": "当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。",
    }


def _render_review(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Milestone 12-主画像稳定性复核草稿-v1",
        "",
        "## 1. 批次概览",
        "",
        f"- batch_id：`{payload.get('batch_id')}`",
        f"- 生成时间：`{payload.get('generated_at')}`",
        f"- 样本数：`{summary.get('account_count')}`",
        f"- 当前 promote：`allow={summary.get('decision_counts', {}).get('allow', 0)} / warn={summary.get('decision_counts', {}).get('warn', 0)} / block={summary.get('decision_counts', {}).get('block', 0)}`",
        f"- persona_boundary_unstable：`{summary.get('warning_code_counts', {}).get('persona_boundary_unstable', 0)}`",
        "",
        "## 2. 复核口径",
        "",
        "本文件是 LLM/人工画像复核前的抽象输入草稿，不是写回结果。",
        "",
        "建议动作只能落入：`keep_persona`、`change_persona`、`keep_pending_review`、`hold`。",
        "",
        "## 3. 公司清单",
        "",
    ]
    for item in payload.get("accounts") or []:
        lines.extend(
            [
                f"### {item.get('account_name')}（{item.get('account_id')}）",
                "",
                f"- 主线 / 当前画像：`{item.get('primary_track')} / {item.get('current_persona')}`",
                f"- 当前状态：`{item.get('current_review_status')}`",
                f"- 当前 promote：`{item.get('current_promotion_decision')}`",
                f"- warn：`{', '.join(item.get('warning_codes') or []) or '无'}`",
                f"- 产品与服务：{item.get('product_service_summary') or '待补' }",
                f"- 入池理由：{item.get('admission_reason_summary') or '待补' }",
                f"- 待复核问题：{item.get('expected_review_question')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    promote_payload = _load_json(args.promote_result_file)
    results = [item for item in promote_payload.get("results") or [] if isinstance(item, dict)]

    paths = resolve_static_pool_paths()
    main_rows = load_main_rows(paths["main"], "accounts_main")
    _profile_headers, profile_rows = load_sheet_rows(paths["profile"], "account_profiles")
    _evidence_headers, evidence_rows = load_sheet_rows(paths["governance"], "evidence_log")
    _queue_headers, queue_rows = load_sheet_rows(paths["governance"], "review_queue")
    main_rows = attach_account_ids(main_rows, profile_rows)

    main_by_id = _lookup_by_id(main_rows)
    profile_by_id = _lookup_by_id(profile_rows)
    evidence_by_id = _group_by_id(evidence_rows)
    queue_by_id = _group_by_id(queue_rows)

    accounts = []
    decision_counts: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    for result in results:
        account_id = _clean(result.get("account_id"))
        gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
        decision_counts[_clean(gate.get("decision"))] += 1
        warning_counts.update(_issue_codes(gate, "warning_issues"))
        accounts.append(
            _build_account_payload(
                result,
                main_by_id.get(account_id, {}),
                profile_by_id.get(account_id, {}),
                evidence_by_id.get(account_id, []),
                queue_by_id.get(account_id, []),
                max_evidence=args.max_evidence_per_account,
            )
        )

    output = {
        "batch_id": "milestone12_persona_stability_review_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {
            "promote_result_file": args.promote_result_file,
            "main_file": str(paths["main"]),
            "profile_file": str(paths["profile"]),
            "governance_file": str(paths["governance"]),
        },
        "llm_boundary": {
            "input_is_abstracted": True,
            "raw_source_text_included": False,
            "direct_writeback_allowed": False,
            "allowed_use": "persona stability draft review only",
        },
        "summary": {
            "account_count": len(accounts),
            "decision_counts": dict(decision_counts),
            "warning_code_counts": dict(warning_counts),
        },
        "accounts": accounts,
    }
    _write_json(args.output_file, output)
    if args.review_file:
        _write_text(args.review_file, _render_review(output))
    print(json.dumps({"output_file": args.output_file, "review_file": args.review_file, "account_count": len(accounts)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
