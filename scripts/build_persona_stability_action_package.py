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

from shared.static_pool import STANDARD_PERSONA_IDS, VALID_REVIEW_STATUSES

DEFAULT_LLM_REVIEW = "deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_llm_review_v1.json"
DEFAULT_EVIDENCE_PATCH = "configs/execution_batches/milestone12_persona_stability_evidence_patch_v1.json"
DEFAULT_BASE_FACT_PATCH = "configs/execution_batches/milestone11_warn_quality_facts_v1.json"
DEFAULT_ACTION_PACKAGE = "deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_action_package_v1.json"
DEFAULT_FACT_PATCH = "configs/execution_batches/milestone12_persona_stability_facts_v1.json"
DEFAULT_QUEUE_PATCH = "configs/execution_batches/milestone12_persona_stability_queue_v1.json"
DEFAULT_REVIEW = "docs/03-执行与校验/Milestone 12-画像稳定性行动包复盘-v1.md"

VALID_ACTIONS = {"keep_persona", "change_persona", "keep_pending_review", "hold"}
WRITEBACK_STATUSES = {"active", "hold"}
STRONG_EVIDENCE = {"A", "S"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert persona stability review output into safe fact/queue patch packages.")
    parser.add_argument("--llm-review-file", default=DEFAULT_LLM_REVIEW)
    parser.add_argument("--evidence-patch-file", default=DEFAULT_EVIDENCE_PATCH)
    parser.add_argument("--base-fact-patch-file", default=DEFAULT_BASE_FACT_PATCH)
    parser.add_argument("--action-package-file", default=DEFAULT_ACTION_PACKAGE)
    parser.add_argument("--fact-patch-file", default=DEFAULT_FACT_PATCH)
    parser.add_argument("--queue-patch-file", default=DEFAULT_QUEUE_PATCH)
    parser.add_argument("--review-file", default=DEFAULT_REVIEW)
    parser.add_argument(
        "--allow-llm-writeback-ready",
        action="store_true",
        help="Allow writeback-ready LLM recommendations to produce review_status fact patches.",
    )
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_optional_json(path: str) -> dict[str, Any]:
    if not path or not Path(path).exists():
        return {}
    return _load_json(path)


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _queue_type_for(action: str, status: str) -> str:
    if action == "change_persona" or status == "hold":
        return "boundary_review"
    return "verification"


def _evidence_by_account(evidence_patch: dict[str, Any]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in evidence_patch.get("accounts") or []:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        if not account_id:
            continue
        rows = item.get("evidence_rows") or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict):
                copied = dict(row)
                copied.setdefault("account_id", account_id)
                grouped[account_id].append(copied)
    return grouped


def _accounts_by_id(patch: dict[str, Any]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for item in patch.get("accounts") or []:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        if account_id:
            result[account_id] = dict(item)
    return result


def _merge_fact_account(base: dict[str, object], overlay: dict[str, object]) -> dict[str, object]:
    merged = dict(base)
    for key, value in overlay.items():
        if key == "evidence_rows":
            base_rows = list(merged.get("evidence_rows") or []) if isinstance(merged.get("evidence_rows"), list) else []
            overlay_rows = list(value or []) if isinstance(value, list) else []
            merged["evidence_rows"] = base_rows + overlay_rows
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested = dict(merged.get(key) or {})
            nested.update(value)
            merged[key] = nested
        else:
            merged[key] = value
    return merged


def _strong_evidence_count(rows: list[dict[str, object]]) -> int:
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
        if any(token in source_type for token in ("annual", "official", "ir", "announcement")):
            count += 1
    return count


def _validate_evidence_rows(rows: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for idx, row in enumerate(rows, start=1):
        for field in ("source_type", "source_locator", "evidence_strength", "supports_dimension", "summary"):
            if not _clean(row.get(field)):
                errors.append(f"evidence_{idx}_missing_{field}")
    return errors


def _validate_account(item: dict[str, object], evidence_rows: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    account_id = _clean(item.get("account_id"))
    action = _clean(item.get("recommended_action"))
    status = _clean(item.get("recommended_review_status"))
    persona = _clean(item.get("recommended_persona") or item.get("current_persona"))
    if not account_id:
        errors.append("missing_account_id")
    if action not in VALID_ACTIONS:
        errors.append(f"invalid_action:{action or '<empty>'}")
    if status not in VALID_REVIEW_STATUSES:
        errors.append(f"invalid_review_status:{status or '<empty>'}")
    if persona and persona not in STANDARD_PERSONA_IDS:
        errors.append(f"nonstandard_persona:{persona}")
    errors.extend(_validate_evidence_rows(evidence_rows))
    return errors


def _build_items(
    payload: dict[str, Any],
    evidence_patch: dict[str, Any],
    base_fact_patch: dict[str, Any],
    *,
    allow_writeback_ready: bool,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    action_items: list[dict[str, object]] = []
    fact_accounts: list[dict[str, object]] = []
    queue_accounts: list[dict[str, object]] = []
    evidence_by_id = _evidence_by_account(evidence_patch)
    base_fact_by_id = _accounts_by_id(base_fact_patch)
    today = date.today().isoformat()
    for raw in payload.get("accounts") or []:
        if not isinstance(raw, dict):
            continue
        account_id = _clean(raw.get("account_id"))
        account_name = _clean(raw.get("account_name"))
        action = _clean(raw.get("recommended_action"))
        status = _clean(raw.get("recommended_review_status"))
        persona = _clean(raw.get("recommended_persona") or raw.get("current_persona"))
        writeback_ready = bool(raw.get("writeback_ready"))
        evidence_rows = evidence_by_id.get(account_id, [])
        strong_evidence_count = _strong_evidence_count(evidence_rows)
        errors = _validate_account(raw, evidence_rows)
        status_patch_allowed = bool(
            allow_writeback_ready
            and writeback_ready
            and strong_evidence_count > 0
            and not errors
            and status in WRITEBACK_STATUSES
            and action in {"keep_persona", "change_persona", "hold"}
        )
        queue_type = _queue_type_for(action, status)
        action_item = {
            "account_id": account_id,
            "account_name": account_name,
            "recommended_action": action,
            "recommended_review_status": status,
            "recommended_persona": persona,
            "confidence": _clean(raw.get("confidence")),
            "writeback_ready": writeback_ready,
            "status_patch_allowed": status_patch_allowed,
            "fact_patch_allowed": status_patch_allowed,
            "queue_type": queue_type,
            "strong_evidence_count": strong_evidence_count,
            "evidence_patch_rows": len(evidence_rows),
            "validation_errors": errors,
            "evidence_based_reason": _clean(raw.get("evidence_based_reason")),
            "remaining_risk": _clean(raw.get("remaining_risk")),
        }
        action_items.append(action_item)
        fact_account: dict[str, object] | None = None
        if evidence_rows:
            fact_account = {
                "account_id": account_id,
                "account_name": account_name,
                "evidence_rows": evidence_rows,
            }
        if status_patch_allowed:
            main_fields = {"review_status": status, "persona_tag": persona}
            fact_account = fact_account or {"account_id": account_id, "account_name": account_name}
            fact_account["main_fields"] = main_fields
            fact_account["profile_fields"] = main_fields
        base_fact_account = base_fact_by_id.get(account_id, {})
        if base_fact_account or fact_account:
            fact_accounts.append(_merge_fact_account(base_fact_account, fact_account or {"account_id": account_id, "account_name": account_name}))
        if account_id:
            note_parts = []
            if _clean(raw.get("remaining_risk")):
                note_parts.append(_clean(raw.get("remaining_risk")))
            if strong_evidence_count:
                note_parts.append(f"已补强 evidence={strong_evidence_count} 条，仍需人工确认是否可转 active")
            queue_accounts.append(
                {
                    "queue_item_id": f"m12_{account_id}_{queue_type}",
                    "queue_type": queue_type,
                    "account_id": account_id,
                    "priority": "P1",
                    "status": "open",
                    "owner": "codex",
                    "note": "Milestone 12画像稳定性复核：" + "；".join(note_parts or ["待补强一手证据后复核画像边界"]),
                    "created_at": today,
                }
            )
    return action_items, fact_accounts, queue_accounts


def _render_review(action_package: dict[str, Any]) -> str:
    summary = action_package.get("summary") or {}
    lines = [
        "# Milestone 12-画像稳定性行动包复盘-v1",
        "",
        "## 1. 摘要",
        "",
        f"- 输入：`{action_package.get('source_file')}`",
        f"- evidence patch：`{action_package.get('evidence_patch_file')}`",
        f"- 样本数：`{summary.get('account_count')}`",
        f"- action 分布：`{summary.get('action_counts')}`",
        f"- status 分布：`{summary.get('status_counts')}`",
        f"- evidence patch 账户数：`{summary.get('evidence_patch_account_count')}`",
        f"- 强 evidence 条数：`{summary.get('strong_evidence_total')}`",
        f"- 允许生成状态 fact patch：`{summary.get('status_patch_allowed_count')}`",
        f"- fact patch 账户数：`{summary.get('fact_patch_account_count')}`",
        f"- 待补证/复核队列：`{summary.get('queue_patch_count')}`",
        "",
        "## 2. 结论",
        "",
    ]
    if summary.get("status_patch_allowed_count"):
        lines.append("存在可进入后续状态 fact patch 的画像状态建议，但仍必须先走 report_only 和 gate check。")
    else:
        lines.append("本轮没有生成可直接用于状态转正的 fact patch。强 evidence 已进入 fact patch，画像状态仍保持待复核。")
    lines.extend(["", "## 3. 明细", ""])
    for item in action_package.get("accounts") or []:
        lines.extend(
            [
                f"### {item.get('account_name')}（{item.get('account_id')}）",
                "",
                f"- 建议动作：`{item.get('recommended_action')}`",
                f"- 建议状态：`{item.get('recommended_review_status')}`",
                f"- 建议画像：`{item.get('recommended_persona')}`",
                f"- 强 evidence：`{item.get('strong_evidence_count')}`",
                f"- status_patch_allowed：`{item.get('status_patch_allowed')}`",
                f"- queue_type：`{item.get('queue_type')}`",
                f"- 剩余风险：{item.get('remaining_risk') or '待补' }",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    source = _load_json(args.llm_review_file)
    evidence_patch = _load_optional_json(args.evidence_patch_file)
    base_fact_patch = _load_optional_json(args.base_fact_patch_file)
    action_items, fact_accounts, queue_accounts = _build_items(
        source,
        evidence_patch,
        base_fact_patch,
        allow_writeback_ready=args.allow_llm_writeback_ready,
    )
    action_counts = Counter(_clean(item.get("recommended_action")) for item in action_items)
    status_counts = Counter(_clean(item.get("recommended_review_status")) for item in action_items)
    evidence_account_count = sum(1 for item in action_items if int(item.get("evidence_patch_rows") or 0) > 0)
    strong_evidence_total = sum(int(item.get("strong_evidence_count") or 0) for item in action_items)
    status_patch_allowed_count = sum(1 for item in action_items if item.get("status_patch_allowed"))
    action_package = {
        "batch_id": "milestone12_persona_stability_action_package_v1",
        "source_file": args.llm_review_file,
        "evidence_patch_file": args.evidence_patch_file if evidence_patch else "",
        "base_fact_patch_file": args.base_fact_patch_file if base_fact_patch else "",
        "policy": {
            "llm_direct_writeback_allowed": False,
            "allow_llm_writeback_ready_flag": bool(args.allow_llm_writeback_ready),
            "status_patch_requires_writeback_ready": True,
            "status_patch_requires_strong_evidence": True,
            "valid_actions": sorted(VALID_ACTIONS),
            "valid_review_statuses": list(VALID_REVIEW_STATUSES),
        },
        "summary": {
            "account_count": len(action_items),
            "action_counts": dict(action_counts),
            "status_counts": dict(status_counts),
            "evidence_patch_account_count": evidence_account_count,
            "strong_evidence_total": strong_evidence_total,
            "status_patch_allowed_count": status_patch_allowed_count,
            "fact_patch_allowed_count": status_patch_allowed_count,
            "fact_patch_account_count": len(fact_accounts),
            "queue_patch_count": len(queue_accounts),
            "validation_error_count": sum(1 for item in action_items if item.get("validation_errors")),
        },
        "accounts": action_items,
    }
    fact_patch = {
        "batch_id": "milestone12_persona_stability_facts_v1",
        "source_file": args.llm_review_file,
        "evidence_patch_file": args.evidence_patch_file if evidence_patch else "",
        "base_fact_patch_file": args.base_fact_patch_file if base_fact_patch else "",
        "policy": "Base quality patches are inherited, then M12 evidence rows are appended. Review_status changes require writeback_ready plus strong evidence and valid local gates.",
        "accounts": fact_accounts,
    }
    queue_patch = {
        "batch_id": "milestone12_persona_stability_queue_v1",
        "source_file": args.llm_review_file,
        "evidence_patch_file": args.evidence_patch_file if evidence_patch else "",
        "accounts": queue_accounts,
    }
    _write_json(args.action_package_file, action_package)
    _write_json(args.fact_patch_file, fact_patch)
    _write_json(args.queue_patch_file, queue_patch)
    if args.review_file:
        _write_text(args.review_file, _render_review(action_package))
    print(
        json.dumps(
            {
                "action_package_file": args.action_package_file,
                "fact_patch_file": args.fact_patch_file,
                "queue_patch_file": args.queue_patch_file,
                "review_file": args.review_file,
                "summary": action_package["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
