"""Constants shared by static-pool governance scripts."""

VALID_REVIEW_STATUSES = ("active", "pending_review", "hold", "removed")
VALID_QUEUE_TYPES = (
    "new_intake",
    "verification",
    "promotion_review",
    "boundary_review",
    "knowledge_extraction",
    "cleanup_review",
)

FORMAL_L5_REVIEW_STATUS = "active"
OBSERVATION_L5_REVIEW_STATUS = "pending_review"

LEGACY_REVIEW_STATUS_MAP = {
    "queued": OBSERVATION_L5_REVIEW_STATUS,
    "auto_ingested": OBSERVATION_L5_REVIEW_STATUS,
    "promotion_completed": OBSERVATION_L5_REVIEW_STATUS,
}

PROMOTION_DECISIONS = ("allow", "warn", "block")

STANDARD_PERSONA_IDS = {
    "retail_brand_beauty",
    "retail_brand_maternal_pet",
    "retail_fashion_group",
    "retail_multi_store",
    "retail_high_sku_brand",
    "cbec_multi_platform_brand",
    "cbec_platform_operator",
    "mfg_multi_factory_group",
    "mfg_rnd_sales_complex",
}

LEGACY_PERSONA_TAG_MAP = {
    "cbec_brand_outbound": "cbec_multi_platform_brand",
    "cbec_supply_chain_complex": "cbec_multi_platform_brand",
    "retail_multi_store_chain": "retail_multi_store",
    "retail_chain_fnb": "retail_multi_store",
}

RISK_FLAGS = {
    "generic_fact_risk",
    "persona_overreach",
    "track_boundary_risk",
    "maturity_overrated",
    "evidence_thin",
    "official_source_missing",
    "nonstandard_persona",
}

PLACEHOLDER_VALUES = {
    "",
    "待补充",
    "待确认",
    "待补官网/年报/IR口径",
    "待补官网 / 年报 / IR 披露",
    "待补公开披露",
    "待补公开财报口径",
    "待补最近定期报告和经营披露",
    "待补官网招聘页",
    "待补更强官方披露",
    "待补公司级市场参考",
    "待补公司级资产映射",
    "待补字段级 evidence",
    "待补案例映射",
}

GENERIC_PRODUCT_HINTS = (
    "品牌消费品",
    "品牌零售",
    "消费品业务",
    "产品矩阵与渠道协同复杂度",
)
GENERIC_MODEL_HINTS = (
    "以品牌消费品经营为主",
    "依赖线上线下或多渠道协同",
    "覆盖研发、制造与销售协同",
    "强调品类管理、履约效率和供应链协同",
)
GENERIC_ADMISSION_HINTS = (
    "适合作为",
    "新增 L5 候选",
    "扩池候选",
    "相邻样本",
)
GENERIC_PROFILE_TEXT_HINTS = (
    "已达到 L3 可读档案层最低门槛",
    "已达到可读档案层最低可用标准",
    "当前可确认",
    "可作为静态背景补充",
)

FROZEN_SOURCE_TAGS = {
    "legacy_archive_page",
    "legacy_archive_body",
    "legacy_profile_long_text",
    "legacy_main_explanation",
    "legacy_focus_note",
    "legacy_topic_pack",
    "raw_source_file",
    "raw_pdf",
    "raw_docx",
}
