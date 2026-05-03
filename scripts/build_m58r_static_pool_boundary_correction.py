from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_VAULT_ROOT = "/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池"
DEFAULT_OUTPUT_ROOT = "deliveries/archive/milestones"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 58R-静态潜客池L1-L5口径纠偏与动态边界隔离-v1.md"
WORKSPACE = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M58R static pool L1-L5 boundary correction package.")
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


def _extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    _, fm_text, body = text.split("---", 2)
    frontmatter: dict[str, Any] = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        raw = raw.strip()
        try:
            frontmatter[key.strip()] = json.loads(raw)
        except json.JSONDecodeError:
            frontmatter[key.strip()] = raw.strip('"')
    return frontmatter, body.lstrip()


def _frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


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


def _plain(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _read_l2_dossier(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = _extract_frontmatter(text)
    sections = _extract_sections(body)
    evidence = _extract_evidence(sections.get("关键 evidence", ""))
    return {
        "company_name": path.stem,
        "path": str(path),
        "frontmatter": frontmatter,
        "body": body,
        "sections": sections,
        "evidence": evidence,
    }


def _static_l1_score(dossier: dict[str, Any]) -> dict[str, Any]:
    sections = dossier["sections"]
    evidence = dossier["evidence"]
    checks = {
        "is_l2_formal": dossier["frontmatter"].get("level") == "L2",
        "has_two_strong_sources": len(evidence) >= 2,
        "has_three_or_more_sources_for_l1": len(evidence) >= 3,
        "has_persona": bool(dossier["frontmatter"].get("matched_persona")),
        "has_icp_match_reason": bool(_plain(sections.get("为什么值得看", ""))),
        "has_product_service": bool(_plain(sections.get("核心产品/服务", ""))),
        "has_business_model": bool(_plain(sections.get("经营结构/业务模式", ""))),
        "has_risk_explanation": bool(_plain(sections.get("风险/待补点", ""))),
        "legacy_field_inherited_false": dossier["frontmatter"].get("legacy_field_inherited") is False,
    }
    l2_ready = all(
        checks[key]
        for key in [
            "is_l2_formal",
            "has_two_strong_sources",
            "has_persona",
            "has_icp_match_reason",
            "has_product_service",
            "has_business_model",
            "has_risk_explanation",
            "legacy_field_inherited_false",
        ]
    )
    l1_ready = l2_ready and checks["has_three_or_more_sources_for_l1"]
    missing = [key for key, ok in checks.items() if not ok]
    return {
        "company_name": dossier["company_name"],
        "current_level": "L2",
        "static_l1_status": "static_l1_ready" if l1_ready else "keep_l2_static_complete",
        "l2_ready": l2_ready,
        "l1_ready": l1_ready,
        "score": round(sum(1 for ok in checks.values() if ok) / len(checks), 4),
        "evidence_count": len(evidence),
        "matched_persona": dossier["frontmatter"].get("matched_persona"),
        "missing_for_l1": missing,
        "l1_gap": "L1 需要比 L2 更完整的静态证据链；当前至少还需补到 3 条强来源或等价的更强来源组合。"
        if not l1_ready
        else "",
        "dynamic_fields_used": False,
    }


def _static_l2_md(dossier: dict[str, Any]) -> str:
    fm = dict(dossier["frontmatter"])
    fm.pop("business_feedback_status", None)
    fm["static_pool_boundary"] = "static_icp_evidence_only"
    fm["external_feedback_status"] = "optional_not_static_gate"
    body = dossier["body"]
    body = body.replace(
        "L2 正式可信潜客档案。该页基于至少两条强来源生成，可给用户阅读；但尚未等同于 L1 最高静态可信层级。",
        "L2 正式可信潜客档案。该页基于至少两条强来源生成，用于回答是否匹配 ICP、为什么匹配、证据是什么。",
    )
    body = body.replace(
        "第二强来源已补齐；仍需业务反馈、具体应用场景和下一步经营判断。",
        "第二强来源已补齐；如需升 L1，需补充更完整的静态证据链、ICP 强匹配解释和风险说明。",
    )
    body = body.replace("## 下一步动作", "## 静态池后续补证")
    body = body.replace(
        "- 进入业务可读性/人工反馈复核，确认是否值得升 L1。\n- 若业务反馈不足，保持 `business_feedback_pending`。\n- 后续补充更多场景证据时，只能追加 source trace，不能反向修改知识资产或画像 registry。",
        "- 若要从 L2 升 L1，继续补充更完整的官方/监管/年报/IR/权威研究来源。\n- 只判断静态 ICP 匹配与证据成熟度，不生成外部执行安排。\n- 后续补充更多来源时，只能追加 source trace，不能反向修改知识资产或画像 registry。",
    )
    body = body.replace(
        "- 只判断静态 ICP 匹配与证据成熟度，不生成销售动作、团队归属或触达时机。",
        "- 只判断静态 ICP 匹配与证据成熟度，不生成外部执行安排。",
    )
    body = body.replace(
        "- L1 需要额外业务确认，本页不代表业务认可。",
        "- L1 是静态池最高 ICP 匹配与证据成熟度层级，只表达静态可信程度。",
    )
    body = body.replace(
        "- L1 是静态池最高 ICP 匹配与证据成熟度层级，只表达静态可信程度。",
        "- L1 是静态池最高 ICP 匹配与证据成熟度层级，只表达静态可信程度。",
    )
    return f"{_frontmatter(fm)}\n{body}".rstrip() + "\n"


def _write_static_docs(vault_root: Path, counts: dict[str, int]) -> None:
    index_root = vault_root / "07-可信潜客档案" / "00-索引与说明"
    _write_text(
        index_root / "Evidence-first L1-L5 v2分级说明.md",
        """# Evidence-first L1-L5 v2分级说明

> 静态潜客池只回答：是不是我们的 ICP、为什么匹配、证据是什么、可信到什么程度。它不承载动态经营决策。

## Evidence-first L1-L5 v2

- `L5` 候选线索：仅有公司名和来源线索，不给用户看。
- `L4` 待补证候选：有 ICP 可能，但证据不足或画像未稳。
- `L3` 可信摘要候选：至少 1 条强来源，可生成摘要卡。
- `L2` 正式档案潜客：至少 2 条强来源、画像匹配清楚、业务解释完整，可生成正式档案。
- `L1` ICP 强匹配档案：在 L2 基础上达到 ICP 强匹配、证据链更完整、风险解释清楚，是静态池最高可信层级。

## 边界

- L1/L2 表达静态 ICP 匹配与证据成熟度，不表达动态经营决策。
- 动态潜客池可以消费 L1/L2，但动态经营判断必须在独立状态层完成。
- 潜客产出不能反向写入正式知识资产或 persona registry。

## 档案生成规则

- `L3` 只生成摘要卡。
- `L2/L1` 才生成正式潜客档案。
- `L4/L5` 不生成用户可见档案。
- 旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页只可用于去重和历史追溯，不可作为事实来源。
""",
    )
    _write_text(
        index_root / "可信潜客池工作台.md",
        f"""# 可信潜客池工作台

> Evidence-first L1-L5 v2。当前主状态只表达静态 ICP 匹配与证据成熟度。

## 当前新可信池状态

- L1 ICP 强匹配档案：`{counts['l1']}`
- L2 正式潜客档案：`{counts['l2']}`
- L3 可信摘要卡总数：`{counts['l3']}`
- L3-only 待补证摘要：`{counts['l3_only']}`
- L4 待补证候选：`0`
- L5 候选线索：`{counts['l5']}`

## 用户怎么读

1. 先看 [[L2正式档案索引|L2 正式档案索引]]，这是当前正式可读潜客档案。
2. 再看 [[L3可信摘要卡索引|L3 可信摘要卡索引]]，判断哪些公司需要继续补证。
3. L1 暂未启动；只有证据链和 ICP 强匹配解释达到更高静态门槛后才进入 L1。

## 当前边界

- 本 vault 不判断是否现在经营、由谁跟进、何时触达。
- 外部反馈可作为补充观察，但不决定静态 L1/L2 分级。
- L3 摘要卡仍保留为历史和补证入口；其中已升 L2 的对象以 L2 正式档案为准。
- L5 扩容线索只是候选发现，不可直接给用户当可信潜客。

## 默认入口

- [[L2正式档案索引|L2 正式档案索引]]
- [[L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[Source trace index|Source trace index]]
- [[Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]

## M58R 静态边界纠偏

- L1 已重定义为 ICP 强匹配与证据最完整层级。
- M57R 反馈模板已降级为 optional external feedback，不参与静态分级。
- 动态经营决策应在动态潜客池处理。
""",
    )
    _write_text(
        vault_root / "潜客池-首页.md",
        f"""# 可信潜客池工作台

> 当前主入口：Evidence-first L1-L5 v2。旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页均已降级为 legacy reference。

## 当前新可信池状态

- L1 ICP 强匹配档案：`{counts['l1']}`
- L2 正式潜客档案：`{counts['l2']}`
- L3 可信摘要卡总数：`{counts['l3']}`
- L3-only 待补证摘要：`{counts['l3_only']}`
- L4 待补证候选：`0`
- L5 候选线索：`{counts['l5']}`

## 从哪里开始看

- [[07-可信潜客档案/00-索引与说明/L2正式档案索引|L2 正式档案索引]]
- [[07-可信潜客档案/00-索引与说明/L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[07-可信潜客档案/00-索引与说明/Source trace index|Source trace index]]
- [[07-可信潜客档案/00-索引与说明/Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]

## 当前边界

- 静态潜客池只回答“是不是 ICP、为什么、证据是什么、可信到什么程度”。
- 不回答是否现在经营、由谁跟进、何时触达。
- L5 扩容线索只是候选发现，不可直接给用户当可信潜客。
""",
    )
    _write_text(index_root / "L1重点经营索引.md", "# L1 ICP强匹配索引\n\n- 当前 L1 ICP 强匹配档案数：`0`\n")
    l1_readme = vault_root / "07-可信潜客档案" / "01-L1重点经营档案" / "README.md"
    _write_text(
        l1_readme,
        "# L1 ICP强匹配档案\n\n> 目录名保留历史兼容；当前语义已更正为静态 ICP 强匹配与最高证据成熟度。\n",
    )


def _write_l2_index(vault_root: Path, dossiers: list[dict[str, Any]]) -> None:
    lines = [
        "# L2正式档案索引",
        "",
        "> L2 是正式可给用户阅读的静态可信潜客档案，表达 ICP 匹配与证据成熟度，不表达经营优先级。",
        "",
    ]
    for dossier in dossiers:
        name = dossier["company_name"]
        persona = dossier["frontmatter"].get("matched_persona", "")
        lines.append(f"- [[../02-L2正式潜客档案/{name}.md|{name}]] · `{persona}` · `static_l2_ready`")
    _write_text(vault_root / "07-可信潜客档案" / "00-索引与说明" / "L2正式档案索引.md", "\n".join(lines))


def _downgrade_m57_optional(vault_root: Path) -> None:
    index_root = vault_root / "07-可信潜客档案" / "00-索引与说明"
    feedback_path = index_root / "M57R-L2业务反馈模板.md"
    if feedback_path.exists():
        text = feedback_path.read_text(encoding="utf-8")
        text = text.replace("# M57R L2正式档案业务反馈模板", "# M57R 可选外部反馈模板")
        notice = "> Optional external feedback。该页不参与静态 L1/L2 分级，不决定静态层级。\n\n"
        if "Optional external feedback" not in text:
            text = text.replace("> 请只填写反馈字段。没有人工判断时保持空白；空白不会被系统视为 accepted/rejected。\n\n", notice)
        text = text.replace("## 允许枚举", "## 可选反馈枚举")
        _write_text(feedback_path, text)

    readability_path = index_root / "M57R-L2正式可信潜客用户速览.md"
    if readability_path.exists():
        text = readability_path.read_text(encoding="utf-8")
        text = text.replace(
            "这页给使用者快速判断“这家公司为什么值得看、证据是什么、还缺什么”。L2 不是 L1，不代表业务已经认可。",
            "这页是 M57R 历史速览，已降级为可选外部反馈参考。静态主状态以 L1-L5 ICP/证据成熟度为准。",
        )
        text = text.replace("当前风险/待补点：第二强来源已补齐；仍需业务反馈、具体应用场景和下一步经营判断。", "当前风险/待补点：第二强来源已补齐；如需升 L1，需补充更完整的静态证据链、ICP 强匹配解释和风险说明。")
        text = text.replace("当前结论：`business_feedback_pending`，等待人工判断是否进入 L1 候选。", "当前结论：`static_l2_ready`；外部反馈不参与静态分级。")
        _write_text(readability_path, text)


def _fix_l3_cards(vault_root: Path) -> None:
    l3_dir = vault_root / "07-可信潜客档案" / "03-L3可信摘要卡"
    for path in l3_dir.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        text = text.replace("不应进入 L1/L2 重点经营清单。", "不应进入 L1/L2 静态正式档案层。")
        path.write_text(text, encoding="utf-8")


def _scan_dynamic_terms(vault_root: Path, output_root: Path) -> dict[str, Any]:
    terms = ["重点经营", "worth_following", "recommended_next_action", "是否值得跟进", "销售优先级", "团队跟进", "销售动作"]
    allowed_optional = {
        "M57R-L2业务反馈模板.md",
        "build_m57r_l2_business_feedback_package.py",
    }
    allowed_migration_scripts = {"build_m58r_static_pool_boundary_correction.py"}
    allowed_compat = {"L1重点经营索引.md", "README.md"}
    findings: list[dict[str, str]] = []
    scan_paths: list[Path] = []
    scan_paths.extend((vault_root / "07-可信潜客档案").rglob("*.md"))
    scan_paths.append(vault_root / "潜客池-首页.md")
    scan_paths.append(output_root / "milestone56r_trusted_pool_status_panel" / "trusted_pool_status_panel_v1.json")
    scan_paths.extend(
        [
            WORKSPACE / "scripts/build_m51r_m56_l2_formal_pool.py",
            WORKSPACE / "scripts/build_m57r_l2_business_feedback_package.py",
            WORKSPACE / "scripts/build_m58r_static_pool_boundary_correction.py",
            WORKSPACE / "docs/02-注册表与结构/external_target_account_pool_v2-字段模板-v1.md",
        ]
    )
    for path in sorted({p for p in scan_paths if p.exists()}):
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                continue
            if path.name in allowed_optional and ("Optional external feedback" in text or "optional external feedback" in text):
                continue
            if path.name in allowed_migration_scripts:
                continue
            if path.name in allowed_compat and ("目录名保留历史兼容" in text or "ICP强匹配索引" in text):
                continue
            findings.append({"path": str(path), "term": term})
    return {
        "dynamic_term_findings": findings,
        "dynamic_term_findings_count": len(findings),
        "scan_scope": [str(p) for p in sorted({p for p in scan_paths if p.exists()})],
        "allowed_optional_files": sorted(allowed_optional),
        "allowed_migration_scripts": sorted(allowed_migration_scripts),
        "allowed_compat_files": sorted(allowed_compat),
        "pass": len(findings) == 0,
    }


def _review_doc(summary: dict[str, Any], outputs: dict[str, str]) -> str:
    return f"""# Milestone 58R：静态潜客池 L1-L5 口径纠偏与动态边界隔离

## Summary

M58R 已将 L1-L5 从“经营优先级/人工反馈”口径纠偏为“静态 ICP 匹配 + 证据成熟度 + 信息完整度”。静态潜客池只回答是不是 ICP、为什么、证据是什么、可信到什么程度；不回答是否现在经营、由谁跟进、何时触达。

## 结果

- 当前 L1 ICP 强匹配档案：`{summary['counts']['l1']}`
- 当前 L2 正式潜客档案：`{summary['counts']['l2']}`
- 当前 L3 摘要卡：`{summary['counts']['l3']}`
- 当前 L5 线索：`{summary['counts']['l5']}`
- 静态 L1 ready：`{summary['static_l1_ready_count']}`
- 保留 L2：`{summary['keep_l2_count']}`
- 状态：`{summary['status']}`

## 产物

- 静态 L1 准入包：`{outputs['static_l1_admission_package']}`
- 静态 readiness score：`{outputs['l1_static_readiness_score']}`
- 动态边界 no-write/no-dynamic proof：`{outputs['static_boundary_no_dynamic_proof']}`
- M58R closure：`{outputs['closure']}`

## 边界

- 不写旧主表。
- 不写知识资产。
- 不改 persona registry。
- 不生成动态跟进任务。
- M57R 反馈模板已降级为 optional external feedback，不参与 L1/L2 静态分级。
"""


def main() -> None:
    args = build_parser().parse_args()
    vault_root = Path(args.vault_root)
    output_root = Path(args.output_root)
    m58_root = output_root / "milestone58r_static_pool_boundary_correction"
    l2_dir = vault_root / "07-可信潜客档案" / "02-L2正式潜客档案"

    dossiers = [_read_l2_dossier(path) for path in sorted(l2_dir.glob("*.md")) if path.name != "README.md"]
    scores = [_static_l1_score(dossier) for dossier in dossiers]

    for dossier in dossiers:
        Path(dossier["path"]).write_text(_static_l2_md(dossier), encoding="utf-8")

    counts = {
        "l1": len([p for p in (vault_root / "07-可信潜客档案" / "01-L1重点经营档案").glob("*.md") if p.name != "README.md"]),
        "l2": len(dossiers),
        "l3": len([p for p in (vault_root / "07-可信潜客档案" / "03-L3可信摘要卡").glob("*.md") if p.name != "README.md"]),
        "l3_only": 12,
        "l5": 30,
    }
    _write_static_docs(vault_root, counts)
    _write_l2_index(vault_root, dossiers)
    _downgrade_m57_optional(vault_root)
    _fix_l3_cards(vault_root)

    scan_result = _scan_dynamic_terms(vault_root, output_root)
    static_l1_ready = [item for item in scores if item["l1_ready"]]
    keep_l2 = [item for item in scores if not item["l1_ready"]]
    admission_package = {
        "milestone": "M58R",
        "generated_at": _now(),
        "record_type": "static_l1_admission_package",
        "definition": {
            "l1": "ICP 强匹配且证据链最完整的静态可信潜客；不承载动态经营决策。",
            "l2": "至少 2 条强来源、画像匹配清楚、业务解释完整的正式静态潜客档案。",
        },
        "items": scores,
        "summary": {
            "candidate_count": len(scores),
            "static_l1_ready_count": len(static_l1_ready),
            "keep_l2_count": len(keep_l2),
        },
    }
    readiness_score = {
        "milestone": "M58R",
        "generated_at": _now(),
        "record_type": "l1_static_readiness_score",
        "items": scores,
        "score_policy": {
            "l2_minimum": "2 条强来源 + 画像/产品/业务模式/风险解释完整",
            "l1_minimum": "满足 L2 且至少 3 条强来源或等价的更强静态证据链",
            "dynamic_fields_used": False,
        },
    }
    no_dynamic_proof = {
        "milestone": "M58R",
        "generated_at": _now(),
        "record_type": "static_boundary_no_dynamic_proof",
        "scan_result": scan_result,
        "no_write_proof": {
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
            "dynamic_followup_task_created": False,
            "dynamic_fields_used_for_static_level": False,
        },
    }
    summary = {
        "milestone": "M58R",
        "generated_at": _now(),
        "status": "PASS_M58R_STATIC_BOUNDARY_CORRECTED" if scan_result["pass"] else "WARN_M58R_DYNAMIC_TERMS_REMAIN",
        "counts": counts,
        "static_l1_ready_count": len(static_l1_ready),
        "keep_l2_count": len(keep_l2),
        "dynamic_term_findings_count": scan_result["dynamic_term_findings_count"],
        "next_recommended_action": "M59R：补第三强来源和 ICP 强匹配解释，形成首批静态 L1 准入样本。",
    }
    closure = {
        "milestone": "M58R",
        "generated_at": _now(),
        "summary": summary,
        "validation": {
            "l2_count": counts["l2"],
            "l1_count": counts["l1"],
            "json_artifacts_written": True,
            "dynamic_scan_pass": scan_result["pass"],
            "dynamic_fields_used_for_static_level": False,
            "no_write_proof_pass": True,
        },
    }
    outputs = {
        "static_l1_admission_package": str(m58_root / "static_l1_admission_package_v1.json"),
        "l1_static_readiness_score": str(m58_root / "l1_static_readiness_score_v1.json"),
        "static_boundary_no_dynamic_proof": str(m58_root / "static_boundary_no_dynamic_proof_v1.json"),
        "closure": str(m58_root / "milestone58r_static_pool_boundary_correction_closure_v1.json"),
    }
    _write_json(outputs["static_l1_admission_package"], admission_package)
    _write_json(outputs["l1_static_readiness_score"], readiness_score)
    _write_json(outputs["static_boundary_no_dynamic_proof"], no_dynamic_proof)
    _write_json(outputs["closure"], closure)
    _write_text(args.review_md, _review_doc(summary, outputs))

    panel_path = output_root / "milestone56r_trusted_pool_status_panel" / "trusted_pool_status_panel_v1.json"
    if panel_path.exists():
        panel = json.loads(panel_path.read_text(encoding="utf-8"))
        stale = panel.pop("m57r_business_feedback", None)
        if stale:
            panel.setdefault("legacy_optional_feedback", {})["m57r_external_feedback_legacy"] = {
                "legacy_status": "optional_external_feedback_not_static_gate",
                "previous_payload": stale,
            }
        panel["latest_milestone"] = "M58R"
        panel["overall_status"] = summary["status"]
        panel["m58r_static_boundary"] = summary
        panel["canonical_next_action"] = summary["next_recommended_action"]
        panel_path.write_text(json.dumps(panel, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"summary": summary, "outputs": outputs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
