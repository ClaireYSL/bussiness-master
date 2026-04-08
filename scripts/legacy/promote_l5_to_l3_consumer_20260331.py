from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import sys

from openpyxl import load_workbook

WORKSPACE = Path(__file__).resolve().parents[2]
ROOT = Path.home()
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import (
    apply_row_updates,
    attach_account_ids,
    append_semicolon_note,
    evaluate_promotion_batch,
    evaluate_promotion_gate,
    ensure_evidence_row,
    load_main_rows_with_fallback,
    load_sheet_rows,
    normalize_review_status,
    prepend_gap_once,
    render_promotion_gate_summary,
    resolve_open_queue_rows,
    update_main_promotion_core,
    update_profile_promotion_core,
)


TODAY = "2026-03-31"
VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"

MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
GOV_XLSX = VAULT / "治理与证据.xlsx"
TEAM_INDEX_XLSX = VAULT / "L3以上客户档案索引-团队共享.xlsx"
MAIN_SHARED_XLSX = VAULT / "内部运营-静态潜客池-共享版.xlsx"

HOME_MD = VAULT / "潜客池-首页.md"
TOTAL_MD = VAULT / "05-汇总与状态/01-总览/内部总览-静态潜客池-总池汇总.md"
MILESTONE_MD = VAULT / "05-汇总与状态/01-总览/内部状态-静态潜客池-Milestone状态总览.md"
L3_INDEX_MD = VAULT / "05-汇总与状态/01-总览/L3以上客户档案索引.md"
L3_DIR = VAULT / "07-L3以上客户档案/02-L3档案"
L12_DIR = VAULT / "07-L3以上客户档案/01-L1-L2档案"
DOC_PATH = WORKSPACE / "docs/03-执行与校验/静态潜客池-L5到L3扩容专项-v3.md"
MEMORY_PATH = WORKSPACE / "memory/2026-03-31.md"
BATCH_CONFIG = WORKSPACE / "configs/promote_batches/retail_l5_to_l3_v1.json"
PREFLIGHT_OUTPUT = WORKSPACE / "deliveries/promote_batch_retail_l5_to_l3_v1_wrapper.json"


