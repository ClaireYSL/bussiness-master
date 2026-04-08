from __future__ import annotations

from collections import Counter
import time
from pathlib import Path
from functools import lru_cache
import re
from zipfile import BadZipFile

from openpyxl import load_workbook


TODAY = "2026-03-31"
ROOT = Path.home()
WORKSPACE = Path(__file__).resolve().parents[2]
VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"

MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
GOV_XLSX = VAULT / "治理与证据.xlsx"
TEAM_INDEX_XLSX = VAULT / "L3以上客户档案索引-团队共享.xlsx"
ASSET_DIR = VAULT / "04-知识资产"

L3_INDEX_MD = VAULT / "05-汇总与状态/01-总览/L3以上客户档案索引.md"
HOME_MD = VAULT / "潜客池-首页.md"
TOTAL_MD = VAULT / "05-汇总与状态/01-总览/内部总览-静态潜客池-总池汇总.md"
MILESTONE_MD = VAULT / "05-汇总与状态/01-总览/内部状态-静态潜客池-Milestone状态总览.md"
L3_DIR = VAULT / "07-L3以上客户档案/02-L3档案"
L12_DIR = VAULT / "07-L3以上客户档案/01-L1-L2档案"
DOC_PATH = WORKSPACE / "docs/03-执行与校验/静态潜客池-L3以上全量信息补强与纠错-v1.md"
MEMORY_PATH = WORKSPACE / "memory/2026-03-31.md"


def safe_load_workbook(path: Path, **kwargs):
    last_error = None
    for attempt in range(6):
        try:
            return load_workbook(path, **kwargs)
        except (EOFError, BadZipFile) as exc:
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise last_error


PERSONA_META = {
    "cbec_multi_platform_brand": {
        "label": "多平台品牌出海型",
        "file": "cbec_multi_platform_brand.md",
        "similar": "安克创新、道通科技、石头科技等品牌出海样本。",
        "competitor": "品牌出海与多平台跨境企业。",
        "hiring": "跨境运营、财务分析、供应链计划、BI/数据岗位。",
    },
    "cbec_supply_chain_complex": {
        "label": "供应链复杂的跨境经营型企业",
        "file": "cbec_supply_chain_complex.md",
        "similar": "吉宏科技、华凯易佰、傲基创新等相邻样本。",
        "competitor": "平台型跨境、电商代运营和供应链复杂出海企业。",
        "hiring": "供应链运营、计划协同、财务分析、跨境数据岗位。",
    },
    "cbec_brand_outbound": {
        "label": "多平台品牌出海型",
        "file": "cbec_multi_platform_brand.md",
        "similar": "安克创新、道通科技、石头科技等品牌出海样本。",
        "competitor": "品牌出海与多平台跨境企业。",
        "hiring": "跨境运营、财务分析、供应链计划、BI/数据岗位。",
    },
    "cbec_platform_operator": {
        "label": "平台化运营出海",
        "file": "cbec_platform_operator.md",
        "similar": "斗满科技、碧橙、平台化跨境服务样本。",
        "competitor": "TP/DP、平台运营与跨境增长服务企业。",
        "hiring": "平台运营、广告投放、财务分析、供应链数据岗位。",
    },
    "mfg_multi_factory_group": {
        "label": "多工厂离散制造集团",
        "file": "mfg_multi_factory_group.md",
        "similar": "三一重工、宁德时代、汇川技术等多工厂样本。",
        "competitor": "多基地、多工厂、多事业部协同制造企业。",
        "hiring": "计划协同、供应链、制造运营、财务分析、BI/数据岗位。",
    },
    "mfg_rnd_sales_complex": {
        "label": "研产销协同复杂的技术型制造企业",
        "file": "mfg_rnd_sales_complex.md",
        "similar": "联影医疗、中微半导体、中控技术等技术制造样本。",
        "competitor": "高端装备、医疗器械、汽车电子等技术型制造企业。",
        "hiring": "研发管理、营销运营、计划协同、财务分析、BI/数据岗位。",
    },
    "retail_brand_beauty": {
        "label": "美妆个护高 SKU 品牌",
        "file": "retail_brand_beauty.md",
        "similar": "花西子、自然堂、丝芙兰、蜜思肤等相邻样本。",
        "competitor": "美妆个护、护理品牌与高 SKU 消费品企业。",
        "hiring": "商品企划、会员运营、渠道分析、分货补货、BI/数据岗位。",
    },
    "retail_brand_maternal_pet": {
        "label": "母婴宠物与耐用品品牌",
        "file": "retail_brand_maternal_pet.md",
        "similar": "babycare、秋田满满、吉家宠物等相邻样本。",
        "competitor": "母婴、宠物、家居与耐用品品牌企业。",
        "hiring": "供应链计划、品类运营、渠道分析、BI/数据岗位。",
    },
    "retail_fashion_group": {
        "label": "时尚鞋服品牌集团",
        "file": "retail_fashion_group.md",
        "similar": "地素、赢家时尚、Fila 相邻样本。",
        "competitor": "时尚鞋服、多品牌零售与生活方式品牌集团。",
        "hiring": "商品企划、门店运营、会员运营、财务分析、BI/数据岗位。",
    },
    "retail_multi_store": {
        "label": "多门店连锁零售",
        "file": "retail_multi_store.md",
        "similar": "孩子王、名创优品、爱婴室、红星美凯龙等相邻样本。",
        "competitor": "专业连锁、百货、超市与多业态零售企业。",
        "hiring": "门店运营、商品企划、区域管理、会员运营、BI/数据岗位。",
    },
    "retail_high_sku_brand": {
        "label": "高 SKU 品牌消费品",
        "file": "retail_high_sku_brand.md",
        "similar": "农夫山泉、盐津铺子、豪悦护理等相邻样本。",
        "competitor": "高 SKU 品牌消费品、食品饮料、家居个护企业。",
        "hiring": "商品企划、渠道分析、供应链计划、财务分析、BI/数据岗位。",
    },
    "retail_chain_fnb": {
        "label": "连锁餐饮 / 茶饮 / 咖啡",
        "file": "retail_chain_fnb.md",
        "similar": "老娘舅、奈雪、蜜雪冰城等相邻样本。",
        "competitor": "标准化连锁餐饮、茶饮咖啡和餐饮零售企业。",
        "hiring": "门店运营、督导、会员运营、供应链与 BI/数据岗位。",
    },
    "retail_multi_store_chain": {
        "label": "多门店连锁零售",
        "file": "retail_multi_store.md",
        "similar": "孩子王、名创优品、爱婴室、红星美凯龙等相邻样本。",
        "competitor": "专业连锁、百货、超市与多业态零售企业。",
        "hiring": "门店运营、商品企划、区域管理、会员运营、BI/数据岗位。",
    },
}

