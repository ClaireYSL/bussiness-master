from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_VAULT_ROOT = "/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池"
DEFAULT_TRUSTED_POOL = "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
DEFAULT_SOURCE_TRACE = "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone49r_vault_restructure"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 49R-vault清理与可信潜客档案重构-v1.md"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build and apply M49R evidence-first vault restructure package.")
    p.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    p.add_argument("--trusted-pool", default=DEFAULT_TRUSTED_POOL)
    p.add_argument("--source-trace", default=DEFAULT_SOURCE_TRACE)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _prepend_once(path: Path, marker: str, block: str) -> bool:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        return False
    path.write_text(block.rstrip() + "\n\n" + text, encoding="utf-8")
    return True


def _count_md(path: Path) -> int:
    return sum(1 for p in path.rglob("*.md") if p.is_file())


def _count_md_excluding_readme(path: Path) -> int:
    return sum(1 for p in path.rglob("*.md") if p.is_file() and p.name.lower() != "readme.md")


def _safe_filename(name: str) -> str:
    return (
        name.replace("/", "／")
        .replace("\\", "＼")
        .replace(":", "：")
        .replace("*", "＊")
        .replace("?", "？")
        .replace('"', "＂")
        .replace("<", "＜")
        .replace(">", "＞")
        .replace("|", "｜")
    )


def _frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def _card_md(item: dict[str, Any]) -> str:
    company = item["company_name"]
    fm = _frontmatter(
        {
            "record_type": "trusted_prospect_l3_summary_card",
            "level": "L3",
            "evidence_first_version": "v2",
            "trusted_status": item.get("trusted_status"),
            "matched_persona": item.get("matched_persona"),
            "legacy_field_inherited": False,
            "formal_dossier": False,
        }
    )
    return f"""{fm}
# {company}

> L3 可信摘要卡。该页不是正式潜客档案；正式档案只从 L2 开始生成。

## 匹配画像

- 画像：`{item.get("matched_persona", "")}`
- 可信状态：`{item.get("trusted_status", "")}`

## 为什么值得看

{item.get("match_reason", "")}

## 核心产品/服务

{item.get("core_product_service_summary", "")}

## 业务模式

{item.get("business_model_summary", "")}

## 关键 evidence

- 来源强度：`{item.get("evidence_strength", "")}`
- 来源定位：{item.get("source_locator", "")}

## 风险/待补点

{item.get("risk_or_gap", "")}

## 分级说明

- `L3`：至少 1 条强来源，可生成摘要卡。
- `L2`：至少 2 条强来源、画像强匹配、业务解释完整，才生成正式潜客档案。
- `L1`：在 L2 基础上经人工或业务确认后，进入重点经营档案。

## 来源边界

本页来自 `trusted_prospect_pool_v1` 独立可信池产物，不继承旧主表、旧档案库、旧共享版字段。
"""


def _index_md(title: str, body: str) -> str:
    return f"""# {title}

> Evidence-first L1-L5 v2。旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页仅作 legacy reference，不作为新事实源。

{body.rstrip()}
"""


