from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import check_workbook_integrity, resolve_static_pool_paths


DEFAULT_M33 = "deliveries/archive/milestones/milestone33r_workbook_governance_audit/milestone33r_workbook_governance_audit_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone39r_shared_view_deprecation"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 39R-共享版降级与主链收口-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deprecate shared workbook as governance input and make it a regenerable export.")
    parser.add_argument("--m33-package", default=DEFAULT_M33)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 39R-共享版降级与主链收口-v1",
        "",
        "## 摘要",
        "",
        f"- 主表行数：`{summary['main_row_count']}`",
        f"- 档案库行数：`{summary['profile_row_count']}`",
        f"- 共享版当前行数：`{summary['shared_row_count']}`",
        f"- 共享版字段差异：`{summary['ignored_shared_mismatch_count']}`，已从主治理阻塞中移除",
        f"- 主链 source of truth：`{summary['source_of_truth']}`",
        f"- 工作簿完整性：`{summary['workbook_integrity_ok']}`",
        "",
        "## 决策",
        "",
        "- 共享版不再参与主链审计、候选准入或字段一致性判断。",
        "- 共享版保留为可再生导出物，可以按需从主表 + 档案库生成。",
        "- 不删除真实文件，避免不可逆操作；但后续状态面板和治理闭环不再被共享版差异阻塞。",
        "- 项目重新回到核心目标：基于知识库和 ICP 找可信潜客，并提供核心可靠信息。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    m33 = _load_json(args.m33_package)
    m33_summary = m33.get("summary") or {}
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["governance"]], deep_scan=True)
    main_profile_ready = (
        m33_summary.get("main_duplicate_account_id_count") == 0
        and m33_summary.get("profile_duplicate_account_id_count") == 0
        and m33_summary.get("main_not_in_profile_count") == 0
        and m33_summary.get("profile_not_in_main_count") == 0
    )
    summary = {
        "source_of_truth": "main_plus_profile",
        "main_row_count": int(m33_summary.get("main_row_count") or 0),
        "profile_row_count": int(m33_summary.get("profile_row_count") or 0),
        "shared_row_count": int(m33_summary.get("shared_row_count") or 0),
        "ignored_shared_mismatch_count": int(m33_summary.get("shared_mismatch_account_count") or 0),
        "main_profile_ready": main_profile_ready,
        "shared_view_role": "regenerable_export_only",
        "shared_view_participates_in_governance": False,
        "shared_view_participates_in_candidate_admission": False,
        "shared_view_blocks_core_pipeline": False,
        "physical_shared_file_deleted": False,
        "workbook_integrity_ok": bool(integrity.get("ok")),
        "true_writeback_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone39r_shared_view_deprecation_package_v1",
        "generated_at": _now(),
        "static_pool_root": str(pool["root"]),
        "policy": {
            "main_is_source_of_truth": True,
            "profile_is_fact_archive": True,
            "shared_is_regenerable_export_only": True,
            "do_not_use_shared_for_governance_diff": True,
            "do_not_delete_physical_shared_file_by_default": True,
        },
        "summary": summary,
        "active_governance_scope": {
            "included_workbooks": [
                "静态潜客主表.xlsx",
                "潜客档案库.xlsx",
                "治理与证据.xlsx",
            ],
            "excluded_workbooks": [
                {
                    "workbook": "内部运营-静态潜客池-共享版.xlsx",
                    "reason": "可再生消费导出物，不作为事实源或治理差异来源。",
                }
            ],
        },
        "recommended_next_stage": {
            "stage": "M40R_core_pool_quality_resume",
            "goal": "回到可信潜客池建设：统计当前 L1/L2/L3/L5、可消费潜客数、反馈状态和下一批扩容阈值。",
        },
        "workbook_integrity": integrity,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone39r_shared_view_deprecation_package_v1.json", payload)
    _write_json(output_dir / "milestone39r_active_governance_scope_v1.json", payload["active_governance_scope"])
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone39r_shared_view_deprecation_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = main_profile_ready and summary["workbook_integrity_ok"] and not summary["shared_view_blocks_core_pipeline"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