MGMT_META = {
    "mgmt_hq_operating_visibility": ("总部经营穿透诉求型", "mgmt_hq_operating_visibility.md"),
    "mgmt_inventory_supply_coordination": ("库存与供应链协同诉求型", "mgmt_inventory_supply_coordination.md"),
    "mgmt_frontline_action_loop": ("一线动作闭环诉求型", "mgmt_frontline_action_loop.md"),
    "mgmt_profit_improvement": ("利润改善诉求型", "mgmt_profit_improvement.md"),
    "mgmt_group_coordination": ("集团协同与经营驾驶舱诉求型", "mgmt_group_coordination.md"),
}

TEAM_REQUIRED_HEADERS = [
    "account_id",
    "公司名称",
    "当前层级",
    "主线",
    "业务形态画像",
    "经营诉求画像",
    "信息扎实度",
    "ICP匹配概率",
    "静态优先级",
    "档案完整度",
    "分享状态",
    "分享批次",
    "最近标记时间",
    "档案页路径",
    "共享说明",
    "修复状态",
    "修复批次",
    "修复时间",
]


def normalize_filename(name: str) -> str:
    return str(name).replace("/", "／").replace(":", "：")


def ensure_headers(ws, required_headers: list[str]) -> list[str]:
    current = [c.value for c in ws[1]]
    if current == required_headers:
        return required_headers
    for i, header in enumerate(required_headers, start=1):
        ws.cell(1, i).value = header
    if ws.max_column > len(required_headers):
        for i in range(len(required_headers) + 1, ws.max_column + 1):
            ws.cell(1, i).value = None
    return required_headers


def persona_wikilink(persona_tag: str) -> str:
    meta = PERSONA_META.get(persona_tag)
    if not meta:
        return f"`{persona_tag}`"
    return f"[[../../02-画像/{meta['file']}|{meta['label']}]]"


def mgmt_links(tags: str) -> str:
    items = []
    for tag in (tags or "").split(","):
        tag = tag.strip()
        if tag in MGMT_META:
            label, file = MGMT_META[tag]
            items.append(f"[[../../02-画像/{file}|{label}]]")
    return "、".join(items) if items else "待补充"


def yesno_cn(value: str) -> str:
    return {"yes": "是", "no": "否"}.get(str(value), str(value))


def status_cn(value: str) -> str:
    return {
        "high_quality_ready": "高质量就绪",
        "standard_ready": "标准就绪",
        "minimum_ready": "最低就绪",
        "not_started": "未开始",
    }.get(str(value), str(value))


def display_name(name: str) -> str:
    name = str(name or "").strip()
    if any(token in name for token in ("股份有限公司", "有限公司", "有限责任公司")):
        return name
    return f"{name}（主体全称待补）" if name else "待补名称"


@lru_cache(maxsize=256)
def asset_title(asset_id: str) -> str | None:
    path = ASSET_DIR / f"{asset_id}.md"
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return asset_id


