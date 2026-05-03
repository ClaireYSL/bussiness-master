from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M21R = "deliveries/archive/milestones/milestone21r_trusted_match_review/milestone21r_trusted_match_review_package_v1.json"
DEFAULT_M20_FACTS = "configs/execution_batches/milestone20_batch_intake_facts_v1.json"
DEFAULT_M20_CANDIDATES = "deliveries/archive/milestones/milestone20_batch_intake_patch/milestone20_batch_intake_candidates_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone22r_trusted_writeback_admission"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 22R-可信潜客写回准入材料复盘-v1.md"
DEFAULT_GATE = "deliveries/archive/repairs/milestone22r_trusted_writeback_admission_gate_check_v1.json"

BATCH_ID = "milestone22r_trusted_writeback_admission_v1"
TODAY = "2026-04-27"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M22R non-mutating trusted write-back admission package.")
    parser.add_argument("--trusted-review-file", default=DEFAULT_M21R)
    parser.add_argument("--source-facts-file", default=DEFAULT_M20_FACTS)
    parser.add_argument("--source-candidate-file", default=DEFAULT_M20_CANDIDATES)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    parser.add_argument("--gate-file", default=DEFAULT_GATE)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_json_if_exists(path: str | Path) -> dict[str, Any]:
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
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and _clean(item.get("account_id")):
            out[_clean(item.get("account_id"))] = item
    return out


def _source_fact_items(facts: dict[str, Any]) -> list[dict[str, Any]]:
    raw = facts.get("accounts") or facts.get("results") or []
    return [item for item in raw if isinstance(item, dict) and _clean(item.get("account_id"))]


def _ready_review_items(trusted_review: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in trusted_review.get("review_items") or []
        if isinstance(item, dict) and _clean(item.get("trusted_status")) == "trusted_match_ready" and _clean(item.get("account_id"))
    ]


def _candidate_row(source: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": _clean(source.get("account_id") or review.get("account_id")),
        "track": _clean(source.get("track") or review.get("track")),
        "current_level": _clean(source.get("current_level") or source.get("from_level") or review.get("from_level") or "L5"),
        "target_level": _clean(source.get("target_level") or review.get("target_level") or "L3"),
        "candidate_type": "formal_candidate",
        "trusted_status": _clean(review.get("trusted_status")),
        "persona_tag": _clean(review.get("persona")),
        "selection_reason": "M21R 已确认可信画像匹配、核心信息完整、官方来源可追溯；进入 M22R 非写回准入验证。",
    }


def _trusted_validation_gap(review: dict[str, Any]) -> str:
    return (
        "M21R 已确认该公司画像匹配明确、核心公司信息完整、关键 evidence 可追溯；"
        "M22R 仅生成写回准入材料，真实写回仍需 baseline、gate_check、workbook_integrity 和用户单独确认。"
    )


