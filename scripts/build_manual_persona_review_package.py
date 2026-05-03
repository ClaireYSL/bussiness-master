from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_RULE_PACKAGE = "deliveries/archive/milestones/milestone13_persona_boundary_rules/milestone13_persona_boundary_rule_package_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone13_2_manual_persona_review/milestone13_2_manual_persona_review_candidate_package_v1.json"
DEFAULT_TEMPLATE_JSON = "configs/execution_batches/milestone13_2_manual_persona_review_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 13.2-人工画像确认包复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a manual persona review package from M13 boundary-rule output.")
    parser.add_argument("--rule-package-file", default=DEFAULT_RULE_PACKAGE)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--template-json", default=DEFAULT_TEMPLATE_JSON)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
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


def _suggest_action(item: dict[str, object]) -> str:
    reasons = set(item.get("reasons") or [])
    if "active_confirmation_missing" in reasons and not set(item.get("missing_required_dimensions") or []):
        return "人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。"
    if item.get("boundary_decision") == "hold_review":
        return "优先人工核实主体/画像边界，必要时 hold。"
    return "补足缺失维度或保持 keep_pending。"


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Milestone 13.2-人工画像确认包复盘-v1",
        "",
        "## 1. 摘要",
        "",
        f"- 样本数：`{summary.get('account_count')}`",
        f"- 规则决策分布：`{summary.get('boundary_decision_counts')}`",
        f"- 当前默认人工决策：`全部 pending_manual_review`",
        "",
        "## 2. 使用方式",
        "",
        "本包不写回工作簿。若后续需要转 active，请在 template JSON 中把对应账户 `decision` 改为 `confirm_active`，再重新运行 M13 规则脚本。",
        "",
        "## 3. 明细",
        "",
    ]
    for item in payload.get("accounts") or []:
        lines.extend(
            [
                f"### {item.get('account_name')}（{item.get('account_id')}）",
                "",
                f"- persona：`{item.get('persona')}`",
                f"- 规则判断：`{item.get('boundary_decision')}`",
                f"- 强 evidence：`{item.get('strong_evidence_count')}`",
                f"- 待人工确认：{item.get('review_question')}",
                f"- 建议：{item.get('suggested_manual_action')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    rule_package = _load_json(args.rule_package_file)
    accounts = []
    template_accounts = []
    for item in rule_package.get("accounts") or []:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        account = {
            "account_id": account_id,
            "account_name": _clean(item.get("account_name")),
            "persona": _clean(item.get("persona")),
            "boundary_decision": _clean(item.get("boundary_decision")),
            "suggested_review_status": _clean(item.get("suggested_review_status")),
            "strong_evidence_count": int(item.get("strong_evidence_count") or 0),
            "evidence_dimensions": item.get("evidence_dimensions") or [],
            "missing_required_dimensions": item.get("missing_required_dimensions") or [],
            "reasons": item.get("reasons") or [],
            "active_confirmation_hint": _clean(item.get("active_confirmation_hint")),
            "review_question": "是否确认该对象的主画像已稳定，足以从 pending_review 转 active？",
            "suggested_manual_action": _suggest_action(item),
        }
        accounts.append(account)
        template_accounts.append(
            {
                "account_id": account_id,
                "account_name": account["account_name"],
                "decision": "pending_manual_review",
                "allowed_decisions": ["confirm_active", "keep_pending_review", "hold_review"],
                "reviewer": "",
                "review_note": "",
            }
        )
    counts = Counter(item["boundary_decision"] for item in accounts)
    payload = {
        "batch_id": "milestone13_2_manual_persona_review_candidate_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": args.rule_package_file,
        "summary": {
            "account_count": len(accounts),
            "boundary_decision_counts": dict(counts),
            "manual_confirmation_count": 0,
        },
        "accounts": accounts,
    }
    template = {
        "batch_id": "milestone13_2_manual_persona_review_template_v1",
        "source_file": args.output_json,
        "policy": "This file is intentionally not pre-confirmed. Change decision to confirm_active only after human persona review.",
        "accounts": template_accounts,
    }
    _write_json(args.output_json, payload)
    _write_json(args.template_json, template)
    _write_text(args.review_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "template_json": args.template_json, "review_md": args.review_md, "account_count": len(accounts)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
