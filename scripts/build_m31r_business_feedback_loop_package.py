from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_M30 = "deliveries/archive/milestones/milestone30r_post_writeback_consumption_review/milestone30r_post_writeback_consumption_review_package_v1.json"
DEFAULT_TEMPLATE = "configs/execution_batches/milestone30r_post_writeback_business_review_template_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone31r_business_feedback_loop"
DEFAULT_FEEDBACK_TEMPLATE = "configs/execution_batches/milestone31r_business_feedback_collection_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 31R-业务反馈闭环与规则校准建议-v1.md"

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
    parser = argparse.ArgumentParser(description="Build M31R business feedback loop package without formal knowledge writes.")
    parser.add_argument("--m30-package", default=DEFAULT_M30)
    parser.add_argument("--m30-template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--feedback-template", default=DEFAULT_FEEDBACK_TEMPLATE)
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


def _feedback_fields(item: dict[str, Any]) -> dict[str, Any]:
    fields = item.get("business_feedback_fields") if isinstance(item.get("business_feedback_fields"), dict) else {}
    return fields


def _is_reviewed(item: dict[str, Any]) -> bool:
    fields = _feedback_fields(item)
    return bool(_clean(fields.get("worth_following")) or _clean(fields.get("business_fit_rating")) or _clean(fields.get("recommended_next_action")))


def _feedback_item(item: dict[str, Any]) -> dict[str, Any]:
    fields = _feedback_fields(item)
    reviewed = _is_reviewed(item)
    return {
        "account_id": _clean(item.get("account_id")),
        "company_name": _clean(item.get("company_name")),
        "matched_track": _clean(item.get("matched_track")),
        "matched_persona": _clean(item.get("matched_persona")),
        "sample_reason": _clean(item.get("sample_reason")),
        "business_question": "该公司是否值得按当前画像进入后续经营、L2 深研或销售复核？",
        "why_it_matches": _clean(item.get("why_it_matches")),
        "core_product_or_service": _clean(item.get("core_product_or_service")),
        "business_model": _clean(item.get("business_model")),
        "primary_evidence_locator": _clean(item.get("primary_evidence_locator")),
        "feedback_status": "reviewed" if reviewed else "pending_business_feedback",
        "business_feedback_fields": fields,
        "knowledge_asset_boundary_note": "该反馈只能作为潜客观察和规则校准输入，不能直接成为正式知识资产或画像正例。",
    }


def _candidate_observation(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "observation_id": f"m31r_obs_{item['account_id']}_business_feedback_pending_v1",
        "observation_type": "candidate_observation",
        "account_id": item["account_id"],
        "company_name": item["company_name"],
        "persona": item["matched_persona"],
        "track": item["matched_track"],
        "observation_summary": "该潜客已完成 L3 写回并进入业务抽样评估；业务反馈尚未填写，不能作为正式客户案例或画像正例。",
        "feedback_status": item["feedback_status"],
        "formal_knowledge_source_allowed": False,
        "allowed_downstream": ["business_feedback_collection", "source_gap", "rule_calibration_proposal"],
        "forbidden_downstream": ["knowledge_assets", "customer_case", "persona_registry_direct_update"],
    }


def _source_gap(persona: str, count: int) -> dict[str, Any]:
    return {
        "gap_id": f"m31r_gap_{persona}_business_feedback_v1",
        "gap_type": "source_gap",
        "persona": persona,
        "sample_count": count,
        "task_summary": "需要业务侧反馈该画像下抽样潜客是否值得继续经营；反馈结果只能用于校准建议，不能直接写入正式知识资产。",
        "required_inputs": ["worth_following", "recommended_next_action", "business_fit_rating", "disqualify_reason_if_any"],
        "formal_knowledge_source_allowed": False,
        "queue_status": "open",
    }


def _rule_proposal(persona: str, count: int) -> dict[str, Any]:
    return {
        "proposal_id": f"m31r_rule_{persona}_feedback_calibration_v1",
        "proposal_type": "rule_calibration_proposal",
        "persona": persona,
        "sample_count": count,
        "proposal_summary": "该画像已有写回后抽样对象；待业务反馈后，可形成候选选择、优先级或淘汰规则建议。正式画像规则变更仍需真实客户案例/解决方案/权威材料验证。",
        "status": "pending_business_feedback",
        "formal_rule_change_allowed": False,
    }


