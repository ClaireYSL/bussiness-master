from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_SCRIPT = Path(__file__).resolve().parent / "build_trusted_match_review_package.py"
spec = importlib.util.spec_from_file_location("trusted_review_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(base)  # type: ignore[union-attr]

DEFAULT_FACTS = "configs/execution_batches/milestone25r_trusted_expansion_facts_v1.json"
DEFAULT_PROMOTE = "deliveries/archive/milestones/milestone25r_trusted_expansion_intake_patch/milestone25r_trusted_expansion_promote_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone25r_trusted_expansion_review/milestone25r_trusted_expansion_review_package_v1.json"
DEFAULT_TEMPLATE_JSON = "configs/execution_batches/milestone25r_trusted_expansion_review_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 25R-可信扩容画像匹配复核包复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M25R trusted expansion review package.")
    parser.add_argument("--facts-file", default=DEFAULT_FACTS)
    parser.add_argument("--promote-file", default=DEFAULT_PROMOTE)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--template-json", default=DEFAULT_TEMPLATE_JSON)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 25R-可信扩容画像匹配复核包复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 输入对象：`{summary['account_count']}`",
        f"- 可信状态分布：`{summary['trusted_status_counts']}`",
        f"- `trusted_match_ready_count`：`{summary['trusted_match_ready_count']}`",
        f"- 官方证据覆盖率：`{summary['official_evidence_coverage_rate']}`",
        f"- 核心信息完整率：`{summary['core_info_complete_rate']}`",
        f"- 入池理由清晰率：`{summary['admission_reason_clear_rate']}`",
        "",
        "本包不执行写回。它用于把 M25R 的 `persona_boundary_unstable=50` 转成可信度状态。",
        "",
        "## 边界",
        "",
        "- `trusted_match_ready` 只表示可信潜客摘要/准入材料充分，不代表正式知识资产。",
        "- 真实写回仍需用户单独确认。",
        "- 潜客观察不得反向写入 knowledge_assets 或 persona_registry。",
        "",
        "## 明细",
        "",
    ]
    for item in payload["review_items"]:
        card = item["trusted_prospect_card"]
        lines.extend([
            f"### {item['account_name']}（{item['account_id']}）",
            "",
            f"- 可信状态：`{item['trusted_status']}`",
            f"- 主线/画像：`{item['track']}` / `{item['persona']}`",
            f"- 匹配理由：{card['match_reason']}",
            f"- 核心产品/服务：{card['core_product_or_service']}",
            f"- 官方证据覆盖：`{item['official_evidence_coverage']}`，证据数：`{item['evidence_count']}`",
            f"- 风险/待补点：{'；'.join(card['risk_or_gap'])}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    facts = base._load_json(args.facts_file)
    promote = base._load_json(args.promote_file)
    promote_by_id = base._promote_index(promote)
    review_items = [
        base._review_item(item, promote_by_id.get(base._clean(item.get("account_id"))))
        for item in facts.get("results") or []
        if isinstance(item, dict)
    ]
    status_counts = Counter(item["trusted_status"] for item in review_items)
    account_count = len(review_items)
    summary = {
        "account_count": account_count,
        "trusted_status_counts": dict(status_counts),
        "trusted_match_ready_count": status_counts.get("trusted_match_ready", 0),
        "profile_match_pending_count": status_counts.get("profile_match_pending", 0),
        "evidence_pending_count": status_counts.get("evidence_pending", 0),
        "persona_adjust_needed_count": status_counts.get("persona_adjust_needed", 0),
        "not_icp_count": status_counts.get("not_icp", 0),
        "official_evidence_coverage_rate": round(sum(1 for item in review_items if item["official_evidence_coverage"]) / account_count, 4) if account_count else 0,
        "core_info_complete_rate": round(sum(1 for item in review_items if item["core_info_complete"]) / account_count, 4) if account_count else 0,
        "admission_reason_clear_rate": round(sum(1 for item in review_items if item["admission_reason_clear"]) / account_count, 4) if account_count else 0,
    }
    payload = {
        "batch_id": "milestone25r_trusted_expansion_review_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {"facts_file": args.facts_file, "promote_file": args.promote_file},
        "policy": {
            "default_writeback": False,
            "formal_knowledge_write_enabled": False,
            "writeback_requires_explicit_user_confirmation": True,
        },
        "summary": summary,
        "review_items": review_items,
    }
    template = {
        "batch_id": "milestone25r_trusted_expansion_review_template_v1",
        "source_file": args.output_json,
        "allowed_trusted_statuses": base.TRUSTED_STATUS_VALUES,
        "review_items": [base._template_item(item) for item in review_items],
    }
    base._write_json(args.output_json, payload)
    base._write_json(args.template_json, template)
    base._write_text(args.review_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "template_json": args.template_json, "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary["trusted_match_ready_count"] == account_count and account_count == 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())
