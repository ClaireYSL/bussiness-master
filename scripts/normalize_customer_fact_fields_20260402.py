from __future__ import annotations

import time
from pathlib import Path
from zipfile import BadZipFile

from openpyxl import load_workbook


VAULT = Path("/Users/clairaipartner/Documents/Obsidian-Codex/潜客池")
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
MAIN_XLSX = VAULT / "静态潜客主表.xlsx"

TARGET_LEVELS = {"L1", "L2", "L3"}
FACT_PLACEHOLDER = "待补官网/年报/IR口径"
EVENT_PLACEHOLDER = "待补更强官方披露"
MARKET_PLACEHOLDER = "待补公司级市场参考"
ASSET_PLACEHOLDER = "待补公司级资产映射"
PERSONA_LABELS = {
    "cbec_multi_platform_brand": "多平台品牌出海型",
    "cbec_supply_chain_complex": "供应链复杂的跨境经营型企业",
    "cbec_brand_outbound": "多平台品牌出海型",
    "cbec_platform_operator": "平台化运营出海",
    "mfg_multi_factory_group": "多工厂离散制造集团",
    "mfg_rnd_sales_complex": "研产销协同复杂的技术型制造企业",
    "retail_brand_beauty": "美妆个护高 SKU 品牌",
    "retail_brand_maternal_pet": "母婴宠物与耐用品品牌",
    "retail_fashion_group": "时尚鞋服品牌集团",
    "retail_multi_store": "多门店连锁零售",
    "retail_high_sku_brand": "高 SKU 品牌消费品",
    "retail_chain_fnb": "连锁餐饮/茶饮/咖啡",
    "retail_multi_store_chain": "多门店连锁零售",
    "fnb_chain_standardized": "标准化连锁餐饮",
    "fnb_chain_beverage_coffee": "茶饮咖啡连锁",
}

GENERIC_PRODUCT_PREFIXES = (
    "现有材料只能稳定支撑",
    "现有材料可支撑其",
    "现有材料可支撑其属于",
    "研发、制造、销售协同复杂的技术型制造业务。",
    "主营品牌消费品、个护、家居、食品或耐用品等多 SKU 产品",
    "主营技术型设备、材料、工业产品或高复杂制造业务",
    "主营多工厂、多基地制造业务",
    "多工厂、多事业部的集团型制造业务。",
    "跨境供应链复杂、依赖海外仓或多履约链路的出海经营。",
    "品牌出海与多平台经营，产品矩阵和区域经营复杂。",
)
GENERIC_BUSINESS_PREFIXES = (
    "现有候选池材料能支撑",
    "现有材料可支撑其",
    "现有材料可支撑其经营覆盖",
    "现有材料可支撑其经营涉及",
    "以品牌消费品经营为核心",
    "以制造、供应链和多业务单元协同为核心",
    "以品牌、渠道、商品和供应链协同经营为核心",
    "以跨境多平台、多国家和多履约链路协同为核心",
    "集团型制造，依赖多基地",
    "跨境零售与供应链协同并行",
)
GENERIC_CUSTOMER_PREFIXES = (
    "当前关于",
    "当前可先确认其",
    "工业企业、行业客户及项目型客户。",
    "终端消费者、经销/零售渠道及线上线下平台。",
    "医院、医疗机构、科研机构及专业客户。",
    "工程施工、基础设施建设及工业客户。",
    "下游品牌客户、工业客户与渠道/项目型客户",
    "家庭消费客群、母婴宠物用户、直营网点、电商与渠道伙伴。",
    "终端消费者、经销渠道",
    "行业客户",
    "海外终端消费者",
    "大众消费",
)
GENERIC_SYSTEM_PREFIXES = (
    "当前可确认其",
    "已具备",
    "具备",
    "已形成",
    "上市公司公开披露可支撑其已具备",
)
GENERIC_DIGITAL_PREFIXES = (
    "当前尚未获得稳定公开材料直接支撑",
    "公开披露可支撑其具备",
    "围绕",
    "经营驾驶舱",
    "利润改善",
    "总部经营穿透",
    "多平台精细化运营",
)
GENERIC_MARKET_PREFIXES = (
    "相邻",
    "可先参考",
    "品牌出海与多平台跨境企业。",
    "多基地、多工厂、多事业部协同制造企业。",
    "高端装备、医疗器械、汽车电子等技术型制造企业。",
    "高 SKU 品牌消费品",
    "母婴、宠物、家居与耐用品品牌企业。",
    "标准化连锁餐饮、茶饮咖啡和餐饮零售企业。",
    "安克创新",
    "三一重工",
    "联影医疗",
    "农夫山泉",
    "孩子王",
    "babycare",
)
GENERIC_HIRING_PREFIXES = (
    "跨境运营、财务分析、供应链计划、BI/数据岗位。",
    "平台运营、广告投放、财务分析、供应链数据岗位。",
    "计划协同、供应链、制造运营、财务分析、BI/数据岗位。",
    "研发管理、营销运营、计划协同、财务分析、BI/数据岗位。",
    "商品企划、会员运营、渠道分析、分货补货、BI/数据岗位。",
    "供应链计划、品类运营、渠道分析、BI/数据岗位。",
    "商品企划、门店运营、会员运营、财务分析、BI/数据岗位。",
    "门店运营、商品企划、区域管理、会员运营、BI/数据岗位。",
    "商品企划、渠道分析、供应链计划、财务分析、BI/数据岗位。",
    "门店运营、督导、会员运营、供应链与 BI/数据岗位。",
)
GENERIC_PRODUCT_CONTAINS = (
    "属于高 SKU",
    "属于多工厂",
    "属于多门店",
    "属于制造主体",
    "属于品牌消费品主体",
    "属于跨境品牌或供应链出海主体",
    "经营复杂度",
)
GENERIC_BUSINESS_CONTAINS = (
    "具备较强",
    "存在较强",
    "经营复杂度",
    "协同复杂度",
)
GENERIC_CUSTOMER_CONTAINS = (
    "终端消费者",
    "品牌经营团队",
    "渠道伙伴",
    "项目交付团队",
    "集团经营管理层",
    "大众消费",
)
GENERIC_MARKET_EXACTS = {
    "平台型跨境、电商代运营和供应链复杂出海企业。",
    "专业连锁、百货、超市与多业态零售企业。",
    "同类多工厂离散制造集团与装备制造企业。",
    "技术型制造与高端装备企业。",
    "集团型制造和多基地制造企业。",
    "同类连锁零售和品牌零售企业。",
    "品牌消费品与高SKU零售企业。",
    "跨境供应链复杂型经营主体。",
}


