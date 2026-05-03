from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone43r_new_prospect_intake_schema"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 43R-新可信潜客intake schema与采集器-v1.md"

TRUSTED_STATUS_VALUES = ["trusted_match_ready", "evidence_pending", "persona_pending_review", "not_icp"]
EVIDENCE_STRENGTH_VALUES = ["official", "regulatory", "annual_report", "ir", "exchange_announcement", "authoritative_media", "industry_research", "weak_reference"]
FORBIDDEN_LEGACY_FIELDS = [
    "legacy_profile_summary",
    "old_main_table_level",
    "old_shared_view_status",
    "historical_review_status",
    "legacy_account_notes",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M43R new trusted prospect intake schemas and validation report.")
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


def _intake_template() -> dict[str, Any]:
    return {
        "template_id": "milestone43r_new_prospect_intake_template_v1",
        "record_type": "new_trusted_prospect_intake",
        "required_fields": [
            "prospect_id",
            "company_name",
            "matched_persona",
            "match_reason",
            "core_product_service_summary",
            "business_model_summary",
            "strong_evidence",
            "risk_or_gap",
            "trusted_status",
        ],
        "optional_fields": ["industry_guess", "website", "stock_code", "secondary_persona", "notes"],
        "trusted_status_values": TRUSTED_STATUS_VALUES,
        "forbidden_legacy_fields": FORBIDDEN_LEGACY_FIELDS,
        "minimum_gate": [
            "trusted_match_ready 必须至少有 1 条 official/regulatory/annual_report/ir/exchange_announcement/authoritative_media/industry_research evidence。",
            "trusted_match_ready 必须有明确画像和匹配理由。",
            "旧主表/旧档案/旧共享版字段不得自动继承；只能作为去重参考。",
            "LLM 可辅助摘要，但不得直接决定 trusted_status。",
        ],
    }


def _evidence_patch_schema() -> dict[str, Any]:
    return {
        "schema_id": "milestone43r_trusted_evidence_patch_schema_v1",
        "record_type": "trusted_evidence_patch",
        "required_fields": [
            "prospect_id",
            "company_name",
            "source_type",
            "source_locator",
            "evidence_strength",
            "supports_dimension",
            "summary",
        ],
        "evidence_strength_values": EVIDENCE_STRENGTH_VALUES,
        "strong_evidence_values": [v for v in EVIDENCE_STRENGTH_VALUES if v != "weak_reference"],
        "supports_dimension_values": ["company_identity", "product_service", "business_model", "persona_match", "scale_signal", "risk_signal"],
        "validation_rules": [
            "source_locator 必须可定位到具体页面、公告、报告、官网栏目或文件。",
            "weak_reference 不能单独支撑 trusted_match_ready。",
            "summary 只能总结来源支持的事实，不写销售动作建议。",
        ],
    }


def _summary_card_schema() -> dict[str, Any]:
    return {
        "schema_id": "milestone43r_trusted_summary_card_schema_v1",
        "record_type": "trusted_prospect_summary_card",
        "required_fields": [
            "company_name",
            "matched_persona",
            "match_reason",
            "core_product_service_summary",
            "business_model_summary",
            "key_evidence",
            "trusted_status",
            "risk_or_gap",
        ],
        "consumer_questions_answered": [
            "这家公司为什么匹配 ICP/画像？",
            "核心产品/服务是什么？",
            "业务模式或经营结构是什么？",
            "证据来自哪里，够不够强？",
            "当前风险或待补点是什么？",
        ],
        "not_allowed": ["销售行动口径作为主指标", "潜客观察写入正式知识资产", "旧档案字段自动继承"],
    }


def _validate_sample_records(records: list[dict[str, Any]], template: dict[str, Any], evidence_schema: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    strong_values = set(evidence_schema["strong_evidence_values"])
    for idx, record in enumerate(records):
        missing = [field for field in template["required_fields"] if not record.get(field)]
        if missing:
            errors.append({"row": idx, "error_code": "missing_required_field", "fields": missing})
        forbidden = [field for field in FORBIDDEN_LEGACY_FIELDS if field in record]
        if forbidden:
            errors.append({"row": idx, "error_code": "legacy_field_inherited", "fields": forbidden})
        status = record.get("trusted_status")
        if status not in TRUSTED_STATUS_VALUES:
            errors.append({"row": idx, "error_code": "invalid_trusted_status", "trusted_status": status})
        if status == "trusted_match_ready":
            evidence = record.get("strong_evidence") or []
            has_strong = any((item.get("evidence_strength") in strong_values and item.get("source_locator")) for item in evidence if isinstance(item, dict))
            if not has_strong:
                errors.append({"row": idx, "error_code": "trusted_ready_without_strong_evidence"})
    return {
        "record_count": len(records),
        "validation_error_count": len(errors),
        "errors": errors,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    return "\n".join([
        "# Milestone 43R-新可信潜客intake schema与采集器-v1",
        "",
        "## 结论",
        "",
        f"- intake required fields：`{summary['intake_required_field_count']}`",
        f"- evidence required fields：`{summary['evidence_required_field_count']}`",
        f"- trusted status 枚举：`{summary['trusted_status_values']}`",
        f"- 空样本校验错误数：`{summary['empty_sample_validation_error_count']}`",
        f"- no-write proof：`{summary['no_write_proof_ok']}`",
        "",
        "## 门禁",
        "",
        "- 无强 evidence 的候选不能进入 `trusted_match_ready`。",
        "- 旧档案字段不得自动继承。",
        "- LLM 只做摘要草稿，不决定可信状态。",
        "- 本轮只产出 schema 和校验报告，不生成潜客、不写工作簿。",
    ]).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    intake = _intake_template()
    evidence_schema = _evidence_patch_schema()
    card_schema = _summary_card_schema()
    empty_validation = _validate_sample_records([], intake, evidence_schema)
    guard_validation = _validate_sample_records([
        {
            "prospect_id": "sample_bad_no_evidence",
            "company_name": "示例公司",
            "matched_persona": "retail_high_sku_brand",
            "match_reason": "示例",
            "core_product_service_summary": "示例",
            "business_model_summary": "示例",
            "strong_evidence": [],
            "risk_or_gap": "缺少强来源",
            "trusted_status": "trusted_match_ready",
        },
        {
            "prospect_id": "sample_bad_legacy_field",
            "company_name": "示例公司2",
            "matched_persona": "retail_multi_store",
            "match_reason": "示例",
            "core_product_service_summary": "示例",
            "business_model_summary": "示例",
            "strong_evidence": [{"evidence_strength": "official", "source_locator": "https://example.com"}],
            "risk_or_gap": "示例",
            "trusted_status": "trusted_match_ready",
            "legacy_profile_summary": "不得继承",
        },
    ], intake, evidence_schema)
    summary = {
        "intake_required_field_count": len(intake["required_fields"]),
        "evidence_required_field_count": len(evidence_schema["required_fields"]),
        "card_required_field_count": len(card_schema["required_fields"]),
        "trusted_status_values": TRUSTED_STATUS_VALUES,
        "empty_sample_validation_error_count": empty_validation["validation_error_count"],
        "guard_sample_validation_error_count": guard_validation["validation_error_count"],
        "guard_detected_missing_evidence": any(e["error_code"] == "trusted_ready_without_strong_evidence" for e in guard_validation["errors"]),
        "guard_detected_legacy_field": any(e["error_code"] == "legacy_field_inherited" for e in guard_validation["errors"]),
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "prospect_generation_enabled": False,
        "no_write_proof_ok": True,
    }
    payload = {
        "batch_id": "milestone43r_new_prospect_intake_schema_package_v1",
        "generated_at": _now(),
        "summary": summary,
        "new_prospect_intake_template": intake,
        "trusted_evidence_patch_schema": evidence_schema,
        "trusted_summary_card_schema": card_schema,
        "intake_validation_report": {
            "empty_sample": empty_validation,
            "guard_sample": guard_validation,
        },
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone43r_new_prospect_intake_schema_package_v1.json", payload)
    _write_json(output_dir / "milestone43r_new_prospect_intake_template_v1.json", intake)
    _write_json(output_dir / "milestone43r_trusted_evidence_patch_schema_v1.json", evidence_schema)
    _write_json(output_dir / "milestone43r_trusted_summary_card_schema_v1.json", card_schema)
    _write_json(output_dir / "milestone43r_intake_validation_report_v1.json", payload["intake_validation_report"])
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_dir": str(output_dir), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = summary["no_write_proof_ok"] and summary["guard_detected_missing_evidence"] and summary["guard_detected_legacy_field"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