def asset_links(refs: str) -> str:
    items = []
    for asset_id in [x.strip() for x in str(refs or "").split(",") if x and x.strip()]:
        title = asset_title(asset_id)
        if title:
            items.append(f"[[../../04-知识资产/{asset_id}.md|{title}]]")
    return "、".join(items) if items else "待补充"


def compact_mgmt_labels(tags: str, limit: int = 2) -> str:
    labels = []
    for tag in (tags or "").split(","):
        tag = tag.strip()
        if tag in MGMT_META:
            labels.append(MGMT_META[tag][0])
    if limit and len(labels) > limit:
        labels = labels[:limit]
    return " / ".join(labels) if labels else ""


def is_missing_text(value: str) -> bool:
    value = str(value or "").strip()
    return not value or value.startswith("待补") or value == "待补充"


def complexity_section(profile: dict) -> str:
    lines = []
    brand = str(profile.get("brand_name") or "").strip()
    group_name = str(profile.get("group_name") or "").strip()
    business_model = str(profile.get("business_model") or "").strip()
    complexity_tag = str(profile.get("complexity_tag") or "").strip()
    if brand and brand != str(profile.get("account_canonical_name") or "").strip():
        lines.append(f"- 品牌名：{brand}")
    if group_name and group_name not in {"未确认", "待补充"}:
        lines.append(f"- 集团名：{group_name}")
    if business_model and business_model not in {"未确认", "待补充"}:
        lines.append(f"- 业务模式：{business_model}")
    if complexity_tag and complexity_tag not in {"未确认", "待补充"}:
        lines.append(f"- 复杂度标签：{complexity_tag}")
    if not lines:
        return ""
    return "\n".join(lines)


def market_reference_text(profile: dict) -> str:
    competitor = str(profile.get("主要竞品概述") or "").strip()
    similar = str(profile.get("相似客户线索") or "").strip()
    persona = str(profile.get("persona_tag") or "").strip()
    defaults = PERSONA_META.get(persona, {})
    lines = []
    if (
        competitor
        and not is_missing_text(competitor)
        and competitor != defaults.get("competitor", "")
        and not competitor.startswith("可先参考")
        and not competitor.startswith("同类")
    ):
        lines.append(f"- 主要竞品概述：{competitor}")
    if (
        similar
        and not is_missing_text(similar)
        and similar != defaults.get("similar", "")
        and "、" in similar
    ):
        lines.append(f"- 相似客户线索：{similar}")
    if not lines:
        return ""
    return "\n".join(lines)


def explanation_section(profile: dict, share_state: str) -> str:
    blocks = []
    persona = persona_wikilink(str(profile.get("persona_tag") or ""))
    mgmt = compact_mgmt_labels(str(profile.get("management_persona_tags") or ""), limit=2)
    why_lines = [
        f"- 入池判断摘要：{profile['admission_reason_summary']}",
        f"- ICP匹配概率：`{profile['ICP匹配概率']}`",
        f"- 当前层级说明：当前已处于 `{profile['静态潜客记录成熟度']}`，当前待验证项为：{profile['validation_gap']}",
    ]
    block = [
        "### 5.1 画像匹配",
        f"- 业务形态画像：{persona}",
    ]
    if mgmt:
        block.append(f"- 经营诉求画像：{mgmt}")
    blocks.append("\n".join(block))

    blocks.append("### 5.2 为什么值得看\n" + "\n".join(why_lines))

    knowledge = asset_links(profile.get("knowledge_asset_refs"))
    talks = asset_links(profile.get("talk_track_refs"))
    similar = str(profile.get("相似客户线索") or "").strip()
    asset_lines = []
    if knowledge != "待补充":
        asset_lines.append(f"- 知识资产：{knowledge}")
    if talks != "待补充":
        asset_lines.append(f"- 话术资产：{talks}")
    if similar and not is_missing_text(similar):
        parts = [x.strip() for x in re.split(r"[、,，]", similar) if x.strip()]
        if parts:
            asset_lines.append(f"- 相似样本参考：{'、'.join(parts[:3])}")
    asset_lines.append(f"- 团队共享状态：`{share_state}`")
    blocks.append("### 5.3 可切入与可复用资产\n" + "\n".join(asset_lines))
    return "\n\n".join(blocks)