def _promote_ready_fact(source_fact: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    fact = copy.deepcopy(source_fact)
    fact["source_milestone"] = "M22R"
    fact["trusted_status"] = _clean(review.get("trusted_status"))
    fact["trusted_review_source"] = DEFAULT_M21R
    fact["writeback_admission_status"] = "admission_ready_report_only"
    fact["writeback_admission_note"] = "M22R 只做准入验证；不得绕过 gate 和用户确认直接写回。"

    main_fields = fact.get("main_fields") if isinstance(fact.get("main_fields"), dict) else {}
    profile_fields = fact.get("profile_fields") if isinstance(fact.get("profile_fields"), dict) else {}
    rectification = fact.get("rectification") if isinstance(fact.get("rectification"), dict) else {}
    rewrite = rectification.get("rewrite_suggestion") if isinstance(rectification.get("rewrite_suggestion"), dict) else {}

    validation_gap = _trusted_validation_gap(review)
    for fields in (main_fields, profile_fields, rewrite):
        fields["primary_track"] = _clean(review.get("track") or fields.get("primary_track"))
        fields["persona_tag"] = _clean(review.get("persona") or fields.get("persona_tag"))
        fields["validation_gap"] = validation_gap
        fields["review_status"] = "active"
    main_fields["review_status"] = "active"
    profile_fields["profile_status"] = "active"
    rewrite["review_status"] = "active"

    rectification["final_candidate_type"] = "formal_candidate"
    rectification["final_review_status"] = "active"
    rectification["suggested_primary_persona"] = _clean(review.get("persona") or rectification.get("suggested_primary_persona"))
    rectification["rectification_action"] = validation_gap
    rectification["rewrite_suggestion"] = rewrite

    fact["main_fields"] = main_fields
    fact["profile_fields"] = profile_fields
    fact["rectification"] = rectification
    return fact


def _queue_row(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": _clean(fact.get("account_id")),
        "account_name": _clean(fact.get("account_name")),
        "queue_type": "promotion_review",
        "priority": "P1",
        "status": "open",
        "owner": "codex",
        "note": "M22R 可信画像匹配准入材料已生成；真实 write_back 需用户单独确认后由标准执行链路关闭。",
        "created_at": TODAY,
    }


def _base_enrich_config(fact_patch_file: str, output_dir: Path) -> dict[str, Any]:
    return {
        "batch_id": "milestone22r_trusted_writeback_admission_enrich_v1",
        "goal": "Milestone 22R：可信潜客写回准入 enrich 复核",
        "from_level": "L5",
        "target_level": "L3",
        "promote_target_level": "L3",
        "write_back": False,
        "workbook_lock_timeout_seconds": 0.0,
        "rectification_file": fact_patch_file,
        "source_policy": "M22R 仅使用 M21R 可信画像匹配结果、M20 结构化 facts 与强 evidence；不发送原始长文，不直接写回。",
        "output": {
            "enrich_file": str(output_dir / "milestone22r_trusted_writeback_admission_enrich_v1.json"),
            "summary_file": str(output_dir / "milestone22r_trusted_writeback_admission_enrich_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 22R-可信潜客写回准入-enrich复盘-v1.md",
        },
        "account_ids": [],
    }


def _base_promote_config(fact_patch_file: str, queue_patch_file: str, output_dir: Path) -> dict[str, Any]:
    return {
        "batch_id": "milestone22r_trusted_writeback_admission_promote_v1",
        "goal": "Milestone 22R：可信潜客写回准入 promote 复核",
        "account_ids": [],
        "from_level": "L5",
        "target_level": "L3",
        "auto_open_promotion_review_for_selected": True,
        "workbook_lock_timeout_seconds": 0.0,
        "write_back": False,
        "limit": 9999,
        "enrich_result_file": str(output_dir / "milestone22r_trusted_writeback_admission_enrich_v1.json"),
        "fact_patch_file": fact_patch_file,
        "queue_patch_file": queue_patch_file,
        "output_file": str(output_dir / "milestone22r_trusted_writeback_admission_promote_v1.json"),
        "summary_file": str(output_dir / "milestone22r_trusted_writeback_admission_summary_v1.json"),
        "review_file": "docs/03-执行与校验/Milestone 22R-可信潜客写回准入-promote复盘-v1.md",
    }


def _registry(candidate_file: str, fact_patch_file: str, queue_patch_file: str, output_dir: Path) -> dict[str, Any]:
    return {
        "milestone_id": "milestone22r_trusted_writeback_admission",
        "batch_id": BATCH_ID,
        "goal": "Milestone 22R：可信潜客写回准入材料与非写回验证",
        "candidate_file": candidate_file,
        "fact_patch_file": fact_patch_file,
        "queue_patch_file": queue_patch_file,
        "enrich": {
            "config_file": "configs/enrich_batches/milestone22r_trusted_writeback_admission_enrich_v1.json",
            "output_file": str(output_dir / "milestone22r_trusted_writeback_admission_enrich_v1.json"),
            "summary_file": str(output_dir / "milestone22r_trusted_writeback_admission_enrich_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 22R-可信潜客写回准入-enrich复盘-v1.md",
        },
        "promote": {
            "config_file": "configs/promote_batches/milestone22r_trusted_writeback_admission_promote_v1.json",
            "output_file": str(output_dir / "milestone22r_trusted_writeback_admission_promote_v1.json"),
            "summary_file": str(output_dir / "milestone22r_trusted_writeback_admission_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 22R-可信潜客写回准入-promote复盘-v1.md",
        },
        "run_output": {
            "summary_file": str(output_dir / "milestone22r_trusted_writeback_admission_run_summary_v1.json"),
            "review_file": "docs/03-执行与校验/Milestone 22R-可信潜客写回准入最终复盘-v1.md",
            "report_baseline_file": str(output_dir / "milestone22r_trusted_writeback_admission_report_baseline_v1.json"),
        },
        "mode_policy": {
            "default_phase": "report_only",
            "require_report_baseline": True,
            "write_back_after_report_only": False,
        },
    }


def _admission_item(review: dict[str, Any], fact: dict[str, Any]) -> dict[str, Any]:
    card = review.get("trusted_prospect_card") if isinstance(review.get("trusted_prospect_card"), dict) else {}
    return {
        "account_id": _clean(review.get("account_id")),
        "account_name": _clean(review.get("account_name") or fact.get("account_name")),
        "trusted_status": _clean(review.get("trusted_status")),
        "track": _clean(review.get("track")),
        "persona": _clean(review.get("persona")),
        "target_level": _clean(review.get("target_level") or "L3"),
        "writeback_admission": "ready_for_report_only_gate",
        "core_product_or_service": _clean(card.get("core_product_or_service")),
        "match_reason": _clean(card.get("match_reason")),
        "official_source_count": int(review.get("official_source_count") or 0),
        "evidence_count": int(review.get("evidence_count") or 0),
        "risk_or_gap": card.get("risk_or_gap") or [],
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 22R-可信潜客写回准入材料复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 输入可信候选：`{summary['trusted_input_count']}`",
        f"- 写回准入候选：`{summary['admission_candidate_count']}`",
        f"- fact patch：`{summary['fact_patch_count']}`",
        f"- queue patch：`{summary['queue_patch_count']}`",
        f"- 画像分布：`{summary['persona_counts']}`",
        f"- 主线分布：`{summary['track_counts']}`",
        f"- report-only：`allow={summary.get('report_only_allow', 0)} / warn={summary.get('report_only_warn', 0)} / block={summary.get('report_only_block', 0)}`",
        f"- gate check：`{'PASS' if summary.get('gate_ok') else 'PENDING'}`",
        "- 本轮真实写回：`false`",
        "",
        "M22R 的职责是把 M21R 的可信画像匹配结果转成标准执行链路可验证的准入材料。它不是写回动作本身。",
        "",
        "## 准入边界",
        "",
        "- 只有 `trusted_match_ready` 会进入本包。",
        "- 本包会生成 `review_status=active` 的 fact patch，用于 report-only 验证规则是否可放行。",
        "- 真实工作簿写回必须另行获得用户确认，并使用 `--require-report-baseline`、gate check 和 workbook integrity。",
        "",
        "## 候选明细",
        "",
    ]
    for item in payload["admission_items"]:
        lines.append(
            f"- `{item['account_id']}` {item['account_name']}：`{item['track']}` / `{item['persona']}`，证据 `{item['evidence_count']}` 条，官方来源 `{item['official_source_count']}` 个。"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    trusted_review = _load_json(args.trusted_review_file)
    source_facts = _load_json(args.source_facts_file)
    source_candidates = _load_json(args.source_candidate_file)

    ready_reviews = _ready_review_items(trusted_review)
    facts_by_id = _items_by_id(_source_fact_items(source_facts))
    candidates_by_id = _items_by_id(source_candidates.get("accounts") or [])

    candidate_rows: list[dict[str, Any]] = []
    fact_rows: list[dict[str, Any]] = []
    queue_rows: list[dict[str, Any]] = []
    admission_items: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for review in ready_reviews:
        account_id = _clean(review.get("account_id"))
        source_fact = facts_by_id.get(account_id)
        if not source_fact:
            skipped.append({"account_id": account_id, "reason": "source_fact_missing"})
            continue
        fact = _promote_ready_fact(source_fact, review)
        candidate_rows.append(_candidate_row(candidates_by_id.get(account_id, {}), review))
        fact_rows.append(fact)
        queue_rows.append(_queue_row(fact))
        admission_items.append(_admission_item(review, fact))

    candidate_file = output_dir / "milestone22r_trusted_writeback_candidates_v1.json"
    fact_patch_file = Path("configs/execution_batches/milestone22r_trusted_writeback_admission_facts_v1.json")
    queue_patch_file = Path("configs/execution_batches/milestone22r_trusted_writeback_admission_queue_v1.json")
    enrich_config_file = Path("configs/enrich_batches/milestone22r_trusted_writeback_admission_enrich_v1.json")
    promote_config_file = Path("configs/promote_batches/milestone22r_trusted_writeback_admission_promote_v1.json")
    registry_file = Path("configs/execution_batches/milestone22r_trusted_writeback_admission_registry_v1.json")
    package_file = output_dir / "milestone22r_trusted_writeback_admission_package_v1.json"
    run_summary_file = output_dir / "milestone22r_trusted_writeback_admission_run_summary_v1.json"
    promote_file = output_dir / "milestone22r_trusted_writeback_admission_promote_v1.json"
    baseline_file = output_dir / "milestone22r_trusted_writeback_admission_report_baseline_v1.json"

    run_summary = _load_json_if_exists(run_summary_file)
    promote_payload = _load_json_if_exists(promote_file)
    gate_payload = _load_json_if_exists(args.gate_file)
    report_summary = run_summary.get("summary") if isinstance(run_summary.get("summary"), dict) else {}

    now = _now()
    candidate_payload = {
        "batch_id": "milestone22r_trusted_writeback_candidates_v1",
        "generated_at": now,
        "source_file": args.trusted_review_file,
        "accounts": candidate_rows,
    }
    fact_payload = {"batch_id": "milestone22r_trusted_writeback_admission_facts_v1", "generated_at": now, "results": fact_rows, "accounts": fact_rows}
    queue_payload = {"batch_id": "milestone22r_trusted_writeback_admission_queue_v1", "generated_at": now, "accounts": queue_rows}
    registry_payload = _registry(str(candidate_file), str(fact_patch_file), str(queue_patch_file), output_dir)

    package_payload = {
        "batch_id": "milestone22r_trusted_writeback_admission_package_v1",
        "generated_at": now,
        "source_files": {
            "trusted_review_file": args.trusted_review_file,
            "source_facts_file": args.source_facts_file,
            "source_candidate_file": args.source_candidate_file,
        },
        "generated_files": {
            "candidate_file": str(candidate_file),
            "fact_patch_file": str(fact_patch_file),
            "queue_patch_file": str(queue_patch_file),
            "enrich_config_file": str(enrich_config_file),
            "promote_config_file": str(promote_config_file),
            "registry_file": str(registry_file),
            "run_summary_file": str(run_summary_file),
            "promote_file": str(promote_file),
            "report_baseline_file": str(baseline_file),
            "gate_file": args.gate_file,
        },
        "policy": {
            "true_writeback_executed": False,
            "report_only_first": True,
            "requires_explicit_user_confirmation_for_writeback": True,
            "north_star_metric": "可信画像匹配潜客数",
        },
        "summary": {
            "trusted_input_count": len(ready_reviews),
            "admission_candidate_count": len(candidate_rows),
            "fact_patch_count": len(fact_rows),
            "queue_patch_count": len(queue_rows),
            "skipped_count": len(skipped),
            "report_only_allow": int(report_summary.get("allow") or 0),
            "report_only_warn": int(report_summary.get("warn") or 0),
            "report_only_block": int(report_summary.get("block") or 0),
            "report_only_result_count": len(promote_payload.get("results") or []),
            "gate_ok": bool(gate_payload.get("ok")),
            "track_counts": dict(Counter(item["track"] for item in admission_items)),
            "persona_counts": dict(Counter(item["persona"] for item in admission_items)),
        },
        "skipped": skipped,
        "admission_items": admission_items,
    }

    _write_json(candidate_file, candidate_payload)
    _write_json(fact_patch_file, fact_payload)
    _write_json(queue_patch_file, queue_payload)
    _write_json(enrich_config_file, _base_enrich_config(str(fact_patch_file), output_dir))
    _write_json(promote_config_file, _base_promote_config(str(fact_patch_file), str(queue_patch_file), output_dir))
    _write_json(registry_file, registry_payload)
    _write_json(package_file, package_payload)
    _write_text(args.review_md, _render_markdown(package_payload))

    print(json.dumps({"output_json": str(package_file), "review_md": args.review_md, "summary": package_payload["summary"]}, ensure_ascii=False, indent=2))
    return 0 if not skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