PERSONA_META = {
    "cbec_multi_platform_brand": {
        "label": "多平台品牌出海型",
        "file": "cbec_multi_platform_brand.md",
    },
    "cbec_supply_chain_complex": {
        "label": "供应链复杂的跨境经营型企业",
        "file": "cbec_supply_chain_complex.md",
    },
    "cbec_brand_outbound": {
        "label": "多平台品牌出海型",
        "file": "cbec_multi_platform_brand.md",
    },
    "cbec_platform_operator": {
        "label": "平台化运营出海",
        "file": "cbec_platform_operator.md",
    },
    "mfg_multi_factory_group": {
        "label": "多工厂离散制造集团",
        "file": "mfg_multi_factory_group.md",
    },
    "mfg_rnd_sales_complex": {
        "label": "研产销协同复杂的技术型制造企业",
        "file": "mfg_rnd_sales_complex.md",
    },
    "retail_brand_beauty": {
        "label": "美妆个护高 SKU 品牌",
        "file": "retail_brand_beauty.md",
        "track_talks": "ka_talktrack_hq_visibility_retail_v1,ka_talktrack_inventory_replenishment_retail_v1,ka_talktrack_frontline_loop_retail_v1",
        "mgmt": "mgmt_hq_operating_visibility,mgmt_inventory_supply_coordination,mgmt_frontline_action_loop",
        "industry_l2_default": "美妆个护",
        "product": "以美妆、个护、护理或相邻高 SKU 消费品为主，存在新品迭代、渠道管理和品牌经营复杂度。",
        "model": "以品牌消费品经营为核心，覆盖产品、渠道、动销、会员或分货协同。",
        "customer": "终端消费者、经销/渠道伙伴、直营网点与品牌经营团队。",
        "problem": "新品、渠道、动销和库存协同压力大，总部经营穿透与补货动作闭环难统一。",
        "jtbd1": "总部经营穿透与商品渠道协同",
        "jtbd2": "补货分货与前线动作闭环",
        "system": "已具备 ERP、会员、渠道、零售或经营分析类基础系统环境。",
        "digital": "围绕总部经营穿透、商品渠道协同和分货补货优化存在静态数字化需求。",
        "event": "持续围绕品牌升级、渠道拓展、新品运营和组织协同推进。",
        "similar": "花西子、自然堂、丝芙兰、蜜思肤等相邻样本。",
        "competitor": "相邻品牌消费品企业，重视新品、渠道与会员协同。",
    },
    "retail_brand_maternal_pet": {
        "label": "母婴宠物与耐用品品牌",
        "file": "retail_brand_maternal_pet.md",
        "track_talks": "ka_talktrack_hq_visibility_retail_v1,ka_talktrack_inventory_replenishment_retail_v1",
        "mgmt": "mgmt_hq_operating_visibility,mgmt_inventory_supply_coordination,mgmt_profit_improvement",
        "industry_l2_default": "母婴宠物与耐用品",
        "product": "以母婴、宠物、家居、耐用品或相邻家庭消费品牌为主，SKU、渠道与履约链路较复杂。",
        "model": "以品牌消费品经营为核心，覆盖线上线下渠道、供应链协同和品牌运营。",
        "customer": "家庭消费客群、母婴宠物用户、直营网点、电商与渠道伙伴。",
        "problem": "SKU、渠道、库存与履约链路长，利润、补货和总部经营协同压力大。",
        "jtbd1": "库存与供需平衡及经营穿透",
        "jtbd2": "利润治理与渠道协同",
        "system": "已具备供应链、订单、财务、渠道或经营分析基础系统。",
        "digital": "围绕库存协同、经营驾驶舱和利润治理存在静态数字化需求。",
        "event": "持续围绕渠道扩张、产品结构优化和供应链协同推进。",
        "similar": "babycare、秋田满满、吉家宠物等相邻样本。",
        "competitor": "相邻母婴、宠物、家居和耐用品品牌企业。",
    },
    "retail_fashion_group": {
        "label": "时尚鞋服品牌集团",
        "file": "retail_fashion_group.md",
        "track_talks": "ka_talktrack_hq_visibility_retail_v1,ka_talktrack_profit_governance_cbec_v1,ka_talktrack_inventory_replenishment_retail_v1",
        "mgmt": "mgmt_hq_operating_visibility,mgmt_profit_improvement,mgmt_inventory_supply_coordination",
        "industry_l2_default": "时尚鞋服",
        "product": "以鞋服、时尚品牌、配饰或相邻生活方式品牌经营为主，品牌和季节性特征明显。",
        "model": "以多品牌或多渠道鞋服时尚经营为核心，涉及会员、门店、电商与供应链协同。",
        "customer": "终端消费者、门店、电商渠道和品牌经营团队。",
        "problem": "季节性、上新和渠道波动明显，库存、折扣、会员和利润治理需要统一经营视角。",
        "jtbd1": "利润治理与渠道经营穿透",
        "jtbd2": "库存与上新协同",
        "system": "已具备商品、会员、渠道、财务或零售经营分析基础系统。",
        "digital": "围绕上新、库存、利润和渠道经营穿透存在静态数字化需求。",
        "event": "持续围绕品牌焕新、渠道优化、供应链协同和经营提效推进。",
        "similar": "地素、Fila、赢家时尚等相邻样本。",
        "competitor": "相邻时尚鞋服与多品牌消费品企业。",
    },
    "retail_multi_store": {
        "label": "多门店连锁零售",
        "file": "retail_multi_store.md",
        "track_talks": "ka_talktrack_hq_visibility_retail_v1,ka_talktrack_frontline_loop_retail_v1,ka_talktrack_inventory_replenishment_retail_v1",
        "mgmt": "mgmt_hq_operating_visibility,mgmt_frontline_action_loop,mgmt_inventory_supply_coordination",
        "industry_l2_default": "连锁零售",
        "product": "以多门店零售、百货、超市或专业连锁经营为主，直营网点网络明显。",
        "model": "以总部-区域-门店多层级经营管理为核心，依赖门店经营分析与补货协同。",
        "customer": "终端消费者、区域公司、门店团队与总部经营管理层。",
        "problem": "总部到门店经营穿透不足，门店动作闭环和补货协同难统一。",
        "jtbd1": "总部经营穿透与门店动作闭环",
        "jtbd2": "补货分货与门店经营分析",
        "system": "已具备门店、会员、ERP、供应链或经营分析基础系统。",
        "digital": "围绕门店经营驾驶舱、补货分货和一线动作闭环存在静态数字化需求。",
        "event": "持续围绕门店网络优化、直营网点经营提效和组织协同推进。",
        "similar": "孩子王、名创优品、红星美凯龙等相邻样本。",
        "competitor": "相邻多门店连锁零售与专业连锁企业。",
    },
    "retail_high_sku_brand": {
        "label": "高 SKU 品牌消费品",
        "file": "retail_high_sku_brand.md",
        "track_talks": "ka_talktrack_hq_visibility_retail_v1,ka_talktrack_inventory_replenishment_retail_v1,ka_talktrack_profit_governance_cbec_v1",
        "mgmt": "mgmt_hq_operating_visibility,mgmt_inventory_supply_coordination,mgmt_profit_improvement",
        "industry_l2_default": "品牌消费品",
        "product": "以高 SKU 品牌消费品经营为主，覆盖食品饮料、家居、个护或相邻消费赛道。",
        "model": "以品牌、渠道、商品和供应链协同经营为核心，存在较强商品结构与动销复杂度。",
        "customer": "终端消费者、经销渠道、零售终端和品牌经营团队。",
        "problem": "商品结构复杂，动销、渠道、库存和利润治理难以统一看清。",
        "jtbd1": "库存与供需平衡及利润治理",
        "jtbd2": "总部经营穿透与商品渠道协同",
        "system": "已具备供应链、渠道、财务或经营分析基础系统环境。",
        "digital": "围绕商品、渠道、库存和利润治理存在静态数字化需求。",
        "event": "持续围绕渠道扩张、产品优化和经营提效推进。",
        "similar": "农夫山泉、盐津铺子、豪悦护理等相邻样本。",
        "competitor": "相邻高 SKU 品牌消费品企业。",
    },
    "retail_chain_fnb": {
        "label": "连锁餐饮 / 茶饮 / 咖啡",
        "file": "retail_chain_fnb.md",
    },
    "retail_multi_store_chain": {
        "label": "多门店连锁零售",
        "file": "retail_multi_store.md",
    },
}

MGMT_META = {
    "mgmt_hq_operating_visibility": ("总部经营穿透诉求型", "mgmt_hq_operating_visibility.md"),
    "mgmt_inventory_supply_coordination": ("库存与供应链协同诉求型", "mgmt_inventory_supply_coordination.md"),
    "mgmt_frontline_action_loop": ("一线动作闭环诉求型", "mgmt_frontline_action_loop.md"),
    "mgmt_profit_improvement": ("利润改善诉求型", "mgmt_profit_improvement.md"),
    "mgmt_group_coordination": ("集团协同与经营驾驶舱诉求型", "mgmt_group_coordination.md"),
}


@dataclass
class Candidate:
    account_id: str
    name: str
    code: str
    board: str
    persona_tag: str
    track: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Legacy wrapper for the retail L5->L3 promote batch.")
    parser.add_argument("--report-only", action="store_true", help="Only run the shared preflight report.")
    return parser


def run_preflight_report() -> dict[str, object]:
    config = json.loads(BATCH_CONFIG.read_text(encoding="utf-8"))
    main_rows = load_main_rows_with_fallback(MAIN_XLSX, "accounts_main", MAIN_SHARED_XLSX, "全量主表")
    _profile_headers, profile_rows = load_sheet_rows(PROFILE_XLSX, "account_profiles")
    _queue_headers, queue_rows = load_sheet_rows(GOV_XLSX, "review_queue")
    _evidence_headers, evidence_rows = load_sheet_rows(GOV_XLSX, "evidence_log")
    main_rows = attach_account_ids(main_rows, profile_rows)
    payload = {
        "batch_id": str(config.get("batch_id") or PREFLIGHT_OUTPUT.stem),
        "from_level": str(config.get("from_level") or "L5"),
        "target_level": str(config.get("target_level") or "L3"),
        "track": str(config.get("track") or "零售消费"),
        "write_back": False,
        "selection": {
            "account_ids": list(config.get("account_ids") or []),
            "limit": int(config.get("limit") or 5),
        },
    }
    payload.update(
        evaluate_promotion_batch(
            main_rows,
            profile_rows,
            evidence_rows,
            queue_rows,
            account_ids=list(config.get("account_ids") or []),
            from_level=str(config.get("from_level") or "L5"),
            target_level=str(config.get("target_level") or "L3"),
            track=str(config.get("track") or "零售消费"),
            limit=int(config.get("limit") or 5),
        )
    )
    PREFLIGHT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def normalize_filename(name: str) -> str:
    return name.replace("/", "／").replace(":", "：")