def _contains_forbidden_write_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(key in FORBIDDEN_WRITE_KEYS for key in payload) or any(_contains_forbidden_write_key(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_contains_forbidden_write_key(item) for item in payload)
    return False


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 31R-业务反馈闭环与规则校准建议-v1",
        "",
        "## 摘要",
        "",
        f"- 抽样反馈对象：`{summary['sample_count']}`",
        f"- 已反馈：`{summary['business_reviewed_count']}`",
        f"- 待反馈：`{summary['pending_business_feedback_count']}`",
        f"- 候选观察：`{summary['candidate_observation_count']}`",
        f"- source gap：`{summary['source_gap_count']}`",
        f"- 规则校准建议：`{summary['rule_calibration_proposal_count']}`",
        f"- no-write proof：`{summary['no_write_proof_ok']}`",
        "",
        "## 结论",
        "",
        "- M31R 不伪造业务反馈；当前 15 家抽样对象均等待业务侧填写。",
        "- 本包只生成反馈采集结构、候选观察、source gap 和规则校准建议。",
        "- 潜客反馈不能直接改写正式知识资产或画像注册表。",
        "",
        "## 反馈对象",
        "",
    ]
    for item in payload["feedback_items"]:
        lines.extend(
            [
                f"### {item['company_name']}（{item['account_id']}）",
                "",
                f"- 主线/画像：`{item['matched_track']}` / `{item['matched_persona']}`",
                f"- 状态：`{item['feedback_status']}`",
                f"- 为什么匹配：{item['why_it_matches']}",
                f"- 关键 evidence：{item['primary_evidence_locator']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    m30 = _load_json(args.m30_package)
    m30_template = _load_json(args.m30_template)
    template_items = m30_template.get("sample_review_items") or m30.get("sample_review_items") or []
    feedback_items = [_feedback_item(item) for item in template_items if isinstance(item, dict)]
    observations = [_candidate_observation(item) for item in feedback_items]

    persona_counts = Counter(item["matched_persona"] for item in feedback_items)
    source_gaps = [_source_gap(persona, count) for persona, count in sorted(persona_counts.items())]
    rule_proposals = [_rule_proposal(persona, count) for persona, count in sorted(persona_counts.items())]
    reviewed_count = sum(1 for item in feedback_items if item["feedback_status"] == "reviewed")
    pending_count = len(feedback_items) - reviewed_count
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
    generated_for_scan = {
        "feedback_items": feedback_items,
        "candidate_observations": observations,
        "source_gaps": source_gaps,
        "rule_proposals": rule_proposals,
    }
    no_write_proof["forbidden_write_keys_detected"] = _contains_forbidden_write_key(generated_for_scan)
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
        "sample_count": len(feedback_items),
        "business_reviewed_count": reviewed_count,
        "pending_business_feedback_count": pending_count,
        "candidate_observation_count": len(observations),
        "source_gap_count": len(source_gaps),
        "rule_calibration_proposal_count": len(rule_proposals),
        "persona_counts": dict(persona_counts),
        "feedback_status_counts": dict(Counter(item["feedback_status"] for item in feedback_items)),
        "no_write_proof_ok": bool(no_write_proof["ok"]),
        "formal_knowledge_write_enabled": False,
        "true_writeback_enabled": False,
    }
    payload = {
        "batch_id": "milestone31r_business_feedback_loop_package_v1",
        "generated_at": _now(),
        "source_files": {
            "m30_package": args.m30_package,
            "m30_template": args.m30_template,
        },
        "policy": {
            "true_writeback_enabled": False,
            "formal_knowledge_write_enabled": False,
            "not_customer_case": True,
            "not_persona_registry_update": True,
            "correct_flow": "business_feedback -> candidate_observation/source_gap/rule_calibration_proposal -> real material validation -> human review -> formal knowledge asset",
        },
        "summary": summary,
        "feedback_items": feedback_items,
        "candidate_observation_package": observations,
        "source_gap_queue": source_gaps,
        "rule_calibration_proposal": rule_proposals,
        "knowledge_asset_no_write_proof": no_write_proof,
    }
    feedback_template = {
        "batch_id": "milestone31r_business_feedback_collection_template_v1",
        "generated_at": _now(),
        "source_file": str(Path(args.output_dir) / "milestone31r_business_feedback_loop_package_v1.json"),
        "allowed_worth_following_values": ["yes", "no", "unclear"],
        "allowed_recommended_next_actions": [
            "advance_to_l2_research",
            "sales_review",
            "keep_l3_monitoring",
            "disqualify",
            "needs_more_context",
        ],
        "feedback_items": feedback_items,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone31r_business_feedback_loop_package_v1.json", payload)
    _write_json(output_dir / "milestone31r_candidate_observation_package_v1.json", {"batch_id": "milestone31r_candidate_observation_package_v1", "items": observations})
    _write_json(output_dir / "milestone31r_source_gap_queue_v1.json", {"batch_id": "milestone31r_source_gap_queue_v1", "items": source_gaps})
    _write_json(output_dir / "milestone31r_rule_calibration_proposal_v1.json", {"batch_id": "milestone31r_rule_calibration_proposal_v1", "items": rule_proposals})
    _write_json(output_dir / "milestone31r_knowledge_asset_no_write_proof_v1.json", no_write_proof)
    _write_json(args.feedback_template, feedback_template)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone31r_business_feedback_loop_package_v1.json"), "feedback_template": args.feedback_template, "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["sample_count"] == 15 and summary["no_write_proof_ok"] and not summary["true_writeback_enabled"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
