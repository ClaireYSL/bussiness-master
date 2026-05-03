from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_FACTS = "configs/execution_batches/milestone20_batch_intake_facts_v1.json"
DEFAULT_PROMOTE = "deliveries/archive/milestones/milestone20_batch_intake_patch/milestone20_batch_intake_promote_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone21r_trusted_match_review/milestone21r_trusted_match_review_package_v1.json"
DEFAULT_TEMPLATE_JSON = "configs/execution_batches/milestone21r_trusted_match_review_template_v1.json"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 21R-可信画像匹配复核包复盘-v1.md"

TRUSTED_STATUS_VALUES = [
    "trusted_match_ready",
    "profile_match_pending",
    "evidence_pending",
    "persona_adjust_needed",
    "not_icp",
]

OFFICIAL_SOURCE_TYPES = {"cninfo", "official_website", "annual_report", "ir", "announcement"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M21R trusted persona-match review package.")
    parser.add_argument("--facts-file", default=DEFAULT_FACTS)
    parser.add_argument("--promote-file", default=DEFAULT_PROMOTE)
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


def _promote_index(promote: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in promote.get("results") or []:
        if isinstance(item, dict) and _clean(item.get("account_id")):
            out[_clean(item.get("account_id"))] = item
    return out


def _issue_codes(rows: object) -> list[str]:
    if not isinstance(rows, list):
        return []
    return [_clean(row.get("code")) for row in rows if isinstance(row, dict) and _clean(row.get("code"))]


def _field_complete(value: str, min_len: int = 12) -> bool:
    return len(_clean(value)) >= min_len


def _official_evidence_rows(evidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in evidence_rows
        if isinstance(row, dict)
        and _clean(row.get("source_type")) in OFFICIAL_SOURCE_TYPES
        and _clean(row.get("source_locator"))
    ]


def _evidence_traceable(evidence_rows: list[dict[str, Any]]) -> bool:
    return any(_clean(row.get("source_locator")) for row in evidence_rows if isinstance(row, dict))


def _persona_match_clear(track: str, persona: str, admission: str, knowledge_refs: str) -> bool:
    if not track or not persona:
        return False
    if not _field_complete(admission, min_len=24):
        return False
    if persona in admission or track in admission:
        return True
    return bool(_clean(knowledge_refs))


def _risk_notes(
    status: str,
    warning_codes: list[str],
    core_info_complete: bool,
    official_evidence_coverage: bool,
    persona_match_clear: bool,
) -> list[str]:
    notes: list[str] = []
    if not core_info_complete:
        notes.append("核心产品/商业模式/入池理由仍不完整。")
    if not official_evidence_coverage:
        notes.append("缺少可定位的一手或官方来源。")
    if not persona_match_clear:
        notes.append("画像匹配理由仍需补强或人工复核。")
    if "persona_boundary_unstable" in warning_codes and status != "trusted_match_ready":
        notes.append("promote 仍提示画像边界不稳定。")
    if not notes and warning_codes:
        notes.append("原 promote warn 已通过 M21R 可信信息复核解释；后续写回仍需 gate 和用户确认。")
    if not notes:
        notes.append("暂无阻断性风险；后续写回仍需 baseline/gate/integrity。")
    return notes


def _trusted_status(
    *,
    blocking_codes: list[str],
    warning_codes: list[str],
    core_info_complete: bool,
    official_evidence_coverage: bool,
    evidence_traceable: bool,
    admission_reason_clear: bool,
    persona_match_clear: bool,
    persona: str,
) -> str:
    if blocking_codes:
        return "not_icp"
    if not persona:
        return "persona_adjust_needed"
    if not official_evidence_coverage or not evidence_traceable:
        return "evidence_pending"
    if not core_info_complete or not admission_reason_clear:
        return "evidence_pending"
    if not persona_match_clear:
        return "profile_match_pending"
    # M21R intentionally treats persona_boundary_unstable as resolvable when
    # the account has clear persona, core facts, and official evidence.
    if set(warning_codes) <= {"persona_boundary_unstable"}:
        return "trusted_match_ready"
    return "profile_match_pending" if warning_codes else "trusted_match_ready"


def _review_item(fact_item: dict[str, Any], promote_item: dict[str, Any] | None) -> dict[str, Any]:
    account_id = _clean(fact_item.get("account_id"))
    account_name = _clean(fact_item.get("account_name"))
    main_fields = fact_item.get("main_fields") if isinstance(fact_item.get("main_fields"), dict) else {}
    evidence_rows = fact_item.get("evidence_rows") if isinstance(fact_item.get("evidence_rows"), list) else []
    gate = promote_item.get("promotion_gate") if isinstance(promote_item, dict) and isinstance(promote_item.get("promotion_gate"), dict) else {}
    warning_codes = _issue_codes(gate.get("warning_issues"))
    blocking_codes = _issue_codes(gate.get("blocking_issues"))
    track = _clean(main_fields.get("primary_track") or (promote_item or {}).get("primary_track"))
    persona = _clean(main_fields.get("persona_tag") or (promote_item or {}).get("persona_tag"))
    product_summary = _clean(main_fields.get("公司产品与服务概述"))
    business_model_summary = _clean(main_fields.get("商业模式概述"))
    admission_reason_summary = _clean(main_fields.get("admission_reason_summary"))
    knowledge_refs = _clean((promote_item or {}).get("knowledge_asset_refs"))
    official_rows = _official_evidence_rows(evidence_rows)
    core_info_complete = all(
        [
            _field_complete(product_summary),
            _field_complete(business_model_summary),
            _field_complete(admission_reason_summary, min_len=24),
            bool(track),
            bool(persona),
        ]
    )
    official_evidence_coverage = bool(official_rows)
    evidence_traceable = _evidence_traceable(evidence_rows)
    admission_reason_clear = _field_complete(admission_reason_summary, min_len=24)
    persona_clear = _persona_match_clear(track, persona, admission_reason_summary, knowledge_refs)
    status = _trusted_status(
        blocking_codes=blocking_codes,
        warning_codes=warning_codes,
        core_info_complete=core_info_complete,
        official_evidence_coverage=official_evidence_coverage,
        evidence_traceable=evidence_traceable,
        admission_reason_clear=admission_reason_clear,
        persona_match_clear=persona_clear,
        persona=persona,
    )
    return {
        "account_id": account_id,
        "account_name": account_name,
        "trusted_status": status,
        "track": track,
        "persona": persona,
        "from_level": _clean((promote_item or {}).get("from_level")),
        "target_level": _clean((promote_item or {}).get("target_level")),
        "core_info_complete": core_info_complete,
        "official_evidence_coverage": official_evidence_coverage,
        "evidence_traceable": evidence_traceable,
        "admission_reason_clear": admission_reason_clear,
        "persona_match_clear": persona_clear,
        "promotion_warning_codes": warning_codes,
        "promotion_blocking_codes": blocking_codes,
        "official_source_count": len(official_rows),
        "evidence_count": len(evidence_rows),
        "knowledge_asset_refs": knowledge_refs,
        "trusted_prospect_card": {
            "company_name": account_name,
            "matched_persona": persona,
            "matched_track": track,
            "match_reason": admission_reason_summary,
            "core_product_or_service": product_summary,
            "business_model": business_model_summary,
            "key_evidence": [
                {
                    "source_type": _clean(row.get("source_type")),
                    "source_locator": _clean(row.get("source_locator")),
                    "summary": _clean(row.get("summary")),
                    "evidence_strength": _clean(row.get("evidence_strength")),
                }
                for row in evidence_rows
                if isinstance(row, dict)
            ][:5],
            "trusted_status": status,
            "risk_or_gap": _risk_notes(status, warning_codes, core_info_complete, official_evidence_coverage, persona_clear),
        },
    }


def _template_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": item["account_id"],
        "account_name": item["account_name"],
        "system_trusted_status": item["trusted_status"],
        "manual_trusted_status_override": "",
        "allowed_trusted_statuses": TRUSTED_STATUS_VALUES,
        "reviewer": "",
        "review_date": "",
        "review_note": "",
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 21R-可信画像匹配复核包复盘-v1",
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
        "本包不执行写回。它用于把 M20 的 `persona_boundary_unstable` 转成可信画像匹配状态。",
        "",
        "## 状态口径",
        "",
        "- `trusted_match_ready`：画像匹配明确、核心信息可靠、证据可追溯。",
        "- `profile_match_pending`：画像可能匹配，但边界仍需复核。",
        "- `evidence_pending`：画像可能匹配，但证据或核心字段不足。",
        "- `persona_adjust_needed`：当前画像可能不准确。",
        "- `not_icp`：不符合当前 ICP 或存在阻断项。",
        "",
        "## 明细",
        "",
    ]
    for item in payload["review_items"]:
        card = item["trusted_prospect_card"]
        lines.extend(
            [
                f"### {item['account_name']}（{item['account_id']}）",
                "",
                f"- 可信状态：`{item['trusted_status']}`",
                f"- 主线/画像：`{item['track']}` / `{item['persona']}`",
                f"- 匹配理由：{card['match_reason']}",
                f"- 核心产品/服务：{card['core_product_or_service']}",
                f"- 经营结构：{card['business_model']}",
                f"- 官方证据覆盖：`{item['official_evidence_coverage']}`，证据数：`{item['evidence_count']}`",
                f"- 风险/待补点：{'；'.join(card['risk_or_gap'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## 写回边界",
            "",
            "- 只有 `trusted_match_ready` 可进入 M22R 写回准入材料。",
            "- 真实写回仍需 baseline、gate_check、workbook integrity 和用户单独确认。",
            "- M23A/M21 业务反馈类产物只作为可读性参考，不作为主写回准入依据。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    facts = _load_json(args.facts_file)
    promote = _load_json(args.promote_file)
    promote_by_id = _promote_index(promote)
    review_items = [
        _review_item(item, promote_by_id.get(_clean(item.get("account_id"))))
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
        "official_evidence_coverage_rate": round(sum(1 for item in review_items if item["official_evidence_coverage"]) / account_count, 4)
        if account_count
        else 0,
        "core_info_complete_rate": round(sum(1 for item in review_items if item["core_info_complete"]) / account_count, 4)
        if account_count
        else 0,
        "admission_reason_clear_rate": round(sum(1 for item in review_items if item["admission_reason_clear"]) / account_count, 4)
        if account_count
        else 0,
    }
    payload = {
        "batch_id": "milestone21r_trusted_match_review_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {"facts_file": args.facts_file, "promote_file": args.promote_file},
        "north_star_metric": {
            "name": "可信画像匹配潜客数",
            "definition": "同时满足 ICP/画像匹配明确、核心公司信息完整、关键 evidence 可追溯、入池/上移理由清楚、风险和待补点明确、当前治理状态可解释的公司数量。",
        },
        "policy": {
            "default_writeback": False,
            "writeback_admission_status": "trusted_match_ready",
            "writeback_requires": [
                "trusted_status == trusted_match_ready",
                "official_evidence_coverage == true",
                "core_info_complete == true",
                "admission_reason_clear == true",
                "report_only/gate_check PASS",
                "workbook_integrity ok=true",
                "explicit user confirmation",
            ],
        },
        "summary": summary,
        "review_items": review_items,
    }
    template = {
        "batch_id": "milestone21r_trusted_match_review_template_v1",
        "source_file": args.output_json,
        "allowed_trusted_statuses": TRUSTED_STATUS_VALUES,
        "review_items": [_template_item(item) for item in review_items],
    }
    _write_json(args.output_json, payload)
    _write_json(args.template_json, template)
    _write_text(args.review_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "template_json": args.template_json, "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