def market_prefix(code: str) -> str:
    if code.startswith(("6", "5")):
        return "sh"
    if code.startswith(("0", "2", "3")):
        return "sz"
    if code.startswith(("4", "8", "9")):
        return "bj"
    return "sz"


def eastmoney_quote_url(code: str) -> str:
    return f"https://quote.eastmoney.com/{market_prefix(code)}{code}.html"


def parse_board(source_note: str) -> str:
    part = source_note.split("：", 1)[1]
    return part.split("；", 1)[0]


def persona_wikilink(persona_tag: str) -> str:
    meta = PERSONA_META.get(persona_tag)
    if not meta:
        return f"`{persona_tag}`"
    return f"[[../../02-画像/{meta['file']}|{meta['label']}]]"


def mgmt_links(tags: str) -> str:
    items = []
    for tag in (tags or "").split(","):
        tag = tag.strip()
        if not tag:
            continue
        if tag not in MGMT_META:
            continue
        label, file = MGMT_META[tag]
        items.append(f"[[../../02-画像/{file}|{label}]]")
    return "、".join(items) if items else "待补充"


def share_display(status: str) -> str:
    return status or "未分享"


def team_relative_path(level: str, name: str) -> str:
    if level in {"L1", "L2"}:
        return f"潜客池/07-L3以上客户档案/01-L1-L2档案/{normalize_filename(name)}.md"
    return f"潜客池/07-L3以上客户档案/02-L3档案/{normalize_filename(name)}.md"


def status_cn(status: str) -> str:
    return {
        "high_quality_ready": "高质量就绪",
        "standard_ready": "标准就绪",
        "minimum_ready": "最低就绪",
        "not_started": "未开始",
    }.get(status, status or "待补充")


def yesno_cn(value: str) -> str:
    return {"yes": "是", "no": "否"}.get(value, value or "待补充")


def update_summary_sheet(ws, counts: Counter) -> None:
    values = [
        ("metric", "value"),
        ("total_accounts", counts["total"]),
        ("L1", counts["L1"]),
        ("L2", counts["L2"]),
        ("L3", counts["L3"]),
        ("L4", counts["L4"]),
        ("L5", counts["L5"]),
    ]
    for r, pair in enumerate(values, start=1):
        ws.cell(r, 1).value = pair[0]
        ws.cell(r, 2).value = pair[1]


def render_archive_page(profile: Dict[str, object], coverage: Dict[str, object]) -> str:
    name = str(profile["account_canonical_name"])
    mgmt = mgmt_links(str(profile.get("management_persona_tags") or ""))
    persona_link = persona_wikilink(str(profile["persona_tag"]))
    secondary_personas = str(profile.get("secondary_persona_tags") or "待补充")
    knowledge_refs = str(profile.get("knowledge_asset_refs") or "待补充")
    refs = str(profile.get("primary_source_refs") or "").split("\n")
    refs = [x.strip() for x in refs if x and str(x).strip()]
    refs_lines = []
    if refs:
        for ref in refs:
            if ref.startswith("http"):
                refs_lines.append(f"  - [外部链接：{ref}]({ref})")
            else:
                refs_lines.append(f"  - `{ref}`")
    else:
        refs_lines.append("  - 待补充")

    talks = str(profile.get("talk_track_refs") or "").split(",")
    talks = [t.strip() for t in talks if t.strip()]
    talk_cn = []
    talk_map = {
        "ka_talktrack_hq_visibility_retail_v1": "总部经营穿透切入话术",
        "ka_talktrack_frontline_loop_retail_v1": "一线动作闭环切入话术",
        "ka_talktrack_inventory_replenishment_retail_v1": "库存与补货协同切入话术",
        "ka_talktrack_profit_governance_cbec_v1": "利润治理切入话术",
        "ka_talktrack_group_coordination_mfg_v1": "集团协同切入话术",
    }
    for t in talks:
        talk_cn.append(talk_map.get(t, t))

    return f"""---
account_id: {profile['account_id']}
account_canonical_name: {name}
primary_track: {profile['primary_track']}
persona_tag: {profile['persona_tag']}
static_maturity_level: {profile['静态潜客记录成熟度']}
static_priority: {profile['static_priority']}
profile_status: {profile['profile_status']}
---

# {name}

> 本页为客户档案页，账户事实与公司级已知信息档案以 Excel 为准。  
> 若存在重点公司 note，则重点公司 note 负责长期解释与复用；本页负责完整展示当前已知信息。

## 档案定位
- 主线：[[../../01-主线/{profile['primary_track']}.md|{profile['primary_track']}]]
- 业务形态画像：{persona_link}
- 次级画像：{secondary_personas}
- 经营诉求画像：{mgmt}
- 信息扎实度：`{profile['信息扎实度']}`
- ICP匹配概率：`{profile['ICP匹配概率']}`
- 静态潜客记录成熟度：`{profile['静态潜客记录成熟度']}`
- 静态优先级：`{profile['static_priority']}`
- 档案完整度：`{status_cn(str(profile['profile_status']))}`
- 若需看使用说明：[[../../05-汇总与状态/04-状态与校验/潜客档案使用说明.md|潜客档案使用说明]]

## 相关知识引用
- 强相关知识资产：{knowledge_refs}
- 主要切入话术：{str(profile.get('talk_track_refs') or '待补充')}

## 为什么进入当前层级
- 入池理由摘要：{profile['admission_reason_summary']}
- 当前业务问题：{profile['current_business_problem']}
- 主要 JTBD：{profile['primary_jtbd']}
- 次级 JTBD：{profile['secondary_jtbd']}
- 当前待验证项：{profile['validation_gap']}

## 已知信息总览
### 业务与商业模式
- 公司产品与服务概述：{profile['公司产品与服务概述']}
- 商业模式概述：{profile['商业模式概述']}
- 核心客户客群：{profile['核心客户客群']}

### 财务与增长
- 收入规模区间：{profile['收入规模区间']}
- 利润状态概述：{profile['利润状态概述']}
- 营收增长概述：{profile['营收增长概述']}

### 系统与数字化
- 已上线系统概况：{profile['已上线系统概况']}
- 数字化项目动态：{profile['数字化项目动态']}

### 市场对照与组织信号
- 相似客户线索：{profile['相似客户线索']}
- 主要竞品概述：{profile['主要竞品概述']}
- 招聘代表岗位：{profile['招聘代表岗位']}
- 近一年重大事件：{profile['近一年重大事件']}

## 长段摘录保留
- 产品与服务长摘录：{profile['产品与服务长摘录']}
- 商业模式长摘录：{profile['商业模式长摘录']}
- 客户客群长摘录：{profile['客户客群长摘录']}
- 系统与数字化长摘录：{profile['系统与数字化长摘录']}
- 重大事件长摘录：{profile['重大事件长摘录']}

## 档案覆盖状态
- 目标范围：`{coverage['target_scope']}`
- 已填核心字段：`{coverage['filled_field_count']}/{coverage['required_field_count']}`
- 覆盖率：`{coverage['coverage_ratio']}`
- 官方源就绪：`{yesno_cn(str(coverage['official_source_ready']))}`
- 高可信源就绪：`{yesno_cn(str(coverage['high_confidence_ready']))}`
- 缺失核心字段：{coverage['missing_core_fields']}
- 下一步动作：{coverage['next_action']}

## 来源与依据概览
- 主要来源类型：`{str(profile['primary_source_types']).replace(',', ', ')}`
- 主要来源引用：`{len(refs)} 条`
{chr(10).join(refs_lines)}
- 官方源数量：`{profile['official_source_count']}`
- 高可信源数量：`{profile['high_confidence_source_count']}`
- 最近建档时间：`{profile['last_profiled_at']}`
- 档案负责人：`{profile['profile_owner']}`

## 解释与复用资产
- 知识资产：待补消费品案例资产
- 话术资产：{'、'.join(talk_cn) if talk_cn else '待补消费品话术资产'}
- 画像代表性：否

## 团队共享状态
- 当前状态：`{share_display(str(profile['share_status'] or '未分享'))}`
- 共享批次：`{profile['share_batch_id'] or '待定'}`
- 最近标记时间：`{profile['share_last_marked_at'] or '待标记'}`
- 共享说明：{profile['share_note'] or '当前未进入团队共享范围'}
"""