def safe_load_workbook(path: Path, **kwargs):
    last_error = None
    for attempt in range(6):
        try:
            return load_workbook(path, **kwargs)
        except (EOFError, BadZipFile) as exc:
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise last_error
GENERIC_SIMILAR_EXACTS = {
    "地素、Fila、赢家时尚等相邻样本。",
    "吉宏科技、华凯易佰、傲基创新等相邻样本。",
    "花西子、自然堂、丝芙兰、蜜思肤等相邻样本。",
    "汇川技术、迈瑞医疗、中控技术。",
    "立讯精密、宁德时代、三一重工。",
    "名创优品、孩子王、家家悦。",
    "良品铺子、水羊、三只松鼠。",
    "致欧家居、华凯易佰、赛维时代。",
}


def system_fact_text(track: str, persona: str) -> str:
    if track == "跨境电商":
        return "当前可确认其跨境经营链路覆盖订单、供应链、财务等关键环节；具体 ERP、投放、履约或利润分析系统名称仍待官网、年报或 IR 口径补齐。"
    if track == "零售消费":
        if persona in {"retail_multi_store", "retail_multi_store_chain", "retail_chain_fnb", "fnb_chain_standardized", "fnb_chain_beverage_coffee"}:
            return "当前可确认其经营覆盖门店、商品、会员、供应链和财务等关键环节；具体 ERP、会员、补货、渠道或经营分析系统名称仍待官网、年报或 IR 口径补齐。"
        return "当前可确认其经营覆盖商品、渠道、供应链和财务等关键环节；具体 ERP、会员、渠道、财务或经营分析系统名称仍待官网、年报或 IR 口径补齐。"
    return "当前可确认其经营链路覆盖研发、制造、供应链和财务等关键环节；具体 ERP、MES、计划、供应链或财务系统名称仍待官网、年报或 IR 口径补齐。"


def digital_fact_text(track: str, persona: str) -> str:
    if track == "跨境电商":
        return "当前尚未获得稳定公开材料直接支撑具体数字化项目名称；现阶段仅能确认其在多平台经营、履约协同和利润分析等方面复杂度较高。"
    if track == "零售消费":
        if persona in {"retail_multi_store", "retail_multi_store_chain"}:
            return "当前尚未获得稳定公开材料直接支撑具体数字化项目名称；现阶段仅能确认其在门店经营、会员分析、补货分货和区域复盘等方面复杂度较高。"
        if persona in {"retail_chain_fnb", "fnb_chain_standardized", "fnb_chain_beverage_coffee"}:
            return "当前尚未获得稳定公开材料直接支撑具体数字化项目名称；现阶段仅能确认其在门店经营、督导动作、会员运营和供应链协同等方面复杂度较高。"
        return "当前尚未获得稳定公开材料直接支撑具体数字化项目名称；现阶段仅能确认其在商品、渠道、库存和利润治理等方面复杂度较高。"
    if persona == "mfg_rnd_sales_complex":
        return "当前尚未获得稳定公开材料直接支撑具体数字化项目名称；现阶段仅能确认其在研产销协同、项目交付和经营分析等方面复杂度较高。"
    return "当前尚未获得稳定公开材料直接支撑具体数字化项目名称；现阶段仅能确认其在多基地协同、计划供应链和经营分析等方面复杂度较高。"


SYSTEM_EXACTS = {
    "上市公司公开披露可支撑其已具备与经营复杂度匹配的经营管理、供应链、财务或经营分析基础系统环境。",
    "已具备供应链、订单、财务、渠道或经营分析基础系统。",
    "已具备供应链、渠道、财务或经营分析基础系统环境。",
    "已具备商品、会员、渠道、财务或零售经营分析基础系统。",
    "已具备与经营复杂度相匹配的经营管理、供应链或财务基础系统。",
    "已具备门店、会员、ERP、供应链或经营分析基础系统。",
    "具备制造经营与财务管理基础系统。",
    "已形成研发、制造、供应链与经营管理基础系统。",
    "已具备生产、供应链、财务、研发或经营分析基础系统。",
    "已具备生产、计划、供应链、财务或经营分析基础系统。",
    "具备跨境经营和供应链基础系统。",
    "具备跨境经营、财务和供应链基础系统。",
    "已具备门店经营、商品管理、会员、供应链或财务等基础系统。",
    "已具备 ERP、会员、渠道、零售或经营分析类基础系统环境。",
    "具备制造、供应链与经营管理基础系统。",
    "已具备跨境运营、广告投放、供应链或财务等基础系统。",
    "具备基础零售经营和数据分析系统。",
    "具备消费品经营与供应链管理基础系统。",
    "具备制造经营与集团管理基础系统。",
}

