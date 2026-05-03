from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CANDIDATES = "deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_candidates_v1.json"
DEFAULT_PROMOTE_BEFORE = "deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_promote_v1.json"
DEFAULT_PROMOTE_AFTER = "deliveries/archive/milestones/milestone14_2_intake_quality_unblock/milestone14_2_intake_quality_promote_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone14_3_candidate_preflight/milestone14_3_candidate_preflight_package_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 14.3-候选预检与分层选择复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build candidate preflight package for expansion batches.")
    parser.add_argument("--candidate-file", default=DEFAULT_CANDIDATES)
    parser.add_argument("--before-promote-file", default=DEFAULT_PROMOTE_BEFORE)
    parser.add_argument("--after-promote-file", default=DEFAULT_PROMOTE_AFTER)
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


def _codes(result: dict[str, Any], key: str) -> list[str]:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    rows = gate.get(key) if isinstance(gate.get(key), list) else []
    return [_clean(row.get("code")) for row in rows if isinstance(row, dict) and _clean(row.get("code"))]


def _decision(result: dict[str, Any]) -> str:
    gate = result.get("promotion_gate") if isinstance(result.get("promotion_gate"), dict) else {}
    return _clean(gate.get("decision"))


def _preflight_status(after_result: dict[str, Any]) -> str:
    decision = _decision(after_result)
    blocking = _codes(after_result, "blocking_issues")
    warnings = _codes(after_result, "warning_issues")
    if decision == "allow":
        return "executable_now"
    if not blocking and warnings:
        return "needs_human_review"
    if blocking and set(blocking) <= {"missing_field", "official_source_missing"}:
        return "needs_patch"
    if blocking:
        return "not_ready"
    return "needs_patch"


def _next_action(status: str, blocking: list[str], warnings: list[str]) -> str:
    if status == "executable_now":
        return "可进入 report_only/gate；如需真实写回，先进入 M17 准入确认。"
    if status == "needs_human_review":
        return f"规则层已无 block；人工复核 warn：{','.join(warnings) or '无'}。"
    if status == "needs_patch":
        return f"补齐字段或官方来源后再进入 promote；当前 block：{','.join(blocking) or '待定位'}。"
    return f"暂不扩容，先处理业务口径或画像边界；当前 block：{','.join(blocking) or '待定位'}。"


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 14.3-候选预检与分层选择复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 候选数：`{summary['candidate_count']}`",
        f"- 预检分层：`{summary['preflight_status_counts']}`",
        f"- 修复前决策：`{summary['before_decision_counts']}`",
        f"- 修复后决策：`{summary['after_decision_counts']}`",
        "",
        "## 分层结果",
        "",
    ]
    for item in payload["items"]:
        lines.append(f"- `{item['preflight_status']}` `{item['account_id']}` {item['account_name']}：{item['next_action']}")
    lines.extend(
        [
            "",
            "## 后续选择规则",
            "",
            "1. `executable_now` 可进入小批 report-only，但真实 write_back 仍需单独确认。",
            "2. `needs_human_review` 可进入人工确认包或共享消费 pending 层。",
            "3. `needs_patch` 不进入扩容执行批次，先补最小字段和官方来源。",
            "4. `not_ready` 暂不纳入扩容，先回到画像或业务口径治理。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    candidates = _load_json(args.candidate_file)
    before = _load_json(args.before_promote_file)
    after = _load_json(args.after_promote_file)
    before_by_id = {_clean(item.get("account_id")): item for item in before.get("results") or [] if isinstance(item, dict)}
    after_by_id = {_clean(item.get("account_id")): item for item in after.get("results") or [] if isinstance(item, dict)}

    items = []
    for candidate in candidates.get("accounts") or []:
        account_id = _clean(candidate.get("account_id")) if isinstance(candidate, dict) else ""
        if not account_id:
            continue
        before_result = before_by_id.get(account_id, {})
        after_result = after_by_id.get(account_id, {})
        blocking = _codes(after_result, "blocking_issues")
        warnings = _codes(after_result, "warning_issues")
        status = _preflight_status(after_result)
        items.append(
            {
                "account_id": account_id,
                "account_name": _clean(after_result.get("account_canonical_name")) or account_id,
                "track": _clean(candidate.get("track")),
                "before_decision": _decision(before_result),
                "after_decision": _decision(after_result),
                "after_blocking_codes": blocking,
                "after_warning_codes": warnings,
                "preflight_status": status,
                "next_action": _next_action(status, blocking, warnings),
            }
        )

    payload = {
        "batch_id": "milestone14_3_candidate_preflight_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {
            "candidate_file": args.candidate_file,
            "before_promote_file": args.before_promote_file,
            "after_promote_file": args.after_promote_file,
        },
        "summary": {
            "candidate_count": len(items),
            "preflight_status_counts": dict(Counter(item["preflight_status"] for item in items)),
            "before_decision_counts": dict(Counter(item["before_decision"] for item in items)),
            "after_decision_counts": dict(Counter(item["after_decision"] for item in items)),
        },
        "items": items,
    }
    _write_json(args.output_json, payload)
    _write_text(args.output_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
