from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M23R = "deliveries/archive/milestones/milestone23r_trusted_prospect_summary/milestone23r_trusted_prospect_summary_package_v1.json"
DEFAULT_BOUNDARY_DOC = "docs/00-当前总览/BusinessMaster知识资产来源边界与潜客观察隔离原则-v1.md"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone24r_knowledge_source_governance"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 24R-知识资产来源治理与潜客观察隔离复盘-v1.md"

ALLOWED_FORMAL_SOURCE_TYPES = [
    "served_customer_case",
    "internal_solution_material",
    "verified_playbook",
    "industry_research",
    "annual_report",
    "announcement",
    "ir",
    "regulatory_disclosure",
    "human_reviewed_mapping_fact",
]
FORBIDDEN_PROSPECT_SOURCE_TYPES = [
    "trusted_prospect_card",
    "candidate_observation",
    "promote_result",
    "report_only_summary",
    "profile_page_summary",
    "llm_candidate_summary",
]
OBSERVATION_TYPES = {"candidate_observation", "source_gap", "persona_boundary_question", "rule_calibration_proposal"}
FORBIDDEN_WRITE_KEYS = {"knowledge_assets_write", "customer_case_write", "persona_registry_write", "formal_asset_write"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M24R knowledge-source governance package without formal asset writes.")
    parser.add_argument("--trusted-summary-file", default=DEFAULT_M23R)
    parser.add_argument("--boundary-doc", default=DEFAULT_BOUNDARY_DOC)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _observation(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "observation_id": f"m24r_obs_{card['account_id']}_trusted_match_v1",
        "account_id": card["account_id"],
        "company_name": card["company_name"],
        "observation_type": "candidate_observation",
        "persona": card["matched_persona"],
        "track": card["matched_track"],
        "observation_summary": "该潜客与当前画像匹配且公司事实可追溯；该观察不能作为客户案例或画像正例。",
        "source_package": DEFAULT_M23R,
        "formal_knowledge_source_allowed": False,
        "allowed_downstream": ["trusted_prospect_summary", "source_gap", "rule_calibration_proposal"],
        "forbidden_downstream": ["knowledge_assets", "customer_case", "persona_registry_direct_update"],
    }


def _persona_boundary_question(persona: str, track: str, count: int) -> dict[str, Any]:
    return {
        "proposal_id": f"m24r_rule_{persona}_boundary_v1",
        "proposal_type": "rule_calibration_proposal",
        "persona": persona,
        "track": track,
        "candidate_count": count,
        "proposal_summary": "该画像在潜客批次中出现稳定候选，但这只能说明候选匹配；是否调整画像定义必须回到真实客户案例、解决方案或行业权威材料验证。",
        "status": "needs_human_and_source_review",
        "formal_rule_change_allowed": False,
    }


def _source_gap(persona: str, track: str, count: int) -> dict[str, Any]:
    return {
        "gap_id": f"m24r_gap_{persona}_source_v1",
        "gap_type": "source_gap",
        "persona": persona,
        "track": track,
        "candidate_count": count,
        "required_source_types": ["served_customer_case", "internal_solution_material", "industry_research", "verified_playbook"],
        "task_summary": "为该画像补真实客户案例、解决方案或行业材料，用于校准画像定义；不得使用潜客摘要作为正式来源。",
        "queue_status": "open",
        "formal_knowledge_source_allowed": False,
    }


def _learning_queue_task(gap: dict[str, Any]) -> dict[str, Any]:
    return {
        "queue_item_id": f"m24r_lq_{gap['persona']}_v1",
        "queue_type": "learning_source_gap",
        "persona": gap["persona"],
        "track": gap["track"],
        "status": "open",
        "priority": "P1",
        "material_requirement": "寻找真实客户案例、内部解决方案、行业研究或权威公开材料。",
        "forbidden_materials": ["trusted_prospect_card", "candidate_summary", "promote_result", "llm_candidate_summary"],
        "note": gap["task_summary"],
    }


def _contains_forbidden_formal_write(payload: Any) -> bool:
    """Detect generated write-package keys, not policy text listing forbidden concepts."""
    found = False

    def walk(value: Any) -> None:
        nonlocal found
        if found:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key) in FORBIDDEN_WRITE_KEYS:
                    found = True
                    return
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)
    return found


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 24R-知识资产来源治理与潜客观察隔离复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 潜客观察：`{summary['candidate_observation_count']}`",
        f"- source gap：`{summary['source_gap_count']}`",
        f"- 规则校准建议：`{summary['rule_calibration_proposal_count']}`",
        f"- learning queue 补源任务：`{summary['learning_queue_task_count']}`",
        f"- no-write proof：`{summary['no_write_proof_ok']}`",
        "",
        "## 结论",
        "",
        "- 本轮没有生成正式 `knowledge_assets` 写入包。",
        "- 潜客摘要只进入观察、补源和待评审规则建议。",
        "- 任何正式知识资产更新都必须回到真实素材验证和人工评审。",
        "",
        "## 来源边界",
        "",
    ]
    for item in payload["knowledge_source_policy_package"]["forbidden_prospect_sources"]:
        lines.append(f"- 禁用正式来源：`{item}`")
    lines.extend(["", "## 画像补源任务", ""])
    for item in payload["source_gap_queue"]:
        lines.append(f"- `{item['persona']}`：{item['task_summary']}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    trusted_summary = _load_json(args.trusted_summary_file)
    cards = trusted_summary.get("trusted_prospect_cards") or []
    output_dir = Path(args.output_dir)
    now = _now()

    observations = [_observation(card) for card in cards if isinstance(card, dict)]
    grouped: dict[tuple[str, str], int] = defaultdict(int)
    for card in cards:
        if isinstance(card, dict):
            grouped[(_clean(card.get("matched_track")), _clean(card.get("matched_persona")))] += 1
    source_gaps = [_source_gap(persona, track, count) for (track, persona), count in sorted(grouped.items())]
    rule_proposals = [_persona_boundary_question(persona, track, count) for (track, persona), count in sorted(grouped.items())]
    learning_queue = [_learning_queue_task(gap) for gap in source_gaps]

    policy = {
        "package_id": "milestone24r_knowledge_source_policy_package_v1",
        "allowed_formal_source_types": ALLOWED_FORMAL_SOURCE_TYPES,
        "forbidden_prospect_sources": FORBIDDEN_PROSPECT_SOURCE_TYPES,
        "allowed_candidate_outputs": sorted(OBSERVATION_TYPES),
        "formal_knowledge_write_enabled": False,
        "correct_flow": "candidate_observation -> learning_queue source_gap -> real material validation -> human review -> formal knowledge asset",
        "boundary_doc": args.boundary_doc,
    }
    generated_payloads = {
        "policy": policy,
        "observations": observations,
        "source_gaps": source_gaps,
        "rule_proposals": rule_proposals,
        "learning_queue": learning_queue,
    }
    observation_types = {item.get("observation_type") for item in observations} | {"source_gap", "rule_calibration_proposal"}
    no_write_proof = {
        "proof_id": "milestone24r_knowledge_asset_no_write_proof_v1",
        "formal_knowledge_write_enabled": False,
        "knowledge_assets_write_package_generated": False,
        "persona_registry_write_package_generated": False,
        "all_observations_marked_non_formal_source": all(item.get("formal_knowledge_source_allowed") is False for item in observations),
        "all_source_gaps_marked_non_formal_source": all(item.get("formal_knowledge_source_allowed") is False for item in source_gaps),
        "observation_types_allowed": observation_types <= OBSERVATION_TYPES,
        "forbidden_formal_write_keys_detected": _contains_forbidden_formal_write(generated_payloads),
    }
    no_write_proof["ok"] = (
        no_write_proof["formal_knowledge_write_enabled"] is False
        and no_write_proof["knowledge_assets_write_package_generated"] is False
        and no_write_proof["persona_registry_write_package_generated"] is False
        and no_write_proof["all_observations_marked_non_formal_source"]
        and no_write_proof["all_source_gaps_marked_non_formal_source"]
        and no_write_proof["observation_types_allowed"]
        and not no_write_proof["forbidden_formal_write_keys_detected"]
    )
    summary = {
        "candidate_observation_count": len(observations),
        "source_gap_count": len(source_gaps),
        "rule_calibration_proposal_count": len(rule_proposals),
        "learning_queue_task_count": len(learning_queue),
        "persona_counts": dict(Counter(card.get("matched_persona") for card in cards if isinstance(card, dict))),
        "formal_knowledge_write_enabled": False,
        "no_write_proof_ok": bool(no_write_proof["ok"]),
    }
    payload = {
        "batch_id": "milestone24r_knowledge_source_governance_package_v1",
        "generated_at": now,
        "source_files": {"trusted_summary_file": args.trusted_summary_file, "boundary_doc": args.boundary_doc},
        "summary": summary,
        "knowledge_source_policy_package": policy,
        "candidate_observation_package": observations,
        "source_gap_queue": source_gaps,
        "rule_calibration_proposal": rule_proposals,
        "learning_queue_source_gap_tasks": learning_queue,
        "knowledge_asset_no_write_proof": no_write_proof,
    }
    _write_json(output_dir / "milestone24r_knowledge_source_governance_package_v1.json", payload)
    _write_json(output_dir / "milestone24r_knowledge_source_policy_package_v1.json", policy)
    _write_json(output_dir / "milestone24r_candidate_observation_package_v1.json", {"batch_id": "milestone24r_candidate_observation_package_v1", "items": observations})
    _write_json(output_dir / "milestone24r_source_gap_queue_v1.json", {"batch_id": "milestone24r_source_gap_queue_v1", "items": source_gaps})
    _write_json(output_dir / "milestone24r_rule_calibration_proposal_v1.json", {"batch_id": "milestone24r_rule_calibration_proposal_v1", "items": rule_proposals})
    _write_json(output_dir / "milestone24r_knowledge_asset_no_write_proof_v1.json", no_write_proof)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone24r_knowledge_source_governance_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if no_write_proof["ok"] and len(observations) == 30 else 1


if __name__ == "__main__":
    raise SystemExit(main())
