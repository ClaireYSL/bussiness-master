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

from shared.static_pool import (
    attach_account_ids,
    evaluate_promotion_batch,
    load_main_rows,
    load_sheet_rows,
    resolve_static_pool_paths,
)

DEFAULT_M18 = "deliveries/archive/milestones/milestone18_l3_operationalization/milestone18_l3_operational_package_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone19_expansion_feedback/milestone19_expansion_feedback_package_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 19-扩容节奏与业务反馈闭环复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M19 expansion cadence and business feedback package.")
    parser.add_argument("--m18-package", default=DEFAULT_M18)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--target-next-batch", type=int, default=30)
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


def _issue_codes(result: dict[str, Any], key: str) -> list[str]:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    rows = gate.get(key) if isinstance(gate.get(key), list) else []
    return [_clean(row.get("code")) for row in rows if isinstance(row, dict) and _clean(row.get("code"))]


def _feedback_item(item: dict[str, Any]) -> dict[str, Any]:
    persona = _clean(item.get("persona"))
    track = _clean(item.get("track"))
    return {
        "account_id": _clean(item.get("account_id")),
        "account_name": _clean(item.get("account_name")),
        "track": track,
        "persona": persona,
        "feedback_status": "pending_business_feedback",
        "recommended_reviewer": "sales_or_research_owner",
        "business_feedback_fields": {
            "fit_score_1_to_5": "",
            "is_real_target": "",
            "best_use_case": "",
            "contact_or_channel_hint": "",
            "disqualify_reason": "",
            "next_action": "",
        },
        "starter_question": f"这家公司是否符合 `{track}/{persona}` 的真实业务优先级，是否值得进入 L2 补强？",
        "evidence_brief": {
            "product_summary": _clean(item.get("product_summary")),
            "business_model_summary": _clean(item.get("business_model_summary")),
            "why_worth_review": _clean(item.get("why_worth_review")),
            "remaining_gap": _clean(item.get("validation_gap")),
            "evidence_count": int(item.get("evidence_count") or 0),
        },
    }


def _preflight_status(result: dict[str, Any]) -> str:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    decision = _clean(gate.get("decision"))
    blocking = _issue_codes(result, "blocking_issues")
    warnings = _issue_codes(result, "warning_issues")
    if decision == "allow":
        return "executable_now"
    if decision == "warn" and not blocking:
        return "needs_review"
    if blocking and set(blocking) <= {"missing_field", "official_source_missing"}:
        return "needs_intake_patch"
    if warnings and not blocking:
        return "needs_quality_patch"
    return "not_ready"


def _candidate_item(result: dict[str, Any]) -> dict[str, Any]:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    blocking = _issue_codes(result, "blocking_issues")
    warnings = _issue_codes(result, "warning_issues")
    status = _preflight_status(result)
    return {
        "account_id": _clean(result.get("account_id")),
        "account_name": _clean(result.get("account_canonical_name")),
        "track": _clean(result.get("primary_track")),
        "persona": _clean(result.get("persona_tag")),
        "current_level": _clean(result.get("from_level")),
        "target_level": _clean(result.get("target_level")),
        "latest_decision": _clean(gate.get("decision")),
        "preflight_status": status,
        "blocking_codes": blocking,
        "warning_codes": warnings,
        "next_action": {
            "executable_now": "可进入下一轮 report-only；真实写回仍需 gate 和确认。",
            "needs_review": "可进入人工复核或业务反馈后再决定是否 patch/writeback。",
            "needs_intake_patch": "先补产品、商业模式、官方来源和入池理由。",
            "needs_quality_patch": "先补 evidence 或去模板化字段。",
            "not_ready": "暂不进入扩容，回到画像或事实源治理。",
        }.get(status, "待复核。"),
    }