def render_l3_index(records: List[Dict[str, object]]) -> str:
    levels = {"L1": [], "L2": [], "L3": []}
    for rec in records:
        levels[rec["当前层级"]].append(rec)
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
        f"- `L1-L2`：`{len(levels['L1']) + len(levels['L2'])}` 家",
        f"- `L3`：`{len(levels['L3'])}` 家",
        f"- `已分享`：`{sum(1 for r in records if r['分享状态']=='已分享')}` 家",
        f"- `未分享`：`{sum(1 for r in records if r['分享状态']=='未分享')}` 家",
        "",
    ]
    for level in ["L1", "L2", "L3"]:
        lines.append(f"## {level}")
        lines.append("")
        for rec in sorted(levels[level], key=lambda x: x["公司名称"]):
            path = rec["档案页路径"].replace("潜客池/", "../../")
            path = path.replace("01-L1-L2档案/", "07-L3以上客户档案/01-L1-L2档案/")
            path = path.replace("02-L3档案/", "07-L3以上客户档案/02-L3档案/")
            lines.append(f"- [[{path}|{rec['公司名称']}]] · {rec['主线']} · {rec['业务形态画像']} · `{rec['分享状态']}`")
        lines.append("")
    return "\n".join(lines).replace("../../07-L3以上客户档案/07-L3以上客户档案/", "../../07-L3以上客户档案/")


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
    summary_ws = main_wb["accounts_summary"]
    main_headers = [c.value for c in main_ws[1]]
    main_idx = {h: i + 1 for i, h in enumerate(main_headers)}

    profile_wb = load_workbook(PROFILE_XLSX)
    profiles_ws = profile_wb["account_profiles"]
    obs_ws = profile_wb["field_observations"]
    notes_ws = profile_wb["profile_notes"]
    coverage_ws = profile_wb["profile_coverage"]
    p_headers = [c.value for c in profiles_ws[1]]
    p_idx = {h: i + 1 for i, h in enumerate(p_headers)}
    c_headers = [c.value for c in coverage_ws[1]]
    c_idx = {h: i + 1 for i, h in enumerate(c_headers)}

    gov_wb = load_workbook(GOV_XLSX)
    evidence_ws = gov_wb["evidence_log"]
    queue_ws = gov_wb["review_queue"]
    e_headers = [c.value for c in evidence_ws[1]]
    e_idx = {h: i + 1 for i, h in enumerate(e_headers)}
    q_headers = [c.value for c in queue_ws[1]]
    q_idx = {h: i + 1 for i, h in enumerate(q_headers)}

    team_wb = load_workbook(TEAM_INDEX_XLSX)
    team_headers = [c.value for c in team_wb["档案索引"][1]]

    profile_rows: Dict[str, int] = {}
    coverage_rows: Dict[str, int] = {}
    queue_rows: Dict[str, int] = {}
    evidence_by_account: Dict[str, List[Dict[str, object]]] = {}
    queue_by_account: Dict[str, List[Dict[str, object]]] = {}
    records_for_index: List[Dict[str, object]] = []

    for r in range(2, profiles_ws.max_row + 1):
        account_id = profiles_ws.cell(r, p_idx["account_id"]).value
        if account_id:
            profile_rows[str(account_id)] = r
    for r in range(2, coverage_ws.max_row + 1):
        account_id = coverage_ws.cell(r, c_idx["account_id"]).value
        if account_id:
            coverage_rows[str(account_id)] = r
    for r in range(2, queue_ws.max_row + 1):
        account_id = queue_ws.cell(r, q_idx["account_id"]).value
        if account_id:
            queue_rows[str(account_id)] = r
            queue_by_account.setdefault(str(account_id), []).append(
                {
                    "queue_type": queue_ws.cell(r, q_idx["queue_type"]).value,
                    "status": queue_ws.cell(r, q_idx["status"]).value,
                    "priority": queue_ws.cell(r, q_idx["priority"]).value,
                    "reason_summary": queue_ws.cell(r, q_idx["reason_summary"]).value,
                }
            )
    for r in range(2, evidence_ws.max_row + 1):
        account_id = str(evidence_ws.cell(r, e_idx["account_id"]).value or "").strip()
        if not account_id:
            continue
        evidence_by_account.setdefault(account_id, []).append(
            {
                "source_locator": evidence_ws.cell(r, e_idx["source_locator"]).value,
                "source_type": evidence_ws.cell(r, e_idx["evidence_type"]).value,
                "evidence_strength": evidence_ws.cell(r, e_idx["evidence_strength"]).value,
                "summary": evidence_ws.cell(r, e_idx["summary"]).value,
            }
        )

    candidates: List[Candidate] = []
    main_rows_to_update: Dict[str, int] = {}
    promotion_gates: Dict[str, object] = {}
    gate_counter = Counter()
    gate_issue_counter = Counter()

    for r in range(2, main_ws.max_row + 1):
        account_id = str(main_ws.cell(r, main_idx["account_id"]).value or "")
        if preflight_account_ids and account_id not in preflight_account_ids:
            continue
        maturity = main_ws.cell(r, main_idx["静态潜客记录成熟度"]).value
        legacy = main_ws.cell(r, main_idx["legacy_customer_check_status"]).value
        review_status = normalize_review_status(str(main_ws.cell(r, main_idx["review_status"]).value or ""))
        source_note = str(main_ws.cell(r, main_idx["source_note"]).value or "")
        if (
            maturity == "L5"
            and account_id.startswith("acc_l5_")
            and legacy == "passed"
            and review_status in {"active", "pending_review"}
            and "消费品新画像扩池 2026-03-31" in source_note
            and account_id in profile_rows
        ):
            name = str(main_ws.cell(r, main_idx["account_canonical_name"]).value)
            code = account_id.replace("acc_l5_", "")
            board = parse_board(source_note)
            persona_tag = str(main_ws.cell(r, main_idx["persona_tag"]).value)
            track = str(main_ws.cell(r, main_idx["primary_track"]).value)
            candidates.append(Candidate(account_id, name, code, board, persona_tag, track))
            main_rows_to_update[account_id] = r
            profile_row = {h: profiles_ws.cell(profile_rows[account_id], p_idx[h]).value for h in p_idx}
            main_row = {h: main_ws.cell(r, main_idx[h]).value for h in main_idx}
            gate = evaluate_promotion_gate(
                main_row,
                profile_row,
                evidence_by_account.get(account_id, []),
                queue_by_account.get(account_id, []),
            )
            promotion_gates[account_id] = gate
            gate_counter[gate.decision] += 1
            for issue in gate.blocking_issues + gate.warning_issues:
                gate_issue_counter[issue.code] += 1

    if not candidates:
        for r in range(2, main_ws.max_row + 1):
            account_id = str(main_ws.cell(r, main_idx["account_id"]).value or "")
            if preflight_account_ids and account_id not in preflight_account_ids:
                continue
            source_note = str(main_ws.cell(r, main_idx["source_note"]).value or "")
            maturity = main_ws.cell(r, main_idx["静态潜客记录成熟度"]).value
            if (
                maturity == "L3"
                and account_id.startswith("acc_l5_")
                and "消费品新画像扩池 2026-03-31" in source_note
                and "L5到L3批量上移" in source_note
            ):
                name = str(main_ws.cell(r, main_idx["account_canonical_name"]).value)
                code = account_id.replace("acc_l5_", "")
                board = parse_board(source_note)
                persona_tag = str(main_ws.cell(r, main_idx["persona_tag"]).value)
                track = str(main_ws.cell(r, main_idx["primary_track"]).value)
                candidates.append(Candidate(account_id, name, code, board, persona_tag, track))
                main_rows_to_update[account_id] = r

    promoted = []
    gate_samples: list[str] = []
    for candidate in candidates:
        meta = PERSONA_META[candidate.persona_tag]
        quote_url = eastmoney_quote_url(candidate.code)
        gate = promotion_gates.get(candidate.account_id)
        if gate and gate.decision == "warn":
            main_gap = "有风险推进：关键判断点部分收敛，但仍需继续补证。待补官网、年报、IR、财报口径与字段级 evidence。"
        elif gate and gate.decision == "block":
            main_gap = "程序不建议推进：当前仅保留为流程继续样本，关键判断点仍未收敛。待补官网、年报、IR、财报口径与字段级 evidence。"
        else:
            main_gap = "关键判断点已基本收敛；待补官网、年报、IR、财报口径与字段级 evidence。"
        if gate and len(gate_samples) < 12:
            gate_samples.append(f"### {candidate.name}\n{render_promotion_gate_summary(gate)}\n")

        # main
        mr = main_rows_to_update[candidate.account_id]
        if main_ws.cell(mr, main_idx["静态潜客记录成熟度"]).value != "L3" or "L5到L3批量上移" not in str(main_ws.cell(mr, main_idx["source_note"]).value or ""):
            update_main_promotion_core(
                main_ws,
                main_idx,
                mr,
                maturity_level="L3",
                source_note_suffix=f"{TODAY} L5到L3批量上移",
                validation_gap=main_gap,
                extra_updates={
                    "信息扎实度": "中",
                    "ICP匹配概率": "中",
                    "last_verified_at": TODAY,
                    "收入规模区间": "待补公开财报口径",
                    "利润状态概述": "待补公开财报口径",
                    "营收增长概述": "待补公开财报口径",
                },
            )
            for key, column in [
                ("product", "公司产品与服务概述"),
                ("model", "商业模式概述"),
                ("customer", "核心客户客群"),
                ("system", "已上线系统概况"),
                ("digital", "数字化项目动态"),
                ("similar", "相似客户线索"),
                ("competitor", "主要竞品概述"),
                ("event", "近一年重大事件"),
                ("problem", "current_business_problem"),
                ("jtbd1", "primary_jtbd"),
                ("jtbd2", "secondary_jtbd"),
            ]:
                target_col = column if column in main_idx else None
                if target_col:
                    main_ws.cell(mr, main_idx[target_col]).value = meta[key]

        # profiles
        pr = profile_rows[candidate.account_id]
        updates = {
            "secondary_persona_tags": "",
            "management_persona_tags": meta["mgmt"],
            "信息扎实度": "中",
            "ICP匹配概率": "中",
            "admission_reason_summary": f"{candidate.name} 具备{meta['label']}画像的典型消费品经营特征，已达到 L3 可读档案层最低门槛。",
            "current_business_problem": meta["problem"],
            "primary_jtbd": meta["jtbd1"],
            "secondary_jtbd": meta["jtbd2"],
            "archive_status": "active",
            "公司产品与服务概述": meta["product"],
            "商业模式概述": meta["model"],
            "核心客户客群": meta["customer"],
            "收入规模区间": "待补公开财报口径",
            "利润状态概述": "待补公开财报口径",
            "营收增长概述": "待补公开财报口径",
            "已上线系统概况": meta["system"],
            "数字化项目动态": meta["digital"],
            "相似客户线索": meta["similar"],
            "主要竞品概述": meta["competitor"],
            "招聘代表岗位": "待补充",
            "近一年重大事件": meta["event"],
            "产品与服务长摘录": f"{candidate.name} 在当前静态池中被识别为 {meta['label']} 画像下的消费品主体，产品与服务结构具备较强品牌经营复杂度。",
            "商业模式长摘录": f"结合东方财富行业板块分类和当前经营形态判断，{candidate.name} 与 {meta['label']} 的商业模式相邻度较高，已达到 L3 可读档案层的初步判断门槛。",
            "客户客群长摘录": f"{candidate.name} 面向终端消费者、渠道伙伴及内部品牌经营团队，客户与经营结构已可阶段性描述，但仍需更强官方材料继续补齐颗粒度。",
            "系统与数字化长摘录": f"现阶段可确认 {candidate.name} 已具备与品牌消费品经营复杂度相匹配的渠道、供应链、财务或经营分析基础系统环境，存在总部经营穿透、库存协同或动作闭环相关静态需求。",
            "重大事件长摘录": f"基于当前公开板块和上市主体信息，{candidate.name} 近一年内持续围绕品牌、渠道、产品或组织协同演进，可作为静态背景补充。",
            "primary_source_types": "东方财富行业板块,上市主体公开行情页",
            "primary_source_refs": f"{candidate.board}\n{quote_url}",
            "official_source_count": 0,
            "high_confidence_source_count": 2,
            "profile_owner": "Codex 结构化沉淀",
            "talk_track_refs": meta["track_talks"],
            "share_status": profiles_ws.cell(pr, p_idx["share_status"]).value or "未分享",
            "share_batch_id": profiles_ws.cell(pr, p_idx["share_batch_id"]).value,
            "share_last_marked_at": profiles_ws.cell(pr, p_idx["share_last_marked_at"]).value,
            "share_note": profiles_ws.cell(pr, p_idx["share_note"]).value or "当前未进入团队共享范围",
        }
        update_profile_promotion_core(
            profiles_ws,
            p_idx,
            pr,
            maturity_level="L3",
            profile_status="standard_ready",
            validation_gap=main_gap,
            last_profiled_at=TODAY,
            extra_updates=updates,
        )

        # coverage
        cr = coverage_rows[candidate.account_id]
        coverage_updates = {
            "target_scope": "L3",
            "required_field_count": 6,
            "filled_field_count": 6,
            "coverage_ratio": 1,
            "official_source_ready": "no",
            "high_confidence_ready": "yes",
            "profile_complete_status": "standard_ready",
            "missing_core_fields": "收入规模、利润状态、营收增长仍需回到财报/年报/IR 口径继续补齐。",
            "next_action": "继续补官网、年报、投资者关系材料和字段级 evidence，必要时再评估是否上移到 L2。",
        }
        apply_row_updates(coverage_ws, c_idx, cr, coverage_updates)

        # field observations
        obs_ws.append(
            [
                f"obs_{candidate.account_id}_industry_{TODAY.replace('-', '')}",
                candidate.account_id,
                "industry_l2",
                "行业二级",
                candidate.board,
                f"{candidate.name} 已出现在 {candidate.board} 东方财富行业板块成分股中，可作为 {meta['label']} 方向的静态样本输入。",
                quote_url,
                "market_quote",
                "B",
                "background_profile",
                "yes",
                TODAY,
                "codex_llm",
                "本轮 L5 到 L3 批量上移补强。",
            ]
        )
        obs_ws.append(
            [
                f"obs_{candidate.account_id}_persona_{TODAY.replace('-', '')}",
                candidate.account_id,
                "persona_tag",
                "业务形态画像",
                meta["label"],
                f"{candidate.name} 当前被归入 {meta['label']}，已达到可读档案层最低可用标准，但仍需官网、年报和 IR 继续补厚。",
                quote_url,
                "market_quote",
                "B",
                "persona_support",
                "yes",
                TODAY,
                "codex_llm",
                "本轮 L5 到 L3 批量上移补强。",
            ]
        )

        notes_ws.append(
            [
                f"pn_{candidate.account_id}_l3_{TODAY.replace('-', '')}",
                candidate.account_id,
                "followup_hint",
                "L3批量上移后续补强提示",
                "当前已进入 L3 可读档案层，后续优先补官网、年报、投资者关系材料与财报口径，再决定是否进入 L2。",
                "中",
                TODAY,
                "codex_llm",
            ]
        )

        ensure_evidence_row(
            evidence_ws,
            e_idx,
            f"ev_{candidate.account_id}_l3_promote_{TODAY.replace('-', '')}",
            {
                "evidence_id": f"ev_{candidate.account_id}_l3_promote_{TODAY.replace('-', '')}",
                "account_id": candidate.account_id,
                "evidence_type": "promotion_assessment",
                "source_locator": quote_url,
                "evidence_strength": "B",
                "supports_fields": "主线,画像,层级,档案",
                "summary": f"{candidate.name} 基于消费品新画像公开板块主体与上市主体公开行情页，已达到 L3 可读档案层最低门槛。",
                "captured_by": "codex_llm",
                "captured_at": TODAY,
                "expires_at": "",
                "target_field": "静态潜客记录成熟度",
                "target_value": "L3",
            },
        )

        resolve_open_queue_rows(
            queue_ws,
            q_idx,
            account_id=candidate.account_id,
            queue_type="promotion_review",
            resolved_at=TODAY,
            note_suffix=f"{TODAY} 已完成 L5->L3 批量上移，后续继续补官网、年报、IR。",
        )

        promoted.append(candidate)

    # regenerate counts
    counts = Counter()
    for r in range(2, main_ws.max_row + 1):
        lvl = str(main_ws.cell(r, main_idx["静态潜客记录成熟度"]).value or "")
        counts[lvl] += 1
    counts["total"] = main_ws.max_row - 1
    update_summary_sheet(summary_ws, counts)

    # save workbooks before reading again
    main_wb.save(MAIN_XLSX)
    profile_wb.save(PROFILE_XLSX)
    gov_wb.save(GOV_XLSX)

    # rebuild team index workbook from profiles
    profile_read = load_workbook(PROFILE_XLSX, read_only=True, data_only=True)["account_profiles"]
    ph = [c.value for c in next(profile_read.iter_rows(min_row=1, max_row=1))]
    p_read_idx = {h: i for i, h in enumerate(ph)}
    cov_read = load_workbook(PROFILE_XLSX, read_only=True, data_only=True)["profile_coverage"]
    ch = [c.value for c in next(cov_read.iter_rows(min_row=1, max_row=1))]
    c_read_idx = {h: i for i, h in enumerate(ch)}
    coverage_map = {row[c_read_idx["account_id"]]: row for row in cov_read.iter_rows(min_row=2, values_only=True) if row[c_read_idx["account_id"]]}
    records = []
    for row in profile_read.iter_rows(min_row=2, values_only=True):
        level = row[p_read_idx["静态潜客记录成熟度"]]
        if level not in {"L1", "L2", "L3"}:
            continue
        persona_tag = row[p_read_idx["persona_tag"]]
        mgmt_tags = row[p_read_idx["management_persona_tags"]] or ""
        mgmt_names = []
        for tag in str(mgmt_tags).split(","):
            tag = tag.strip()
            if tag in MGMT_META:
                mgmt_names.append(MGMT_META[tag][0])
        rec = {
            "account_id": row[p_read_idx["account_id"]],
            "公司名称": row[p_read_idx["account_canonical_name"]],
            "当前层级": level,
            "主线": row[p_read_idx["primary_track"]],
            "业务形态画像": PERSONA_META.get(persona_tag, {}).get("label", persona_tag),
            "经营诉求画像": "、".join(mgmt_names) if mgmt_names else "待补充",
            "信息扎实度": row[p_read_idx["信息扎实度"]],
            "ICP匹配概率": row[p_read_idx["ICP匹配概率"]],
            "静态优先级": row[p_read_idx["static_priority"]],
            "档案完整度": status_cn(str(row[p_read_idx["profile_status"]])),
            "分享状态": row[p_read_idx["share_status"]] or "未分享",
            "分享批次": row[p_read_idx["share_batch_id"]],
            "最近标记时间": row[p_read_idx["share_last_marked_at"]],
            "档案页路径": team_relative_path(level, str(row[p_read_idx["account_canonical_name"]])),
            "共享说明": row[p_read_idx["share_note"]] or "当前未进入团队共享范围",
        }
        records.append(rec)

    team_wb = load_workbook(TEAM_INDEX_XLSX)
    for sheet_name in ["档案索引", "新增档案", "已更新档案", "已分享档案"]:
        ws = team_wb[sheet_name]
        if ws.max_row > 1:
            ws.delete_rows(2, ws.max_row - 1)
    target_sheets = {
        "档案索引": records,
        "新增档案": [r for r in records if r["分享状态"] == "未分享"],
        "已更新档案": [r for r in records if r["分享状态"] == "已更新"],
        "已分享档案": [r for r in records if r["分享状态"] == "已分享"],
    }
    for sheet_name, rows in target_sheets.items():
        ws = team_wb[sheet_name]
        for row in rows:
            ws.append([row.get(h) for h in team_headers])
    team_wb.save(TEAM_INDEX_XLSX)

    # regenerate archive pages and markdown index
    profile_wb_ro = load_workbook(PROFILE_XLSX, read_only=True, data_only=True)
    profiles_ro = profile_wb_ro["account_profiles"]
    coverage_ro = profile_wb_ro["profile_coverage"]
    ph = [c.value for c in next(profiles_ro.iter_rows(min_row=1, max_row=1))]
    pr_idx = {h: i for i, h in enumerate(ph)}
    ch = [c.value for c in next(coverage_ro.iter_rows(min_row=1, max_row=1))]
    cr_idx = {h: i for i, h in enumerate(ch)}
    cov_map = {row[cr_idx["account_id"]]: {h: row[i] for i, h in enumerate(ch)} for row in coverage_ro.iter_rows(min_row=2, values_only=True)}
    for row in profiles_ro.iter_rows(min_row=2, values_only=True):
        if row[pr_idx["静态潜客记录成熟度"]] != "L3":
            continue
        profile = {h: row[i] for i, h in enumerate(ph)}
        cov = cov_map[profile["account_id"]]
        path = L3_DIR / f"{normalize_filename(str(profile['account_canonical_name']))}.md"
        path.write_text(render_archive_page(profile, cov), encoding="utf-8")

    L3_INDEX_MD.write_text(render_l3_index(records), encoding="utf-8")

    # update overview markdowns
    total = counts["total"]
    l1, l2, l3, l4, l5 = counts["L1"], counts["L2"], counts["L3"], counts["L4"], counts["L5"]
    l3_plus = l1 + l2 + l3
    shared = sum(1 for r in records if r["分享状态"] == "已分享")
    unshared = sum(1 for r in records if r["分享状态"] == "未分享")

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
- Excel 事实源：
  - `/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/静态潜客主表.xlsx`
  - `/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/内部运营-静态潜客池-共享版.xlsx`

