from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
ROOT = Path.home()
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import attach_account_ids, evaluate_promotion_batch, load_main_rows, load_sheet_rows
from shared.static_pool import write_back_promotion_results

VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"
MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
MAIN_SHARED_XLSX = VAULT / "内部运营-静态潜客池-共享版.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
GOV_XLSX = VAULT / "治理与证据.xlsx"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generic promote evaluation entry for the static pool.")
    parser.add_argument("--config-file", help="Optional JSON batch config file.")
    parser.add_argument("--enrich-result-file", help="Optional enrich result JSON to consume before promotion evaluation.")
    parser.add_argument("--account-id", action="append", default=[], help="Specific account IDs to evaluate.")
    parser.add_argument("--from-level", help="Current level to filter, for example L5.")
    parser.add_argument("--target-level", help="Target level for this batch, for example L3.")
    parser.add_argument("--track", help="Track filter, for example 零售消费.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of accounts to include.")
    parser.add_argument("--output-file", help="Where to write the promotion evaluation report.")
    parser.add_argument("--report-only", action="store_true", help="Only build the promotion report, do not write back.")
    parser.add_argument("--write-back", action="store_true", help="Write allow results back to the shared fact layer.")
    return parser


def load_primary_main_rows() -> list[dict[str, object]]:
    return load_main_rows(MAIN_XLSX, "accounts_main")


def _clean(value: object) -> str:
    return str(value or "").strip()


def load_enrich_payload(path: str | None) -> dict[str, object]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_output_file(path: str | None, batch_hint: str) -> Path:
    if path:
        return Path(path)
    base = Path(tempfile.gettempdir()) / "codex-static-pool-runs"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{batch_hint}.json"


