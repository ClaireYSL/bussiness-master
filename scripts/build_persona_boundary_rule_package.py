from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import STANDARD_PERSONA_IDS

DEFAULT_CONFIG = "configs/execution_batches/milestone13_persona_boundary_rules_v1.json"
STRONG_EVIDENCE = {"A", "S"}
DEFAULT_ALLOWED_WARNINGS = {"persona_boundary_unstable", "promotion_review_missing"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate executable persona-boundary rules for M13.")
    parser.add_argument("--config-file", default=DEFAULT_CONFIG)
    parser.add_argument("--manual-review-file", help="Optional reviewed decisions that can confirm active candidates.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_optional_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    return _load_json(str(p))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _by_id(items: list[dict[str, object]], key: str = "account_id") -> dict[str, dict[str, object]]:
    return {_clean(item.get(key)): item for item in items if _clean(item.get(key))}


def _group_evidence(fact_patch: dict[str, Any]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for account in fact_patch.get("accounts") or []:
        if not isinstance(account, dict):
            continue
        account_id = _clean(account.get("account_id"))
        for row in account.get("evidence_rows") or []:
            if isinstance(row, dict) and account_id:
                copied = dict(row)
                copied.setdefault("account_id", account_id)
                grouped[account_id].append(copied)
    return grouped


def _strong_count(rows: list[dict[str, object]]) -> int:
    count = 0
    for row in rows:
        strength = _clean(row.get("evidence_strength") or row.get("strength")).upper()
        locator = _clean(row.get("source_locator")).lower()
        source_type = _clean(row.get("source_type")).lower()
        if strength in STRONG_EVIDENCE:
            count += 1
            continue
        if any(token in locator for token in ("cninfo", "年报", "官网", "公告", "ir", "investor")):
            count += 1
            continue
        if any(token in source_type for token in ("annual", "official", "ir", "announcement", "listed")):
            count += 1
    return count


def _evidence_dimensions(rows: list[dict[str, object]]) -> set[str]:
    dims: set[str] = set()
    for row in rows:
        raw = _clean(row.get("supports_dimension"))
        for item in raw.replace("，", ",").replace(";", ",").split(","):
            if item.strip():
                dims.add(item.strip())
    return dims


def _issue_codes(gate: dict[str, Any], key: str) -> list[str]:
    result: list[str] = []
    for item in gate.get(key) or []:
        if isinstance(item, dict) and _clean(item.get("code")):
            result.append(_clean(item.get("code")))
    return result


def _manual_by_id(payload: dict[str, Any]) -> dict[str, dict[str, object]]:
    return _by_id([item for item in payload.get("accounts") or [] if isinstance(item, dict)])


def _evaluate_account(
    *,
    action_item: dict[str, object],
    promote_item: dict[str, object],
    llm_item: dict[str, object],
    evidence_rows: list[dict[str, object]],
    manual_item: dict[str, object],
    config: dict[str, Any],
) -> dict[str, object]:
    defaults = config.get("rule_defaults") or {}
    persona_rules = config.get("persona_rules") or {}
    account_id = _clean(action_item.get("account_id") or promote_item.get("account_id") or llm_item.get("account_id"))
    account_name = _clean(action_item.get("account_name") or promote_item.get("account_canonical_name") or llm_item.get("account_name"))
    persona = _clean(action_item.get("recommended_persona") or promote_item.get("persona_tag") or llm_item.get("current_persona"))
    gate = promote_item.get("promotion_gate") if isinstance(promote_item.get("promotion_gate"), dict) else {}
    decision = _clean(gate.get("decision"))
    warning_codes = _issue_codes(gate, "warning_issues")
    blocking_codes = _issue_codes(gate, "blocking_issues")
    strong_count = _strong_count(evidence_rows)
    dimensions = _evidence_dimensions(evidence_rows)
    persona_rule = persona_rules.get(persona) if isinstance(persona_rules.get(persona), dict) else {}
    required_dims = set(persona_rule.get("required_evidence_dimensions") or [])
    missing_dims = sorted(required_dims - dimensions)
    min_strong = int(defaults.get("min_strong_evidence_for_active") or 2)
    allowed_warnings = set(defaults.get("active_allowed_warning_codes") or sorted(DEFAULT_ALLOWED_WARNINGS))
    manual_decision = _clean(manual_item.get("decision") or manual_item.get("boundary_decision"))
    llm_action = _clean(llm_item.get("recommended_action") or action_item.get("recommended_action"))
    llm_status = _clean(llm_item.get("recommended_review_status") or action_item.get("recommended_review_status"))
    llm_writeback_ready = bool(llm_item.get("writeback_ready") or action_item.get("writeback_ready"))

    reasons: list[str] = []
    if persona not in STANDARD_PERSONA_IDS:
        reasons.append("nonstandard_persona")
    if decision == "block" or blocking_codes:
        reasons.append("local_promote_block")
    if strong_count < min_strong:
        reasons.append("strong_evidence_below_threshold")
    if missing_dims:
        reasons.append("persona_required_dimensions_missing")
    disallowed_warnings = sorted(set(warning_codes) - allowed_warnings)
    if disallowed_warnings:
        reasons.append("disallowed_warning_codes")
    has_confirmation = manual_decision == "confirm_active" or (
        llm_action == "keep_persona" and llm_status == "active" and llm_writeback_ready
    )
    if bool(defaults.get("active_requires_manual_or_llm_confirmation", True)) and not has_confirmation:
        reasons.append("active_confirmation_missing")

    if "nonstandard_persona" in reasons or "local_promote_block" in reasons:
        boundary_decision = "hold_review"
        suggested_review_status = "hold"
        queue_type = "boundary_review"
    elif not reasons:
        boundary_decision = "active_candidate"
        suggested_review_status = "active"
        queue_type = "promotion_review"
    else:
        boundary_decision = "keep_pending_review"
        suggested_review_status = "pending_review"
        queue_type = "verification"

    return {
        "account_id": account_id,
        "account_name": account_name,
        "persona": persona,
        "boundary_decision": boundary_decision,
        "suggested_review_status": suggested_review_status,
        "queue_type": queue_type,
        "local_promote_decision": decision,
        "warning_codes": warning_codes,
        "blocking_codes": blocking_codes,
        "strong_evidence_count": strong_count,
        "evidence_dimensions": sorted(dimensions),
        "missing_required_dimensions": missing_dims,
        "llm_recommended_action": llm_action,
        "llm_recommended_status": llm_status,
        "llm_writeback_ready": llm_writeback_ready,
        "manual_decision": manual_decision,
        "reasons": reasons,
        "active_confirmation_hint": _clean(persona_rule.get("active_confirmation_hint")),
    }


def _build_fact_patch(source_fact_patch: dict[str, Any], decisions: list[dict[str, object]]) -> dict[str, Any]:
    source_by_id = _by_id([item for item in source_fact_patch.get("accounts") or [] if isinstance(item, dict)])
    accounts: list[dict[str, object]] = []
    for item in decisions:
        account_id = _clean(item.get("account_id"))
        base = dict(source_by_id.get(account_id, {}))
        if not base:
            base = {"account_id": account_id, "account_name": _clean(item.get("account_name"))}
        if item.get("boundary_decision") == "active_candidate":
            fields = {"review_status": "active", "persona_tag": _clean(item.get("persona"))}
            base["main_fields"] = {**dict(base.get("main_fields") or {}), **fields}
            base["profile_fields"] = {**dict(base.get("profile_fields") or {}), **fields}
        accounts.append(base)
    return {
        "batch_id": "milestone13_persona_boundary_facts_v1",
        "policy": "M13 inherits M12 evidence/quality facts. review_status=active is emitted only for active_candidate decisions.",
        "accounts": accounts,
    }


def _build_queue_patch(decisions: list[dict[str, object]]) -> dict[str, Any]:
    today = date.today().isoformat()
    accounts = []
    for item in decisions:
        account_id = _clean(item.get("account_id"))
        if not account_id:
            continue
        accounts.append(
            {
                "queue_item_id": f"m13_{account_id}_{_clean(item.get('queue_type'))}",
                "queue_type": _clean(item.get("queue_type")),
                "account_id": account_id,
                "priority": "P1" if item.get("boundary_decision") != "active_candidate" else "P2",
                "status": "open",
                "owner": "codex",
                "note": "Milestone 13画像边界规则：" + ",".join(item.get("reasons") or ["active_candidate_ready_for_gate"]),
                "created_at": today,
            }
        )
    return {
        "batch_id": "milestone13_persona_boundary_queue_v1",
        "accounts": accounts,
    }


def _render_review(package: dict[str, Any]) -> str:
    summary = package.get("summary") or {}
    lines = [
        "# Milestone 13-画像边界规则评估复盘-v1",
        "",
        "## 1. 摘要",
        "",
        f"- 样本数：`{summary.get('account_count')}`",
        f"- 决策分布：`{summary.get('decision_counts')}`",
        f"- 强 evidence 合计：`{summary.get('strong_evidence_total')}`",
        f"- active fact patch 数：`{summary.get('active_candidate_count')}`",
        "",
        "## 2. 规则结论",
        "",
    ]
    if summary.get("active_candidate_count"):
        lines.append("本轮存在可转 active 的候选，但仍需进入 report_only 与 gate check。")
    else:
        lines.append("本轮没有对象满足 active_candidate 条件；原因主要是缺少人工或 LLM 转正确认。")
    lines.extend(["", "## 3. 明细", ""])
    for item in package.get("accounts") or []:
        lines.extend(
            [
                f"### {item.get('account_name')}（{item.get('account_id')}）",
                "",
                f"- persona：`{item.get('persona')}`",
                f"- boundary_decision：`{item.get('boundary_decision')}`",
                f"- suggested_review_status：`{item.get('suggested_review_status')}`",
                f"- strong_evidence_count：`{item.get('strong_evidence_count')}`",
                f"- warning_codes：`{', '.join(item.get('warning_codes') or []) or '无'}`",
                f"- reasons：`{', '.join(item.get('reasons') or []) or '无'}`",
                f"- active_confirmation_hint：{item.get('active_confirmation_hint') or 'n/a'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    config = _load_json(args.config_file)
    sources = config.get("source_files") or {}
    outputs = config.get("decision_outputs") or {}
    action_package = _load_json(_clean(sources.get("m12_action_package")))
    fact_patch = _load_json(_clean(sources.get("m12_fact_patch")))
    promote_result = _load_json(_clean(sources.get("m12_promote_result")))
    llm_review = _load_json(_clean(sources.get("m12_llm_review")))
    manual_review = _load_optional_json(args.manual_review_file)

    action_by_id = _by_id([item for item in action_package.get("accounts") or [] if isinstance(item, dict)])
    promote_by_id = _by_id([item for item in promote_result.get("results") or [] if isinstance(item, dict)])
    llm_by_id = _by_id([item for item in llm_review.get("accounts") or [] if isinstance(item, dict)])
    evidence_by_id = _group_evidence(fact_patch)
    manual_by_id = _manual_by_id(manual_review)

    account_ids = sorted(set(action_by_id) | set(promote_by_id) | set(llm_by_id))
    decisions = [
        _evaluate_account(
            action_item=action_by_id.get(account_id, {}),
            promote_item=promote_by_id.get(account_id, {}),
            llm_item=llm_by_id.get(account_id, {}),
            evidence_rows=evidence_by_id.get(account_id, []),
            manual_item=manual_by_id.get(account_id, {}),
            config=config,
        )
        for account_id in account_ids
    ]
    decision_counts = Counter(_clean(item.get("boundary_decision")) for item in decisions)
    strong_total = sum(int(item.get("strong_evidence_count") or 0) for item in decisions)
    package = {
        "batch_id": "milestone13_persona_boundary_rule_package_v1",
        "config_file": args.config_file,
        "manual_review_file": args.manual_review_file or "",
        "summary": {
            "account_count": len(decisions),
            "decision_counts": dict(decision_counts),
            "strong_evidence_total": strong_total,
            "active_candidate_count": int(decision_counts.get("active_candidate") or 0),
            "keep_pending_review_count": int(decision_counts.get("keep_pending_review") or 0),
            "hold_review_count": int(decision_counts.get("hold_review") or 0),
        },
        "accounts": decisions,
    }
    fact_out = _build_fact_patch(fact_patch, decisions)
    queue_out = _build_queue_patch(decisions)
    _write_json(_clean(outputs.get("rule_package_file")), package)
    _write_json(_clean(outputs.get("fact_patch_file")), fact_out)
    _write_json(_clean(outputs.get("queue_patch_file")), queue_out)
    _write_text(_clean(outputs.get("review_file")), _render_review(package))
    print(
        json.dumps(
            {
                "rule_package_file": _clean(outputs.get("rule_package_file")),
                "fact_patch_file": _clean(outputs.get("fact_patch_file")),
                "queue_patch_file": _clean(outputs.get("queue_patch_file")),
                "review_file": _clean(outputs.get("review_file")),
                "summary": package["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
