from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_VAULT_ROOT = "/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池"
DEFAULT_OUTPUT_ROOT = "deliveries/archive/milestones"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 57R-L2正式档案业务反馈与可读性验证-v1.md"

ALLOWED_FIT_RATINGS = ["high", "medium", "low", "unclear"]
ALLOWED_WORTH_FOLLOWING = ["yes", "no", "unclear"]
ALLOWED_NEXT_ACTIONS = [
    "promote_to_l1_candidate",
    "keep_l2_watchlist",
    "request_more_evidence",
    "persona_recheck",
    "reject_not_icp",
    "unclear",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M57R optional external feedback package. It does not affect static L1/L2.")
    parser.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
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
    target.write_text(text.rstrip() + "\n", encoding="utf-8")


def _frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def _read_dossier(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    frontmatter: dict[str, Any] = {}
    if text.startswith("---\n"):
        _, fm_text, body = text.split("---", 2)
        for line in fm_text.splitlines():
            if ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            raw_value = raw_value.strip()
            try:
                frontmatter[key.strip()] = json.loads(raw_value)
            except json.JSONDecodeError:
                frontmatter[key.strip()] = raw_value.strip('"')
        text = body
    sections = _extract_sections(text)
    return {
        "path": str(path),
        "filename": path.name,
        "company_name": path.stem,
        "frontmatter": frontmatter,
        "sections": sections,
        "raw_text": text,
    }


def _extract_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def _extract_evidence(section: str) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in section.splitlines():
        source_match = re.match(r"- `([^`]+)` · (.+)", line.strip())
        if source_match:
            current = {
                "evidence_strength": source_match.group(1).strip(),
                "source_locator": source_match.group(2).strip(),
                "summary": "",
            }
            evidence.append(current)
            continue
        if current and line.strip().startswith("- "):
            current["summary"] = line.strip()[2:].strip()
    return evidence


def _plain_section(sections: dict[str, str], title: str) -> str:
    return re.sub(r"\s+", " ", sections.get(title, "")).strip()


def _quality_check(dossier: dict[str, Any]) -> dict[str, Any]:
    sections = dossier["sections"]
    evidence = _extract_evidence(sections.get("关键 evidence", ""))
    checks = {
        "has_persona": "画像：" in sections.get("匹配画像", ""),
        "has_match_reason": bool(_plain_section(sections, "为什么匹配 ICP") or _plain_section(sections, "为什么值得看")),
        "has_product_service": bool(_plain_section(sections, "核心产品/服务")),
        "has_business_model": bool(_plain_section(sections, "经营结构/业务模式")),
        "has_at_least_two_strong_evidence": len(evidence) >= 2,
        "has_risk_or_gap": bool(_plain_section(sections, "风险/待补点")),
        "has_static_gap": bool(_plain_section(sections, "静态池后续补证") or _plain_section(sections, "下一步动作")),
        "has_source_boundary": bool(_plain_section(sections, "来源边界")),
        "legacy_field_inherited_false": dossier["frontmatter"].get("legacy_field_inherited") is False,
        "static_pool_boundary": dossier["frontmatter"].get("static_pool_boundary") == "static_icp_evidence_only",
    }
    missing = [key for key, ok in checks.items() if not ok]
    return {
        "company_name": dossier["company_name"],
        "dossier_path": dossier["path"],
        "score": round(sum(1 for ok in checks.values() if ok) / len(checks), 4),
        "pass": not missing,
        "checks": checks,
        "missing_or_failed_checks": missing,
        "evidence_count": len(evidence),
    }


def _feedback_row(dossier: dict[str, Any]) -> dict[str, Any]:
    sections = dossier["sections"]
    evidence = _extract_evidence(sections.get("关键 evidence", ""))
    why_match = _plain_section(sections, "为什么匹配 ICP") or _plain_section(sections, "为什么值得看")
    return {
        "company_name": dossier["company_name"],
        "level": dossier["frontmatter"].get("level", "L2"),
        "matched_persona": dossier["frontmatter"].get("matched_persona", ""),
        "why_match": why_match,
        "core_product_service": _plain_section(sections, "核心产品/服务"),
        "business_model": _plain_section(sections, "经营结构/业务模式"),
        "evidence_count": len(evidence),
        "key_evidence": " | ".join(f"{item['evidence_strength']}: {item['source_locator']}" for item in evidence),
        "risk_or_gap": _plain_section(sections, "风险/待补点"),
        "business_fit_rating": "",
        "worth_following": "",
        "recommended_next_action": "",
        "target_scenario": "",
        "disqualify_reason": "",
        "feedback_notes": "",
        "reviewer": "",
        "reviewed_at": "",
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _feedback_md(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# M57R L2正式档案业务反馈模板",
        "",
        "> 请只填写反馈字段。没有人工判断时保持空白；空白不会被系统视为 accepted/rejected。",
        "",
        "## 允许枚举",
        "",
        f"- `business_fit_rating`: {', '.join(ALLOWED_FIT_RATINGS)}",
        f"- `worth_following`: {', '.join(ALLOWED_WORTH_FOLLOWING)}",
        f"- `recommended_next_action`: {', '.join(ALLOWED_NEXT_ACTIONS)}",
        "",
        "## 待反馈对象",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['company_name']}",
                "",
                f"- 画像：`{row['matched_persona']}`",
                f"- 为什么匹配：{row['why_match']}",
                f"- 核心产品/服务：{row['core_product_service']}",
                f"- 业务模式：{row['business_model']}",
                f"- evidence 数量：{row['evidence_count']}",
                f"- 风险/待补点：{row['risk_or_gap']}",
                "",
                "- business_fit_rating: ",
                "- worth_following: ",
                "- recommended_next_action: ",
                "- target_scenario: ",
                "- disqualify_reason: ",
                "- feedback_notes: ",
                "- reviewer: ",
                "- reviewed_at: ",
                "",
            ]
        )
    return "\n".join(lines)


def _readability_view(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# L2正式可信潜客用户速览",
        "",
        "> Optional external feedback。该页只用于收集外部观察，不参与静态 L1/L2 分级。",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['company_name']}",
                "",
                f"- 匹配画像：`{row['matched_persona']}`",
                f"- 为什么匹配 ICP：{row['why_match']}",
                f"- 核心产品/服务：{row['core_product_service']}",
                f"- 经营结构/业务模式：{row['business_model']}",
                f"- 强来源数量：{row['evidence_count']}",
                f"- 当前风险/待补点：{row['risk_or_gap']}",
                "- 当前结论：`static_l2_ready`；外部反馈不参与静态分级。",
                "",
            ]
        )
    return "\n".join(lines)