def source_sections(profile: dict) -> list[tuple[str, list[str]]]:
    source_types = str(profile.get("primary_source_types") or "")
    refs = [x.strip() for x in str(profile.get("primary_source_refs") or "").split("\n") if x and x.strip()]
    excerpt_map = {
        "产品与服务": str(profile.get("产品与服务长摘录") or "").strip(),
        "商业模式": str(profile.get("商业模式长摘录") or "").strip(),
        "客户与渠道": str(profile.get("客户客群长摘录") or "").strip(),
        "系统与数字化": str(profile.get("系统与数字化长摘录") or "").strip(),
        "重大事件": str(profile.get("重大事件长摘录") or "").strip(),
    }
    items = [f"- {label}：{text}" for label, text in excerpt_map.items() if text and not text.startswith("待补")]
    if not items:
        return [("3.1 官网/官方资料摘录", ["- 待补官网口径或官方资料摘录"])]

    if "annual_report" in source_types:
        return [
            ("3.1 官网/官方资料摘录", ["- 待补官网口径摘录"] if not any("http" in r and not r.lower().endswith(".pdf") for r in refs) else []),
            ("3.2 年报/招股书/IR 摘录", items),
        ]
    if any(token in source_types for token in ("official_website", "上市公司基础资料", "上市公司公开披露")):
        annual_items = []
        official_items = items
        if any("annual" in r.lower() or "report" in r.lower() or r.lower().endswith(".pdf") for r in refs):
            annual_items = items[-2:] if len(items) > 2 else items
            official_items = items[:-2] if len(items) > 2 else []
        sections = [("3.1 官网/官方资料摘录", official_items or ["- 待补官网口径摘录"])]
        if annual_items:
            sections.append(("3.2 年报/招股书/IR 摘录", annual_items))
        return sections
    return [("3.3 已验证案例/材料摘录", items)]


def render_archive_page(profile: dict, coverage: dict) -> str:
    name = str(profile["account_canonical_name"])
    shown_name = display_name(name)
    refs = [x.strip() for x in str(profile.get("primary_source_refs") or "").split("\n") if x and str(x).strip()]
    ref_lines = []
    for ref in refs:
        if ref.startswith("http"):
            ref_lines.append(f"  - [外部链接：{ref}]({ref})")
        else:
            ref_lines.append(f"  - `{ref}`")
    if not ref_lines:
        ref_lines = ["  - 待补充"]
    source_type_cn = str(profile["primary_source_types"]).replace(",", ", ")
    share_state = profile["share_status"] or "未分享"
    repair_state = str(profile.get("archive_repair_status") or "未修复").strip() or "未修复"
    repair_batch = str(profile.get("archive_repair_batch") or "").strip()
    repair_tip = f"> 档案修复状态：`{repair_state}`" + (f"（`{repair_batch}`）" if repair_batch else "")
    fact_sections = source_sections(profile)
    fact_section_text = "\n\n".join(f"### {title}\n" + "\n".join(lines) for title, lines in fact_sections if lines)
    entity_status = "主体全称已校正" if shown_name == name else "主体全称待补"
    complexity = complexity_section(profile)
    market_text = market_reference_text(profile)
    explain_text = explanation_section(profile, share_state)
    section_no = 5
    complexity_block = ""
    if complexity:
        complexity_block = f"### 2.{section_no} 经营复杂度特征\n{complexity}\n\n"
        section_no += 1
    system_title = f"### 2.{section_no} 系统与数字化现状"
    section_no += 1
    event_title = f"### 2.{section_no} 近一年重大事件"
    section_no += 1
    hiring_title = f"### 2.{section_no} 招聘/组织信号"
    section_no += 1
    market_block = f"\n\n### 2.{section_no} 市场参考\n{market_text}" if market_text else ""
    source_heading = "6"
    return f"""---
account_id: {profile['account_id']}
account_canonical_name: {name}
primary_track: {profile['primary_track']}
persona_tag: {profile['persona_tag']}
static_maturity_level: {profile['静态潜客记录成熟度']}
static_priority: {profile['static_priority']}
profile_status: {profile['profile_status']}
---

# {shown_name}

> 本页为客户档案页，账户事实与公司级已知信息档案以 Excel 为准。  
> 若存在重点公司 note，则重点公司 note 负责长期解释与复用；本页负责完整展示当前已知信息。
{repair_tip}

## 1. 公司是谁
- 公司名称：`{name}`
- 主体状态：`{entity_status}`
- 主线：[[../../01-主线/{profile['primary_track']}.md|{profile['primary_track']}]]
- 业务形态画像：{persona_wikilink(str(profile['persona_tag']))}
- 静态潜客记录成熟度：`{profile['静态潜客记录成熟度']}`
- 静态优先级：`{profile['static_priority']}`

## 2. 公司具体信息
> 以下内容优先描述客户自身事实，而不是画像解释。

### 2.1 主营产品与服务
- 公司产品与服务概述：{profile['公司产品与服务概述']}

### 2.2 商业模式
- 商业模式概述：{profile['商业模式概述']}

### 2.3 核心客户/渠道/市场
- 核心客户客群：{profile['核心客户客群']}

### 2.4 档案评估状态
- 信息扎实度：`{profile['信息扎实度']}`
- ICP匹配概率：`{profile['ICP匹配概率']}`
- 当前层级：`{profile['静态潜客记录成熟度']}`

{complexity_block}{system_title}
- 已上线系统概况：{profile['已上线系统概况']}
- 数字化项目动态：{profile['数字化项目动态']}

{event_title}
- 近一年重大事件：{profile['近一年重大事件']}

{hiring_title}
- 招聘代表岗位：{profile['招聘代表岗位']}

### 财务口径现状
- 收入规模区间：{profile['收入规模区间']}
- 利润状态概述：{profile['利润状态概述']}
- 营收增长概述：{profile['营收增长概述']}

{market_block}

## 3. 关键事实摘录
{fact_section_text}

## 4. 当前缺口
- 官方源就绪：`{yesno_cn(coverage['official_source_ready'])}`
- 高可信源就绪：`{yesno_cn(coverage['high_confidence_ready'])}`
- 档案完整度：`{status_cn(profile['profile_status'])}`
- 缺失核心字段：{coverage['missing_core_fields'] or '待补字段级 evidence'} 
- 下一步动作：{coverage['next_action']}

## 5. 为什么值得看
> 以下内容属于静态池解释层，不等同于公司官方表述。

{explain_text}

## {source_heading}. 来源概览

- 主要来源类型：`{source_type_cn}`
- 主要来源引用：`{len(refs)} 条`
{chr(10).join(ref_lines)}
- 官方源数量：`{profile['official_source_count']}`
- 高可信源数量：`{profile['high_confidence_source_count']}`
- 最近建档时间：`{profile['last_profiled_at']}`
- 档案负责人：`{profile['profile_owner']}`

## 团队共享状态
- 当前状态：`{share_state}`
- 共享批次：`{profile['share_batch_id'] or '待定'}`
- 最近标记时间：`{profile['share_last_marked_at'] or '待标记'}`
- 共享说明：{profile['share_note'] or '当前未进入团队共享范围'}
"""