DIGITAL_EXACTS = {
    "公开披露可支撑其具备产销协同、供应链协同、财务管控和经营分析相关系统环境。",
    "围绕库存协同、经营驾驶舱和利润治理存在静态数字化需求。",
    "公开披露可支撑其具备经营分析、供应链协同和利润改善相关治理场景。",
    "围绕商品、渠道、库存和利润治理存在静态数字化需求。",
    "围绕上新、库存、利润和渠道经营穿透存在静态数字化需求。",
    "围绕门店经营驾驶舱、补货分货和一线动作闭环存在静态数字化需求。",
    "经营驾驶舱、LTC协同和利润改善价值较高。",
    "经营分析、商品结构优化与利润改善相关需求明显。",
    "经营驾驶舱、产销协同与价值流透明化需求明显。",
    "多基地经营穿透、价值流分析与集团协同需求明显。",
    "集团经营穿透、计划协同与价值流透明化需求明显。",
    "公开披露可支撑其具备平台经营分析、供应链履约协同和利润改善相关治理场景。",
    "供应链协同、库存优化与利润改善是典型切入点。",
    "利润改善、全球经营分析和品牌出海协同价值高。",
    "总部经营穿透、门店动作闭环和区域经营分析需求明显。",
    "围绕总部经营穿透、商品渠道协同和分货补货优化存在静态数字化需求。",
    "集团经营驾驶舱、多工厂协同和价值流透明化价值高。",
    "多平台精细化运营、T+1利润分析和经营驾驶舱需求明显。",
    "利润改善、库存优化和供需协同是典型切入点。",
    "总部经营穿透、区域复盘和门店动作闭环价值较高。",
}

PRODUCT_EXACTS = {
    "研发、制造、销售协同复杂的技术型制造业务。",
    "主营品牌消费品、个护、家居、食品或耐用品等多 SKU 产品，具备较强商品与渠道复杂度。",
    "主营技术型设备、材料、工业产品或高复杂制造业务，具备研产销协同复杂度。",
    "主营多工厂、多基地制造业务，具备集团化制造协同复杂度。",
    "多工厂、多事业部的集团型制造业务。",
    "跨境供应链复杂、依赖海外仓或多履约链路的出海经营。",
    "主营半导体相关产品或设备，属于研产销协同复杂的技术型制造主体。",
    "品牌出海与多平台经营，产品矩阵和区域经营复杂。",
    "主营零售渠道、百货、连锁卖场或区域零售网络业务，具备多门店经营复杂度。",
    "主营工业金属相关产品或制造业务，属于多工厂、多业务单元协同的制造主体。",
    "主营一般零售相关业务，属于多门店、多区域经营的零售主体。",
    "主营家居用品相关产品或品牌业务，属于高 SKU、多渠道经营的品牌消费品主体。",
    "主营跨境品牌消费品业务，具备多平台、多国家、多产品线经营复杂度。",
    "以线下连锁零售或品牌直营网点经营为核心，依赖门店网络和区域协同。",
    "主营食品加工相关产品或品牌业务，属于高 SKU、多渠道经营的品牌消费品主体。",
    "品牌消费品经营，SKU较多，渠道与供应链协同复杂。",
    "主营家居用品相关业务，属于多平台经营的跨境品牌或供应链出海主体。",
    "主营休闲食品相关产品或品牌业务，属于高 SKU、多渠道经营的品牌消费品主体。",
    "主营调味发酵品Ⅱ相关产品或品牌业务，属于高 SKU、多渠道经营的品牌消费品主体。",
    "主营互联网电商相关业务，属于多平台经营的跨境品牌或供应链出海主体。",
}

BUSINESS_EXACTS = {
    "以品牌经营和渠道销售为核心，通过线上线下渠道覆盖目标市场。",
    "以品牌经营为核心，通过经销、零售终端及线上线下渠道覆盖市场。",
    "以品牌消费品经营为核心，覆盖线上线下渠道、供应链协同和品牌运营。",
    "以制造、供应链和多业务单元协同为核心，具备较强的集团经营与计划协同复杂度。",
    "以品牌、渠道、商品和供应链协同经营为核心，存在较强商品结构与动销复杂度。",
    "以多品牌或多渠道鞋服时尚经营为核心，涉及会员、门店、电商与供应链协同。",
    "以品牌消费品销售和多渠道经营为核心，具备商品、渠道、供应链与利润协同复杂度。",
    "以总部-区域-门店多层级经营管理为核心，依赖门店经营分析与补货协同。",
    "技术驱动型制造，依赖研产销和区域协同。",
    "以研发、生产、销售和交付协同为核心，具备较强的技术型制造经营复杂度。",
    "以品牌零售和多渠道销售为核心，兼具经销、电商、直营网点或零售终端协同特征。",
    "以研发、生产、销售协同的技术型制造经营为核心，存在项目型交付、复杂产品线或行业客户特征。",
    "集团型制造，依赖多基地研发、生产与经营协同。",
    "以集团化、多基地制造经营为核心，存在工厂、事业部、区域和供应链协同特征。",
    "以跨境多平台、多国家和多履约链路协同为核心，具备投放、供应链、仓配与利润协同复杂度。",
    "跨境零售与供应链协同并行，依赖平台、仓配和履约体系。",
    "以直营网点、连锁渠道或区域网络经营为核心，具备总部到终端的经营协同复杂度。",
    "品牌出海与平台运营并行，依赖全球市场和站点协同。",
    "以直营网点、加盟网络或区域门店运营为核心，存在总部到区域到门店的经营协同链条。",
    "以品牌消费品经营为核心，覆盖产品、渠道、动销、会员或分货协同。",
    "集团型制造，依赖多基地协同和总部经营管理。",
    "以品牌出海和多平台运营为核心，存在海外渠道、平台运营与供应链协同特征。",
}