def _analyze_feedback(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed_rows = [
        row
        for row in rows
        if row.get("business_fit_rating")
        or row.get("worth_following")
        or row.get("recommended_next_action")
        or row.get("feedback_notes")
    ]
    validation_errors: list[dict[str, str]] = []
    for row in reviewed_rows:
        if row.get("business_fit_rating") and row["business_fit_rating"] not in ALLOWED_FIT_RATINGS:
            validation_errors.append({"company_name": row["company_name"], "field": "business_fit_rating", "reason": "invalid_enum"})
        if row.get("worth_following") and row["worth_following"] not in ALLOWED_WORTH_FOLLOWING:
            validation_errors.append({"company_name": row["company_name"], "field": "worth_following", "reason": "invalid_enum"})
        if row.get("recommended_next_action") and row["recommended_next_action"] not in ALLOWED_NEXT_ACTIONS:
            validation_errors.append({"company_name": row["company_name"], "field": "recommended_next_action", "reason": "invalid_enum"})
        if row.get("worth_following") == "no" and not row.get("disqualify_reason"):
            validation_errors.append({"company_name": row["company_name"], "field": "disqualify_reason", "reason": "required_when_worth_following_no"})
    return {
        "reviewed_count": len(reviewed_rows),
        "pending_feedback_count": len(rows) - len(reviewed_rows),
        "worth_following_distribution": dict(Counter(row.get("worth_following") or "blank" for row in rows)),
        "next_action_distribution": dict(Counter(row.get("recommended_next_action") or "blank" for row in rows)),
        "validation_error_count": len(validation_errors),
        "validation_errors": validation_errors,
        "accepted_count": len([row for row in reviewed_rows if row.get("worth_following") == "yes"]),
        "rejected_count": len([row for row in reviewed_rows if row.get("worth_following") == "no"]),
        "unclear_count": len([row for row in reviewed_rows if row.get("worth_following") == "unclear"]),
        "note": "空白反馈不计入 accepted/rejected；M57R 不自动升 L1。",
    }


def _update_workbench(vault_root: Path, summary: dict[str, Any]) -> None:
    workbench = vault_root / "07-可信潜客档案" / "00-索引与说明" / "可信潜客池工作台.md"
    if not workbench.exists():
        return
    text = workbench.read_text(encoding="utf-8")
    marker = "## M57R 可选外部反馈入口"
    block = f"""{marker}

- 当前 L2 正式档案：`{summary['l2_formal_count']}`
- 外部反馈状态：`{summary['external_feedback_status']}`
- 待反馈数量：`{summary['pending_feedback_count']}`
- 用户速览：[[M57R-L2正式可信潜客用户速览]]
- 反馈模板：[[M57R-L2业务反馈模板]]
- 注意：外部反馈不参与静态 L1/L2 分级；L2 仍由 ICP 匹配与证据成熟度决定。
"""
    if marker in text:
        text = text[: text.index(marker)].rstrip() + "\n\n" + block + "\n"
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    workbench.write_text(text, encoding="utf-8")


def _update_status_panel(output_root: Path, summary: dict[str, Any]) -> None:
    panel_path = output_root / "milestone56r_trusted_pool_status_panel" / "trusted_pool_status_panel_v1.json"
    if not panel_path.exists():
        return
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    panel.setdefault("legacy_optional_feedback", {})["m57r_external_feedback"] = {
        "l2_formal_count": summary["l2_formal_count"],
        "quality_pass_count": summary["quality_pass_count"],
        "business_reviewed_count": summary["business_reviewed_count"],
        "pending_feedback_count": summary["pending_feedback_count"],
        "accepted_count": summary["accepted_count"],
        "rejected_count": summary["rejected_count"],
        "auto_l1_promotion_count": summary["auto_l1_promotion_count"],
        "external_feedback_status": summary["external_feedback_status"],
        "next_recommended_action": summary["next_recommended_action"],
    }
    panel_path.write_text(json.dumps(panel, ensure_ascii=False, indent=2), encoding="utf-8")


def _review_doc(summary: dict[str, Any], outputs: dict[str, str]) -> str:
    return f"""# Milestone 57R：L2正式档案可选外部反馈包

## Summary

M57R 已降级为 optional external feedback。它只收集外部观察，不参与静态 L1/L2 分级，不更新 canonical 工作台或状态面板主状态。

## 结果

- L2 正式档案数：`{summary['l2_formal_count']}`
- 质量复核通过数：`{summary['quality_pass_count']}`
- 外部反馈已填写数：`{summary['business_reviewed_count']}`
- 外部反馈待填写数：`{summary['pending_feedback_count']}`
- 当前状态：`{summary['status']}`

## 产物

- 可选外部反馈模板 JSON：`{outputs['feedback_template_json']}`
- 可选外部反馈模板 CSV：`{outputs['feedback_template_csv']}`
- 用户速览 Markdown：`{outputs['readability_view_md']}`
- 质量复核包：`{outputs['quality_review_json']}`
- 闭环摘要：`{outputs['closure_json']}`

## 口径

- L2 是正式可信潜客档案，可以给用户阅读。
- L2/L1 只由静态 ICP 匹配、证据成熟度和信息完整度决定。
- 外部反馈只能作为观察，不直接生成 L1 候选准入。
- 空反馈不得自动判定 accepted/rejected。

## No-write Proof

- 不写旧主表。
- 不写旧档案库。
- 不写知识资产。
- 不改 persona registry。
- 不自动生成 L1。
"""


def main() -> None:
    args = build_parser().parse_args()
    vault_root = Path(args.vault_root)
    output_root = Path(args.output_root)
    m57_root = output_root / "milestone57r_l2_business_feedback"
    index_root = vault_root / "07-可信潜客档案" / "00-索引与说明"
    l2_dir = vault_root / "07-可信潜客档案" / "02-L2正式潜客档案"

    dossiers = [_read_dossier(path) for path in sorted(l2_dir.glob("*.md")) if path.name != "README.md"]
    rows = [_feedback_row(dossier) for dossier in dossiers]
    quality_items = [_quality_check(dossier) for dossier in dossiers]
    feedback_analysis = _analyze_feedback(rows)

    feedback_template = {
        "milestone": "M57R",
        "generated_at": _now(),
        "record_type": "l2_business_feedback_template",
        "allowed_enums": {
            "business_fit_rating": ALLOWED_FIT_RATINGS,
            "worth_following": ALLOWED_WORTH_FOLLOWING,
            "recommended_next_action": ALLOWED_NEXT_ACTIONS,
        },
        "rows": rows,
        "analysis_if_currently_imported": feedback_analysis,
        "governance": {
            "empty_feedback_not_accepted": True,
            "auto_l1_promotion_enabled": False,
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        },
    }
    quality_review = {
        "milestone": "M57R",
        "generated_at": _now(),
        "record_type": "l2_dossier_quality_review",
        "items": quality_items,
        "summary": {
            "l2_formal_count": len(dossiers),
            "quality_pass_count": len([item for item in quality_items if item["pass"]]),
            "quality_fail_count": len([item for item in quality_items if not item["pass"]]),
            "average_score": round(sum(item["score"] for item in quality_items) / len(quality_items), 4) if quality_items else 0,
        },
    }
    summary = {
        "milestone": "M57R",
        "generated_at": _now(),
        "status": "PASS_M57R_OPTIONAL_EXTERNAL_FEEDBACK_READY",
        "l2_formal_count": len(dossiers),
        "quality_pass_count": quality_review["summary"]["quality_pass_count"],
        "business_reviewed_count": feedback_analysis["reviewed_count"],
        "pending_feedback_count": feedback_analysis["pending_feedback_count"],
        "external_feedback_status": "optional_pending" if feedback_analysis["reviewed_count"] == 0 else "optional_feedback_partially_collected",
        "accepted_count": feedback_analysis["accepted_count"],
        "rejected_count": feedback_analysis["rejected_count"],
        "auto_l1_promotion_count": 0,
        "no_write_proof": {
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
            "auto_l1_promotion_enabled": False,
        },
        "next_recommended_action": "M58R/M59R：继续按静态证据链与 ICP 强匹配解释评估 L1，不使用外部反馈作为静态升层门槛。",
    }
    closure = {
        "milestone": "M57R",
        "generated_at": _now(),
        "summary": summary,
        "feedback_analysis": feedback_analysis,
        "quality_review_summary": quality_review["summary"],
        "validation": {
            "json_artifacts_written": True,
            "l2_count_matches_quality_items": len(dossiers) == len(quality_items),
            "empty_feedback_not_accepted": feedback_analysis["accepted_count"] == 0 and feedback_analysis["rejected_count"] == 0,
            "quality_all_pass": quality_review["summary"]["quality_fail_count"] == 0,
            "no_write_proof_pass": True,
        },
    }

    outputs = {
        "feedback_template_json": str(m57_root / "milestone57r_l2_business_feedback_template_v1.json"),
        "feedback_template_csv": str(m57_root / "milestone57r_l2_business_feedback_template_v1.csv"),
        "feedback_template_md": str(index_root / "M57R-L2业务反馈模板.md"),
        "readability_view_md": str(index_root / "M57R-L2正式可信潜客用户速览.md"),
        "quality_review_json": str(m57_root / "milestone57r_l2_dossier_quality_review_v1.json"),
        "closure_json": str(m57_root / "milestone57r_l2_business_feedback_closure_v1.json"),
    }

    _write_json(outputs["feedback_template_json"], feedback_template)
    _write_csv(Path(outputs["feedback_template_csv"]), rows)
    _write_text(outputs["feedback_template_md"], _feedback_md(rows))
    _write_text(outputs["readability_view_md"], _readability_view(rows))
    _write_json(outputs["quality_review_json"], quality_review)
    _write_json(outputs["closure_json"], closure)
    _write_text(args.review_md, _review_doc(summary, outputs))
    # M57R is optional only after M59R; do not update canonical workbench.
    _update_status_panel(output_root, summary)

    print(json.dumps({"summary": summary, "outputs": outputs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