def _next_batch_plan(candidates: list[dict[str, Any]], target_next_batch: int) -> dict[str, Any]:
    preferred_status = {"executable_now", "needs_review", "needs_intake_patch"}
    eligible = [item for item in candidates if item["preflight_status"] in preferred_status]
    picked = eligible[:target_next_batch]
    executable_count = len([item for item in candidates if item["preflight_status"] == "executable_now"])
    if executable_count == 0 and picked:
        cadence = "下一轮不是直接扩容写回，而是选择 30 家 needs_intake_patch 做补证试运行；完成 patch 后再 report-only/gate。"
        objective = "intake_patch_trial"
    else:
        cadence = "先 30 家 report-only，若 block 率低于 30% 且 gate PASS，再考虑下一轮 50 家；默认不直接写回。"
        objective = "report_only_expansion"
    return {
        "target_size": target_next_batch,
        "objective": objective,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "executable_now_count": executable_count,
        "picked_count": len(picked),
        "picked_account_ids": [item["account_id"] for item in picked],
        "track_mix": dict(Counter(item["track"] for item in picked)),
        "status_mix": dict(Counter(item["preflight_status"] for item in picked)),
        "cadence": cadence,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    plan = payload["next_batch_plan"]
    lines = [
        "# Milestone 19-扩容节奏与业务反馈闭环复盘-v1",
        "",
        "## 摘要",
        "",
        f"- L3 反馈对象：`{summary['feedback_item_count']}`",
        f"- 下一轮候选池：`{summary['next_candidate_count']}`",
        f"- 下一轮建议选取：`{plan['picked_count']} / {plan['target_size']}`",
        f"- 候选状态分布：`{summary['candidate_status_counts']}`",
        "",
        "## 业务反馈模板",
        "",
    ]
    for item in payload["feedback_items"]:
        lines.extend(
            [
                f"### {item['account_name']}（{item['account_id']}）",
                "",
                f"- 主线/画像：`{item['track']}` / `{item['persona']}`",
                f"- 问题：{item['starter_question']}",
                f"- 证据摘要：{item['evidence_brief']['why_worth_review']}",
                f"- 待反馈字段：`fit_score_1_to_5 / is_real_target / best_use_case / contact_or_channel_hint / disqualify_reason / next_action`",
                "",
            ]
        )
    lines.extend(
        [
            "## 下一轮扩容节奏",
            "",
            f"- 节奏：{plan['cadence']}",
            f"- track mix：`{plan['track_mix']}`",
            f"- status mix：`{plan['status_mix']}`",
            "",
            "## 安全边界",
            "",
            "- M19 不执行写回，只生成反馈模板和扩容建议。",
            "- 下一轮扩容仍必须走 `select/preflight -> report_only -> gate -> write_back确认`。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    m18 = _load_json(args.m18_package)
    feedback_items = [_feedback_item(item) for item in m18.get("items") or [] if isinstance(item, dict)]

    main_rows = load_main_rows(pool["main"], "accounts_main")
    _headers, profile_rows = load_sheet_rows(pool["profile"], "account_profiles")
    _headers, queue_rows = load_sheet_rows(pool["governance"], "review_queue")
    _headers, evidence_rows = load_sheet_rows(pool["governance"], "evidence_log")
    main_rows = attach_account_ids(main_rows, profile_rows)

    candidate_results: list[dict[str, Any]] = []
    for track in ["零售消费", "跨境电商", "先进制造"]:
        eval_payload = evaluate_promotion_batch(
            main_rows,
            profile_rows,
            evidence_rows,
            queue_rows,
            from_level="L5",
            target_level="L3",
            track=track,
            limit=9999,
        )
        candidate_results.extend(_candidate_item(item) for item in eval_payload.get("results") or [] if isinstance(item, dict))

    candidate_results = sorted(
        [item for item in candidate_results if item["account_id"]],
        key=lambda item: (item["preflight_status"] != "executable_now", item["track"], item["latest_decision"], item["account_id"]),
    )
    plan = _next_batch_plan(candidate_results, args.target_next_batch)
    payload = {
        "batch_id": "milestone19_expansion_feedback_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {"m18_package": args.m18_package},
        "static_pool_root": str(pool["root"]),
        "summary": {
            "feedback_item_count": len(feedback_items),
            "next_candidate_count": len(candidate_results),
            "candidate_status_counts": dict(Counter(item["preflight_status"] for item in candidate_results)),
            "candidate_decision_counts": dict(Counter(item["latest_decision"] for item in candidate_results)),
        },
        "feedback_items": feedback_items,
        "next_batch_candidates": candidate_results,
        "next_batch_plan": plan,
    }
    _write_json(args.output_json, payload)
    _write_text(args.output_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "summary": payload["summary"], "next_batch_plan": plan}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