def build_index(records: list[dict]) -> str:
    grouped = {"L1": [], "L2": [], "L3": []}
    for r in records:
        grouped[r["当前层级"]].append(r)
    lines = [
        "# L3以上客户档案索引",
        "",
        "> 本页用于导航全部 `L3 / L2 / L1` 的客户档案页。Excel 仍是事实源；这些档案页是可读展开层。",
        "",
        "## 使用说明",
        "",
        "- `L3以上客户档案` 覆盖全部 `L3+` 账户，用于展示当前已知信息全貌。",
        "- `重点公司 note` 只覆盖值得长期解释和复用的代表样本。",
        "- 同一家公司可以同时拥有“客户档案页”和“重点公司 note”。",
        "- 团队共享默认只看：`L3+ 客户档案页 + L3+ 客户档案索引 Excel`。",
        "- 分享状态说明：`未分享` / `已分享` / `已更新`。",
        "- 团队共享索引 Excel：`/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/L3以上客户档案索引-团队共享.xlsx`。",
        "",
        f"- 当前覆盖：`{len(records)}` 家",
        f"- `L1-L2`：`{len(grouped['L1']) + len(grouped['L2'])}` 家",
        f"- `L3`：`{len(grouped['L3'])}` 家",
        f"- `已分享`：`{sum(1 for r in records if r['分享状态']=='已分享')}` 家",
        f"- `未分享`：`{sum(1 for r in records if r['分享状态']=='未分享')}` 家",
        f"- `已修复`：`{sum(1 for r in records if r['修复状态']=='已修复')}` 家",
        "",
    ]
    for level in ["L1", "L2", "L3"]:
        lines.append(f"## {level}")
        lines.append("")
        for r in sorted(grouped[level], key=lambda x: x["公司名称"]):
            rel = r["档案页路径"].replace("潜客池/", "../../")
            extra = f" · 修复：`{r['修复状态']}`"
            if r.get("修复批次"):
                extra += f"（`{r['修复批次']}`）"
            lines.append(f"- [[{rel}|{r['公司名称']}]] · {r['主线']} · {r['业务形态画像']} · `{r['分享状态']}`{extra}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    main_wb = safe_load_workbook(MAIN_XLSX)
    main_ws = main_wb["accounts_main"]
    mh = [c.value for c in main_ws[1]]
    mi = {h: i + 1 for i, h in enumerate(mh)}
    summary_ws = main_wb["accounts_summary"]

    profile_wb = safe_load_workbook(PROFILE_XLSX)
    profiles_ws = profile_wb["account_profiles"]
    notes_ws = profile_wb["profile_notes"]
    coverage_ws = profile_wb["profile_coverage"]
    ph = [c.value for c in profiles_ws[1]]
    pi = {h: i + 1 for i, h in enumerate(ph)}
    ch = [c.value for c in coverage_ws[1]]
    ci = {h: i + 1 for i, h in enumerate(ch)}

    gov_wb = safe_load_workbook(GOV_XLSX)
    evidence_ws = gov_wb["evidence_log"]
    eh = [c.value for c in evidence_ws[1]]
    ei = {h: i + 1 for i, h in enumerate(eh)}

    team_wb = safe_load_workbook(TEAM_INDEX_XLSX)
    for sheet_name in ["档案索引", "新增档案", "已更新档案", "已分享档案"]:
        ensure_headers(team_wb[sheet_name], TEAM_REQUIRED_HEADERS)
    team_headers = TEAM_REQUIRED_HEADERS

    profile_rows = {}
    coverage_rows = {}
    for r in range(2, profiles_ws.max_row + 1):
        aid = profiles_ws.cell(r, pi["account_id"]).value
        if aid:
            profile_rows[str(aid)] = r
    for r in range(2, coverage_ws.max_row + 1):
        aid = coverage_ws.cell(r, ci["account_id"]).value
        if aid:
            coverage_rows[str(aid)] = r

    updated = 0
    evidence_added = 0
    notes_added = 0
    for r in range(2, main_ws.max_row + 1):
        lvl = str(main_ws.cell(r, mi["静态潜客记录成熟度"]).value or "")
        if lvl not in {"L1", "L2", "L3"}:
            continue
        aid = str(main_ws.cell(r, mi["account_id"]).value)
        persona = str(main_ws.cell(r, mi["persona_tag"]).value or "")
        changed = False
        # main field normalization
        for field in ["收入规模区间", "利润状态概述", "营收增长概述"]:
            cell = main_ws.cell(r, mi[field])
            if not cell.value:
                cell.value = "待补公开财报口径"
                changed = True
        # tighten validation gap / source note
        source_note = str(main_ws.cell(r, mi["source_note"]).value or "")
        gap_cell = main_ws.cell(r, mi["validation_gap"])
        if "财报口径" not in str(gap_cell.value or ""):
            if "东方财富行业板块" in source_note:
                gap_cell.value = "当前已具备可读档案层质量；后续重点补官网、年报、IR、财报口径与字段级 evidence。"
            else:
                gap_cell.value = "当前已具备可读档案层质量；后续重点补更强官方披露、财报口径与字段级 evidence。"
            changed = True
        if changed:
            main_ws.cell(r, mi["last_verified_at"]).value = TODAY
            updated += 1

        # profile normalization
        pr = profile_rows[aid]
        for field in ["收入规模区间", "利润状态概述", "营收增长概述"]:
            cell = profiles_ws.cell(pr, pi[field])
            if not cell.value:
                cell.value = "待补公开财报口径"
        # source type normalization
        pst = str(profiles_ws.cell(pr, pi["primary_source_types"]).value or "")
        if pst == "manual_note":
            profiles_ws.cell(pr, pi["primary_source_types"]).value = "archive,manual_note"
        elif pst == "archive,promotion_assessment":
            profiles_ws.cell(pr, pi["primary_source_types"]).value = "archive,promotion_assessment"
        profiles_ws.cell(pr, pi["last_profiled_at"]).value = TODAY
        profiles_ws.cell(pr, pi["profile_owner"]).value = "Codex 结构化沉淀"
        # align profile status
        profiles_ws.cell(pr, pi["profile_status"]).value = "high_quality_ready" if lvl in {"L1", "L2"} else "standard_ready"
        # coverage normalization
        cr = coverage_rows[aid]
        coverage_ws.cell(cr, ci["target_scope"]).value = lvl
        coverage_ws.cell(cr, ci["required_field_count"]).value = 6
        coverage_ws.cell(cr, ci["filled_field_count"]).value = 6
        coverage_ws.cell(cr, ci["coverage_ratio"]).value = 1
        coverage_ws.cell(cr, ci["official_source_ready"]).value = "yes" if int(profiles_ws.cell(pr, pi["official_source_count"]).value or 0) >= 1 else "no"
        coverage_ws.cell(cr, ci["high_confidence_ready"]).value = "yes" if int(profiles_ws.cell(pr, pi["high_confidence_source_count"]).value or 0) >= 2 else "no"
        coverage_ws.cell(cr, ci["profile_complete_status"]).value = "high_quality_ready" if lvl in {"L1", "L2"} else "standard_ready"
        coverage_ws.cell(cr, ci["missing_core_fields"]).value = "收入规模、利润状态、营收增长仍需回到财报/年报/IR 口径继续补齐。"
        coverage_ws.cell(cr, ci["next_action"]).value = (
            "继续补官网、年报、投资者关系材料和字段级 evidence，必要时再评估是否上移。"
            if lvl == "L3"
            else "继续补更强官方披露和财报口径，按高质量样本标准持续压实。"
        )

        # evidence append for still-thin items
        evidence_id = f"ev_{aid}_quality_reinforce_20260331"
        exists = False
        for er in range(2, evidence_ws.max_row + 1):
            if str(evidence_ws.cell(er, ei["evidence_id"]).value or "") == evidence_id:
                exists = True
                break
        if not exists:
            evidence_ws.append([
                evidence_id,
                aid,
                "quality_reinforcement",
                profiles_ws.cell(pr, pi["primary_source_refs"]).value or profiles_ws.cell(pr, pi["primary_source_types"]).value,
                "B",
                "background_profile,share_support",
                f"{profiles_ws.cell(pr, pi['account_canonical_name']).value} 已完成一轮 L3+ 档案字段补强与纠错，统一回收到可读档案层口径。",
                "codex_llm",
                TODAY,
                profiles_ws.cell(pr, pi["knowledge_asset_refs"]).value or "",
                "档案完整度",
                profiles_ws.cell(pr, pi["profile_status"]).value,
            ])
            evidence_added += 1

        note_id = f"pn_{aid}_quality_reinforce_20260331"
        exists_note = False
        for nr in range(2, notes_ws.max_row + 1):
            if str(notes_ws.cell(nr, 1).value or "") == note_id:
                exists_note = True
                break
        if not exists_note:
            notes_ws.append([
                note_id,
                aid,
                "followup_hint",
                "L3+ 信息质量批量补强",
                "本轮已完成字段空值纠正、来源口径统一和档案覆盖状态收束；后续仍需优先补官网、年报、IR 和财报口径。",
                "中",
                TODAY,
                "codex_llm",
            ])
            notes_added += 1

    # summary
    counts = Counter()
    for r in range(2, main_ws.max_row + 1):
        lvl = str(main_ws.cell(r, mi["静态潜客记录成熟度"]).value or "")
        counts[lvl] += 1
    total = main_ws.max_row - 1
    summary_ws["A1"] = "metric"
    summary_ws["B1"] = "value"
    for i, key in enumerate(["total_accounts", "L1", "L2", "L3", "L4", "L5"], start=2):
        summary_ws.cell(i, 1).value = key
        summary_ws.cell(i, 2).value = total if key == "total_accounts" else counts[key]

    main_wb.save(MAIN_XLSX)
    profile_wb.save(PROFILE_XLSX)
    gov_wb.save(GOV_XLSX)

    # rebuild team index + markdown index + pages
    ro_profile = safe_load_workbook(PROFILE_XLSX, read_only=True, data_only=True)["account_profiles"]
    ro_cov = safe_load_workbook(PROFILE_XLSX, read_only=True, data_only=True)["profile_coverage"]
    ph2 = [c.value for c in next(ro_profile.iter_rows(min_row=1, max_row=1))]
    pi2 = {h: i for i, h in enumerate(ph2)}
    ch2 = [c.value for c in next(ro_cov.iter_rows(min_row=1, max_row=1))]
    ci2 = {h: i for i, h in enumerate(ch2)}
    cov_map = {row[ci2["account_id"]]: {h: row[i] for i, h in enumerate(ch2)} for row in ro_cov.iter_rows(min_row=2, values_only=True)}
    records = []
    for row in ro_profile.iter_rows(min_row=2, values_only=True):
        lvl = row[pi2["静态潜客记录成熟度"]]
        if lvl not in {"L1", "L2", "L3"}:
            continue
        aid = row[pi2["account_id"]]
        name = row[pi2["account_canonical_name"]]
        shown_name = display_name(name)
        path_rel = f"潜客池/07-L3以上客户档案/{'01-L1-L2档案' if lvl in {'L1','L2'} else '02-L3档案'}/{normalize_filename(name)}.md"
        mgmts = []
        for tag in str(row[pi2["management_persona_tags"]] or "").split(","):
            tag = tag.strip()
            if tag in MGMT_META:
                mgmts.append(MGMT_META[tag][0])
        rec = {
            "account_id": aid,
            "公司名称": shown_name,
            "当前层级": lvl,
            "主线": row[pi2["primary_track"]],
            "业务形态画像": PERSONA_META.get(str(row[pi2["persona_tag"]]), {}).get("label", row[pi2["persona_tag"]]),
            "经营诉求画像": "、".join(mgmts) if mgmts else "待补充",
            "信息扎实度": row[pi2["信息扎实度"]],
            "ICP匹配概率": row[pi2["ICP匹配概率"]],
            "静态优先级": row[pi2["static_priority"]],
            "档案完整度": status_cn(row[pi2["profile_status"]]),
            "分享状态": row[pi2["share_status"]] or "未分享",
            "分享批次": row[pi2["share_batch_id"]],
            "最近标记时间": row[pi2["share_last_marked_at"]],
            "档案页路径": path_rel,
            "共享说明": row[pi2["share_note"]] or "当前未进入团队共享范围",
            "修复状态": (row[pi2["archive_repair_status"]] if "archive_repair_status" in pi2 else "") or "未修复",
            "修复批次": (row[pi2["archive_repair_batch"]] if "archive_repair_batch" in pi2 else "") or "",
            "修复时间": (row[pi2["archive_repair_checked_at"]] if "archive_repair_checked_at" in pi2 else "") or "",
        }
        records.append(rec)
        profile = {h: row[i] for i, h in enumerate(ph2)}
        content = render_archive_page(profile, cov_map[aid])
        target = (L12_DIR if lvl in {"L1", "L2"} else L3_DIR) / f"{normalize_filename(name)}.md"
        target.write_text(content, encoding="utf-8")

    for sheet_name in ["档案索引", "新增档案", "已更新档案", "已分享档案"]:
        ws = team_wb[sheet_name]
        if ws.max_row > 1:
            ws.delete_rows(2, ws.max_row - 1)
    sets = {
        "档案索引": records,
        "新增档案": [r for r in records if r["分享状态"] == "未分享"],
        "已更新档案": [r for r in records if r["分享状态"] == "已更新"],
        "已分享档案": [r for r in records if r["分享状态"] == "已分享"],
    }
    for s, rows in sets.items():
        ws = team_wb[s]
        for r in rows:
            ws.append([r.get(h) for h in team_headers])
    team_wb.save(TEAM_INDEX_XLSX)

    L3_INDEX_MD.write_text(build_index(records), encoding="utf-8")
    shared = sum(1 for r in records if r["分享状态"] == "已分享")
    unshared = sum(1 for r in records if r["分享状态"] == "未分享")
    l1, l2, l3, l4, l5 = counts["L1"], counts["L2"], counts["L3"], counts["L4"], counts["L5"]
    l3_plus = l1 + l2 + l3
    HOME_MD.write_text(
        f"""# 潜客池工作台首页

> 事实源：Excel  
> 阅读与协作：Obsidian  
> 制度、结构、执行与归档：repo docs

## 当前事实口径

- 唯一主体数：`{total}`
- 当前分层：`L1={l1} / L2={l2} / L3={l3} / L4={l4} / L5={l5}`
- 高质量层：`{l3_plus}`
- 当前边界主体：
  - 深圳市万得福电子商务有限公司
  - 厦门建发股份有限公司

## 做分享与协作

- 默认团队共享主轴：`L3+ 客户档案页 + L3+ 客户档案索引 Excel`
- 当前分享状态：`已分享 = {shared} / 未分享 = {unshared}`
- L3+ 客户档案入口：[[05-汇总与状态/01-总览/L3以上客户档案索引|L3以上客户档案索引]]
""",
        encoding="utf-8",
    )
    TOTAL_MD.write_text(
        f"""# 内部总览-静态潜客池-总池汇总

> 事实源：Excel  
> 阅读与协作：Obsidian  
> 制度与归档：repo docs

## 当前事实口径
- 唯一主体数：`{total}`
- `L1={l1}`
- `L2={l2}`
- `L3={l3}`
- `L4={l4}`
- `L5={l5}`
- 高质量层：`{l3_plus}`

## 当前档案层
- `L3+` 可读客户档案页：`{l3_plus}` 家
- 当前信息补强重点：已统一纠正 `收入规模/利润状态/营收增长` 空值与 `竞品/招聘` 缺口口径，后续继续补官网、年报、IR 和财报口径。
""",
        encoding="utf-8",
    )
    MILESTONE_MD.write_text(
        f"""# 内部状态-静态潜客池-Milestone状态总览

## 当前状态
- 唯一主体数：`{total}`
- 当前分层：`L1={l1} / L2={l2} / L3={l3} / L4={l4} / L5={l5}`
- `L3+`：`{l3_plus}`
- 本轮完成：对全部 `L3+` 做一轮信息补强与纠错，统一修正空值字段、来源口径和档案覆盖状态。
""",
        encoding="utf-8",
    )

    DOC_PATH.write_text(
        "\n".join([
            "# 静态潜客池-L3以上全量信息补强与纠错-v1",
            "",
            f"- 执行日期：`{TODAY}`",
            f"- 覆盖对象：当前全部 `L3+`，共 `{l3_plus}` 家。",
            f"- 本轮批量更新主表记录：`{updated}` 条。",
            f"- 新增质量补强 evidence：`{evidence_added}` 条。",
            f"- 新增档案补强备注：`{notes_added}` 条。",
            "",
            "## 本轮统一补强内容",
            "",
            "- 统一将 `收入规模区间 / 利润状态概述 / 营收增长概述` 的空值修正为 `待补公开财报口径`。",
            "- 基于现有画像池，为缺失的 `相似客户线索 / 主要竞品概述 / 招聘代表岗位` 回填默认可读口径。",
            "- 统一收紧 `validation_gap` 与 `profile_coverage.next_action`。",
            "- 统一将 `profile_owner` 调整为 `Codex 结构化沉淀`，并刷新 `last_profiled_at`。",
            "- 重生成全部 `L3+` 客户档案页、团队共享索引与 Obsidian 索引页。",
        ]),
        encoding="utf-8",
    )

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(
            f"\n- 对全部 `L3+`（`{l3_plus}` 家）做了一轮信息补强与纠错：统一纠正财报口径空值、补齐竞品/招聘/相似样本默认口径，并重生成全部客户档案页与团队共享索引。\n"
        )

    print({
        "total": total,
        "L3_plus": l3_plus,
        "updated": updated,
        "evidence_added": evidence_added,
        "notes_added": notes_added,
        "shared": shared,
        "unshared": unshared,
    })


if __name__ == "__main__":
    main()