CUSTOMER_EXACTS = {
    "下游品牌客户、工业客户与渠道/项目型客户",
    "家庭消费客群、母婴宠物用户、直营网点、电商与渠道伙伴。",
    "终端消费者、经销渠道、零售终端和品牌经营团队。",
    "终端消费者、门店、电商渠道和品牌经营团队。",
    "终端消费者、经销渠道与直营网点体系",
    "终端消费者、区域公司、门店团队与总部经营管理层。",
    "行业客户与专业市场客户。",
    "终端消费者、经销渠道、电商平台与零售终端体系",
    "行业客户、渠道伙伴、项目交付团队与内部经营管理层",
    "行业客户、区域市场、工厂/事业部与集团经营管理层",
    "海外终端消费者、平台渠道与跨境履约链路",
    "行业客户与制造类B端客户。",
    "海外家庭消费或专业消费客群。",
    "终端消费者、门店网络与区域经营单元",
    "海外消费客群与平台用户。",
    "到店消费者、区域门店、加盟商及总部经营团队",
    "终端消费者、经销/渠道伙伴、直营网点与品牌经营团队。",
    "海外消费者、电商平台、分销渠道与内部运营团队",
    "大众消费或细分零售消费客群。",
    "大众消费品或细分品牌消费客群。",
}


def normalize_excerpt(account_name: str, track: str, persona: str) -> str:
    if track == "跨境电商":
        return f"现阶段可确认 {account_name} 的经营链路覆盖订单、供应链、财务等关键环节；具体 ERP、投放、履约或利润分析系统名称仍待官网、年报或 IR 口径补齐。"
    if track == "零售消费":
        if persona in {"retail_multi_store", "retail_multi_store_chain", "retail_chain_fnb", "fnb_chain_standardized", "fnb_chain_beverage_coffee"}:
            return f"现阶段可确认 {account_name} 的经营覆盖门店、商品、会员、供应链和财务等关键环节；具体 ERP、会员、补货、渠道或经营分析系统名称仍待官网、年报或 IR 口径补齐。"
        return f"现阶段可确认 {account_name} 的经营覆盖商品、渠道、供应链和财务等关键环节；具体 ERP、会员、渠道、财务或经营分析系统名称仍待官网、年报或 IR 口径补齐。"
    return f"现阶段可确认 {account_name} 的经营链路覆盖研发、制造、供应链和财务等关键环节；具体 ERP、MES、计划、供应链或财务系统名称仍待官网、年报或 IR 口径补齐。"


def normalize_product_excerpt(account_name: str, current: str) -> str:
    if "被识别为" in current and "方向的代表性公司" in current:
        direction = current.split("被识别为", 1)[1].split("方向的代表性公司", 1)[0].strip()
        return f"现有强核验材料和历史记录可支撑 {account_name} 属于{direction}方向的经营主体；更细的产品线、业务结构和公司官方表述仍待官网、年报或 IR 材料继续补充。"
    return current


def normalize_business_excerpt(account_name: str, persona: str, current: str) -> str:
    if "当前已知信息显示" in current and "相邻度较高" in current:
        label = PERSONA_LABELS.get(persona, "当前画像")
        return f"现有强核验材料和历史记录可支撑 {account_name} 的经营结构与“{label}”相邻；更细的业务分部、客户结构和收入构成仍待官网、年报或 IR 材料补充。"
    return current


def normalize_customer_excerpt(current: str) -> str:
    if "已经能够被阶段性描述" in current:
        return "现有材料只能支撑其客户链路和典型使用场景的粗粒度判断；区域、产品线或业务分部颗粒度仍待官网、年报或 IR 材料继续补充。"
    return current


def normalize_event_excerpt(current: str) -> str:
    if "可以作为静态背景补充" in current:
        return "现有公开资料仅能支撑其仍处于持续经营、组织推进或市场拓展阶段的粗粒度判断；具体年度事件仍待更强官方披露补充。"
    return current


def normalize_revenue_text(current: str) -> str:
    current = str(current or "").strip()
    if not current:
        return "待补公开财报口径"
    if current in {"待补公开财报口径", "待补充"}:
        return "待补公开财报口径"
    guessed_tokens = [
        "区间",
        "营收体量",
        "营收。",
        "亿元",
        "百亿级",
        "千亿级",
        "数十亿级",
    ]
    if any(token in current for token in guessed_tokens):
        return "待补公开财报口径"
    return current


def normalize_profit_text(current: str) -> str:
    current = str(current or "").strip()
    if not current:
        return "待补公开财报口径"
    if current in {"待补公开财报口径", "待补充"}:
        return "待补公开财报口径"
    generic_prefixes = [
        "利润受",
        "项目型装备业务利润受",
        "跨境投放效率",
        "利润表现受",
        "利润与门店扩张",
        "连锁零售经营下利润受",
    ]
    if any(current.startswith(prefix) for prefix in generic_prefixes) or "利润管理依赖" in current or "利润和库存压力" in current:
        return "待补公开财报口径"
    return current


def normalize_growth_text(current: str) -> str:
    current = str(current or "").strip()
    if not current:
        return "待补公开财报口径"
    if current in {"待补公开财报口径", "待补充"}:
        return "待补公开财报口径"
    generic_prefixes = [
        "受",
        "增长与",
        "与",
        "依赖",
        "多业务线扩张",
        "增长依赖",
        "近年保持",
        "增长受",
        "门店经营优化",
        "多品类",
    ]
    if any(current.startswith(prefix) for prefix in generic_prefixes) or "驱动增长" in current:
        return "待补公开财报口径"
    return current