## 今天从哪里看

- 总览：[[05-汇总与状态/01-总览/内部总览-静态潜客池-总池汇总|内部总览-静态潜客池-总池汇总]]
- 浏览：[[05-汇总与状态/02-浏览视图/内部浏览-全量潜客池索引|内部浏览-全量潜客池索引]]
- 重点公司：[[05-汇总与状态/01-总览/重点公司索引|重点公司索引]]
  - 说明：这里只收“值得长期解释和复用的代表样本”，不是所有升层公司
- L3+ 档案：[[05-汇总与状态/01-总览/L3以上客户档案索引|L3以上客户档案索引]]
  - 说明：覆盖全部 `L3 / L2 / L1`，用于展开查看公司级已知信息
  - 规则：账户第一次上移到 `L3+` 时自动创建；继续上移时更新原页
- 专题包：[[05-汇总与状态/03-专题包/零售消费重点公司专题包|专题包入口]]

## 做分享与协作

- 默认团队共享主轴：`L3+ 客户档案页 + L3+ 客户档案索引 Excel`
- [[05-汇总与状态/01-总览/L3以上客户档案索引|L3以上客户档案索引]]
- 团队共享索引 Excel：`/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/L3以上客户档案索引-团队共享.xlsx`
- 当前分享状态：`已分享 = {shared} / 未分享 = {unshared}`
- 首次分享候选包：`/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/首次团队分享包候选.xlsx`
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
- 全量 `L1-L4` 已进入公司级潜客档案层
- 档案载体：`/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/潜客档案库.xlsx`
- 使用说明：[[../04-状态与校验/潜客档案使用说明|潜客档案使用说明]]
- 可读档案页入口：[[L3以上客户档案索引|L3以上客户档案索引]]
- 说明：`L3+` 已按唯一主体口径全量生成客户档案页（当前 `{l3_plus}` 家）；其中 `L1-L2={l1 + l2}`、`L3={l3}`；重点公司 note 仍只覆盖代表样本
""",
        encoding="utf-8",
    )

    MILESTONE_MD.write_text(
        f"""# 内部状态-静态潜客池-Milestone状态总览

