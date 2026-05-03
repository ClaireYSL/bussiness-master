from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIRMATION = "deliveries/archive/milestones/milestone27r_m25r_persona_confirmation/milestone27r_m25r_persona_confirmation_package_v1.json"
DEFAULT_SOURCE_FACTS = "configs/execution_batches/milestone25r_trusted_expansion_facts_v1.json"
DEFAULT_SOURCE_CANDIDATES = "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_candidates_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone28r_m25r_promote_admission"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 28R-M25R二次promote准入试运行复盘-v1.md"

BATCH_ID = "milestone28r_m25r_promote_admission_v1"
TODAY = "2026-04-27"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M28R non-writeback promote admission package from M27R recommendations.")
    parser.add_argument("--confirmation-file", default=DEFAULT_CONFIRMATION)
    parser.add_argument("--source-facts-file", default=DEFAULT_SOURCE_FACTS)
    parser.add_argument("--source-candidate-file", default=DEFAULT_SOURCE_CANDIDATES)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


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


def _accounts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in (payload.get("accounts") or payload.get("results") or []) if isinstance(item, dict)]


def _ready_items(confirmation: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in confirmation.get("confirmation_items") or []
        if isinstance(item, dict)
        and _clean(item.get("system_recommendation")) == "confirm_active_candidate"
        and _clean(item.get("account_id"))
    ]


def _active_fact(source: dict[str, Any], confirmation: dict[str, Any]) -> dict[str, Any]:
    fact = copy.deepcopy(source)
    fact["source_milestone"] = "M28R"
    fact["persona_confirmation_source"] = DEFAULT_CONFIRMATION
    fact["persona_confirmation_status"] = "system_recommended_confirm_active_candidate"
    fact["writeback_admission_status"] = "report_only_admission_ready"
    fact["writeback_admission_note"] = "M28R 只做 report-only/gate 准入试跑；真实 promote 写回仍需用户单独确认。"
    note = (
        "M27R 系统建议为 confirm_active_candidate，M28R 仅用于非写回准入试跑；"
        "不得把潜客观察写入正式知识资产，真实写回仍需 gate、baseline 和用户确认。"
    )
    main_fields = fact.get("main_fields") if isinstance(fact.get("main_fields"), dict) else {}
    profile_fields = fact.get("profile_fields") if isinstance(fact.get("profile_fields"), dict) else {}
    rectification = fact.get("rectification") if isinstance(fact.get("rectification"), dict) else {}
    rewrite = rectification.get("rewrite_suggestion") if isinstance(rectification.get("rewrite_suggestion"), dict) else {}
    persona = _clean(confirmation.get("matched_persona") or main_fields.get("persona_tag"))
    track = _clean(confirmation.get("matched_track") or main_fields.get("primary_track"))
    for fields in (main_fields, profile_fields, rewrite):
        fields["primary_track"] = track
        fields["persona_tag"] = persona
        fields["validation_gap"] = note
        fields["review_status"] = "active"
    profile_fields["profile_status"] = "active"
    main_fields["review_status"] = "active"
    rectification["final_candidate_type"] = "formal_candidate"
    rectification["final_review_status"] = "active"
    rectification["suggested_primary_persona"] = persona
    rectification["rectification_action"] = note
    rectification["rewrite_suggestion"] = rewrite
    fact["main_fields"] = main_fields
    fact["profile_fields"] = profile_fields
    fact["rectification"] = rectification
    return fact


def _candidate(source: dict[str, Any], confirmation: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": _clean(confirmation.get("account_id") or source.get("account_id")),
        "track": _clean(confirmation.get("matched_track") or source.get("track")),
        "current_level": _clean(source.get("current_level") or confirmation.get("from_level") or "L5"),
        "target_level": _clean(source.get("target_level") or confirmation.get("target_level") or "L3"),
        "candidate_type": "formal_candidate",
        "persona_tag": _clean(confirmation.get("matched_persona")),
        "confirmation_status": "system_recommended_confirm_active_candidate",
        "selection_reason": "M27R 系统建议 confirm_active_candidate；M28R 仅执行非写回 report-only/gate 准入试跑。",
    }


def _queue(fact: dict[str, Any]) -> dict[str, str]:
    return {
        "account_id": _clean(fact.get("account_id")),
        "account_name": _clean(fact.get("account_name")),
        "queue_type": "promotion_review",
        "priority": "P1",
        "status": "open",
        "owner": "codex",
        "note": "M28R report-only 准入试跑候选；真实 promote 写回需用户单独确认。",
        "created_at": TODAY,
    }


