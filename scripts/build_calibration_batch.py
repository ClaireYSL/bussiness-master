from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
ROOT = Path.home()
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import (
    attach_account_ids,
    classify_l5_candidate,
    evaluate_promotion_gate,
    load_sheet_rows,
    normalize_review_status,
    should_allow_frozen_text_as_input,
    to_jsonable,
)

VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"
MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
MAIN_SHARED_XLSX = VAULT / "内部运营-静态潜客池-共享版.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
GOV_XLSX = VAULT / "治理与证据.xlsx"
TEMPLATE_PATH = WORKSPACE / "prompts/delegate/calibration_input_template.json"

ALLOWED_SOURCE_TAGS = (
    "abstract_knowledge",
    "public_source_summary",
    "structured_main_record",
    "structured_profile_record",
    "evidence_summary",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a calibrated task package for the external LLM.")
    parser.add_argument("--account-id", action="append", default=[], help="Account IDs to include.")
    parser.add_argument("--track", help="Filter by primary_track when account IDs are not provided.")
    parser.add_argument("--level", help="Filter by 静态潜客记录成熟度 when account IDs are not provided.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of accounts to include.")
    parser.add_argument("--output-file", required=True, help="Where to write the generated JSON task package.")
    parser.add_argument(
        "--input-source-tag",
        action="append",
        default=["abstract_knowledge", "structured_main_record", "structured_profile_record", "evidence_summary"],
        help="Declared source tags for the package. Frozen source tags will be rejected.",
    )
    return parser

def load_main_rows() -> list[dict[str, object]]:
    try:
        _headers, rows = load_sheet_rows(MAIN_XLSX, "accounts_main")
        return rows
    except Exception:
        _headers, rows = load_sheet_rows(MAIN_SHARED_XLSX, "全量主表")
        normalized_rows = []
        for row in rows:
            canonical_name = row.get("公司主体")
            normalized_rows.append(
                {
                    "account_id": "",
                    "account_canonical_name": canonical_name,
                    "primary_track": row.get("主线"),
                    "persona_tag": row.get("业务形态画像"),
                    "secondary_persona_tags": row.get("辅助画像标签") or row.get("次级画像"),
                    "公司产品与服务概述": row.get("公司产品与服务概述"),
                    "商业模式概述": row.get("商业模式概述"),
                    "admission_reason_summary": row.get("一话入池理由"),
                    "validation_gap": row.get("待验证项"),
                    "信息扎实度": row.get("信息扎实度"),
                    "ICP匹配概率": row.get("ICP匹配概率"),
                    "静态潜客记录成熟度": row.get("静态潜客记录成熟度"),
                    "review_status": "pending_review",
                    "knowledge_asset_refs": row.get("主要知识资产引用"),
                    "talk_track_refs": row.get("主要切入话术引用"),
                }
            )
        return normalized_rows

def filter_accounts(main_rows: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    if args.account_id:
        wanted = set(args.account_id)
        filtered = [row for row in main_rows if str(row.get("account_id") or "") in wanted]
        return filtered[: args.limit]
    filtered = []
    for row in main_rows:
        if args.track and str(row.get("primary_track") or "") != args.track:
            continue
        if args.level and str(row.get("静态潜客记录成熟度") or "") != args.level:
            continue
        filtered.append(row)
        if len(filtered) >= args.limit:
            break
    return filtered


def build_public_source_summary(profile_row: dict[str, object], evidence_rows: list[dict[str, object]]) -> list[str]:
    summary = []
    source_refs = str(profile_row.get("primary_source_refs") or "").splitlines()
    for ref in source_refs:
        ref = ref.strip()
        if ref:
            summary.append(ref)
    for evidence in evidence_rows[:3]:
        text = str(evidence.get("summary") or "").strip()
        if text and text not in summary:
            summary.append(text)
    return summary[:6]


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    for source_tag in args.input_source_tag:
        if source_tag not in ALLOWED_SOURCE_TAGS:
            raise SystemExit(f"Unknown source tag: {source_tag}")
        if not should_allow_frozen_text_as_input(source_tag):
            raise SystemExit(f"Frozen input source is not allowed for calibration batch: {source_tag}")

    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    main_rows = load_main_rows()
    _profile_headers, profile_rows = load_sheet_rows(PROFILE_XLSX, "account_profiles")
    profile_id_to_name = {
        str(row.get("account_id") or "").strip(): str(row.get("account_canonical_name") or "").strip()
        for row in profile_rows
        if row.get("account_id")
    }
    main_rows = attach_account_ids(main_rows, profile_rows)
    _queue_headers, queue_rows = load_sheet_rows(GOV_XLSX, "review_queue")
    _evidence_headers, evidence_rows = load_sheet_rows(GOV_XLSX, "evidence_log")

    profile_map = {str(row.get("account_id") or ""): row for row in profile_rows if row.get("account_id")}
    profile_by_name = {str(row.get("account_canonical_name") or ""): row for row in profile_rows if row.get("account_canonical_name")}
    queue_map: dict[str, list[dict[str, object]]] = {}
    for row in queue_rows:
        account_id = str(row.get("account_id") or "").strip()
        if account_id:
            queue_map.setdefault(account_id, []).append(row)
    evidence_map: dict[str, list[dict[str, object]]] = {}
    for row in evidence_rows:
        account_id = str(row.get("account_id") or "").strip()
        if account_id:
            evidence_map.setdefault(account_id, []).append(row)

    selected_rows = filter_accounts(main_rows, args)
    if args.account_id and len(selected_rows) < len(set(args.account_id)):
        wanted_names = {profile_id_to_name.get(account_id, "") for account_id in args.account_id}
        wanted_names.discard("")
        already = {str(row.get("account_id") or "") for row in selected_rows}
        for row in main_rows:
            if str(row.get("account_id") or "") in already:
                continue
            if str(row.get("account_canonical_name") or "") in wanted_names:
                selected_rows.append(row)
                if len(selected_rows) >= args.limit:
                    break
    samples = []
    validation_summaries = []
    for main_row in selected_rows:
        account_id = str(main_row.get("account_id") or "")
        profile_row = profile_map.get(account_id) or profile_by_name.get(str(main_row.get("account_canonical_name") or ""), {})
        if not account_id:
            account_id = str(profile_row.get("account_id") or "")
            main_row["account_id"] = account_id
        evidence = evidence_map.get(account_id, [])
        queues = queue_map.get(account_id, [])
        main_row["review_status"] = normalize_review_status(str(main_row.get("review_status") or ""))

        validation = classify_l5_candidate(main_row, evidence)
        promotion_gate = evaluate_promotion_gate(main_row, profile_row, evidence, queues)
        public_source_summary = build_public_source_summary(profile_row, evidence)

        samples.append(
            {
                "account_id": account_id,
                "account_canonical_name": main_row.get("account_canonical_name"),
                "current_record": {
                    "primary_track": main_row.get("primary_track"),
                    "persona_tag": main_row.get("persona_tag"),
                    "secondary_persona_tags": main_row.get("secondary_persona_tags")
                    or profile_row.get("secondary_persona_tags")
                    or "",
                    "公司产品与服务概述": main_row.get("公司产品与服务概述"),
                    "商业模式概述": main_row.get("商业模式概述"),
                    "admission_reason_summary": main_row.get("admission_reason_summary"),
                    "validation_gap": main_row.get("validation_gap"),
                    "信息扎实度": main_row.get("信息扎实度"),
                    "ICP匹配概率": main_row.get("ICP匹配概率"),
                    "静态潜客记录成熟度": main_row.get("静态潜客记录成熟度"),
                    "review_status": main_row.get("review_status"),
                    "knowledge_asset_refs": main_row.get("knowledge_asset_refs")
                    or profile_row.get("knowledge_asset_refs")
                    or "",
                    "talk_track_refs": main_row.get("talk_track_refs") or profile_row.get("talk_track_refs") or "",
                    "candidate_type": validation.candidate_type,
                },
                "public_source_summary": public_source_summary,
                "evidence_summary": [
                    {
                        "evidence_type": row.get("evidence_type"),
                        "strength": row.get("evidence_strength"),
                        "supports": str(row.get("supports_dimension") or "").split(","),
                        "summary": row.get("summary"),
                    }
                    for row in evidence[:5]
                ],
                "local_validation": {
                    "l5_candidate": to_jsonable(validation),
                    "promotion_gate": to_jsonable(promotion_gate),
                },
            }
        )
        validation_summaries.append(
            {
                "account_id": account_id,
                "candidate_type": validation.candidate_type,
                "review_status": validation.review_status,
                "promotion_decision": promotion_gate.decision,
            }
        )

    output_payload = dict(template)
    output_payload["task_id"] = f"calibration_batch_{len(samples)}"
    output_payload["source_boundary_check"] = {
        "declared_source_tags": args.input_source_tag,
        "frozen_input_detected": False,
    }
    output_payload["samples"] = samples
    output_payload["local_validation_summary"] = validation_summaries

    output_path = Path(args.output_file)
    output_path.write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_file": str(output_path),
                "sample_count": len(samples),
                "account_ids": [sample["account_id"] for sample in samples],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
