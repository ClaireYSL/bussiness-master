from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M13_RULE = "deliveries/archive/milestones/milestone13_persona_boundary_rules/milestone13_persona_boundary_rule_package_v1.json"
DEFAULT_M14_PROMOTE = "deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_promote_v1.json"
DEFAULT_M14_2_PROMOTE = "deliveries/archive/milestones/milestone14_2_intake_quality_unblock/milestone14_2_intake_quality_promote_v1.json"
DEFAULT_M14_3_PREFLIGHT = "deliveries/archive/milestones/milestone14_3_candidate_preflight/milestone14_3_candidate_preflight_package_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone15_2_share_consumption/milestone15_2_share_consumption_package_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 15.2-共享消费层增强复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a non-writeback share-consumption package for usable static-pool candidates.")
    parser.add_argument("--m13-rule-package", default=DEFAULT_M13_RULE)
    parser.add_argument("--m14-promote-file", default=DEFAULT_M14_PROMOTE)
    parser.add_argument("--m14-2-promote-file", default=DEFAULT_M14_2_PROMOTE)
    parser.add_argument("--m14-3-preflight-file", default=DEFAULT_M14_3_PREFLIGHT)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
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


def _issue_codes(gate: dict[str, Any], key: str) -> list[str]:
    return [_clean(item.get("code")) for item in gate.get(key) or [] if isinstance(item, dict) and _clean(item.get("code"))]


def _m13_share_item(item: dict[str, object]) -> dict[str, object]:
    decision = _clean(item.get("boundary_decision"))
    risk = ",".join(item.get("reasons") or []) or "待人工画像确认"
    return {
        "account_id": _clean(item.get("account_id")),
        "account_name": _clean(item.get("account_name")),
        "source_milestone": "M13",
        "share_status": "high_value_pending" if decision == "keep_pending_review" else decision,
        "persona": _clean(item.get("persona")),
        "why_worth_review": f"已具备 {item.get('strong_evidence_count')} 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。",
        "evidence_enough": bool(int(item.get("strong_evidence_count") or 0) >= 2 and not item.get("missing_required_dimensions")),
        "remaining_risk": risk,
        "next_action": "人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。",
    }


def _m14_backlog_item(item: dict[str, object], preflight: dict[str, object] | None = None) -> dict[str, object]:
    gate = item.get("promotion_gate") if isinstance(item.get("promotion_gate"), dict) else {}
    blocking = _issue_codes(gate, "blocking_issues")
    warnings = _issue_codes(gate, "warning_issues")
    decision = _clean(gate.get("decision"))
    preflight_status = _clean((preflight or {}).get("preflight_status"))
    if decision == "allow":
        share_status = "ready_for_human_review"
        evidence_enough = True
        next_action = "规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。"
        risk = "待人工确认画像边界和真实业务优先级。"
    elif preflight_status == "needs_human_review":
        share_status = "ready_for_human_review"
        evidence_enough = True
        next_action = _clean((preflight or {}).get("next_action")) or "人工复核 warn 后再决定是否进入写回准入。"
        risk = ",".join(warnings) or "待人工复核。"
    elif preflight_status == "needs_patch":
        share_status = "needs_intake_patch"
        evidence_enough = False
        next_action = _clean((preflight or {}).get("next_action")) or "先补最小字段、官方来源和入池理由。"
        risk = ",".join(blocking + warnings)
    else:
        share_status = "not_share_ready"
        evidence_enough = False
        next_action = _clean((preflight or {}).get("next_action")) or "暂不进入共享消费，先完成候选预检治理。"
        risk = ",".join(blocking + warnings)
    return {
        "account_id": _clean(item.get("account_id")),
        "account_name": _clean(item.get("account_canonical_name")),
        "source_milestone": "M14.2",
        "share_status": share_status,
        "persona": _clean(item.get("persona_tag")),
        "why_worth_review": "小批扩容候选，已完成 report_only 预检。",
        "evidence_enough": evidence_enough,
        "remaining_risk": risk,
        "next_action": next_action,
        "preflight_status": preflight_status,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Milestone 15.2-共享消费层增强复盘-v1",
        "",
        "## 1. 摘要",
        "",
        f"- 可进入人工消费对象：`{summary.get('ready_for_human_review')}`",
        f"- 高价值 pending：`{summary.get('high_value_pending')}`",
        f"- 待入池补丁对象：`{summary.get('needs_intake_patch')}`",
        f"- 暂不共享对象：`{summary.get('not_share_ready')}`",
        f"- 状态分布：`{summary.get('share_status_counts')}`",
        "",
        "## 2. 共享对象",
        "",
    ]
    for item in payload.get("items") or []:
        if item.get("share_status") in {"not_share_ready", "needs_intake_patch"}:
            continue
        lines.extend(
            [
                f"### {item.get('account_name')}（{item.get('account_id')}）",
                "",
                f"- 画像：`{item.get('persona')}`",
                f"- 状态：`{item.get('share_status')}`",
                f"- 为什么值得看：{item.get('why_worth_review')}",
                f"- 剩余风险：{item.get('remaining_risk')}",
                f"- 下一步：{item.get('next_action')}",
                "",
            ]
        )
    lines.extend(["## 3. 待补和暂不共享对象", ""])
    for item in payload.get("items") or []:
        if item.get("share_status") not in {"not_share_ready", "needs_intake_patch"}:
            continue
        lines.append(f"- `{item.get('share_status')}` `{item.get('account_id')}` {item.get('account_name')}：{item.get('remaining_risk')}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    m13 = _load_json(args.m13_rule_package)
    m14 = _load_json(args.m14_2_promote_file) if Path(args.m14_2_promote_file).exists() else _load_json(args.m14_promote_file)
    preflight_payload = _load_json(args.m14_3_preflight_file) if Path(args.m14_3_preflight_file).exists() else {}
    preflight_by_id = {
        _clean(item.get("account_id")): item
        for item in preflight_payload.get("items") or []
        if isinstance(item, dict) and _clean(item.get("account_id"))
    }
    items = [_m13_share_item(item) for item in m13.get("accounts") or [] if isinstance(item, dict)]
    items.extend(_m14_backlog_item(item, preflight_by_id.get(_clean(item.get("account_id")))) for item in m14.get("results") or [] if isinstance(item, dict))
    status_counts = Counter(_clean(item.get("share_status")) for item in items)
    payload = {
        "batch_id": "milestone15_2_share_consumption_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {
            "m13_rule_package": args.m13_rule_package,
            "m14_promote_file": args.m14_promote_file,
            "m14_2_promote_file": args.m14_2_promote_file,
            "m14_3_preflight_file": args.m14_3_preflight_file,
        },
        "summary": {
            "item_count": len(items),
            "share_status_counts": dict(status_counts),
            "share_ready_or_pending": len([item for item in items if item.get("share_status") != "not_share_ready"]),
            "not_share_ready": int(status_counts.get("not_share_ready") or 0),
            "ready_for_human_review": int(status_counts.get("ready_for_human_review") or 0),
            "high_value_pending": int(status_counts.get("high_value_pending") or 0),
            "needs_intake_patch": int(status_counts.get("needs_intake_patch") or 0),
        },
        "items": items,
    }
    _write_json(args.output_json, payload)
    _write_text(args.output_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