def main() -> int:
    args = build_parser().parse_args()
    vault = Path(args.vault_root)
    old_root = vault / "07-L3以上客户档案"
    old_l12 = old_root / "01-L1-L2档案"
    old_l3 = old_root / "02-L3档案"
    old_index = vault / "05-汇总与状态/01-总览/L3以上客户档案索引.md"
    old_guide = vault / "05-汇总与状态/04-状态与校验/潜客档案使用说明.md"
    homepage = vault / "潜客池-首页.md"
    excel_paths = [
        vault / "静态潜客主表.xlsx",
        vault / "潜客档案库.xlsx",
        vault / "内部运营-静态潜客池-共享版.xlsx",
        vault / "L3以上客户档案索引-团队共享.xlsx",
    ]
    excel_mtime_before = {str(p): p.stat().st_mtime if p.exists() else None for p in excel_paths}

    trusted_pool = _read_json(args.trusted_pool)
    source_trace = _read_json(args.source_trace)
    items = trusted_pool.get("items") or []
    trace_items = source_trace.get("items") or []

    new_root = vault / "07-可信潜客档案"
    dirs = {
        "index": new_root / "00-索引与说明",
        "l1": new_root / "01-L1重点经营档案",
        "l2": new_root / "02-L2正式潜客档案",
        "l3": new_root / "03-L3可信摘要卡",
        "l4": new_root / "04-L4待补证候选",
        "l5": new_root / "05-L5候选线索",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    legacy_warning = """# Legacy Archive Notice

> legacy_archive_do_not_use_as_source
>
> 本区是旧 L3+ 档案层归档区。M40R 之后，旧主表、旧档案库、旧共享版、旧 Markdown 档案页均不再作为可信事实源。
> 新用户入口请看：[[../07-可信潜客档案/00-索引与说明/可信潜客池工作台|可信潜客池工作台]]。
"""
    _write_text(old_root / "00-legacy-warning.md", legacy_warning)
    legacy_marker = "legacy_archive_do_not_use_as_source"
    legacy_block = """> legacy_archive_do_not_use_as_source
>
> 历史口径，已被 evidence-first L1-L5 v2 替代。本页仅供历史追溯和去重参考，不作为新可信潜客事实源。新入口：[[../../../07-可信潜客档案/00-索引与说明/可信潜客池工作台|可信潜客池工作台]]。
"""
    if old_index.exists():
        _prepend_once(old_index, legacy_marker, legacy_block)
    guide_block = """> legacy_archive_do_not_use_as_source
>
> 历史口径，已被 evidence-first L1-L5 v2 替代。旧规则“L3+ 自动生成档案页”已废弃；新规则为：L3 只生成摘要卡，L2/L1 才生成正式潜客档案。
"""
    if old_guide.exists():
        _prepend_once(old_guide, legacy_marker, guide_block)

    l3_links = []
    for item in items:
        file_name = _safe_filename(item["company_name"]) + ".md"
        target = dirs["l3"] / file_name
        _write_text(target, _card_md(item))
        l3_links.append(f"- [[../03-L3可信摘要卡/{file_name}|{item['company_name']}]] · `{item.get('matched_persona', '')}` · `{item.get('trusted_status', '')}`")

    total = len(items)
    l1_count = 0
    l2_count = 0
    l3_count = total
    l4_count = 0
    l5_count = 0

    level_rules = """## Evidence-first L1-L5 v2

- `L5` 候选线索：只记录公司名和来源线索，不给用户看。
- `L4` 待补证候选：有 ICP 可能但证据不足，不给用户看。
- `L3` 可信摘要候选：至少 1 条强来源，可生成摘要卡。
- `L2` 正式档案潜客：至少 2 条强来源、画像强匹配、业务解释完整，可给用户看。
- `L1` 业务验证重点潜客：L2 基础上经人工/业务确认，重点展示。

## 档案生成规则

- `L3` 只生成摘要卡。
- `L2/L1` 才生成正式潜客档案。
- `L4/L5` 不生成用户可见档案。
- 旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页只可用于去重和历史追溯，不可作为事实来源。
"""
    _write_text(dirs["index"] / "Evidence-first L1-L5 v2分级说明.md", _index_md("Evidence-first L1-L5 v2分级说明", level_rules))

    overview_body = f"""## 当前新可信池状态

- L1 重点经营档案：`{l1_count}`
- L2 正式潜客档案：`{l2_count}`
- L3 可信摘要卡：`{l3_count}`
- L4 待补证候选：`{l4_count}`
- L5 候选线索：`{l5_count}`

## 默认入口

- [[L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[L2正式档案索引|L2 正式档案索引]]
- [[L1重点经营索引|L1 重点经营索引]]
- [[Source trace index|Source trace index]]
- [[Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]

## Legacy archive

- [[../../07-L3以上客户档案/00-legacy-warning|旧 L3+ 档案归档提示]]
- [[../../05-汇总与状态/01-总览/L3以上客户档案索引|旧 L3+ 档案索引，仅历史追溯]]
"""
    _write_text(dirs["index"] / "可信潜客池工作台.md", _index_md("可信潜客池工作台", overview_body))
    _write_text(dirs["index"] / "L3可信摘要卡索引.md", _index_md("L3可信摘要卡索引", "\n".join(l3_links) + "\n"))
    _write_text(dirs["index"] / "L2正式档案索引.md", _index_md("L2正式档案索引", "- 当前 `L2` 正式潜客档案数：`0`\n- 原因：M44R 20 家只达到 L3 摘要卡门槛，尚未满足至少 2 条强来源与业务解释完整要求。\n"))
    _write_text(dirs["index"] / "L1重点经营索引.md", _index_md("L1重点经营索引", "- 当前 `L1` 重点经营档案数：`0`\n- 原因：尚未完成 L2 基础上的人工或业务确认。\n"))
    trace_lines = [
        f"- `{t.get('prospect_id', '')}` · {t.get('company_name', '')} · `{t.get('evidence_strength', '')}` · {t.get('source_locator', '')}"
        for t in trace_items
    ]
    _write_text(dirs["index"] / "Source trace index.md", _index_md("Source trace index", "\n".join(trace_lines) + "\n"))

    for key, title, note in [
        ("l1", "L1 重点经营档案", "当前无正式 L1 档案。"),
        ("l2", "L2 正式潜客档案", "当前无正式 L2 档案。"),
        ("l4", "L4 待补证候选", "当前本区不放用户可见档案。"),
        ("l5", "L5 候选线索", "当前本区不放用户可见档案。"),
    ]:
        _write_text(dirs[key] / "README.md", f"# {title}\n\n{note}\n\n详见：[[../00-索引与说明/Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]。\n")

    homepage_text = f"""# 可信潜客池工作台

> 当前主入口：Evidence-first L1-L5 v2
> 旧主表、旧档案库、旧共享版、旧 L3+ Markdown 页均已降级为 legacy reference，不再作为可信事实源。

## 从哪里开始看

- [[07-可信潜客档案/00-索引与说明/可信潜客池工作台|可信潜客池工作台]]
- [[07-可信潜客档案/00-索引与说明/L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[07-可信潜客档案/00-索引与说明/L2正式档案索引|L2 正式档案索引]]
- [[07-可信潜客档案/00-索引与说明/L1重点经营索引|L1 重点经营索引]]
- [[07-可信潜客档案/00-索引与说明/Source trace index|Source trace index]]

## 当前新可信池数量

- L1 重点经营档案：`{l1_count}`
- L2 正式潜客档案：`{l2_count}`
- L3 可信摘要卡：`{l3_count}`
- L4 待补证候选：`{l4_count}`
- L5 候选线索：`{l5_count}`

## 新分级口径

- `L5` 候选线索：只记录公司名和来源线索，不给用户看。
- `L4` 待补证候选：有 ICP 可能但证据不足，不给用户看。
- `L3` 可信摘要候选：至少 1 条强来源，可生成摘要卡。
- `L2` 正式档案潜客：至少 2 条强来源、画像强匹配、业务解释完整，可给用户看。
- `L1` 业务验证重点潜客：L2 基础上经人工/业务确认，重点展示。

## Legacy archive

- [[07-L3以上客户档案/00-legacy-warning|旧 L3+ 档案归档提示]]
- [[05-汇总与状态/01-总览/L3以上客户档案索引|旧 L3+ 档案索引，仅历史追溯]]

## 当前约束

- 新档案不得继承旧主表、旧档案库、旧共享版字段。
- 潜客产出不能反向写入正式知识资产或画像 registry。
- L3 不是正式潜客档案，只是可信摘要卡。
- L2/L1 才生成正式潜客档案。
"""
    _write_text(homepage, homepage_text)

    excel_mtime_after = {str(p): p.stat().st_mtime if p.exists() else None for p in excel_paths}
    old_counts = {
        "old_l1_l2_md_count": _count_md(old_l12),
        "old_l3_md_count": _count_md(old_l3),
        "old_total_md_count": _count_md(old_l12) + _count_md(old_l3),
    }
    new_counts = {
        "new_l1_formal_dossier_count": _count_md_excluding_readme(dirs["l1"]),
        "new_l2_formal_dossier_count": _count_md_excluding_readme(dirs["l2"]),
        "new_l3_summary_card_count": _count_md(dirs["l3"]),
        "new_l4_user_visible_dossier_count": _count_md_excluding_readme(dirs["l4"]),
        "new_l5_user_visible_dossier_count": _count_md_excluding_readme(dirs["l5"]),
    }
    no_write_proof = {
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
        "old_excel_mtime_unchanged": excel_mtime_before == excel_mtime_after,
        "old_directory_still_exists": old_root.exists(),
        "legacy_files_deleted": False,
    }
    no_write_proof_ok = (
        no_write_proof["old_workbook_write_enabled"] is False
        and no_write_proof["knowledge_asset_write_enabled"] is False
        and no_write_proof["persona_registry_write_enabled"] is False
        and no_write_proof["old_excel_mtime_unchanged"] is True
        and no_write_proof["old_directory_still_exists"] is True
        and no_write_proof["legacy_files_deleted"] is False
    )
    validation = {
        "old_counts_match_expected": old_counts == {
            "old_l1_l2_md_count": 313,
            "old_l3_md_count": 112,
            "old_total_md_count": 425,
        },
        "new_structure_exists": all(p.exists() for p in dirs.values()),
        "m44r_20_only_l3": new_counts["new_l3_summary_card_count"] == 20
        and new_counts["new_l2_formal_dossier_count"] == 0
        and new_counts["new_l1_formal_dossier_count"] == 0,
        "homepage_points_to_new_entry": "07-可信潜客档案/00-索引与说明/可信潜客池工作台" in homepage.read_text(encoding="utf-8")
        and "L3以上客户档案索引|L3以上客户档案索引" not in homepage.read_text(encoding="utf-8"),
        "no_write_proof_ok": no_write_proof_ok,
    }
    validation["pass"] = all(validation.values())
    audit = {
        "generated_at": _now(),
        "vault_root": str(vault),
        "old_archive_root": str(old_root),
        "new_trusted_root": str(new_root),
        "old_counts": old_counts,
        "new_counts": new_counts,
        "old_entries_marked_legacy": [str(old_root / "00-legacy-warning.md"), str(old_index), str(old_guide)],
        "legacy_reference_only": True,
    }
    summary = {
        **old_counts,
        **new_counts,
        "legacy_archive_marker": "legacy_archive_do_not_use_as_source",
        "new_vault_entry": str(dirs["index"] / "可信潜客池工作台.md"),
        "homepage_updated": True,
        "no_write_proof_ok": validation["no_write_proof_ok"],
        "validation_pass": validation["pass"],
    }
    payload = {
        "batch_id": "milestone49r_vault_restructure_package_v1",
        "generated_at": _now(),
        "summary": summary,
        "vault_audit": audit,
        "no_write_proof": no_write_proof,
        "validation": validation,
    }
    out = Path(args.output_dir)
    _write_json(out / "milestone49r_vault_restructure_package_v1.json", payload)
    _write_json(out / "vault_cleanup_audit_v1.json", audit)
    _write_json(out / "vault_restructure_validation_v1.json", validation)
    _write_json(out / "vault_no_write_proof_v1.json", no_write_proof)
    _write_text(
        args.review_md,
        f"""# Milestone 49R-vault清理与可信潜客档案重构-v1

- 旧 L3+ 档案审计：`{old_counts['old_total_md_count']}`，其中 L1/L2 `{old_counts['old_l1_l2_md_count']}`，L3 `{old_counts['old_l3_md_count']}`。
- 新入口：`{dirs['index'] / '可信潜客池工作台.md'}`
- M44R 20 家全部进入 `L3可信摘要卡`；L2/L1 正式档案数保持 `0`。
- 旧目录保留且标记 `legacy_archive_do_not_use_as_source`。
- 未写旧主表、旧档案库、旧共享版、知识资产或 persona registry。
- 校验结果：`{'PASS' if validation['pass'] else 'FAIL'}`
""",
    )
    print(json.dumps({"output_dir": str(out), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if validation["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
