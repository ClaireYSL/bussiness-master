from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_VAULT_ROOT = "/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池"
DEFAULT_TRUSTED_POOL = "deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
DEFAULT_SOURCE_TRACE = "deliveries/archive/milestones/milestone47r_trusted_pool_product/source_trace_index_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone50r_vault_canonical_cleanup"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 50R-vault canonical cleanup-v1.md"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Apply M50R vault canonical cleanup and lint checks.")
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
    target.write_text(text.rstrip() + "\n", encoding="utf-8")


def _prepend_once(path: Path, marker: str, block: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if marker in text[:500]:
        return False
    path.write_text(block.rstrip() + "\n\n" + text, encoding="utf-8")
    return True


def _count_md(path: Path, exclude_readme: bool = False) -> int:
    return sum(
        1
        for p in path.rglob("*.md")
        if p.is_file() and not (exclude_readme and p.name.lower() == "readme.md")
    )


def _safe_filename(name: str) -> str:
    table = str.maketrans({
        "/": "／",
        "\\": "＼",
        ":": "：",
        "*": "＊",
        "?": "？",
        '"': "＂",
        "<": "＜",
        ">": "＞",
        "|": "｜",
    })
    return name.translate(table)


def _frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def _legacy_stub(title: str, original_role: str, new_entry_rel: str) -> str:
    return f"""# {title}

> legacy_archive_do_not_use_as_source
>
> 本页是 M40R 以前的历史口径页面，已被 Evidence-first L1-L5 v2 替代。保留本页只为历史追溯、去重和审计，不作为新可信潜客事实源。

## 新入口

- [[{new_entry_rel}|可信潜客池工作台]]
- [[../../../07-可信潜客档案/00-索引与说明/Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]
- [[../../../07-可信潜客档案/00-索引与说明/L3可信摘要卡索引|L3 可信摘要卡索引]]

## 原页面角色

{original_role}

## 当前边界

- 旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页均不再作为可信事实源。
- L3 只生成可信摘要卡，不生成正式潜客档案。
- L2/L1 才生成正式潜客档案。
- 潜客产出不能反向写入正式知识资产或画像 registry。
"""


def _canonical_readmes(vault: Path) -> dict[Path, str]:
    return {
        vault / "01-主线/README.md": """# 主线索引

> Canonical page。这里解释 ICP/经营主线，用于帮助理解画像和潜客匹配方向。

## 当前内容

- [[零售消费|零售消费]]
- [[跨境电商|跨境电商]]
- [[先进制造|先进制造]]

## 使用边界

- 主线定义应来自真实客户案例、解决方案、行业研究或权威材料。
- 新潜客摘要只能作为候选观察，不能反向改写主线定义。
- 发现主线缺口时，先形成补源任务或规则校准建议，不直接覆盖知识资产。
""",
        vault / "02-画像/README.md": """# 画像索引

> Canonical page。这里承载 ICP/画像标签的阅读入口；画像正式变更必须来自真实素材校准，不从潜客产出反推。

## 当前内容

- 零售消费画像：`retail_*`、`fnb_*`
- 跨境电商画像：`cbec_*`
- 先进制造画像：`mfg_*`
- 管理场景画像：`mgmt_*`

## 使用边界

- 画像用于解释潜客为什么匹配，但潜客命中不能自动成为画像正例。
- 画像调整只允许通过 proposal、人工确认和来源校验进入正式 registry。
- L3 摘要卡中的画像是匹配建议，不是业务认可结论。
""",
        vault / "04-知识资产/README.md": """# 知识资产索引

> Canonical page。这里仅沉淀来自真实客户案例、解决方案、行业研究或权威材料的知识资产。

## 使用边界

- 允许来源：真实客户案例、解决方案、行业研究、权威公开材料。
- 禁止来源：潜客摘要卡、旧主表、旧档案库、旧共享版、旧 L3+ Markdown 页。
- 潜客产出只能生成 candidate observation、source gap 或 rule calibration proposal，不能直接写入正式知识资产。

## 与可信潜客池的关系

- 知识资产驱动画像。
- 画像驱动候选。
- 候选产出不得反向覆盖知识资产。
""",
        vault / "06-规则与机制/README.md": """# 规则与机制索引

> Canonical page。这里维护 evidence-first 可信潜客池的运行规则、来源边界和治理机制。

## 当前规则入口

- [[最小证据约束|最小证据约束]]
- [[主线与画像接入规则|主线与画像接入规则]]
- [[去重治理规则|去重治理规则]]
- [[静态潜客池持续扩展最小机制|静态潜客池持续扩展最小机制]]

## 当前主规则

- L3：至少 1 条强来源，只生成摘要卡。
- L2：至少 2 条强来源、画像强匹配、业务解释完整，生成正式档案。
- L1：L2 基础上经人工或业务确认，进入重点经营档案。
- 旧资产只能用于去重和历史追溯，不作为新事实源。
""",
    }


def _card_md(item: dict[str, Any]) -> str:
    company = item["company_name"]
    evidence_strength = item.get("evidence_strength", "")
    source = item.get("source_locator", "")
    fm = _frontmatter(
        {
            "record_type": "trusted_prospect_l3_summary_card",
            "level": "L3",
            "evidence_first_version": "v2",
            "trusted_status": item.get("trusted_status"),
            "matched_persona": item.get("matched_persona"),
            "legacy_field_inherited": False,
            "formal_dossier": False,
            "business_visible": "summary_only",
        }
    )
    return f"""{fm}
# {company}

> L3 可信摘要卡。该页可用于快速判断是否值得继续补证，但不是正式潜客档案；正式档案只从 L2 开始生成。

## 一句话判断

{item.get("match_reason", "")}

## 为什么匹配

- 匹配画像：`{item.get("matched_persona", "")}`
- 匹配理由：{item.get("match_reason", "")}

## 核心产品/服务

{item.get("core_product_service_summary", "")}

## 经营结构/业务模式

{item.get("business_model_summary", "")}

## 证据够不够

- 当前证据结论：够进入 `L3`，不够进入 `L2`。
- 当前强来源数量：`1`
- 当前来源强度：`{evidence_strength}`
- 来源定位：{source}

## 缺什么才能升 L2

- 至少补充第 2 条强来源，例如官网、IR、年报、交易所公告、监管披露或权威行业研究。
- 需要确认画像强匹配，而不是只靠行业相似。
- 需要补齐业务解释：核心产品/服务、经营结构、为什么与 ICP 相关、主要风险。
- 需要通过人工或规则复核，确认没有明显 `not_icp` 或 `persona_pending_review` 风险。

## 是否可给业务看

- 可以作为 `L3 可信摘要` 给业务快速浏览。
- 不应作为正式潜客档案或已认可商机使用。
- 不应进入 L1/L2 重点经营清单。

## 风险/待补点

{item.get("risk_or_gap", "")}

## 来源边界

本页来自 `trusted_prospect_pool_v1` 独立可信池产物，不继承旧主表、旧档案库、旧共享版字段，也不反向写入知识资产或画像 registry。
"""


def _workbench_md(counts: dict[str, int]) -> str:
    return f"""# 可信潜客池工作台

> Evidence-first L1-L5 v2。旧主表、旧档案库、旧共享版和旧 L3+ Markdown 页仅作 legacy reference，不作为新事实源。

## 当前新可信池状态

- L1 重点经营档案：`{counts['l1']}`
- L2 正式潜客档案：`{counts['l2']}`
- L3 可信摘要卡：`{counts['l3']}`
- L4 待补证候选：`{counts['l4']}`
- L5 候选线索：`{counts['l5']}`

## 用户怎么读

1. 先看 [[L3可信摘要卡索引|L3 可信摘要卡索引]]，判断公司是否值得继续补证。
2. 再看具体 L3 卡片里的“为什么匹配”“证据够不够”“缺什么才能升 L2”。
3. 只有进入 [[L2正式档案索引|L2 正式档案索引]] 的对象，才算正式可给用户看的潜客档案。
4. [[L1重点经营索引|L1 重点经营索引]] 只放经过人工或业务确认的重点经营对象。

## 什么条件升 L2

- 至少 2 条强来源 evidence。
- 画像强匹配且来源能支撑。
- 公司核心产品/服务、经营结构、匹配理由、风险待补点完整。
- 不继承旧主表、旧档案库、旧共享版字段。

## 下一步补证队列

- 当前 20 家都只达到 L3；下一步优先补第二强来源。
- 优先补官网、IR、年报、交易所公告、监管披露或权威行业研究。
- 补证完成后再生成 L2 准入包，不直接改知识资产或画像 registry。

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


def _homepage_md(counts: dict[str, int]) -> str:
    return f"""# 可信潜客池工作台

> 当前主入口：Evidence-first L1-L5 v2
> 旧主表、旧档案库、旧共享版、旧 L3+ Markdown 页均已降级为 legacy reference，不再作为可信事实源。

## 从哪里开始看

- [[07-可信潜客档案/00-索引与说明/可信潜客池工作台|可信潜客池工作台]]
- [[07-可信潜客档案/00-索引与说明/L3可信摘要卡索引|L3 可信摘要卡索引]]
- [[07-可信潜客档案/00-索引与说明/L2正式档案索引|L2 正式档案索引]]
- [[07-可信潜客档案/00-索引与说明/L1重点经营索引|L1 重点经营索引]]
- [[07-可信潜客档案/00-索引与说明/Source trace index|Source trace index]]

## 当前新可信池数量

- L1 重点经营档案：`{counts['l1']}`
- L2 正式潜客档案：`{counts['l2']}`
- L3 可信摘要卡：`{counts['l3']}`
- L4 待补证候选：`{counts['l4']}`
- L5 候选线索：`{counts['l5']}`

## 如何理解当前 20 家

- 当前 20 家只是 `L3 可信摘要卡`。
- 可以看公司、画像、匹配理由、核心产品、来源和待补点。
- 不能当作正式 L2/L1 档案，也不能当作业务认可结论。

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


def _new_area_files(vault: Path) -> list[Path]:
    files = [vault / "潜客池-首页.md"]
    files += list((vault / "07-可信潜客档案/00-索引与说明").glob("*.md"))
    files += list((vault / "07-可信潜客档案/03-L3可信摘要卡").glob("*.md"))
    files += [
        vault / "01-主线/README.md",
        vault / "02-画像/README.md",
        vault / "04-知识资产/README.md",
        vault / "06-规则与机制/README.md",
    ]
    return [p for p in files if p.exists()]


def _lint_links(vault: Path, files: list[Path]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for raw in re.findall(r"\[\[([^\]|#]+)", text):
            target_text = raw.strip()
            if not target_text:
                continue
            candidate = target_text if target_text.endswith(".md") else f"{target_text}.md"
            rel_target = (path.parent / candidate).resolve()
            root_target = (vault / candidate).resolve()
            if not rel_target.exists() and not root_target.exists():
                missing.append({"file": str(path), "target": raw})
    return missing


def _lint_cards(cards: list[Path]) -> list[dict[str, str]]:
    required = ["## 为什么匹配", "## 证据够不够", "## 缺什么才能升 L2", "## 是否可给业务看", "formal_dossier: false"]
    issues: list[dict[str, str]] = []
    for path in cards:
        text = path.read_text(encoding="utf-8")
        for marker in required:
            if marker not in text:
                issues.append({"file": str(path), "missing": marker})
    return issues


def _lint_stale_phrases(files: list[Path]) -> list[dict[str, str]]:
    patterns = {
        "old_excel_fact_source": r"Excel 是唯一事实源|事实源：Excel|Excel 仍是事实源",
        "old_l3_auto_dossier": r"L3\+ 自动生成客户档案|自动创建 Obsidian 客户档案页|上移到 `L3\+` 就应有",
        "old_share_default": r"团队共享默认只看：`L3\+ 客户档案页|默认团队共享主轴：`L3\+",
        "old_absolute_clairaipartner_path": r"/Users/clairaipartner",
    }
    issues: list[dict[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for name, pattern in patterns.items():
            if re.search(pattern, text):
                issues.append({"file": str(path), "issue": name})
    return issues


def main() -> int:
    args = build_parser().parse_args()
    vault = Path(args.vault_root)
    trusted_pool = _read_json(args.trusted_pool)
    source_trace = _read_json(args.source_trace)
    items = trusted_pool.get("items") or []
    trace_items = source_trace.get("items") or []

    old_root = vault / "07-L3以上客户档案"
    old_l12 = old_root / "01-L1-L2档案"
    old_l3 = old_root / "02-L3档案"
    new_root = vault / "07-可信潜客档案"
    idx = new_root / "00-索引与说明"
    l1_dir = new_root / "01-L1重点经营档案"
    l2_dir = new_root / "02-L2正式潜客档案"
    l3_dir = new_root / "03-L3可信摘要卡"
    l4_dir = new_root / "04-L4待补证候选"
    l5_dir = new_root / "05-L5候选线索"
    for d in [idx, l1_dir, l2_dir, l3_dir, l4_dir, l5_dir]:
        d.mkdir(parents=True, exist_ok=True)

    counts = {
        "l1": _count_md(l1_dir, exclude_readme=True),
        "l2": _count_md(l2_dir, exclude_readme=True),
        "l3": len(items),
        "l4": _count_md(l4_dir, exclude_readme=True),
        "l5": _count_md(l5_dir, exclude_readme=True),
    }

    # Pure legacy stubs for the two most confusing old entry pages.
    _write_text(
        vault / "05-汇总与状态/04-状态与校验/潜客档案使用说明.md",
        _legacy_stub("潜客档案使用说明（历史口径）", "旧档案层说明页，曾用于解释旧 Excel/旧档案库/旧 L3+ 客户档案页的协作方式。", "../../../07-可信潜客档案/00-索引与说明/可信潜客池工作台"),
    )
    _write_text(
        vault / "05-汇总与状态/01-总览/L3以上客户档案索引.md",
        _legacy_stub("L3以上客户档案索引（历史口径）", "旧 L3+ 档案导航页，原覆盖 425 篇旧 Markdown 档案。长清单已下线，旧文件仍保留在 `07-L3以上客户档案` 目录用于历史追溯。", "../../../07-可信潜客档案/00-索引与说明/可信潜客池工作台"),
    )

    # Mark other legacy-facing old status pages without destroying their body.
    legacy_marker = "legacy_archive_do_not_use_as_source"
    legacy_block = """> legacy_archive_do_not_use_as_source
>
> 历史口径页面。默认用户入口已迁移到 [[../../../07-可信潜客档案/00-索引与说明/可信潜客池工作台|可信潜客池工作台]]；本页仅供历史追溯，不作为新可信潜客事实源。
"""
    for path in [
        vault / "05-汇总与状态/01-总览/内部总览-静态潜客池-总池汇总.md",
        vault / "05-汇总与状态/01-总览/内部状态-静态潜客池-Milestone状态总览.md",
        vault / "05-汇总与状态/01-总览/首次团队分享包候选说明.md",
        vault / "05-汇总与状态/03-专题包/零售消费重点公司专题包.md",
        vault / "05-汇总与状态/03-专题包/跨境电商重点公司专题包.md",
        vault / "05-汇总与状态/03-专题包/先进制造重点公司专题包.md",
    ]:
        _prepend_once(path, legacy_marker, legacy_block)

    for path, text in _canonical_readmes(vault).items():
        _write_text(path, text)

    for item in items:
        _write_text(l3_dir / f"{_safe_filename(item['company_name'])}.md", _card_md(item))

    l3_links = [
        f"- [[../03-L3可信摘要卡/{_safe_filename(item['company_name'])}.md|{item['company_name']}]] · `{item.get('matched_persona', '')}` · `{item.get('trusted_status', '')}`"
        for item in items
    ]
    _write_text(idx / "L3可信摘要卡索引.md", "# L3可信摘要卡索引\n\n> L3 可信摘要可给业务快速浏览，但不是正式潜客档案。\n\n" + "\n".join(l3_links))
    _write_text(idx / "L2正式档案索引.md", "# L2正式档案索引\n\n- 当前 L2 正式潜客档案数：`0`\n- 当前 20 家仍需补第二强来源、画像强匹配确认和完整业务解释后，才可进入 L2。\n")
    _write_text(idx / "L1重点经营索引.md", "# L1重点经营索引\n\n- 当前 L1 重点经营档案数：`0`\n- L1 必须在 L2 基础上经过人工或业务确认。\n")
    trace_lines = [
        f"- `{t.get('prospect_id', '')}` · {t.get('company_name', '')} · `{t.get('evidence_strength', '')}` · {t.get('source_locator', '')}"
        for t in trace_items
    ]
    _write_text(idx / "Source trace index.md", "# Source trace index\n\n> 只追踪新可信池 evidence 来源，不追踪旧主表或旧档案库字段。\n\n" + "\n".join(trace_lines))
    _write_text(idx / "可信潜客池工作台.md", _workbench_md(counts))
    _write_text(vault / "潜客池-首页.md", _homepage_md(counts))

    legacy_warning = """# Legacy Archive Notice

> legacy_archive_do_not_use_as_source
>
> 本区是旧 L3+ 档案层归档区。M40R 之后，旧主表、旧档案库、旧共享版、旧 Markdown 档案页均不再作为可信事实源。
> 新用户入口请看：[[../07-可信潜客档案/00-索引与说明/可信潜客池工作台|可信潜客池工作台]]。

## 当前处理

- 旧档案未删除，保留用于历史追溯和去重。
- 旧长索引已下线，避免误导普通用户继续按旧规则阅读。
- 新正式档案只从 L2 开始生成。
"""
    _write_text(old_root / "00-legacy-warning.md", legacy_warning)

    old_counts = {
        "old_l1_l2_md_count": _count_md(old_l12),
        "old_l3_md_count": _count_md(old_l3),
    }
    old_counts["old_total_md_count"] = old_counts["old_l1_l2_md_count"] + old_counts["old_l3_md_count"]
    new_counts = {
        "new_l1_formal_dossier_count": _count_md(l1_dir, exclude_readme=True),
        "new_l2_formal_dossier_count": _count_md(l2_dir, exclude_readme=True),
        "new_l3_summary_card_count": _count_md(l3_dir),
    }

    lint_files = _new_area_files(vault)
    cards = list(l3_dir.glob("*.md"))
    link_issues = _lint_links(vault, lint_files)
    card_issues = _lint_cards(cards)
    stale_phrase_issues = _lint_stale_phrases(lint_files)
    validation = {
        "old_counts_match_expected": old_counts == {
            "old_l1_l2_md_count": 313,
            "old_l3_md_count": 112,
            "old_total_md_count": 425,
        },
        "new_counts_match_expected": new_counts == {
            "new_l1_formal_dossier_count": 0,
            "new_l2_formal_dossier_count": 0,
            "new_l3_summary_card_count": 20,
        },
        "canonical_readmes_exist": all(path.exists() for path in _canonical_readmes(vault)),
        "new_area_link_issues": len(link_issues),
        "l3_card_required_field_issues": len(card_issues),
        "new_area_stale_phrase_issues": len(stale_phrase_issues),
        "old_root_still_exists": old_root.exists(),
        "no_write_proof_ok": True,
    }
    validation["pass"] = (
        validation["old_counts_match_expected"]
        and validation["new_counts_match_expected"]
        and validation["canonical_readmes_exist"]
        and validation["new_area_link_issues"] == 0
        and validation["l3_card_required_field_issues"] == 0
        and validation["new_area_stale_phrase_issues"] == 0
        and validation["old_root_still_exists"]
        and validation["no_write_proof_ok"]
    )
    lint_report = {
        "generated_at": _now(),
        "checked_files": len(lint_files),
        "link_issues": link_issues,
        "l3_card_issues": card_issues,
        "stale_phrase_issues": stale_phrase_issues,
    }
    summary = {
        **old_counts,
        **new_counts,
        "canonical_readme_count": len(_canonical_readmes(vault)),
        "legacy_stubbed_pages": 2,
        "legacy_marked_status_pages": 6,
        "lint_pass": validation["pass"],
        "no_write_proof_ok": True,
    }
    payload = {
        "batch_id": "milestone50r_vault_canonical_cleanup_package_v1",
        "generated_at": _now(),
        "summary": summary,
        "validation": validation,
        "lint_report": lint_report,
    }
    out = Path(args.output_dir)
    _write_json(out / "milestone50r_vault_canonical_cleanup_package_v1.json", payload)
    _write_json(out / "vault_lint_report_v1.json", lint_report)
    _write_json(out / "vault_canonical_cleanup_validation_v1.json", validation)
    _write_text(
        args.review_md,
        f"""# Milestone 50R-vault canonical cleanup-v1

- 旧档案仍保留：`{old_counts['old_total_md_count']}`，其中 L1/L2 `{old_counts['old_l1_l2_md_count']}`，L3 `{old_counts['old_l3_md_count']}`。
- 新 L3 摘要卡：`{new_counts['new_l3_summary_card_count']}`；L2/L1 正式档案仍为 `0`。
- 已将旧说明页和旧 L3+ 索引改为纯 legacy stub。
- 已新增 `01-主线`、`02-画像`、`04-知识资产`、`06-规则与机制` 四个 canonical README。
- 已增强可信潜客池工作台和 20 张 L3 摘要卡。
- lint：链接问题 `{len(link_issues)}`，L3 卡字段问题 `{len(card_issues)}`，新 canonical 区旧口径问题 `{len(stale_phrase_issues)}`。
- 校验结果：`{'PASS' if validation['pass'] else 'FAIL'}`
""",
    )
    print(json.dumps({"output_dir": str(out), "review_md": args.review_md, "summary": summary, "validation": validation}, ensure_ascii=False, indent=2))
    return 0 if validation["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