def normalize_event_text(current: str) -> str:
    current = str(current or "").strip()
    if not current:
        return "待补更强官方披露"
    if current in {"待补充", "待补更强官方披露"}:
        return "待补更强官方披露"
    generic_event_tokens = [
        "持续围绕",
        "复杂度持续存在",
        "复杂度持续增强",
        "利润和库存压力通常持续存在",
        "协同持续增强",
        "经营持续深化",
        "全球品牌经营持续扩张",
        "围绕核心业务扩展",
        "围绕工程机械产品升级",
        "围绕电子制造",
        "围绕新能源场景",
        "多基地、多业务协同持续复杂",
        "围绕机器人业务拓展",
        "持续推进机器人与自动化业务拓展",
        "围绕新能源装备交付",
        "围绕大客户项目交付",
        "继续围绕",
        "经营协同复杂度",
    ]
    if any(token in current for token in generic_event_tokens):
        return "待补更强官方披露"
    return current


def is_placeholder(value: str) -> bool:
    value = str(value or "").strip()
    return not value or value in {
        FACT_PLACEHOLDER,
        EVENT_PLACEHOLDER,
        MARKET_PLACEHOLDER,
        ASSET_PLACEHOLDER,
        "待补公开财报口径",
        "待补字段级 evidence",
        "待补充",
    }


def starts_with_any(value: str, prefixes: tuple[str, ...]) -> bool:
    return any(value.startswith(prefix) for prefix in prefixes)


def is_generic_product_text(value: str) -> bool:
    value = str(value or "").strip()
    return (
        value in PRODUCT_EXACTS
        or starts_with_any(value, GENERIC_PRODUCT_PREFIXES)
        or (value.startswith("主营") and any(token in value for token in GENERIC_PRODUCT_CONTAINS))
    )


def is_generic_business_text(value: str) -> bool:
    value = str(value or "").strip()
    return (
        value in BUSINESS_EXACTS
        or starts_with_any(value, GENERIC_BUSINESS_PREFIXES)
        or (value.startswith(("以", "集团型", "技术驱动型", "品牌出海")) and any(token in value for token in GENERIC_BUSINESS_CONTAINS))
    )


def is_generic_customer_text(value: str) -> bool:
    value = str(value or "").strip()
    return (
        value in CUSTOMER_EXACTS
        or starts_with_any(value, GENERIC_CUSTOMER_PREFIXES)
        or any(token in value for token in GENERIC_CUSTOMER_CONTAINS)
    )


def is_generic_system_text(value: str) -> bool:
    value = str(value or "").strip()
    return value in SYSTEM_EXACTS or starts_with_any(value, GENERIC_SYSTEM_PREFIXES)


def is_generic_digital_text(value: str) -> bool:
    value = str(value or "").strip()
    return value in DIGITAL_EXACTS or starts_with_any(value, GENERIC_DIGITAL_PREFIXES)


def is_generic_market_text(value: str) -> bool:
    value = str(value or "").strip()
    return (
        value in GENERIC_MARKET_EXACTS
        or value in GENERIC_SIMILAR_EXACTS
        or starts_with_any(value, GENERIC_MARKET_PREFIXES)
    )


def is_generic_hiring_text(value: str) -> bool:
    value = str(value or "").strip()
    return value in GENERIC_HIRING_PREFIXES or "BI/数据岗位" in value or "财务分析" in value


def is_source_excerpt(value: str) -> bool:
    value = str(value or "").strip()
    if is_placeholder(value):
        return False
    generic_tokens = [
        "现有强核验材料和历史记录可支撑",
        "现有材料只能稳定支撑",
        "现有候选池材料能支撑",
        "当前关于",
        "当前不应再用模板化",
        "当前已知信息显示",
        "已经能够被阶段性描述",
        "可以作为静态背景补充",
        "适合作为画像候选",
        "可支撑静态样本判断",
        "不足以",
        "仍待一手材料",
        "更诚实的做法",
    ]
    return not any(token in value for token in generic_tokens)


def information_density(
    official_count: int,
    high_count: int,
    company_fact_count: int,
    core_fact_count: int,
    operational_fact_count: int,
    excerpt_count: int,
    market_specific: bool,
    asset_specific: bool,
) -> str:
    if (
        official_count >= 1
        and high_count >= 2
        and core_fact_count >= 3
        and operational_fact_count >= 1
        and company_fact_count >= 4
        and excerpt_count >= 2
        and (market_specific or asset_specific)
    ):
        return "高"
    if official_count >= 1 and core_fact_count >= 2 and company_fact_count >= 3 and excerpt_count >= 1:
        return "中高"
    if official_count >= 1 and core_fact_count >= 1:
        return "中"
    return "中低"


def infer_official_count(source_types: str, refs: str, current: str) -> int:
    current_num = int(str(current or 0) or 0)
    source_types = str(source_types or "")
    refs_list = [x.strip() for x in str(refs or "").split("\n") if x.strip()]
    official_tokens = {
        "official_website",
        "annual_report",
        "investor_relations",
        "official_annual_report",
        "official_prospectus",
        "上市公司基础资料",
        "上市公司公开披露",
    }
    inferred = 0
    for token in source_types.split(","):
        if token.strip() in official_tokens:
            inferred = 1
            break
    if not inferred:
        for ref in refs_list:
            lower = ref.lower()
            if ref.startswith("http") or any(key in lower for key in ["cninfo", "eastmoney", "annual", "report", "investor", "prospectus"]):
                inferred = 1
                break
    return max(current_num, inferred)