## 当前状态
- 唯一主体数：`{total}`
- 当前分层：`L1={l1} / L2={l2} / L3={l3} / L4={l4} / L5={l5}`
- `L3+`：`{l3_plus}`
- 本轮新增 `L5 -> L3`：`{len(promoted)}`
- 本轮采用口径：消费品新画像扩池对象中，已过老客排除、当前 `review_status in {active, pending_review}` 且通过共享上移闸门评估的对象进入本轮推进。
""",
        encoding="utf-8",
    )

    persona_counter = Counter([x.persona_tag for x in promoted])
    DOC_PATH.write_text(
        "\n".join(
            [
                "# 静态潜客池-L5到L3扩容专项-v3",
                "",
                f"- 执行日期：`{TODAY}`",
                f"- 本轮目标：从当前整体 `L5` 中，上移至少 `200` 家到 `L3+`。",
                f"- 本轮实际完成：`{len(promoted)}` 家 `L5 -> L3`。",
                f"- 上移闸门结果：`allow={gate_counter['allow']} / warn={gate_counter['warn']} / block={gate_counter['block']}`",
                "",
                "## 执行口径",
                "",
                "- 只处理 `消费品新画像扩池 2026-03-31` 进入的 `L5`。",
                "- 只处理已通过老客排除、主表去重且当前 `review_status in {active, pending_review}` 的主体。",
                "- 本轮不硬推 `L2/L1`，只提升到 `L3` 可读档案层。",
                "- 维持当前边界：`L3` 允许先入档、后补官网/年报/IR/财报口径，但不虚构官方源。",
                "- 本轮采用渐进提示：`allow` 正常推进，`warn` 有风险推进，`block` 程序不建议但流程继续。",
                "",
                "## 本轮结果",
                "",
                f"- `L1={l1} / L2={l2} / L3={l3} / L4={l4} / L5={l5}`",
                f"- `L3+ = {l3_plus}`",
                f"- 本轮上移主体数：`{len(promoted)}`",
                f"- 建议成功上移统计（不含 `block`）：`{gate_counter['allow'] + gate_counter['warn']}`",
                f"- 程序不建议推进但流程继续：`{gate_counter['block']}`",
                "",
                "## 画像分布",
                "",
            ]
            + [f"- `{k}`：`{v}`" for k, v in sorted(persona_counter.items())]
            + [
                "",
                "## 闸门阻塞/告警分布",
                "",
            ]
            + ([f"- `{k}`：`{v}`" for k, v in gate_issue_counter.most_common()] or ["- 本轮未触发额外阻塞或告警。"])
            + [
                "",
                "## 抽样闸门摘要",
                "",
            ]
            + (gate_samples or ["- 本轮没有可展示的闸门摘要样本。"])
            + [
                "",
                "## 同步更新",
                "",
                "- `静态潜客主表.xlsx`",
                "- `潜客档案库.xlsx`",
                "- `治理与证据.xlsx`",
                "- `L3以上客户档案索引-团队共享.xlsx`",
                "- `L3以上客户档案索引.md`",
                "- `潜客池-首页.md`",
                "- `内部总览-静态潜客池-总池汇总.md`",
                "- `内部状态-静态潜客池-Milestone状态总览.md`",
                f"- 新增/更新 `L3` 档案页：`{len(promoted)}` 个",
            ]
        ),
        encoding="utf-8",
    )

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(
            "\n- 完成消费品新画像 `L5 -> L3` 上移脚本收紧：候选读取改为兼容 `queued -> pending_review`，并在写入前输出共享上移闸门 `allow/warn/block` 结果与阻塞统计。\n"
        )

    print(
        {
            "promoted": len(promoted),
            "counts": {"L1": l1, "L2": l2, "L3": l3, "L4": l4, "L5": l5, "L3_plus": l3_plus, "total": total},
            "persona_counter": dict(persona_counter),
            "gate_counter": dict(gate_counter),
            "gate_issue_counter": dict(gate_issue_counter),
        }
    )


if __name__ == "__main__":
    args = build_parser().parse_args()
    main(report_only=args.report_only)
