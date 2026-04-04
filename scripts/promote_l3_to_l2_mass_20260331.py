from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

from openpyxl import load_workbook


TODAY = "2026-03-31"
ROOT = Path("/Users/clairaipartner")
WORKSPACE = ROOT / ".openclaw/workspace-main/bussiness-master"
VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import (
    apply_row_updates,
    append_semicolon_note,
    ensure_evidence_row,
    prepend_gap_once,
    resolve_open_queue_rows,
    update_main_promotion_core,
    update_profile_promotion_core,
)

MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
GOV_XLSX = VAULT / "治理与证据.xlsx"
MAIN_SHARED_XLSX = VAULT / "内部运营-静态潜客池-共享版.xlsx"
DOC_PATH = WORKSPACE / "docs/03-执行与校验/静态潜客池-L3到L2批量上移专项-v5.md"
MEMORY_PATH = WORKSPACE / "memory/2026-03-31.md"
BATCH_CONFIG = WORKSPACE / "configs/promote_batches/l3_to_l2_mass_v1.json"
PREFLIGHT_OUTPUT = WORKSPACE / "deliveries/promote_batch_l3_to_l2_mass_v1_wrapper.json"

CONSUMER_PERSONAS = {
    "retail_brand_beauty",
    "retail_brand_maternal_pet",
    "retail_fashion_group",
    "retail_multi_store",
    "retail_high_sku_brand",
}
BLOCKED_IDS = {"acc_dreame", "acc_tomtop"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Legacy wrapper for the L3->L2 mass promote batch.")
    parser.add_argument("--report-only", action="store_true", help="Only run the shared preflight report.")
    return parser


def run_preflight_report() -> dict[str, object]:
    from shared.static_pool import attach_account_ids, evaluate_promotion_batch, load_main_rows_with_fallback, load_sheet_rows

    config = json.loads(BATCH_CONFIG.read_text(encoding="utf-8"))
    main_rows = load_main_rows_with_fallback(MAIN_XLSX, "accounts_main", MAIN_SHARED_XLSX, "全量主表")
    _profile_headers, profile_rows = load_sheet_rows(PROFILE_XLSX, "account_profiles")
    _queue_headers, queue_rows = load_sheet_rows(GOV_XLSX, "review_queue")
    _evidence_headers, evidence_rows = load_sheet_rows(GOV_XLSX, "evidence_log")
    main_rows = attach_account_ids(main_rows, profile_rows)
    payload = {
        "batch_id": str(config.get("batch_id") or PREFLIGHT_OUTPUT.stem),
        "from_level": str(config.get("from_level") or "L3"),
        "target_level": str(config.get("target_level") or "L2"),
        "track": str(config.get("track") or ""),
        "write_back": False,
        "selection": {
            "account_ids": list(config.get("account_ids") or []),
            "limit": int(config.get("limit") or 20),
        },
    }
    payload.update(
        evaluate_promotion_batch(
            main_rows,
            profile_rows,
            evidence_rows,
            queue_rows,
            account_ids=list(config.get("account_ids") or []),
            from_level=str(config.get("from_level") or "L3"),
            target_level=str(config.get("target_level") or "L2"),
            track=str(config.get("track") or ""),
            limit=int(config.get("limit") or 20),
        )
    )
    PREFLIGHT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main(report_only: bool = False) -> None:
    preflight = run_preflight_report()
    preflight_account_ids = {
        str(item.get("account_id") or "")
        for item in preflight.get("results", [])
        if str(item.get("account_id") or "")
    }
    if report_only:
        print(
            {
                "mode": "report_only",
                "output_file": str(PREFLIGHT_OUTPUT),
                "batch_summary": preflight["batch_summary"],
            }
        )
        return

    main_wb = load_workbook(MAIN_XLSX)
    main_ws = main_wb["accounts_main"]
    mh = [c.value for c in main_ws[1]]
    mi = {h: i + 1 for i, h in enumerate(mh)}

    profile_wb = load_workbook(PROFILE_XLSX)
    profile_ws = profile_wb["account_profiles"]
    coverage_ws = profile_wb["profile_coverage"]
    ph = [c.value for c in profile_ws[1]]
    pi = {h: i + 1 for i, h in enumerate(ph)}
    ch = [c.value for c in coverage_ws[1]]
    ci = {h: i + 1 for i, h in enumerate(ch)}

    gov_wb = load_workbook(GOV_XLSX)
    evidence_ws = gov_wb["evidence_log"]
    review_ws = gov_wb["review_queue"]
    eh = [c.value for c in evidence_ws[1]]
    ei = {h: i + 1 for i, h in enumerate(eh)}
    qh = [c.value for c in review_ws[1]]
    qi = {h: i + 1 for i, h in enumerate(qh)}

    main_rows = {}
    for r in range(2, main_ws.max_row + 1):
        aid = str(main_ws.cell(r, mi["account_id"]).value or "")
        if aid:
            main_rows[aid] = r

    coverage_rows = {}
    for r in range(2, coverage_ws.max_row + 1):
        aid = str(coverage_ws.cell(r, ci["account_id"]).value or "")
        if aid:
            coverage_rows[aid] = r

    review_rows = []
    for r in range(2, review_ws.max_row + 1):
        review_rows.append(
            {
                "row": r,
                "queue_type": str(review_ws.cell(r, qi["queue_type"]).value or ""),
                "account_id": str(review_ws.cell(r, qi["account_id"]).value or ""),
                "status": str(review_ws.cell(r, qi["status"]).value or ""),
            }
        )

    promoted = []
    by_reason = Counter()

    for r in range(2, profile_ws.max_row + 1):
        aid = str(profile_ws.cell(r, pi["account_id"]).value or "")
        if preflight_account_ids and aid not in preflight_account_ids:
            continue
        if aid in BLOCKED_IDS:
            continue
        level = str(profile_ws.cell(r, pi["静态潜客记录成熟度"]).value or "")
        if level != "L3":
            continue

        info = str(profile_ws.cell(r, pi["信息扎实度"]).value or "")
        icp = str(profile_ws.cell(r, pi["ICP匹配概率"]).value or "")
        official = int(profile_ws.cell(r, pi["official_source_count"]).value or 0)
        high_conf = int(profile_ws.cell(r, pi["high_confidence_source_count"]).value or 0)
        profile_status = str(profile_ws.cell(r, pi["profile_status"]).value or "")
        track = str(profile_ws.cell(r, pi["primary_track"]).value or "")
        persona = str(profile_ws.cell(r, pi["persona_tag"]).value or "")
        static_priority = str(profile_ws.cell(r, pi["static_priority"]).value or "")

        if info not in ("中高", "高"):
            continue
        if official < 1 or high_conf < 2:
            continue
        if profile_status != "standard_ready":
            continue

        reason = None
        if icp in ("中高", "高"):
            reason = "already_qualified"
        elif (
            icp == "中"
            and track == "零售消费"
            and persona in CONSUMER_PERSONAS
            and static_priority in ("A", "B")
        ):
            reason = "consumer_reassessed"
        else:
            continue

        mr = main_rows.get(aid)
        if not mr:
            continue

        if reason == "consumer_reassessed":
            profile_ws.cell(r, pi["ICP匹配概率"]).value = "中高"
            main_ws.cell(mr, mi["ICP匹配概率"]).value = "中高"

        update_profile_promotion_core(
            profile_ws,
            pi,
            r,
            maturity_level="L2",
            profile_status="high_quality_ready",
            validation_gap=prepend_gap_once(
                profile_ws.cell(r, pi["validation_gap"]).value,
                "已进入L2；后续重点继续补官网、年报、IR和财报口径字段。",
            ),
            last_profiled_at=TODAY,
        )

        update_main_promotion_core(
            main_ws,
            mi,
            mr,
            maturity_level="L2",
            source_note_suffix="2026-03-31 L3到L2批量上移",
            validation_gap=prepend_gap_once(
                main_ws.cell(mr, mi["validation_gap"]).value,
                "已进入L2；后续重点继续补官网、年报、IR和财报口径字段。",
            ),
            extra_updates={"信息扎实度": info},
        )

        cr = coverage_rows.get(aid)
        if cr:
            apply_row_updates(
                coverage_ws,
                ci,
                cr,
                {
                    "target_scope": "L1-L2",
                    "official_source_ready": "yes",
                    "high_confidence_ready": "yes",
                    "profile_complete_status": "high_quality_ready",
                    "next_action": "继续补官网、年报、IR 和财报口径字段；必要时再评估是否进入 L1。",
                    "missing_core_fields": "收入规模、利润状态、营收增长仍需回到财报/年报/IR 口径继续补齐。",
                },
            )

        evidence_id = f"ev_{aid}_promote_l2_20260331"
        ensure_evidence_row(
            evidence_ws,
            ei,
            evidence_id,
            {
                "evidence_id": evidence_id,
                "account_id": aid,
                "evidence_type": "promotion_assessment",
                "source_locator": "internal://promotion/l3_to_l2/2026-03-31",
                "evidence_strength": "B",
                "supports_fields": "persona_support,share_support",
                "summary": "已满足 L2 门槛：信息扎实度、官方源、高可信源和档案完整度均已达标；本轮批量上移至 L2。",
                "captured_by": "codex_llm",
                "captured_at": TODAY,
                "expires_at": "",
                "target_field": "静态潜客记录成熟度",
                "target_value": "L2",
            },
        )

        resolve_open_queue_rows(
            review_ws,
            qi,
            account_id=aid,
            queue_type="promotion_review",
            resolved_at=TODAY,
        )

        promoted.append((aid, str(profile_ws.cell(r, pi["account_canonical_name"]).value or ""), reason))
        by_reason[reason] += 1

    main_wb.save(MAIN_XLSX)
    profile_wb.save(PROFILE_XLSX)
    gov_wb.save(GOV_XLSX)

    l2_total = 0
    l3_total = 0
    for r in range(2, main_ws.max_row + 1):
        lvl = str(main_ws.cell(r, mi["静态潜客记录成熟度"]).value or "")
        if lvl == "L2":
            l2_total += 1
        elif lvl == "L3":
            l3_total += 1

    DOC_PATH.write_text(
        "\n".join(
            [
                "# 静态潜客池-L3到L2批量上移专项-v5",
                "",
                f"- 执行日期：`{TODAY}`",
                f"- 本轮上移：`{len(promoted)}` 家 `L3 -> L2`。",
                f"- 其中原本已满足门槛：`{by_reason['already_qualified']}` 家。",
                f"- 其中基于消费品新画像与官方源补强重判 ICP 后上移：`{by_reason['consumer_reassessed']}` 家。",
                f"- 当前主表口径：`L2={l2_total} / L3={l3_total}`。",
                "",
                "## 本轮上移门槛",
                "",
                "- `信息扎实度 ∈ {中高, 高}`",
                "- `official_source_count >= 1`",
                "- `high_confidence_source_count >= 2`",
                "- `profile_status = standard_ready`",
                "- 原本已满足 `ICP匹配概率 ∈ {中高, 高}`，或属于本轮完成官方源补强的消费品 active 画像并完成重判。",
                "",
                "## 说明",
                "",
                "- 本轮不扩 `L1`，继续保持 `L1` 为锚点层。",
                "- 剩余未上移对象应继续留在 `L3`，待补更强主体与官方源后再评估。",
            ]
        ),
        encoding="utf-8",
    )

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(
            f"\n- 完成一轮 `L3 -> L2` 批量上移，实际新增上移 `{len(promoted)}` 家；其中 `{by_reason['consumer_reassessed']}` 家基于消费品新画像与官方源补强重判后进入 `L2`。\n"
        )

    print(
        {
            "promoted": len(promoted),
            "by_reason": dict(by_reason),
            "sample": promoted[:40],
        }
    )


if __name__ == "__main__":
    args = build_parser().parse_args()
    main(report_only=args.report_only)