def infer_high_confidence_count(source_types: str, refs: str, current: str) -> int:
    current_num = int(str(current or 0) or 0)
    source_types = str(source_types or "")
    refs_list = [x.strip() for x in str(refs or "").split("\n") if x.strip()]
    inferred = 0
    high_tokens = {"archive", "manual_note", "high_confidence_public", "promotion_assessment"}
    for token in source_types.split(","):
        if token.strip() in high_tokens:
            inferred += 1
    if refs_list and inferred == 0:
        inferred = 1
    if refs_list and inferred == 1 and len(refs_list) > 1:
        inferred = 2
    return max(current_num, inferred)


def source_gap_text(official_count: int, high_count: int) -> str:
    gaps = []
    if official_count < 1:
        gaps.append("官网或上市主体公开披露")
    if high_count < 2:
        gaps.append("更高可信材料或字段级 evidence")
    gaps.extend(["收入规模", "利润状态", "营收增长"])
    return "、".join(gaps) + "仍需回到更强来源继续补齐。"


def next_action_text(level: str, official_count: int, high_count: int) -> str:
    if official_count < 1:
        return "优先补官网、上市主体公开披露或 IR 入口，再继续补财报口径与字段级 evidence。"
    if high_count < 2:
        return "继续补高可信材料、年报/IR 与字段级 evidence，避免只停留在单一官方入口。"
    if level == "L3":
        return "继续补官网、年报、投资者关系材料和字段级 evidence，必要时再评估是否上移。"
    return "继续补更强官方披露和财报口径，按高质量样本标准持续压实。"


def normalize_product_text(track: str, persona: str, current: str) -> str:
    if current not in PRODUCT_EXACTS:
        return current
    if track == "跨境电商":
        return "现有材料可支撑其属于跨境出海经营主体；更细的主营品类、自有品牌、站点结构和履约模式仍待官网、年报或 IR 材料补充。"
    if track == "零售消费":
        return "现有材料可支撑其属于品牌消费品或零售经营主体；更细的产品矩阵、渠道结构和公司官方表述仍待官网、年报或 IR 材料补充。"
    return "现有材料可支撑其属于制造经营主体；更细的产品线、基地布局和业务分部结构仍待官网、年报或 IR 材料补充。"


def normalize_business_text(track: str, persona: str, current: str) -> str:
    if current not in BUSINESS_EXACTS:
        return current
    if track == "跨境电商":
        return "现有材料可支撑其经营涉及跨境平台、供应链、仓配、履约或利润治理等关键环节；更细的平台结构、站点协同和收入构成仍待官网、年报或 IR 材料补充。"
    if track == "零售消费":
        return "现有材料可支撑其经营覆盖品牌、渠道、商品、门店、会员或供应链等关键环节；更细的渠道模式、直营网/加盟结构和收入构成仍待官网、年报或 IR 材料补充。"
    return "现有材料可支撑其经营覆盖研发、制造、供应链、交付和财务等关键环节；更细的基地协同、事业部结构和收入构成仍待官网、年报或 IR 材料补充。"


def normalize_customer_text(track: str, current: str) -> str:
    if current not in CUSTOMER_EXACTS:
        return current
    if track == "跨境电商":
        return "当前可先确认其客户链路覆盖海外终端消费者、平台渠道或跨境履约相关环节；更细的国家、站点和客群结构仍待官网、年报或 IR 材料补充。"
    if track == "零售消费":
        return "当前可先确认其客户链路覆盖终端消费者、经销/渠道伙伴、门店网络或品牌经营相关团队；更细的渠道层级和客群结构仍待官网、年报或 IR 材料补充。"
    return "当前可先确认其主要面向工业/制造类 B 端客户、渠道伙伴或项目交付场景；更细的行业分布和客户结构仍待官网、年报或 IR 材料补充。"