def _enrich_config(fact_patch_file: str, output_dir: Path) -> dict[str, Any]:
    return {
        "batch_id": "milestone28r_m25r_promote_admission_enrich_v1",
        "goal": "Milestone 28R：M25R 二次 promote 准入 enrich 复核",
        "from_level": "L5",
        "target_level": "L3",
        "promote_target_level": "L3",
        "write_back": False,
        "workbook_lock_timeout_seconds": 0.0,
        "rectification_file": fact_patch_file,
        "source_policy": "M28R 使用 M27R 画像确认建议和 M25R 结构化事实；不写入知识资产，不真实写回。",
        "output": {
            "enrich_file": str(output_dir / "milestone28r_m25r_promote_admission_enrich_v1.json"),
            "summary_file": str(output_dir / "milestone28r_m25r_promote_admission_enrich_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 28R-M25R二次promote准入-enrich复盘-v1.md",
        },
        "account_ids": [],
    }


def _promote_config(fact_patch_file: str, queue_patch_file: str, output_dir: Path) -> dict[str, Any]:
    return {
        "batch_id": "milestone28r_m25r_promote_admission_promote_v1",
        "goal": "Milestone 28R：M25R 二次 promote 准入 report-only",
        "account_ids": [],
        "from_level": "L5",
        "target_level": "L3",
        "auto_open_promotion_review_for_selected": True,
        "workbook_lock_timeout_seconds": 0.0,
        "write_back": False,
        "limit": 9999,
        "enrich_result_file": str(output_dir / "milestone28r_m25r_promote_admission_enrich_v1.json"),
        "fact_patch_file": fact_patch_file,
        "queue_patch_file": queue_patch_file,
        "output_file": str(output_dir / "milestone28r_m25r_promote_admission_promote_v1.json"),
        "summary_file": str(output_dir / "milestone28r_m25r_promote_admission_summary_v1.json"),
        "review_file": "docs/03-执行与校验/Milestone 28R-M25R二次promote准入-promote复盘-v1.md",
    }


def _registry(candidate_file: str, fact_patch_file: str, queue_patch_file: str, output_dir: Path) -> dict[str, Any]:
    return {
        "milestone_id": "milestone28r_m25r_promote_admission",
        "batch_id": BATCH_ID,
        "goal": "Milestone 28R：M25R 二次 promote 准入试运行",
        "candidate_file": candidate_file,
        "fact_patch_file": fact_patch_file,
        "queue_patch_file": queue_patch_file,
        "enrich": {
            "config_file": "configs/enrich_batches/milestone28r_m25r_promote_admission_enrich_v1.json",
            "output_file": str(output_dir / "milestone28r_m25r_promote_admission_enrich_v1.json"),
            "summary_file": str(output_dir / "milestone28r_m25r_promote_admission_enrich_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 28R-M25R二次promote准入-enrich复盘-v1.md",
        },
        "promote": {
            "config_file": "configs/promote_batches/milestone28r_m25r_promote_admission_promote_v1.json",
            "output_file": str(output_dir / "milestone28r_m25r_promote_admission_promote_v1.json"),
            "summary_file": str(output_dir / "milestone28r_m25r_promote_admission_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 28R-M25R二次promote准入-promote复盘-v1.md",
        },
        "run_output": {
            "summary_file": str(output_dir / "milestone28r_m25r_promote_admission_run_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 28R-M25R二次promote准入最终复盘-v1.md",
            "report_baseline_file": str(output_dir / "milestone28r_m25r_promote_admission_report_baseline_v1.json"),
        },
        "mode_policy": {
            "default_phase": "report_only",
            "require_report_baseline": True,
            "write_back_after_report_only": False,
        },
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 28R-M25R二次promote准入试运行复盘-v1",
        "",
        "## 摘要",
        "",
        f"- M27R confirm active 系统建议：`{summary['confirm_active_input_count']}`",
        f"- 准入候选：`{summary['admission_candidate_count']}`",
        f"- report-only：`allow={summary.get('report_only_allow', 0)} / warn={summary.get('report_only_warn', 0)} / block={summary.get('report_only_block', 0)}`",
        f"- gate check：`{'PASS' if summary.get('gate_ok') else 'PENDING'}`",
        "- 本轮真实写回：`false`",
        "",
        "M28R 是准入试跑，不是写回动作。若后续要真实 promote 写回，仍需用户单独确认。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    confirmation = _load_json(args.confirmation_file)
    source_facts = _load_json(args.source_facts_file)
    source_candidates = _load_json(args.source_candidate_file)
    ready = _ready_items(confirmation)
    facts_by_id = _items_by_id(_accounts(source_facts))
    candidates_by_id = _items_by_id(source_candidates.get("accounts") or [])

    facts: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    queues: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for item in ready:
        account_id = _clean(item.get("account_id"))
        source_fact = facts_by_id.get(account_id)
        if not source_fact:
            skipped.append({"account_id": account_id, "reason": "source_fact_missing"})
            continue
        fact = _active_fact(source_fact, item)
        facts.append(fact)
        candidates.append(_candidate(candidates_by_id.get(account_id, {}), item))
        queues.append(_queue(fact))

    candidate_file = output_dir / "milestone28r_m25r_promote_admission_candidates_v1.json"
    fact_file = Path("configs/execution_batches/milestone28r_m25r_promote_admission_facts_v1.json")
    queue_file = Path("configs/execution_batches/milestone28r_m25r_promote_admission_queue_v1.json")
    enrich_file = Path("configs/enrich_batches/milestone28r_m25r_promote_admission_enrich_v1.json")
    promote_file = Path("configs/promote_batches/milestone28r_m25r_promote_admission_promote_v1.json")
    registry_file = Path("configs/execution_batches/milestone28r_m25r_promote_admission_registry_v1.json")
    package_file = output_dir / "milestone28r_m25r_promote_admission_package_v1.json"

    run_summary = _load_json(output_dir / "milestone28r_m25r_promote_admission_run_summary_v1.json")
    promote_payload = _load_json(output_dir / "milestone28r_m25r_promote_admission_promote_v1.json")
    gate_payload = _load_json("deliveries/archive/repairs/milestone28r_m25r_promote_admission_gate_check_v1.json")
    batch_summary = promote_payload.get("batch_summary") if isinstance(promote_payload.get("batch_summary"), dict) else {}
    now = _now()
    summary = {
        "confirm_active_input_count": len(ready),
        "admission_candidate_count": len(candidates),
        "fact_patch_count": len(facts),
        "queue_patch_count": len(queues),
        "skipped_count": len(skipped),
        "persona_counts": dict(Counter(_clean(item.get("matched_persona")) for item in ready)),
        "track_counts": dict(Counter(_clean(item.get("matched_track")) for item in ready)),
        "report_only_allow": int(batch_summary.get("allow") or 0),
        "report_only_warn": int(batch_summary.get("warn") or 0),
        "report_only_block": int(batch_summary.get("block") or 0),
        "report_only_result_count": int(promote_payload.get("result_count") or 0),
        "gate_ok": bool(gate_payload.get("ok")),
        "true_writeback_enabled": False,
        "formal_knowledge_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone28r_m25r_promote_admission_package_v1",
        "generated_at": now,
        "source_files": {
            "confirmation_file": args.confirmation_file,
            "source_facts_file": args.source_facts_file,
            "source_candidate_file": args.source_candidate_file,
            "run_summary_file": str(output_dir / "milestone28r_m25r_promote_admission_run_summary_v1.json"),
            "promote_file": str(output_dir / "milestone28r_m25r_promote_admission_promote_v1.json"),
            "gate_file": "deliveries/archive/repairs/milestone28r_m25r_promote_admission_gate_check_v1.json",
        },
        "policy": {
            "true_writeback_enabled": False,
            "formal_knowledge_write_enabled": False,
            "requires_user_confirmation_before_real_writeback": True,
        },
        "summary": summary,
        "admission_candidates": candidates,
        "skipped": skipped,
    }
    _write_json(candidate_file, {"batch_id": "milestone28r_m25r_promote_admission_candidates_v1", "generated_at": now, "accounts": candidates})
    _write_json(fact_file, {"batch_id": "milestone28r_m25r_promote_admission_facts_v1", "generated_at": now, "results": facts, "accounts": facts})
    _write_json(queue_file, {"batch_id": "milestone28r_m25r_promote_admission_queue_v1", "generated_at": now, "accounts": queues})
    _write_json(enrich_file, _enrich_config(str(fact_file), output_dir))
    _write_json(promote_file, _promote_config(str(fact_file), str(queue_file), output_dir))
    _write_json(registry_file, _registry(str(candidate_file), str(fact_file), str(queue_file), output_dir))
    _write_json(package_file, payload)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(package_file), "registry_file": str(registry_file), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["admission_candidate_count"] == 50 and not summary["true_writeback_enabled"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
