from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_M31 = "deliveries/archive/milestones/milestone31r_business_feedback_loop/milestone31r_business_feedback_loop_package_v1.json"
DEFAULT_FEEDBACK_INPUT = "configs/execution_batches/milestone31r_business_feedback_collection_template_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone32r_feedback_quality_validation"
DEFAULT_COLLECTION_TEMPLATE = "configs/execution_batches/milestone32r_business_feedback_collection_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 32R-业务反馈采集与质量验证闭环-v1.md"

ALLOWED_WORTH_FOLLOWING = {"yes", "no", "unclear"}
ALLOWED_RECOMMENDED_ACTIONS = {
    "advance_to_l2_research",
    "sales_review",
    "keep_l3_monitoring",
    "disqualify",
    "needs_more_context",
}
ALLOWED_OBSERVATION_TYPES = {"candidate_observation", "source_gap", "rule_calibration_proposal"}
FORBIDDEN_WRITE_KEYS = {
    "knowledge_assets",
    "knowledge_assets_write",
    "customer_case",
    "customer_case_write",
    "persona_registry",
    "persona_registry_write",
    "persona_positive_example",
    "persona_negative_example",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M32R business feedback collection and quality validation package.")
    parser.add_argument("--m31-package", default=DEFAULT_M31)
    parser.add_argument("--feedback-input", default=DEFAULT_FEEDBACK_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--collection-template", default=DEFAULT_COLLECTION_TEMPLATE)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _items_by_id(items: list[Any]) -> dict[str, dict[str, Any]]:
    return {
        _clean(item.get("account_id")): item
        for item in items
        if isinstance(item, dict) and _clean(item.get("account_id"))
    }


def _feedback_fields(item: dict[str, Any]) -> dict[str, Any]:
    fields = item.get("business_feedback_fields") if isinstance(item.get("business_feedback_fields"), dict) else {}
    return {
        "business_fit_rating": _clean(fields.get("business_fit_rating")),
        "worth_following": _clean(fields.get("worth_following")).lower(),
        "recommended_next_action": _clean(fields.get("recommended_next_action")),
        "target_scenario": _clean(fields.get("target_scenario")),
        "disqualify_reason": _clean(fields.get("disqualify_reason")),
        "feedback_notes": _clean(fields.get("feedback_notes")),
        "feedback_owner": _clean(fields.get("feedback_owner")),
        "feedback_date": _clean(fields.get("feedback_date")),
    }


def _is_reviewed(fields: dict[str, str]) -> bool:
    return bool(fields["business_fit_rating"] or fields["worth_following"] or fields["recommended_next_action"])


def _validate_fields(fields: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if fields["business_fit_rating"]:
        try:
            rating = int(fields["business_fit_rating"])
        except ValueError:
            errors.append("business_fit_rating_not_integer")
        else:
            if rating < 1 or rating > 5:
                errors.append("business_fit_rating_out_of_range")
    if fields["worth_following"] and fields["worth_following"] not in ALLOWED_WORTH_FOLLOWING:
        errors.append("worth_following_invalid")
    if fields["recommended_next_action"] and fields["recommended_next_action"] not in ALLOWED_RECOMMENDED_ACTIONS:
        errors.append("recommended_next_action_invalid")
    if fields["worth_following"] == "no" and not fields["disqualify_reason"]:
        errors.append("disqualify_reason_required_when_no")
    return errors


def _review_outcome(fields: dict[str, str], errors: list[str]) -> str:
    if errors:
        return "invalid_feedback"
    if not _is_reviewed(fields):
        return "pending"
    if fields["worth_following"] == "yes":
        return "accepted"
    if fields["worth_following"] == "no":
        return "rejected"
    if fields["worth_following"] == "unclear" or fields["recommended_next_action"] == "needs_more_context":
        return "unclear"
    return "reviewed_unclassified"


def _base_item(source: dict[str, Any], feedback_input: dict[str, Any]) -> dict[str, Any]:
    merged = {**source, **{k: v for k, v in feedback_input.items() if k not in {"business_feedback_fields"}}}
    fields = _feedback_fields(feedback_input if feedback_input else source)
    errors = _validate_fields(fields)
    outcome = _review_outcome(fields, errors)
    return {
        "account_id": _clean(merged.get("account_id")),
        "company_name": _clean(merged.get("company_name")),
        "matched_track": _clean(merged.get("matched_track")),
        "matched_persona": _clean(merged.get("matched_persona")),
        "why_it_matches": _clean(merged.get("why_it_matches")),
        "core_product_or_service": _clean(merged.get("core_product_or_service")),
        "business_model": _clean(merged.get("business_model")),
        "primary_evidence_locator": _clean(merged.get("primary_evidence_locator")),
        "business_feedback_fields": fields,
        "feedback_status": "reviewed" if outcome in {"accepted", "rejected", "unclear", "reviewed_unclassified"} else outcome,
        "review_outcome": outcome,
        "validation_errors": errors,
        "knowledge_asset_boundary_note": "业务反馈只能用于候选观察、source gap 和规则校准建议，不能直接写入正式知识资产。",
    }


def _collection_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": item["account_id"],
        "company_name": item["company_name"],
        "matched_track": item["matched_track"],
        "matched_persona": item["matched_persona"],
        "why_it_matches": item["why_it_matches"],
        "core_product_or_service": item["core_product_or_service"],
        "business_model": item["business_model"],
        "primary_evidence_locator": item["primary_evidence_locator"],
        "business_feedback_fields": {
            "business_fit_rating": item["business_feedback_fields"]["business_fit_rating"],
            "worth_following": item["business_feedback_fields"]["worth_following"],
            "recommended_next_action": item["business_feedback_fields"]["recommended_next_action"],
            "target_scenario": item["business_feedback_fields"]["target_scenario"],
            "disqualify_reason": item["business_feedback_fields"]["disqualify_reason"],
            "feedback_notes": item["business_feedback_fields"]["feedback_notes"],
        },
    }


def _candidate_observation(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "observation_id": f"m32r_obs_{item['account_id']}_{item['review_outcome']}_v1",
        "observation_type": "candidate_observation",
        "account_id": item["account_id"],
        "company_name": item["company_name"],
        "persona": item["matched_persona"],
        "track": item["matched_track"],
        "feedback_status": item["feedback_status"],
        "review_outcome": item["review_outcome"],
        "observation_summary": "该潜客处于 M32R 业务反馈采集闭环；反馈结果只用于潜客池质量验证和规则校准建议。",
        "formal_knowledge_source_allowed": False,
    }


def _source_gap(persona: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = Counter(item["review_outcome"] for item in items)
    return {
        "gap_id": f"m32r_gap_{persona}_feedback_quality_v1",
        "gap_type": "source_gap",
        "persona": persona,
        "sample_count": len(items),
        "review_outcome_counts": dict(outcomes),
        "task_summary": "需要更多业务反馈或真实素材验证该画像下候选是否稳定可消费。",
        "formal_knowledge_source_allowed": False,
        "queue_status": "open",
    }


def _rule_proposal(persona: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = Counter(item["review_outcome"] for item in items)
    return {
        "proposal_id": f"m32r_rule_{persona}_quality_threshold_v1",
        "proposal_type": "rule_calibration_proposal",
        "persona": persona,
        "sample_count": len(items),
        "review_outcome_counts": dict(outcomes),
        "proposal_summary": "基于业务反馈采集结果，为后续 M33R 扩容质量阈值提供校准输入；不得直接修改正式画像规则。",
        "status": "pending_feedback" if outcomes.get("pending") else "feedback_analyzed",
        "formal_rule_change_allowed": False,
    }


def _contains_forbidden_write_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(key in FORBIDDEN_WRITE_KEYS for key in payload) or any(_contains_forbidden_write_key(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_contains_forbidden_write_key(item) for item in payload)
    return False


def _acceptance_by_persona(items: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[item["matched_persona"]].append(item)
    out: dict[str, Any] = {}
    for persona, rows in sorted(grouped.items()):
        reviewed = [row for row in rows if row["review_outcome"] in {"accepted", "rejected", "unclear", "reviewed_unclassified"}]
        accepted = [row for row in rows if row["review_outcome"] == "accepted"]
        out[persona] = {
            "sample_count": len(rows),
            "reviewed_count": len(reviewed),
            "accepted_count": len(accepted),
            "acceptance_rate": (len(accepted) / len(reviewed)) if reviewed else None,
            "outcome_counts": dict(Counter(row["review_outcome"] for row in rows)),
        }
    return out


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 32R-业务反馈采集与质量验证闭环-v1",
        "",
        "## 摘要",
        "",
        f"- 抽样对象：`{summary['sample_count']}`",
        f"- 已反馈：`{summary['business_reviewed_count']}`",
        f"- 待反馈：`{summary['pending_feedback_count']}`",
        f"- accepted/rejected/unclear：`{summary['accepted_count']} / {summary['rejected_count']} / {summary['unclear_count']}`",
        f"- 校验错误：`{summary['validation_error_count']}`",
        f"- no-write proof：`{summary['no_write_proof_ok']}`",
        "",
        "## 结论",
        "",
        "- M32R 不伪造业务反馈；空反馈保持 pending。",
        "- 本包不写工作簿、不写正式知识资产、不修改画像注册表。",
        "- 当模板被业务侧填写后，重跑本脚本即可生成 accepted/rejected/unclear 统计和规则校准建议。",
        "",
        "## 反馈采集对象",
        "",
    ]
    for item in payload["feedback_items"]:
        lines.extend(
            [
                f"### {item['company_name']}（{item['account_id']}）",
                "",
                f"- 主线/画像：`{item['matched_track']}` / `{item['matched_persona']}`",
                f"- 反馈状态：`{item['feedback_status']}`，结果：`{item['review_outcome']}`",
                f"- 为什么匹配：{item['why_it_matches']}",
                f"- 关键 evidence：{item['primary_evidence_locator']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    m31 = _load_json(args.m31_package)
    feedback_input = _load_json(args.feedback_input)
    source_items = m31.get("feedback_items") or []
    input_by_id = _items_by_id(feedback_input.get("feedback_items") or [])
    items = [_base_item(item, input_by_id.get(_clean(item.get("account_id")), {})) for item in source_items if isinstance(item, dict)]
    collection_items = [_collection_item(item) for item in items]
    observations = [_candidate_observation(item) for item in items]

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[item["matched_persona"]].append(item)
    source_gaps = [_source_gap(persona, rows) for persona, rows in sorted(grouped.items())]
    rule_proposals = [_rule_proposal(persona, rows) for persona, rows in sorted(grouped.items())]

    outcome_counts = Counter(item["review_outcome"] for item in items)
    action_counts = Counter(item["business_feedback_fields"]["recommended_next_action"] for item in items if item["business_feedback_fields"]["recommended_next_action"])
    disqualify_counts = Counter(item["business_feedback_fields"]["disqualify_reason"] for item in items if item["business_feedback_fields"]["disqualify_reason"])
    validation_errors = [error for item in items for error in item["validation_errors"]]
    reviewed_count = sum(outcome_counts[key] for key in ("accepted", "rejected", "unclear", "reviewed_unclassified"))
    no_write_proof = {
        "formal_knowledge_write_enabled": False,
        "true_writeback_enabled": False,
        "knowledge_assets_write_package_generated": False,
        "persona_registry_write_package_generated": False,
        "all_observations_non_formal_source": all(item["formal_knowledge_source_allowed"] is False for item in observations),
        "all_source_gaps_non_formal_source": all(item["formal_knowledge_source_allowed"] is False for item in source_gaps),
        "observation_types_allowed": {item["observation_type"] for item in observations} <= ALLOWED_OBSERVATION_TYPES,
        "forbidden_write_keys_detected": False,
    }
    scan_payload = {
        "feedback_items": items,
        "candidate_observations": observations,
        "source_gaps": source_gaps,
        "rule_proposals": rule_proposals,
    }
    no_write_proof["forbidden_write_keys_detected"] = _contains_forbidden_write_key(scan_payload)
    no_write_proof["ok"] = (
        no_write_proof["formal_knowledge_write_enabled"] is False
        and no_write_proof["true_writeback_enabled"] is False
        and no_write_proof["knowledge_assets_write_package_generated"] is False
        and no_write_proof["persona_registry_write_package_generated"] is False
        and no_write_proof["all_observations_non_formal_source"]
        and no_write_proof["all_source_gaps_non_formal_source"]
        and no_write_proof["observation_types_allowed"]
        and not no_write_proof["forbidden_write_keys_detected"]
    )
    summary = {
        "sample_count": len(items),
        "business_reviewed_count": reviewed_count,
        "pending_feedback_count": int(outcome_counts.get("pending") or 0),
        "accepted_count": int(outcome_counts.get("accepted") or 0),
        "rejected_count": int(outcome_counts.get("rejected") or 0),
        "unclear_count": int(outcome_counts.get("unclear") or 0),
        "invalid_feedback_count": int(outcome_counts.get("invalid_feedback") or 0),
        "validation_error_count": len(validation_errors),
        "outcome_counts": dict(outcome_counts),
        "persona_acceptance": _acceptance_by_persona(items),
        "recommended_next_action_counts": dict(action_counts),
        "disqualify_reason_counts": dict(disqualify_counts),
        "candidate_observation_count": len(observations),
        "source_gap_count": len(source_gaps),
        "rule_calibration_proposal_count": len(rule_proposals),
        "no_write_proof_ok": bool(no_write_proof["ok"]),
        "formal_knowledge_write_enabled": False,
        "true_writeback_enabled": False,
    }
    payload = {
        "batch_id": "milestone32r_feedback_quality_validation_package_v1",
        "generated_at": _now(),
        "source_files": {
            "m31_package": args.m31_package,
            "feedback_input": args.feedback_input,
        },
        "policy": {
            "true_writeback_enabled": False,
            "formal_knowledge_write_enabled": False,
            "not_customer_case": True,
            "not_persona_registry_update": True,
            "empty_feedback_is_pending": True,
        },
        "summary": summary,
        "feedback_items": items,
        "feedback_collection_view": collection_items,
        "candidate_observation_package": observations,
        "source_gap_queue": source_gaps,
        "rule_calibration_proposal": rule_proposals,
        "knowledge_asset_no_write_proof": no_write_proof,
    }
    template = {
        "batch_id": "milestone32r_business_feedback_collection_template_v1",
        "generated_at": _now(),
        "source_file": str(Path(args.output_dir) / "milestone32r_feedback_quality_validation_package_v1.json"),
        "allowed_worth_following_values": sorted(ALLOWED_WORTH_FOLLOWING),
        "allowed_recommended_next_actions": sorted(ALLOWED_RECOMMENDED_ACTIONS),
        "feedback_items": collection_items,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone32r_feedback_quality_validation_package_v1.json", payload)
    _write_json(output_dir / "milestone32r_feedback_collection_view_v1.json", {"batch_id": "milestone32r_feedback_collection_view_v1", "items": collection_items})
    _write_json(output_dir / "milestone32r_feedback_analysis_v1.json", {"batch_id": "milestone32r_feedback_analysis_v1", "summary": summary, "items": items})
    _write_json(output_dir / "milestone32r_candidate_observation_package_v1.json", {"batch_id": "milestone32r_candidate_observation_package_v1", "items": observations})
    _write_json(output_dir / "milestone32r_source_gap_queue_v1.json", {"batch_id": "milestone32r_source_gap_queue_v1", "items": source_gaps})
    _write_json(output_dir / "milestone32r_rule_calibration_proposal_v1.json", {"batch_id": "milestone32r_rule_calibration_proposal_v1", "items": rule_proposals})
    _write_json(output_dir / "milestone32r_knowledge_asset_no_write_proof_v1.json", no_write_proof)
    _write_json(args.collection_template, template)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone32r_feedback_quality_validation_package_v1.json"), "collection_template": args.collection_template, "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = (
        summary["sample_count"] == 15
        and summary["no_write_proof_ok"]
        and not summary["formal_knowledge_write_enabled"]
        and not summary["true_writeback_enabled"]
        and summary["validation_error_count"] == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