def process_profile_sheet(ws) -> dict[str, tuple[str, str, str, str, int, int, str, str]]:
    headers = [c.value for c in ws[1]]
    idx = {h: i + 1 for i, h in enumerate(headers)}
    replacements = {}
    updated = 0
    excerpt_updated = 0
    for row in range(2, ws.max_row + 1):
        level = ws.cell(row, idx["静态潜客记录成熟度"]).value
        if level not in TARGET_LEVELS:
            continue
        acc = str(ws.cell(row, idx["account_id"]).value)
        name = str(ws.cell(row, idx["account_canonical_name"]).value)
        track = str(ws.cell(row, idx["primary_track"]).value)
        persona = str(ws.cell(row, idx["persona_tag"]).value)
        source_types_col = idx.get("primary_source_types")
        source_refs_col = idx.get("primary_source_refs")
        fallback_source_note_col = idx.get("source_note")
        current_source_types = str(ws.cell(row, source_types_col).value or "").strip() if source_types_col else ""
        current_refs = str(ws.cell(row, source_refs_col).value or "").strip() if source_refs_col else ""
        if not current_source_types and fallback_source_note_col:
            source_note = str(ws.cell(row, fallback_source_note_col).value or "").strip()
            if "官网" in source_note or "官方" in source_note or "公开披露" in source_note or "东财" in source_note:
                current_source_types = "上市公司公开披露"
            elif source_note:
                current_source_types = "archive,manual_note"

        current_system = str(ws.cell(row, idx["已上线系统概况"]).value or "").strip()
        current_digital = str(ws.cell(row, idx["数字化项目动态"]).value or "").strip()
        excerpt_col = idx.get("系统与数字化长摘录")
        current_excerpt = str(ws.cell(row, excerpt_col).value or "").strip() if excerpt_col else ""

        if is_generic_system_text(current_system):
            ws.cell(row, idx["已上线系统概况"]).value = FACT_PLACEHOLDER
            updated += 1
        if is_generic_digital_text(current_digital):
            ws.cell(row, idx["数字化项目动态"]).value = FACT_PLACEHOLDER
            updated += 1
        for field_name, checker in [
            ("公司产品与服务概述", is_generic_product_text),
            ("商业模式概述", is_generic_business_text),
            ("核心客户客群", is_generic_customer_text),
        ]:
            col = idx.get(field_name)
            if not col:
                continue
            current = str(ws.cell(row, col).value or "").strip()
            if checker(current):
                ws.cell(row, col).value = FACT_PLACEHOLDER
                updated += 1
        for field_name, normalizer in [
            ("收入规模区间", normalize_revenue_text),
            ("利润状态概述", normalize_profit_text),
            ("营收增长概述", normalize_growth_text),
            ("近一年重大事件", normalize_event_text),
        ]:
            col = idx.get(field_name)
            if not col:
                continue
            current = str(ws.cell(row, col).value or "").strip()
            normalized = normalizer(current)
            if normalized != current:
                ws.cell(row, col).value = normalized
                updated += 1
        for field_name, checker, replacement in [
            ("主要竞品概述", is_generic_market_text, MARKET_PLACEHOLDER),
            ("相似客户线索", is_generic_market_text, MARKET_PLACEHOLDER),
            ("招聘代表岗位", is_generic_hiring_text, FACT_PLACEHOLDER),
        ]:
            col = idx.get(field_name)
            if not col:
                continue
            current = str(ws.cell(row, col).value or "").strip()
            if checker(current):
                ws.cell(row, col).value = replacement
                updated += 1
        official_col = idx.get("official_source_count")
        high_col = idx.get("high_confidence_source_count")
        official_count = infer_official_count(current_source_types, current_refs, ws.cell(row, official_col).value if official_col else 0)
        high_count = infer_high_confidence_count(current_source_types, current_refs, ws.cell(row, high_col).value if high_col else 0)
        if official_col and ws.cell(row, official_col).value != official_count:
            ws.cell(row, official_col).value = official_count
            updated += 1
        if high_col and ws.cell(row, high_col).value != high_count:
            ws.cell(row, high_col).value = high_count
            updated += 1
        validation_col = idx.get("validation_gap")
        if validation_col:
            gap = source_gap_text(official_count, high_count)
            if str(ws.cell(row, validation_col).value or "").strip() != gap:
                ws.cell(row, validation_col).value = gap
                updated += 1
        if excerpt_col and (current_excerpt.startswith("现阶段可确认 ") or "经营复杂度相匹配" in current_excerpt):
            ws.cell(row, excerpt_col).value = FACT_PLACEHOLDER
            excerpt_updated += 1
        for field_name, checker, replacement in [
            ("产品与服务长摘录", lambda text: not is_source_excerpt(text), FACT_PLACEHOLDER),
            ("商业模式长摘录", lambda text: not is_source_excerpt(text), FACT_PLACEHOLDER),
            ("客户客群长摘录", lambda text: not is_source_excerpt(text), FACT_PLACEHOLDER),
            ("系统与数字化长摘录", lambda text: not is_source_excerpt(text), FACT_PLACEHOLDER),
            ("重大事件长摘录", lambda text: not is_source_excerpt(text), FACT_PLACEHOLDER),
        ]:
            col = idx.get(field_name)
            if not col:
                continue
            current = str(ws.cell(row, col).value or "").strip()
            if checker(current):
                ws.cell(row, col).value = replacement
                excerpt_updated += 1

        company_fact_fields = [
            "公司产品与服务概述",
            "商业模式概述",
            "核心客户客群",
            "已上线系统概况",
            "数字化项目动态",
            "招聘代表岗位",
            "近一年重大事件",
        ]
        company_fact_count = sum(
            1
            for field in company_fact_fields
            if idx.get(field) and not is_placeholder(str(ws.cell(row, idx[field]).value or "").strip())
        )
        excerpt_fields = ["产品与服务长摘录", "商业模式长摘录", "客户客群长摘录", "系统与数字化长摘录", "重大事件长摘录"]
        core_fact_fields = ["公司产品与服务概述", "商业模式概述", "核心客户客群"]
        operational_fields = ["已上线系统概况", "数字化项目动态", "招聘代表岗位", "近一年重大事件"]
        core_fact_count = sum(
            1
            for field in core_fact_fields
            if idx.get(field) and not is_placeholder(str(ws.cell(row, idx[field]).value or "").strip())
        )
        operational_fact_count = sum(
            1
            for field in operational_fields
            if idx.get(field) and not is_placeholder(str(ws.cell(row, idx[field]).value or "").strip())
        )
        excerpt_count = sum(
            1
            for field in excerpt_fields
            if idx.get(field) and is_source_excerpt(str(ws.cell(row, idx[field]).value or "").strip())
        )
        market_specific = any(
            idx.get(field) and not is_placeholder(str(ws.cell(row, idx[field]).value or "").strip())
            for field in ["主要竞品概述", "相似客户线索"]
        )
        asset_specific = bool(str(ws.cell(row, idx["focus_note_path"]).value or "").strip()) if idx.get("focus_note_path") else False
        sturdiness = information_density(
            official_count,
            high_count,
            company_fact_count,
            core_fact_count,
            operational_fact_count,
            excerpt_count,
            market_specific,
            asset_specific,
        )
        if str(ws.cell(row, idx["信息扎实度"]).value or "").strip() != sturdiness:
            ws.cell(row, idx["信息扎实度"]).value = sturdiness
            updated += 1

        replacements[acc] = (
            str(ws.cell(row, idx["已上线系统概况"]).value or ""),
            str(ws.cell(row, idx["数字化项目动态"]).value or ""),
            str(ws.cell(row, excerpt_col).value or "") if excerpt_col else "",
            str(ws.cell(row, idx.get("近一年重大事件")).value or "") if idx.get("近一年重大事件") else "",
            official_count,
            high_count,
            gap,
            next_action_text(level, official_count, high_count),
            sturdiness,
        )
    return {"replacements": replacements, "updated": updated, "excerpt_updated": excerpt_updated}


