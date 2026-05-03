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


DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone40r_trusted_pool_restart"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 40R-可信潜客池重启与legacy隔离-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M40R trusted pool restart package and legacy isolation policy.")
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


def _legacy_policy() -> dict[str, Any]:
    return {
        "policy_id": "milestone40r_legacy_data_deprecation_policy_v1",
        "status": "active",
        "principle": "历史主表、档案库、共享版不再作为可信事实源；只作为 legacy reference。",
        "legacy_assets": [
            {
                "asset": "静态潜客主表.xlsx",
                "new_role": "legacy_candidate_index",
                "allowed_use": "只用于发现候选线索、去重和历史追溯；不得直接作为可信事实源。",
            },
            {
                "asset": "潜客档案库.xlsx",
                "new_role": "legacy_archive_reference",
                "allowed_use": "只读参考；只有重新补强证据后，字段才能进入新可信潜客包。",
            },
            {
                "asset": "内部运营-静态潜客池-共享版.xlsx",
                "new_role": "deprecated_export",
                "allowed_use": "不再参与治理、候选准入或质量判断；后续如需共享视图，从新可信包再生成。",
            },
            {
                "asset": "治理与证据.xlsx",
                "new_role": "legacy_evidence_and_queue_log",
                "allowed_use": "保留历史写回记录；新增可信证据建议改用 milestone evidence package。",
            },
        ],
        "rules": [
            "不再修复低价值历史字段差异。",
            "旧数据不能直接进入新可信池。",
            "旧候选若要复用，必须按新 evidence-first 流程重新采集强来源证据。",
            "潜客观察不能直接写入正式知识资产。",
            "共享版不再阻塞主线。",
        ],
    }


def _intake_schema() -> dict[str, Any]:
    return {
        "schema_id": "milestone40r_new_prospect_intake_schema_v1",
        "required_fields": [
            "prospect_id",
            "company_canonical_name",
            "matched_persona",
            "match_reason",
            "core_product_service_summary",
            "business_model_summary",
            "official_or_strong_evidence",
            "source_locator",
            "evidence_strength",
            "risk_or_gap",
            "trusted_status",
        ],
        "trusted_status_values": [
            "trusted_match_ready",
            "needs_evidence_patch",
            "persona_pending_review",
            "not_ready",
        ],
        "minimum_entry_gate": [
            "至少 1 条官方或强来源 evidence。",
            "必须有明确匹配画像。",
            "必须有可读的核心产品/服务摘要。",
            "必须说明为什么匹配，而不是只给标签。",
            "必须保留风险或待补点。",
        ],
    }


def _workflow() -> dict[str, Any]:
    return {
        "workflow_id": "milestone40r_trusted_evidence_first_workflow_v1",
        "steps": [
            {
                "step": 1,
                "name": "candidate_discovery",
                "description": "从知识库画像、公开来源、行业名单或 legacy index 发现候选。",
                "output": "candidate_seed",
            },
            {
                "step": 2,
                "name": "evidence_collection",
                "description": "为候选收集官网、年报、IR、公告、CNINFO、权威行业材料等强来源。",
                "output": "evidence_patch",
            },
            {
                "step": 3,
                "name": "trusted_summary_card",
                "description": "基于 evidence 生成可信潜客摘要卡。",
                "output": "trusted_prospect_card",
            },
            {
                "step": 4,
                "name": "persona_match_review",
                "description": "用画像规则判断匹配度，输出 trusted_status。",
                "output": "persona_match_result",
            },
            {
                "step": 5,
                "name": "share_or_queue",
                "description": "可信对象进入共享消费包；不可信对象进入补证队列。",
                "output": "share_package_or_source_gap_queue",
            },
        ],
        "llm_usage_boundary": [
            "LLM 可做摘要草稿、画像复核草稿、补源建议。",
            "LLM 不得直接决定 trusted_status。",
            "LLM 输出不得直接写入正式知识资产。",
        ],
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 40R-可信潜客池重启与legacy隔离-v1",
        "",
        "## 摘要",
        "",
        f"- legacy 隔离状态：`{summary['legacy_isolation_status']}`",
        f"- 新可信池入口：`{summary['new_pool_entry_mode']}`",
        f"- 旧共享版参与主链：`{summary['shared_view_in_core_pipeline']}`",
        f"- 历史档案参与可信判断：`{summary['legacy_profile_in_trusted_decision']}`",
        f"- 工作簿完整性只读检查：`{summary['workbook_integrity_ok']}`",
        "",
        "## 产品决策",
        "",
        "- 停止围绕历史几百条旧档案做局部字段修复。",
        "- 旧主表/档案库/共享版保留，但全部降级为 legacy/reference/export。",
        "- 新可信潜客池从 evidence-first 流程重新采集和生成。",
        "- 下一阶段主线回到：知识库/画像 -> 候选发现 -> 强证据 -> 可信摘要卡 -> 共享消费。",
        "",
        "## 不做事项",
        "",
        "- 不删除旧文件。",
        "- 不把 legacy 档案直接当可信事实源。",
        "- 不把潜客观察反向写入正式知识资产。",
        "- 不再让共享版差异阻塞项目。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    pool = resolve_static_pool_paths()
    integrity = check_workbook_integrity([pool["main"], pool["profile"], pool["main_shared"], pool["governance"]], deep_scan=True)
    legacy_policy = _legacy_policy()
    intake_schema = _intake_schema()
    workflow = _workflow()
    summary = {
        "legacy_isolation_status": "active",
        "new_pool_entry_mode": "evidence_first",
        "shared_view_in_core_pipeline": False,
        "legacy_profile_in_trusted_decision": False,
        "legacy_main_in_trusted_decision": False,
        "legacy_assets_deleted": False,
        "new_schema_required_field_count": len(intake_schema["required_fields"]),
        "minimum_entry_gate_count": len(intake_schema["minimum_entry_gate"]),
        "workbook_integrity_ok": bool(integrity.get("ok")),
        "true_writeback_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    payload = {
        "batch_id": "milestone40r_trusted_pool_restart_package_v1",
        "generated_at": _now(),
        "static_pool_root": str(pool["root"]),
        "summary": summary,
        "legacy_data_deprecation_policy": legacy_policy,
        "new_prospect_intake_schema": intake_schema,
        "trusted_evidence_first_workflow": workflow,
        "next_milestone": {
            "milestone": "M41R",
            "name": "新可信潜客首批 intake 试运行",
            "target": "选择 20-30 家候选，按 evidence-first schema 重新生成可信潜客包，不继承 legacy 档案字段。",
        },
        "workbook_integrity": integrity,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone40r_trusted_pool_restart_package_v1.json", payload)
    _write_json(output_dir / "milestone40r_legacy_data_deprecation_policy_v1.json", legacy_policy)
    _write_json(output_dir / "milestone40r_new_prospect_intake_schema_v1.json", intake_schema)
    _write_json(output_dir / "milestone40r_trusted_evidence_first_workflow_v1.json", workflow)
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone40r_trusted_pool_restart_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = (
        summary["legacy_isolation_status"] == "active"
        and summary["new_pool_entry_mode"] == "evidence_first"
        and not summary["shared_view_in_core_pipeline"]
        and not summary["legacy_profile_in_trusted_decision"]
        and summary["workbook_integrity_ok"]
        and not summary["true_writeback_enabled"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
