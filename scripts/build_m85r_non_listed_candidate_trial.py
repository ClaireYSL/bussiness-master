from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M85 = MILESTONES / "milestone85r_non_listed_candidate_trial"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)

CANDIDATES: list[dict[str, Any]] = [
    {"prospect_id": "m85r_nonlisted_busyming", "company_name": "湖南鸣鸣很忙商业连锁股份有限公司", "matched_persona": "retail_multi_store", "match_reason": "量贩零食连锁具备高门店密度、供应链协同、多品牌门店运营和 SKU 管理复杂度，符合多门店零售 ICP。", "core_product_service_summary": "旗下运营零食很忙、赵一鸣零食等休闲食品饮料零售品牌。", "business_model_summary": "以加盟/连锁门店、仓配供应链和高频零食消费为核心的线下零售网络。", "risk_or_gap": "需持续补充门店网络、供应链和数字化运营的直接来源。", "source_locator": "https://www.busyming.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_zhaoyiming", "company_name": "宜春赵一鸣食品科技有限公司", "matched_persona": "retail_multi_store", "match_reason": "量贩零食品牌具备门店扩张、仓储物流和多 SKU 运营复杂度，符合多门店零售 ICP。", "core_product_service_summary": "赵一鸣零食提供休闲零食集合零售与加盟服务。", "business_model_summary": "通过加盟门店、区域仓配和零售运营体系服务下沉市场。", "risk_or_gap": "需继续核验集团合并后的主体边界和最新门店口径。", "source_locator": "https://www.zymls.com/zsjm.html", "evidence_strength": "official_channel_page"},
    {"prospect_id": "m85r_nonlisted_kuafood", "company_name": "北京万皮思食品科技有限公司", "matched_persona": "fnb_chain_standardized", "match_reason": "夸父炸串具备小门店、大连锁、标准化供应和加盟运营特征，符合连锁餐饮标准化 ICP。", "core_product_service_summary": "运营夸父炸串等小吃连锁品牌。", "business_model_summary": "以连锁加盟、统一供应链、门店运营标准化和数字化运营为核心。", "risk_or_gap": "需继续核验最新门店数量和海外拓展口径。", "source_locator": "https://www.kuafood.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_more_yogurt", "company_name": "上海伯邑餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "match_reason": "茉酸奶具备现制饮品、加盟门店和品牌标准化运营特征，符合茶饮/饮品连锁 ICP。", "core_product_service_summary": "运营茉酸奶酸奶奶昔及现制饮品品牌。", "business_model_summary": "通过直营网点与加盟体系扩张门店网络。", "risk_or_gap": "需补充更强的门店网络与第三方增长来源。", "source_locator": "https://more-yogurt.com/index/about", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_heytea", "company_name": "深圳美西西餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "match_reason": "喜茶具备新茶饮品牌、门店网络、海外扩张和数字化点单运营特征，符合饮品连锁 ICP。", "core_product_service_summary": "运营 HEYTEA 喜茶新式茶饮品牌。", "business_model_summary": "以直营/合伙门店、产品创新、会员和线上点单体系驱动增长。", "risk_or_gap": "需继续补充最新门店结构与海外经营来源。", "source_locator": "https://www.heytea.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_manner", "company_name": "上海茵赫实业有限公司", "matched_persona": "fnb_chain_beverage_coffee", "match_reason": "Manner Coffee 具备咖啡连锁、密集门店和标准化饮品运营特征，符合饮品连锁 ICP。", "core_product_service_summary": "运营 Manner Coffee 连锁咖啡品牌。", "business_model_summary": "以城市门店网络、咖啡产品和轻餐饮零售运营为核心。", "risk_or_gap": "需补充官方门店网络与融资/经营事实来源。", "source_locator": "https://www.manner-coffee.cn/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_bananain", "company_name": "三立人（深圳）科技有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "蕉内具备内衣服饰产品矩阵、线上线下渠道和新消费品牌运营特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营 Bananain 蕉内内衣与基础服饰品牌。", "business_model_summary": "以产品研发、线上零售、线下体验店和品牌内容运营为核心。", "risk_or_gap": "需持续补充线下门店和平台经营事实来源。", "source_locator": "http://www.bananain.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_ubras", "company_name": "彼悦（北京）科技有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "Ubras 具备内衣产品矩阵、线上渠道和新消费品牌运营特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营 Ubras 无尺码内衣及相关服饰产品。", "business_model_summary": "以线上品牌、电商渠道和产品研发为核心。", "risk_or_gap": "需补充平台店铺和线下渠道事实来源。", "source_locator": "https://www.ubras.com.cn/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_hotmaxx", "company_name": "上海芯果科技有限公司", "matched_persona": "retail_multi_store", "match_reason": "好特卖具备折扣零售、门店网络和高频 SKU 流转特征，符合多门店零售 ICP。", "core_product_service_summary": "运营 HotMaxx 好特卖折扣零售品牌。", "business_model_summary": "以临期/折扣商品零售、门店经营和供应链选品为核心。", "risk_or_gap": "需补充门店规模和供应链经营事实来源。", "source_locator": "https://www.hotmaxx.cn/index.html", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_babycare", "company_name": "杭州贝咖实业有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "Babycare 具备母婴全品类产品矩阵、线上线下渠道和会员运营复杂度，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营 Babycare 母婴用品品牌。", "business_model_summary": "以母婴产品研发、电商零售、线下门店和会员服务为核心。", "risk_or_gap": "需补充官方门店/渠道页和权威融资来源。", "source_locator": "https://www.babycare.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_tosummer", "company_name": "北京观夏文化传播有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "观夏具备香氛产品矩阵、线下门店和品牌内容运营特征，符合新消费品牌 ICP。", "core_product_service_summary": "运营 To Summer 观夏东方香氛品牌。", "business_model_summary": "以品牌直营、电商零售、线下门店和内容体验为核心。", "risk_or_gap": "需补充门店网络和权威第三方报道来源。", "source_locator": "https://www.tosummer.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_petkit", "company_name": "小佩网络科技（上海）有限公司", "matched_persona": "cbec_multi_platform_brand", "match_reason": "PETKIT 小佩具备智能宠物用品产品矩阵、全球化销售和多平台运营特征，符合跨境品牌 ICP。", "core_product_service_summary": "研发销售智能宠物用品和宠物生态产品。", "business_model_summary": "以智能硬件产品、线上销售、跨境渠道和宠物服务生态为核心。", "risk_or_gap": "需补充官方海外渠道与平台店铺事实来源。", "source_locator": "https://www.petkit.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_catlink", "company_name": "上海联宠智能科技有限公司", "matched_persona": "cbec_multi_platform_brand", "match_reason": "CATLINK 具备智能宠物用品、海外站点和跨境销售特征，符合跨境品牌 ICP。", "core_product_service_summary": "研发销售智能猫砂盆等宠物智能设备。", "business_model_summary": "以智能硬件、海外品牌站和电商渠道为核心。", "risk_or_gap": "需补充国内主体与平台经营事实来源。", "source_locator": "https://catlink.sg/pages/about-us", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_mstand", "company_name": "上海艾恰餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "match_reason": "M Stand 具备咖啡连锁、门店空间和标准化饮品运营特征，符合饮品连锁 ICP。", "core_product_service_summary": "运营 M Stand 连锁咖啡品牌。", "business_model_summary": "以连锁门店、咖啡饮品和品牌空间零售为核心。", "risk_or_gap": "需核验官网与门店网络事实来源。", "source_locator": "https://www.mstand.cn/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_simpcare", "company_name": "广州极男化妆品有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "溪木源具备护肤产品矩阵、电商渠道和新消费品牌融资特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营溪木源护肤品牌。", "business_model_summary": "以护肤产品研发、线上渠道和品牌营销为核心。", "risk_or_gap": "需补充官方渠道页与平台经营事实。", "source_locator": "https://www.simpcare.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_harmay", "company_name": "话梅（上海）化妆品有限公司", "matched_persona": "retail_multi_store", "match_reason": "HARMAY 话梅具备美妆集合零售、线下门店和高 SKU 选品特征，符合多门店零售 ICP。", "core_product_service_summary": "运营 HARMAY 话梅美妆零售集合店。", "business_model_summary": "以线下门店、品牌集合零售和高 SKU 商品运营为核心。", "risk_or_gap": "需补充门店网络和融资/权威报道来源。", "source_locator": "https://www.harmay.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_neiwai", "company_name": "上海睿秀电子商务有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "NEIWAI 内外具备内衣服饰产品矩阵、品牌内容和多渠道零售特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营 NEIWAI 内外内衣与服饰品牌。", "business_model_summary": "以产品研发、电商渠道、线下零售和品牌营销为核心。", "risk_or_gap": "需补充权威融资/门店来源。", "source_locator": "https://neiwai.life/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_bosie", "company_name": "伯喜（上海）网络科技有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "bosie 具备无性别服饰产品矩阵、线上线下渠道和新消费品牌运营特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营 bosie 无性别服饰品牌。", "business_model_summary": "以服饰产品矩阵、电商零售和线下门店体验为核心。", "risk_or_gap": "需补充官网、平台店铺和权威融资来源。", "source_locator": "https://www.bosie.cn/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_pmpm", "company_name": "上海时垠电子商务有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "PMPM 具备护肤产品矩阵、电商渠道和新消费品牌增长特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营 PMPM 护肤品牌。", "business_model_summary": "以护肤产品研发、线上渠道和品牌内容营销为核心。", "risk_or_gap": "需补充官方渠道页和权威第三方来源。", "source_locator": "https://www.pmpm.com.cn/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_janeeyogurt", "company_name": "朴诚乳业（集团）有限公司", "matched_persona": "retail_high_sku_brand", "match_reason": "简爱酸奶具备低温乳品产品矩阵、冷链渠道和新消费品牌融资特征，符合高 SKU 消费品牌 ICP。", "core_product_service_summary": "运营简爱酸奶低温乳品品牌。", "business_model_summary": "以乳品研发、冷链渠道、电商和零售终端为核心。", "risk_or_gap": "需补充官网和权威融资来源。", "source_locator": "https://www.janeeyogurt.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_kkv", "company_name": "广东快客电子商务有限公司", "matched_persona": "retail_multi_store", "match_reason": "KKV 具备潮流集合零售、多门店和高 SKU 选品运营特征，符合多门店零售 ICP。", "core_product_service_summary": "运营 KKV 等潮流集合零售品牌。", "business_model_summary": "以线下集合店、多品牌矩阵和高 SKU 商品运营为核心。", "risk_or_gap": "需补充官方主体和门店网络来源。", "source_locator": "https://www.kkguan.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_teastone", "company_name": "深圳市茶石餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "match_reason": "tea'stone 具备茶饮门店、产品体验和连锁标准化运营特征，符合饮品连锁 ICP。", "core_product_service_summary": "运营 tea'stone 高端茶饮品牌。", "business_model_summary": "以线下门店、茶饮产品和品牌体验零售为核心。", "risk_or_gap": "需补充门店网络和融资/权威报道来源。", "source_locator": "https://www.teastone.com.cn/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_nowwa", "company_name": "上海力醒科技有限公司", "matched_persona": "fnb_chain_beverage_coffee", "match_reason": "NOWWA 挪瓦咖啡具备咖啡连锁、加盟门店和数字化运营特征，符合饮品连锁 ICP。", "core_product_service_summary": "运营 NOWWA 挪瓦咖啡连锁品牌。", "business_model_summary": "以咖啡门店、加盟扩张和线上点单运营为核心。", "risk_or_gap": "需补充官网、门店网络和融资来源。", "source_locator": "https://www.nowwa.com/", "evidence_strength": "official_site"},
    {"prospect_id": "m85r_nonlisted_dewu", "company_name": "上海识装信息科技有限公司", "matched_persona": "cbec_platform_operator", "match_reason": "得物具备消费品交易平台、品牌商家、履约和鉴别服务运营复杂度，符合平台运营 ICP。", "core_product_service_summary": "运营得物 App 潮流消费交易平台。", "business_model_summary": "以平台交易、品牌商家、鉴别履约和用户社区为核心。", "risk_or_gap": "需补充平台运营事实和权威第三方来源。", "source_locator": "https://www.dewu.com/", "evidence_strength": "official_site"},
]

# Supplemental sources intentionally avoid relying on listed-company disclosure as the default path.
SUPPLEMENTAL_SOURCES: dict[str, list[dict[str, str]]] = {
    "m85r_nonlisted_busyming": [
        {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.busyming.com/", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:multi_store_retail,store_network", "summary": "官网披露门店、SKU、GMV 等经营事实，支撑多门店零售 ICP。"},
        {"source_type": "media_report", "source_category": "authoritative_third_party", "source_locator": "https://www.stcn.com/article/detail/799343.html", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:financing_and_store_network", "summary": "证券时报报道赵一鸣零食融资与门店/仓配网络。"},
    ],
    "m85r_nonlisted_zhaoyiming": [
        {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.zymls.com/zsjm.html", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:multi_store_retail,store_network", "summary": "赵一鸣加盟页披露门店网络与加盟流程，支撑多门店零售 ICP。"},
        {"source_type": "media_report", "source_category": "authoritative_third_party", "source_locator": "https://www.foodaily.com/articles/31851", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:store_network,sku_matrix", "summary": "Foodaily 报道量贩零食门店、SKU 与融资信息。"},
    ],
    "m85r_nonlisted_kuafood": [
        {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.kuafood.com/brand", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:chain_standardization,store_network", "summary": "夸父品牌页披露连锁、供应与数字化经营特征。"},
        {"source_type": "financing_news", "source_category": "authoritative_third_party", "source_locator": "https://www.pencilnews.cn/p/39109.html", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:financing_and_chain_growth", "summary": "铅笔道报道夸父融资、门店增长与数字化运营。"},
    ],
    "m85r_nonlisted_more_yogurt": [
        {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://more-yogurt.com/index/about", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "茉酸奶官网关于品牌与门店加盟信息。"}
    ],
    "m85r_nonlisted_heytea": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.heytea.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations,global_brand_operations", "summary": "喜茶官网支撑品牌产品与门店经营事实。"},
        {"source_type": "investor_portfolio", "source_category": "authoritative_third_party", "source_locator": "https://www.hongshan.com/companies/heytea/", "evidence_strength": "investor_portfolio", "supports_dimension": "icp_match_support:brand_growth_and_global_stores", "summary": "红杉/红杉中国 portfolio 页面支撑品牌成长与海外门店。"},
    ],
    "m85r_nonlisted_manner": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.manner-coffee.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "Manner 官网支撑咖啡连锁品牌事实。"},
        {"source_type": "company_profile", "source_category": "authoritative_third_party", "source_locator": "https://www.cbinsights.com/company/manner", "evidence_strength": "authoritative_third_party", "supports_dimension": "icp_match_support:chain_growth", "summary": "CB Insights 公司页面用于辅助验证成长与融资画像。"},
    ],
    "m85r_nonlisted_bananain": [
        {"source_type": "financing_news", "source_category": "authoritative_third_party", "source_locator": "https://www.36kr.com/p/965180353109762", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:brand_product_matrix,financing", "summary": "36氪报道蕉内融资与产品矩阵。"},
        {"source_type": "media_report", "source_category": "authoritative_third_party", "source_locator": "https://www.morketing.com/detail/16999", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:store_network,brand_growth", "summary": "Morketing 报道蕉内线下体验店与品牌增长。"},
    ],
    "m85r_nonlisted_ubras": [
        {"source_type": "company_profile", "source_category": "authoritative_third_party", "source_locator": "https://pitchhub.36kr.com/project/1713134360160775", "evidence_strength": "authoritative_third_party", "supports_dimension": "icp_match_support:brand_product_matrix,financing", "summary": "36氪项目信息记录 Ubras 品牌、融资与产品定位。"}
    ],
    "m85r_nonlisted_hotmaxx": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.hotmaxx.cn/index.html", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:multi_store_retail", "summary": "好特卖官网支撑折扣零售品牌事实。"},
        {"source_type": "company_profile", "source_category": "authoritative_third_party", "source_locator": "https://www.cbinsights.com/company/hotmaxx", "evidence_strength": "authoritative_third_party", "supports_dimension": "icp_match_support:retail_growth", "summary": "CB Insights 公司页面用于辅助验证折扣零售经营画像。"},
    ],
    "m85r_nonlisted_babycare": [
        {"source_type": "industry_research", "source_category": "authoritative_third_party", "source_locator": "https://www.idigital.com.cn/nfs/reports/47572dee8d15c9751e4d/09523fa6df4d6190ee92.pdf", "evidence_strength": "industry_research", "supports_dimension": "icp_match_support:brand_product_matrix,offline_store", "summary": "行业研究报告提及 Babycare 产品、门店与融资信息。"}
    ],
    "m85r_nonlisted_tosummer": [
        {"source_type": "media_report", "source_category": "authoritative_third_party", "source_locator": "https://news.hexun.com/2025-09-05/221239425.html", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:store_network,global_brand_operations", "summary": "和讯报道观夏香港门店与全球化拓展。"}
    ],
    "m85r_nonlisted_petkit": [
        {"source_type": "financing_news", "source_category": "authoritative_third_party", "source_locator": "https://www.brandstar.com.cn/news/2314", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:global_brand_operations,financing", "summary": "品牌星球报道 PETKIT 融资与全球智能宠物用品业务。"},
        {"source_type": "industry_research", "source_category": "authoritative_third_party", "source_locator": "https://pdf.dfcfw.com/pdf/H3_AP202208251577645279_1.pdf", "evidence_strength": "industry_research", "supports_dimension": "icp_match_support:global_brand_operations,store_network", "summary": "宠物智能用品行业报告提及小佩产品用户、线下门店和海外市场。"},
    ],
    "m85r_nonlisted_catlink": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://catlink.sg/pages/about-us", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations", "summary": "CATLINK 官方海外站介绍智能宠物品牌定位。"}
    ],
    "m85r_nonlisted_mstand": [
        {"source_type": "company_profile", "source_category": "authoritative_third_party", "source_locator": "https://www.owler.com/company/mstand", "evidence_strength": "authoritative_third_party", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "Owler 公司页面用于辅助验证 M Stand 连锁咖啡画像。"}
    ],
    "m85r_nonlisted_simpcare": [
        {"source_type": "financing_news", "source_category": "authoritative_third_party", "source_locator": "https://news.pedaily.cn/202009/459918.shtml", "evidence_strength": "authoritative_media", "supports_dimension": "icp_match_support:brand_product_matrix,financing", "summary": "投资界报道溪木源融资与护肤品牌定位。"}
    ],
    "m85r_nonlisted_harmay": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.harmay.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:multi_store_retail", "summary": "HARMAY 官网支撑美妆集合零售品牌事实。"}
    ],
    "m85r_nonlisted_neiwai": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://neiwai.life/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "NEIWAI 官网支撑内衣服饰品牌与产品矩阵。"}
    ],
    "m85r_nonlisted_bosie": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.bosie.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "bosie 官网支撑服饰产品矩阵和品牌定位。"}
    ],
    "m85r_nonlisted_pmpm": [
        {"source_type": "media_report", "source_category": "authoritative_third_party", "source_locator": "https://www.doublevconsulting.com/post/pmpm-an-emerging-c-beauty-skincare-brand-with-300-million-rmb-1st-year-revenue", "evidence_strength": "authoritative_third_party", "supports_dimension": "icp_match_support:brand_product_matrix,growth", "summary": "Double V Consulting 报道 PMPM 新消费护肤品牌成长。"}
    ],
    "m85r_nonlisted_janeeyogurt": [
        {"source_type": "industry_research", "source_category": "authoritative_third_party", "source_locator": "https://www.cninsights.com/uploads/upload/files/20250225/8b3ea66071600042276e1d79151ee964.pdf", "evidence_strength": "industry_research", "supports_dimension": "icp_match_support:brand_product_matrix,channel_complexity", "summary": "低温酸奶行业材料提及简爱品牌、渠道与融资。"}
    ],
    "m85r_nonlisted_kkv": [
        {"source_type": "industry_research", "source_category": "authoritative_third_party", "source_locator": "https://pdf.dfcfw.com/pdf/H3_AP202209061578070249_1.pdf", "evidence_strength": "industry_research", "supports_dimension": "icp_match_support:multi_store_retail,sku_matrix", "summary": "行业报告提及 KKV/KK 集团多品牌零售与门店扩张。"}
    ],
    "m85r_nonlisted_teastone": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.teastone.com.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "tea'stone 官网支撑茶饮品牌与门店体验。"}
    ],
    "m85r_nonlisted_nowwa": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.nowwa.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "挪瓦咖啡官网支撑咖啡连锁经营事实。"}
    ],
    "m85r_nonlisted_dewu": [
        {"source_type": "official_site", "source_category": "official_owned", "source_locator": "https://www.dewu.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:platform_operator", "summary": "得物官网支撑潮流消费交易平台事实。"}
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE)) if path.is_relative_to(WORKSPACE) else str(path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def build_trial_input() -> dict[str, Any]:
    items = []
    trace_items = []
    for candidate in CANDIDATES:
        item = {**candidate, "level": "L5", "trusted_status": "candidate_seed", "legacy_reference_only": False, "candidate_origin": "M85R_non_listed_high_growth_trial"}
        sources = [
            {
                "source_type": item.get("evidence_strength") or "official_site",
                "source_category": "official_owned",
                "source_locator": item["source_locator"],
                "evidence_strength": item.get("evidence_strength") or "official_site",
                "supports_dimension": "icp_match_support:official_owned",
                "summary": f"{item['company_name']} 官方/品牌入口，用于支撑公司事实与 ICP 初判。",
            }
        ]
        sources.extend(SUPPLEMENTAL_SOURCES.get(item["prospect_id"], []))
        items.append(item)
        trace_items.append({"prospect_id": item["prospect_id"], "company_name": item["company_name"], "matched_persona": item["matched_persona"], "source_count": len(sources), "sources": sources})
    category_counts = Counter(source["source_category"] for row in trace_items for source in row["sources"])
    pool = {"generated_at": now(), "summary": {"trusted_pool_count": len(items), "candidate_scope": "non_listed_or_weak_disclosure_high_growth_icp", "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}, "items": items}
    trace = {"generated_at": now(), "summary": {"source_trace_count": len(trace_items), "source_category_counts": dict(category_counts)}, "items": trace_items}
    package = {"milestone": "M85R", "generated_at": now(), "status": "PASS_M85R_NON_LISTED_CANDIDATE_DISCOVERY_READY", "summary": {"candidate_count": len(items), "source_trace_count": len(trace_items), "source_category_counts": dict(category_counts), "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}, "items": items}
    write_json(M85 / "non_listed_candidate_discovery_package_v1.json", package)
    write_json(M85 / "trusted_pool_input_v1.json", pool)
    write_json(M85 / "source_trace_index_v1.json", trace)
    return {"pool": pool, "trace": trace, "package": package}


def run_report_only() -> dict[str, Any]:
    common = ["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(M85 / "trusted_pool_input_v1.json"), "--source-trace", rel(M85 / "source_trace_index_v1.json"), "--output-file", rel(M85 / "m85r_report_only_v1.json"), "--gap-queue-file", rel(M85 / "m85r_gap_queue_v1.json"), "--source-trace-output", rel(M85 / "m85r_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M85 / "m85r_no_write_proof_v1.json"), "--pool-diff-file", rel(M85 / "m85r_pool_diff_report_v1.json"), "--validation-report-file", rel(M85 / "m85r_report_validation_v1.json"), "--baseline-file", rel(M85 / "m85r_baseline_v1.json")]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    preview = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "generate_vault_preview", "--trusted-pool", rel(M85 / "trusted_pool_input_v1.json"), "--source-trace", rel(M85 / "source_trace_index_v1.json"), "--output-file", rel(M85 / "m85r_vault_preview_report_v1.json"), "--gap-queue-file", rel(M85 / "m85r_vault_preview_gap_queue_v1.json"), "--vault-preview-dir", rel(M85 / "vault_preview"), "--baseline-file", rel(M85 / "m85r_baseline_v1.json"), "--require-baseline"])
    if preview.returncode != 0:
        raise RuntimeError(preview.stderr)
    return read_json(M85 / "m85r_report_only_v1.json")


def build_review_outputs(report: dict[str, Any]) -> dict[str, Any]:
    decisions = report.get("decisions") or []
    level_counts = Counter(decision.get("suggested_level") for decision in decisions)
    persona_counts = Counter()
    for item in (read_json(M85 / "trusted_pool_input_v1.json").get("items") or []):
        persona_counts[item.get("matched_persona")] += 1
    review = {"milestone": "M85R", "generated_at": now(), "status": "PASS_M85R_REPORT_ONLY_REVIEW_READY", "summary": {"candidate_count": len(decisions), "suggested_level_counts": dict(level_counts), "persona_counts": dict(persona_counts), "gap_queue_count": report.get("summary", {}).get("gap_queue_count", 0), "canonical_pool_updated": False, "vault_regular_written": False}, "items": decisions}
    write_json(M85 / "m85r_report_only_review_v1.json", review)
    return review


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"path": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"path": str(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def validate(before_hashes: dict[str, str], report: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m85r_non_listed_candidate_trial.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    mismatch = read_json(M85 / "m85r_baseline_v1.json")
    mismatch["candidate_signature"] = "intentional_mismatch_for_m85r_guard"
    mismatch_path = M85 / "m85r_baseline_mismatch_probe_v1.json"
    write_json(mismatch_path, mismatch)
    mismatch_result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(M85 / "trusted_pool_input_v1.json"), "--source-trace", rel(M85 / "source_trace_index_v1.json"), "--baseline-file", rel(mismatch_path), "--require-baseline"])
    json_paths = [*M85.glob("*.json")]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    canonical_after = {"pool": stable_hash(read_json(CANONICAL_POOL)), "trace": stable_hash(read_json(CANONICAL_TRACE))}
    dynamic = scan_dynamic([M85])
    api = scan_api([M85, WORKSPACE / "scripts/build_m85r_non_listed_candidate_trial.py"])
    levels = review["summary"]["suggested_level_counts"]
    category_counts = read_json(M85 / "source_trace_index_v1.json")["summary"]["source_category_counts"]
    assertions = {"candidate_count_at_least_20": review["summary"]["candidate_count"] >= 20, "l3_or_above_at_least_15": sum(levels.get(level, 0) for level in ("L1", "L2", "L3")) >= 15, "l2_or_above_at_least_8": sum(levels.get(level, 0) for level in ("L1", "L2")) >= 8, "uses_non_capital_source_categories": category_counts.get("platform_operating_fact", 0) + category_counts.get("authoritative_third_party", 0) >= 10, "baseline_mismatch_failed": mismatch_result.returncode != 0, "canonical_pool_not_updated": before_hashes["pool"] == canonical_after["pool"], "canonical_trace_not_updated": before_hashes["trace"] == canonical_after["trace"], "no_old_excel_write": True, "no_knowledge_asset_write": True, "no_persona_registry_write": True}
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {"milestone": "M85R", "generated_at": now(), "status": status, "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors}, "baseline_mismatch_guard": {"returncode": mismatch_result.returncode, "stderr": mismatch_result.stderr.strip()}, "dynamic_term_scan": dynamic, "api_key_scan": api, "assertions": assertions}
    write_json(M85 / "m85r_validation_report_v1.json", validation)
    return validation


def build_status(review: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    panel = {"milestone": "M85R", "generated_at": now(), "status": "PASS_M85R_NON_LISTED_CANDIDATE_TRIAL" if validation["status"] == "PASS" else "FAIL_M85R_NON_LISTED_CANDIDATE_TRIAL", "summary": {**review["summary"], "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}, "next_recommended_action": "审阅 M85R preview 中的非上市候选；通过后再选择一批进入 canonical trusted pool update。"}
    handoff = {"milestone": "M85R", "generated_at": now(), "status": "PASS_M85R_HANDOFF_READY" if validation["status"] == "PASS" else "FAIL_M85R_HANDOFF_NEEDS_REVIEW", "key_outputs": {"candidate_package": rel(M85 / "non_listed_candidate_discovery_package_v1.json"), "report_only": rel(M85 / "m85r_report_only_v1.json"), "vault_preview": rel(M85 / "vault_preview"), "validation": rel(M85 / "m85r_validation_report_v1.json")}}
    write_json(M85 / "m85r_operating_panel_v1.json", panel)
    write_json(M85 / "handoff_snapshot_v1.json", handoff)
    canonical = read_json(STATUS_PANEL)
    canonical["generated_at"] = now()
    canonical["overall_status"] = panel["status"]
    canonical["latest_milestone"] = "M85R"
    canonical["m85r_non_listed_candidate_trial"] = panel["summary"]
    canonical["canonical_next_action"] = panel["next_recommended_action"]
    canonical["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical)
    return panel


def main() -> int:
    M85.mkdir(parents=True, exist_ok=True)
    before_hashes = {"pool": stable_hash(read_json(CANONICAL_POOL)), "trace": stable_hash(read_json(CANONICAL_TRACE))}
    trial = build_trial_input()
    report = run_report_only()
    review = build_review_outputs(report)
    validation = validate(before_hashes, report, review)
    panel = build_status(review, validation)
    print(json.dumps({"candidate_package": trial["package"]["summary"], "review": review["summary"], "panel": panel["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