def overlay_enrich_results(
    main_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    enrich_results: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    main_by_id = {str(row.get("account_id") or "").strip(): dict(row) for row in main_rows if row.get("account_id")}
    profile_by_id = {str(row.get("account_id") or "").strip(): dict(row) for row in profile_rows if row.get("account_id")}
    for item in enrich_results:
        account_id = _clean(item.get("account_id"))
        if not account_id:
            continue
        main_row = dict(main_by_id.get(account_id) or {})
        profile_row = dict(profile_by_id.get(account_id) or {})
        for row in (main_row, profile_row):
            if not row:
                continue
            row["primary_track"] = item.get("primary_track") or row.get("primary_track")
            row["persona_tag"] = item.get("persona_tag") or row.get("persona_tag")
            row["secondary_persona_tags"] = ",".join(item.get("secondary_persona_tags") or [])
            row["knowledge_asset_refs"] = ",".join(item.get("knowledge_asset_refs") or [])
            row["talk_track_refs"] = ",".join(item.get("talk_track_refs") or [])
            row["validation_gap"] = item.get("validation_gap") or row.get("validation_gap")
            row["review_status"] = item.get("review_status") or row.get("review_status")
            row["静态潜客记录成熟度"] = item.get("suggested_maturity") or row.get("静态潜客记录成熟度")
        if main_row:
            main_by_id[account_id] = main_row
        if profile_row:
            profile_by_id[account_id] = profile_row
    return list(main_by_id.values()), list(profile_by_id.values())


def apply_enrich_guardrails(payload: dict[str, object], enrich_results: list[dict[str, object]]) -> None:
    enrich_by_id = {_clean(item.get("account_id")): item for item in enrich_results}
    batch_summary = payload.get("batch_summary") or {}
    for key in ("allow", "warn", "block"):
        batch_summary.setdefault(key, 0)
    recalculated = {"allow": 0, "warn": 0, "block": 0}
    for item in payload.get("results") or []:
        account_id = _clean(item.get("account_id"))
        enrich = enrich_by_id.get(account_id, {})
        gate = item.get("promotion_gate") or {}
        decision = _clean(gate.get("decision"))
        if enrich:
            gate["enrich_candidate_type"] = enrich.get("candidate_type")
            gate["enrich_ready_for_promote"] = enrich.get("enrich_ready_for_promote")
            gate["enrich_minimum_fact_status"] = enrich.get("minimum_fact_status")
            if (
                enrich.get("candidate_type") == "observation"
                or enrich.get("minimum_fact_status") == "fail"
                or not enrich.get("enrich_ready_for_promote")
            ) and decision == "allow":
                gate["decision"] = "block"
                gate["summary"] = "enrich 结果显示该对象仍未准备好进入 promote，程序已将 allow 降为 block。"
                gate.setdefault("blocking_issues", []).append(
                    {
                        "code": "enrich_not_ready",
                        "severity": "block",
                        "field_name": "enrich_ready_for_promote",
                        "message": "enrich 未通过，不能直接进入 allow。",
                    }
                )
                decision = "block"
        recalculated[decision] = recalculated.get(decision, 0) + 1
    payload["batch_summary"] = recalculated


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config: dict[str, object] = {}
    if args.config_file:
        config = json.loads(Path(args.config_file).read_text(encoding="utf-8"))
    config_output = config.get("output") or {}
    enrich_result_file = args.enrich_result_file or str(config.get("enrich_result_file") or "")
    enrich_payload = load_enrich_payload(enrich_result_file or None)
    enrich_results = list(enrich_payload.get("results") or [])

    main_rows = load_primary_main_rows()
    _profile_headers, profile_rows = load_sheet_rows(PROFILE_XLSX, "account_profiles")
    _queue_headers, queue_rows = load_sheet_rows(GOV_XLSX, "review_queue")
    _evidence_headers, evidence_rows = load_sheet_rows(GOV_XLSX, "evidence_log")
    main_rows = attach_account_ids(main_rows, profile_rows)
    if enrich_results:
        main_rows, profile_rows = overlay_enrich_results(main_rows, profile_rows, enrich_results)

    account_ids = args.account_id or list(config.get("account_ids") or []) or [
        _clean(item.get("account_id")) for item in enrich_results if _clean(item.get("account_id"))
    ]
    from_level = args.from_level or str(config.get("from_level") or "")
    target_level = args.target_level or str(config.get("promote_target_level") or config.get("target_level") or "")
    track = args.track or str(config.get("track") or "")
    limit = args.limit if args.limit != 20 or not config.get("limit") else int(config.get("limit") or 20)
    output_file = args.output_file or str(config_output.get("promote_file") or config.get("output_file") or "")
    output_path = resolve_output_file(output_file or None, str(config.get("batch_id") or "promote_static_pool_run"))

    payload = {
        "batch_id": str(config.get("batch_id") or output_path.stem),
        "goal": str(config.get("goal") or ""),
        "from_level": from_level,
        "target_level": target_level,
        "track": track,
        "write_back": {"enabled": False},
        "enrich_result_file": enrich_result_file,
        "selection": {
            "account_ids": account_ids,
            "limit": limit,
        },
    }
    payload.update(
        evaluate_promotion_batch(
            main_rows,
            profile_rows,
            evidence_rows,
            queue_rows,
            account_ids=account_ids,
            from_level=from_level,
            target_level=target_level,
            track=track,
            limit=limit,
        )
    )
    if enrich_results:
        apply_enrich_guardrails(payload, enrich_results)
        payload["enrich_summary"] = {
            "result_count": len(enrich_results),
            "ready_for_promote": sum(1 for item in enrich_results if item.get("enrich_ready_for_promote")),
            "observation": sum(1 for item in enrich_results if item.get("candidate_type") == "observation"),
        }
    if (args.write_back or bool(config.get("write_back"))) and not args.report_only:
        payload["write_back"] = write_back_promotion_results(
            payload["results"],
            batch_id=payload["batch_id"],
            profile_xlsx=PROFILE_XLSX,
            main_xlsx=MAIN_XLSX,
            main_shared_xlsx=MAIN_SHARED_XLSX,
            gov_xlsx=GOV_XLSX,
        )

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_file": str(output_path),
                "result_count": len(payload["results"]),
                "batch_summary": payload["batch_summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