def process_observations(ws, replacements: dict[str, tuple[str, str, str, str, int, int, str, str, str]], personas: dict[str, str], names: dict[str, str]) -> int:
    headers = [c.value for c in ws[1]]
    idx = {h: i + 1 for i, h in enumerate(headers)}
    updated = 0
    for row in range(2, ws.max_row + 1):
        acc = str(ws.cell(row, idx["account_id"]).value or "")
        if acc not in replacements:
            continue
        field = str(ws.cell(row, idx["field_name"]).value or "")
        if ws.cell(row, idx["is_current_best"]).value != "yes":
            continue
        system_text, digital_text, excerpt_text, event_text, official_count, high_count, gap_text, next_text, sturdiness = replacements[acc]
        if field == "已上线系统概况":
            ws.cell(row, idx["field_value_short"]).value = system_text
            ws.cell(row, idx["field_excerpt_long"]).value = excerpt_text
            updated += 1
        elif field == "数字化项目动态":
            ws.cell(row, idx["field_value_short"]).value = digital_text
            ws.cell(row, idx["field_excerpt_long"]).value = excerpt_text
            updated += 1
        elif field == "公司产品与服务概述":
            current = str(ws.cell(row, idx["field_excerpt_long"]).value or "")
            if not is_source_excerpt(current):
                ws.cell(row, idx["field_excerpt_long"]).value = FACT_PLACEHOLDER
                updated += 1
        elif field == "商业模式概述":
            current = str(ws.cell(row, idx["field_excerpt_long"]).value or "")
            if not is_source_excerpt(current):
                ws.cell(row, idx["field_excerpt_long"]).value = FACT_PLACEHOLDER
                updated += 1
        elif field == "核心客户客群":
            current = str(ws.cell(row, idx["field_excerpt_long"]).value or "")
            if not is_source_excerpt(current):
                ws.cell(row, idx["field_excerpt_long"]).value = FACT_PLACEHOLDER
                updated += 1
        elif field == "近一年重大事件":
            current_short = str(ws.cell(row, idx["field_value_short"]).value or "")
            current = str(ws.cell(row, idx["field_excerpt_long"]).value or "")
            changed = False
            if event_text and current_short != event_text:
                ws.cell(row, idx["field_value_short"]).value = event_text
                changed = True
            if not is_source_excerpt(current):
                ws.cell(row, idx["field_excerpt_long"]).value = EVENT_PLACEHOLDER
                changed = True
            if changed:
                updated += 1
    return updated


def update_coverage(ws, replacements: dict[str, tuple[str, str, str, str, int, int, str, str, str]]) -> int:
    headers = [c.value for c in ws[1]]
    idx = {h: i + 1 for i, h in enumerate(headers)}
    updated = 0
    for row in range(2, ws.max_row + 1):
        acc = str(ws.cell(row, idx["account_id"]).value or "")
        if acc not in replacements:
            continue
        _, _, _, _, official_count, high_count, gap_text, next_text, _ = replacements[acc]
        pairs = [
            ("official_source_ready", "yes" if official_count >= 1 else "no"),
            ("high_confidence_ready", "yes" if high_count >= 2 else "no"),
            ("missing_core_fields", gap_text),
            ("next_action", next_text),
        ]
        for field, value in pairs:
            col = idx.get(field)
            if not col:
                continue
            if str(ws.cell(row, col).value or "").strip() != str(value):
                ws.cell(row, col).value = value
                updated += 1
    return updated


def main() -> None:
    profile_wb = safe_load_workbook(PROFILE_XLSX)
    profile_ws = profile_wb["account_profiles"]
    result = process_profile_sheet(profile_ws)
    personas = {}
    names = {}
    for row in range(2, profile_ws.max_row + 1):
        headers = [c.value for c in profile_ws[1]]
        idx = {h: i + 1 for i, h in enumerate(headers)}
        personas[str(profile_ws.cell(row, idx["account_id"]).value)] = str(profile_ws.cell(row, idx["persona_tag"]).value)
        names[str(profile_ws.cell(row, idx["account_id"]).value)] = str(profile_ws.cell(row, idx["account_canonical_name"]).value)
    obs_updated = process_observations(profile_wb["field_observations"], result["replacements"], personas, names)
    coverage_updated = update_coverage(profile_wb["profile_coverage"], result["replacements"])
    profile_wb.save(PROFILE_XLSX)

    main_wb = safe_load_workbook(MAIN_XLSX)
    if "accounts" in main_wb.sheetnames:
        result_main = process_profile_sheet(main_wb["accounts"])
    else:
        result_main = process_profile_sheet(main_wb[main_wb.sheetnames[0]])
    main_wb.save(MAIN_XLSX)

    print(
        {
            "profiles_updated": result["updated"],
            "profile_excerpt_updated": result["excerpt_updated"],
            "observations_updated": obs_updated,
            "coverage_updated": coverage_updated,
            "main_updated": result_main["updated"],
            "main_excerpt_updated": result_main["excerpt_updated"],
        }
    )


if __name__ == "__main__":
    main()
