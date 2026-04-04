# `external_target_account_pool_v2` 首版真实内容 v0.1

## 1. 文档目的

本文件把当前 `v0.7 总池汇总视图` 中已经压实的高质量层账户，迁入 `external_target_account_pool_v2` 的首版真实内容。

本文件的目标不是一次性迁完全部 `354` 家，而是先把最稳定的 `L1 + L2 + L3` 迁入结构化主表，为后续继续迁 `L4/L5` 打下基础。

## 2. 本轮迁移范围

本轮只迁以下层级：

- `L1-高可信母样本`
- `L2-高可信补充样本`
- `L3-中高可信补充样本`

迁移规模：

- `L1=8`
- `L2=36`
- `L3=15`
- 合计 `59`

未纳入本轮：

- `L4=14`
- `L5=281`

原因：

- `L1-L3` 已有相对稳定的画像、理由和证据基础
- `L4/L5` 仍适合继续通过批次文档和核验文档推进，不宜过早全部搬入主表

## 3. 首版字段策略

本轮首版真实内容只填充最稳定的核心字段：

- `account_id`
- `account_canonical_name`
- `brand_name`
- `primary_track`
- `industry_l2`
- `business_model`
- `persona_tag`
- `pool_layer`
- `static_priority`
- `existing_customer_reference`
- `solution_match`
- `knowledge_asset_refs`
- `admission_reason_summary`
- `source_note`
- `validation_gap`

以下字段本轮不强求全填：

- `group_name`
- `company_scale_band`
- `secondary_jtbd`
- `transformation_stage_tag`
- `dynamic_*`

## 4. L1 高可信母样本

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_kidswant` | 孩子王儿童用品股份有限公司 | 孩子王 | 零售消费 | 母婴零售 | 连锁零售 | retail_multi_store | L1 | A | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1 | 多门店、多区域、总部强管理特征明确，可作为多门店连锁零售核心锚点。 | 第一批种子池 v0.2 核验分层版 | 区域经营颗粒度仍可补 |
| `acc_miniso` | 名创优品（广州）有限责任公司 | 名创优品 | 零售消费 | 品牌零售 | 连锁零售 | retail_multi_store | L1 | A | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1 | 零售网络广、区域经营复杂、总部管理半径大，适合做多门店连锁零售核心标尺。 | 第一批种子池 v0.2 核验分层版 | 中国经营主体与组织结构仍可补 |
| `acc_anker` | 安克创新科技股份有限公司 | 安克创新 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L1 | A | 乐其 SmallRig | 跨境利润分析与海外经营驾驶舱 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 全球品牌出海和多平台经营特征稳定，可作为跨境品牌出海核心锚点。 | 第一批种子池 v0.2 核验分层版 | 平台矩阵和区域经营颗粒度仍可补 |
| `acc_autel` | 深圳市道通科技股份有限公司 | 道通科技 | 跨境电商 | 全球渠道经营 | 跨境经营 | cbec_supply_chain_complex | L1 | B | 乐其 SmallRig | 经营分析与全球渠道协同 | ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1,ka_insight_cbec_jtbd_v1 | 全球销售覆盖和产品线复杂度明确，适合作为供应链复杂跨境经营型核心样本。 | 第一批种子池 v0.2 核验分层版 | 主切入更偏跨境还是全球化制造仍可补 |
| `acc_luxshare` | 立讯精密工业股份有限公司 | 立讯精密 | 先进制造 | 消费电子制造 | 多工厂制造 | mfg_multi_factory_group | L1 | A | 零跑汽车 | 制造业经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 多基地、多业务协同和全球制造属性明确，可作为多工厂离散制造集团核心锚点。 | 第一批种子池 v0.2 核验分层版 | 工厂与事业部颗粒度仍可补 |
| `acc_inovance` | 深圳市汇川技术股份有限公司 | 汇川技术 | 先进制造 | 工业自动化 | 技术型制造 | mfg_multi_factory_group | L1 | A | 零跑汽车,昊志机电类案例 | 制造业经营协同 | ka_case_haozhi_dashboard_v1,ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多业务线和经营协同明显，具备稳定的先进制造经营型 BI 锚点价值。 | 第一批种子池 v0.2 核验分层版 | 多工厂颗粒度和渠道协同仍可补 |
| `acc_mindray` | 深圳迈瑞生物医疗电子股份有限公司 | 迈瑞医疗 | 先进制造 | 医疗器械 | 技术型制造 | mfg_rnd_sales_complex | L1 | A | 零跑汽车,昊志机电类案例 | LTC 与经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 全球经营和研产销协同复杂度高，可作为技术型制造核心锚点。 | 第一批种子池 v0.2 核验分层版 | 更细的组织与渠道结构仍可补 |
| `acc_uih` | 上海联影医疗科技股份有限公司 | 联影医疗 | 先进制造 | 医疗器械 | 技术型制造 | mfg_rnd_sales_complex | L1 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高端医疗设备和复杂经营协同特征明确，可作为技术型制造核心锚点。 | 第一批种子池 v0.2 核验分层版 | 集团协同切入颗粒度仍可补 |

## 5. L2 高可信补充样本

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_chowtaiseng` | 周大生珠宝股份有限公司 | 周大生 | 零售消费 | 珠宝零售 | 连锁零售 | retail_multi_store | L2 | B | 鲜丰水果,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 珠宝零售终端网络和连锁经营结构明确，可作为多门店零售补充标尺。 | 第二批扩展候选池 v0.2 首轮核验版 | 区域经营颗粒度仍可补 |
| `acc_ecovacs` | 科沃斯机器人股份有限公司 | 科沃斯 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 全球品牌与海外经营特征稳定，适合作为跨境品牌出海补充标尺。 | 第二批扩展候选池 v0.2 首轮核验版 | 平台结构仍可补 |
| `acc_syoung` | 水羊集团股份有限公司 | 水羊 | 零售消费 | 美妆个护 | 品牌消费品 | retail_high_sku_brand | L2 | B | 自然堂,君乐宝,王小卤 | 渠道 / 商品 / 动销增长分析 | ka_case_naturehall_ai_v1 | 美妆个护、高 SKU、多渠道经营特征明确，可作为品牌消费品补充标尺。 | 第二批扩展候选池 v0.3 第二轮核验版 | 渠道结构颗粒度仍可补 |
| `acc_songmics` | 致欧家居科技股份有限公司 | 致欧科技 | 跨境电商 | 家居出海 | 品牌出海 | cbec_multi_platform_brand | L2 | A | 乐其 SmallRig | 跨境利润分析与经营驾驶舱 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1 | 家居出海链路长、平台和区域经营复杂，可作为跨境品牌出海补充标尺。 | 第二批扩展候选池 v0.3 第二轮核验版 | 海外仓与平台颗粒度仍可补 |
| `acc_zhonghangoptic` | 中航光电科技股份有限公司 | 中航光电 | 先进制造 | 高端连接器制造 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高技术制造与复杂客户协同特征明确，可作为技术型制造补充标尺。 | 第二批扩展候选池 v0.3 第二轮核验版 | 全球经营颗粒度仍可补 |
| `acc_roborock` | 北京石头世纪科技股份有限公司 | 石头科技 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 全球消费电子品牌和海外经营特征成立，可作为品牌出海补充标尺。 | 第二批扩展候选池 v0.4 第三轮核验版 | 平台经营颗粒度仍可补 |
| `acc_bestore` | 良品铺子股份有限公司 | 良品铺子 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L2 | A | 自然堂,君乐宝,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | SKU、渠道和库存联动明显，可作为高 SKU 品牌消费品补充标尺。 | L4 中可信候选首轮强核验 | 渠道与供应链颗粒度仍可补 |
| `acc_suntime` | 赛维时代科技股份有限公司 | 赛维时代 | 跨境电商 | 跨境卖家 | 多平台卖家 | cbec_supply_chain_complex | L2 | A | 乐其 SmallRig | 跨境经营分析与利润分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1,ka_insight_cbec_jtbd_v1 | 多平台、多品牌、多链路经营特征明确，可作为跨境经营型补充标尺。 | L4 中可信候选首轮强核验 | 品牌化程度仍可补 |
| `acc_insta360` | 影石创新科技股份有限公司 | 影石创新 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 消费电子品牌出海特征强，适合作为新一代品牌出海补充标尺。 | L5 放量候选首轮强核验 | 平台与区域颗粒度仍可补 |
| `acc_ecoflow` | 深圳市正浩创新科技股份有限公司 | 正浩 EcoFlow | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 海外业务经营驾驶舱 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1 | 海外消费科技品牌特征明确，适合作为跨境品牌出海补充标尺。 | L5 放量候选第二轮强核验 | 平台矩阵颗粒度仍可补 |
| `acc_supcon` | 中控技术股份有限公司 | 中控技术 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化与技术型制造属性明确，适合作为先进制造补充标尺。 | L5 放量候选第二轮强核验 | 业务条线颗粒度仍可补 |
| `acc_easyhome` | 居然之家新零售集团股份有限公司 | 居然之家 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L2 | B | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 家居零售网络与总部管理半径明显，可作为多门店零售补充标尺。 | 第四至第六批关键账户强核验 | 商场层级与区域结构仍可补 |
| `acc_jackery` | 华宝新能科技股份有限公司 | Jackery | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 海外品牌和全球经营特征明确，适合作为跨境品牌出海补充标尺。 | 第四至第六批关键账户强核验 | 平台矩阵颗粒度仍可补 |
| `acc_lens` | 蓝思科技股份有限公司 | 蓝思科技 | 先进制造 | 消费电子制造 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多基地制造和复杂协同特征明确，可作为多工厂制造补充标尺。 | 第四至第六批关键账户强核验 | 工厂布局颗粒度仍可补 |
| `acc_sunwoda` | 欣旺达电子股份有限公司 | 欣旺达 | 先进制造 | 电池制造 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 制造业经营协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多基地与产业链协同特征明确，可作为先进制造补充标尺。 | 第四至第六批关键账户强核验 | 事业部颗粒度仍可补 |
| `acc_catl` | 宁德时代新能源科技股份有限公司 | 宁德时代 | 先进制造 | 新能源制造 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 全球新能源制造与多基地协同特征明确，可作为多工厂制造补充标尺。 | 第四至第六批关键账户强核验 | 组织与基地颗粒度仍可补 |
| `acc_naura` | 北方华创科技集团股份有限公司 | 北方华创 | 先进制造 | 半导体装备 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高技术装备和复杂经营协同属性明确，可作为技术型制造补充标尺。 | 第四至第六批关键账户强核验 | 业务条线颗粒度仍可补 |
| `acc_shokz` | 深圳市韶音科技有限公司 | 韶音 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1 | 全球消费电子品牌与海外市场特征明确，可作为品牌出海补充标尺。 | 第七批关键账户强核验 | 区域经营颗粒度仍可补 |
| `acc_cfmoto` | 浙江春风动力股份有限公司 | 春风动力 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L2 | B | 乐其 SmallRig | 海外品牌经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 海外渠道与品牌经营特征明显，可作为品牌出海补充标尺。 | 第七批关键账户强核验 | 平台经营颗粒度仍可补 |
| `acc_dsbj` | 苏州东山精密制造股份有限公司 | 东山精密 | 先进制造 | 消费电子制造 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多基地制造与全球客户协同明确，可作为多工厂制造补充标尺。 | 第七批关键账户强核验 | 事业部颗粒度仍可补 |
| `acc_sanhua` | 浙江三花智能控制股份有限公司 | 三花智控 | 先进制造 | 控制部件制造 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 热管理与控制部件业务复杂度高，可作为技术型制造补充标尺。 | 第七批关键账户强核验 | 业务条线颗粒度仍可补 |
| `acc_tuopu` | 宁波拓普集团股份有限公司 | 拓普集团 | 先进制造 | 汽车零部件 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 多工厂计划协同与经营透明化 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多基地制造和全球协同明显，可作为多工厂制造补充标尺。 | 第七批关键账户强核验 | 工厂颗粒度仍可补 |
| `acc_yonghui` | 永辉超市股份有限公司 | 永辉超市 | 零售消费 | 商超便利 | 连锁零售 | retail_multi_store | L2 | B | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1 | 全国商超网络和总部管理半径明显，可作为多门店零售补充标尺。 | 第八至第九批关键账户强核验 | 直营网/合作经营结构仍可补 |
| `acc_bosideng` | 波司登国际控股有限公司 | 波司登 | 零售消费 | 鞋服零售 | 品牌零售 | retail_multi_store | L2 | B | 鲜丰水果,来伊份,博士眼镜 | 鞋服零售经营分析 | ka_case_xianfeng_retail_v1 | 全国零售网络与品牌服饰经营特征明确，可作为多门店零售补充标尺。 | 第八至第九批关键账户强核验 | 中国主体映射与直营网结构仍可补 |
| `acc_wolong` | 卧龙电气驱动集团股份有限公司 | 卧龙电驱 | 先进制造 | 电驱制造 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多基地制造与全球经营明确，可作为多工厂制造补充标尺。 | 第八至第九批关键账户强核验 | 事业部颗粒度仍可补 |
| `acc_btl` | 芜湖伯特利汽车安全系统股份有限公司 | 伯特利 | 先进制造 | 汽车零部件 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 汽车零部件与复杂客户协同特征明显，可作为技术型制造补充标尺。 | 第八至第九批关键账户强核验 | 全球经营颗粒度仍可补 |
| `acc_zhongji` | 中际旭创股份有限公司 | 中际旭创 | 先进制造 | 光通信制造 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 光模块制造和全球客户协同特征明确，可作为技术型制造补充标尺。 | 第八至第九批关键账户强核验 | 事业部颗粒度仍可补 |
| `acc_xtep` | 特步（中国）有限公司 | 特步 | 零售消费 | 鞋服零售 | 品牌零售 | retail_multi_store | L2 | B | 鲜丰水果,来伊份,博士眼镜 | 鞋服零售经营分析 | ka_case_xianfeng_retail_v1 | 全国零售网络和品牌矩阵明确，可作为多门店零售补充标尺。 | 第十至第十一批关键账户强核验 | 直营网/经销结构仍可补 |
| `acc_threesquirrels` | 三只松鼠股份有限公司 | 三只松鼠 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L2 | A | 自然堂,君乐宝,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 多 SKU 和全渠道经营特征明确，可作为高 SKU 品牌消费品补充标尺。 | 第十至第十一批关键账户强核验 | 渠道与库存颗粒度仍可补 |
| `acc_huali` | 华利实业集团股份有限公司 | 华利集团 | 跨境电商 | 跨境经营 | 跨境经营 | cbec_supply_chain_complex | L2 | B | 乐其 SmallRig | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 全球鞋履制造与复杂海外客户协同明确，可作为复杂跨境经营补充标尺。 | 第十至第十一批关键账户强核验 | 平台经营颗粒度仍可补 |
| `acc_sany` | 三一重工股份有限公司 | 三一重工 | 先进制造 | 工程机械 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多基地制造和全球经营明显，可作为多工厂制造补充标尺。 | 第十至第十一批关键账户强核验 | 工厂布局与事业部颗粒度仍可补 |
| `acc_desay` | 惠州市德赛西威汽车电子股份有限公司 | 德赛西威 | 先进制造 | 汽车电子 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 汽车电子和全球客户协同明显，可作为技术型制造补充标尺。 | 第十至第十一批关键账户强核验 | 业务条线颗粒度仍可补 |
| `acc_zhouheiya` | 周黑鸭国际控股有限公司 | 周黑鸭 | 零售消费 | 连锁食品零售 | 连锁零售 | retail_multi_store | L2 | B | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1 | 连锁网络和区域经营特征明确，可作为多门店零售补充标尺。 | 第十一至第十二批关键账户强核验 | 中国经营主体和直营网结构仍可补 |
| `acc_mengtianhome` | 梦天家居集团股份有限公司 | 梦天家居 | 跨境电商 | 家居出海 | 跨境经营 | cbec_supply_chain_complex | L2 | B | 乐其 SmallRig | 供应链复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居产品海外经营与供应链协同特征明确，可作为跨境经营补充标尺。 | 第十一至第十二批关键账户强核验 | 海外客户结构和品牌边界仍可补 |
| `acc_siasun` | 沈阳新松机器人自动化股份有限公司 | 机器人股份 | 先进制造 | 自动化装备 | 多工厂制造 | mfg_multi_factory_group | L2 | B | 零跑汽车,昊志机电类案例 | 多工厂经营驾驶舱 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化装备和多业务协同明确，可作为多工厂制造补充标尺。 | 第十一至第十二批关键账户强核验 | 制造基地与业务线颗粒度仍可补 |
| `acc_timeselectric` | 株洲中车时代电气股份有限公司 | 时代电气 | 先进制造 | 高技术电气制造 | 技术型制造 | mfg_rnd_sales_complex | L2 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 轨交电气与高技术制造协同明确，可作为技术型制造补充标尺。 | 第十一至第十二批关键账户强核验 | 全球经营与业务条线颗粒度仍可补 |

## 6. L3 中高可信补充样本

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_mgstationery` | 上海晨光文具股份有限公司 | 晨光文具 | 零售消费 | 文具零售 | 品牌消费品 | retail_high_sku_brand | L3 | B | 自然堂,君乐宝,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 品类和渠道复杂度成立，可作为高 SKU 品牌消费品次级样本。 | 第二批扩展候选池 v0.2 首轮核验版 | 渠道与库存颗粒度仍可补 |
| `acc_ugreen` | 深圳市绿联科技股份有限公司 | 绿联科技 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L3 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 品牌出海方向成立，可作为跨境品牌出海次级样本。 | 第二批扩展候选池 v0.3 第二轮核验版 | 海外平台与组织颗粒度仍可补 |
| `acc_biemlfdlkk` | 比音勒芬服饰股份有限公司 | 比音勒芬 | 零售消费 | 鞋服零售 | 品牌零售 | retail_multi_store | L3 | B | 鲜丰水果,来伊份,博士眼镜 | 鞋服零售经营分析 | ka_case_xianfeng_retail_v1 | 零售网络和品牌服饰经营成立，可作为多门店零售次级样本。 | 第二批扩展候选池 v0.4 第三轮核验版 | 区域和组织颗粒度仍可补 |
| `acc_hangke` | 浙江杭可科技股份有限公司 | 杭可科技 | 先进制造 | 装备制造 | 技术型制造 | mfg_rnd_sales_complex | L3 | B | 零跑汽车,昊志机电类案例 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 新能源装备与海外布局明确，可作为先进制造次级样本。 | 第二批扩展候选池 v0.4 第三轮核验版 | 研产销协同颗粒度仍可补 |
| `acc_botanee` | 云南贝泰妮生物科技集团股份有限公司 | 贝泰妮 | 零售消费 | 美妆个护 | 品牌消费品 | retail_high_sku_brand | L3 | B | 自然堂,君乐宝,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 美妆个护和品牌消费品属性成立，可作为高 SKU 品牌消费品次级样本。 | L5 放量候选首轮强核验 | 渠道与供应链颗粒度仍可补 |
| `acc_hymson` | 深圳市海目星激光科技集团股份有限公司 | 海目星 | 先进制造 | 装备制造 | 多工厂制造 | mfg_multi_factory_group | L3 | B | 零跑汽车,昊志机电类案例 | 多工厂经营驾驶舱 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 装备制造方向成立，可作为多工厂制造次级样本。 | L5 放量候选首轮强核验 | 工厂与业务线颗粒度仍可补 |
| `acc_dji` | 深圳市大疆创新科技有限公司 | DJI 大疆 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L3 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 全球品牌和海外经营特征明确，但仍偏边界高价值样本。 | L5 放量候选第二轮强核验 | 平台与主体结构仍可补 |
| `acc_dencare` | 重庆登康口腔护理用品股份有限公司 | 登康口腔 | 零售消费 | 个护消费品 | 品牌消费品 | retail_high_sku_brand | L3 | B | 自然堂,君乐宝,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 品牌消费品和渠道经营属性成立，可作为高 SKU 品牌消费品次级样本。 | L5 放量候选第二轮强核验 | 渠道与库存颗粒度仍可补 |
| `acc_hla` | 海澜之家集团股份有限公司 | 海澜之家 | 零售消费 | 鞋服零售 | 品牌零售 | retail_multi_store | L3 | A | 鲜丰水果,来伊份,博士眼镜 | 鞋服零售经营分析 | ka_case_xianfeng_retail_v1 | 大规模门店网络明确，可作为多门店零售次级样本。 | L4 中可信候选首轮强核验 | 加盟/直营网颗粒度仍可补 |
| `acc_easyhome_hkyb` | 华凯易佰科技股份有限公司 | 易佰网络 | 跨境电商 | 跨境卖家 | 多平台卖家 | cbec_supply_chain_complex | L3 | A | 乐其 SmallRig | 跨境经营分析与利润分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 多平台多店铺经营成立，可作为跨境经营型次级样本。 | L4 中可信候选首轮强核验 | 品牌化程度仍可补 |
| `acc_taotao` | 涛涛车业股份有限公司 | 涛涛车业 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L3 | B | 乐其 SmallRig | 跨境品牌出海分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 出行类品牌出海方向成立，可作为品牌出海次级样本。 | 第七批关键账户强核验 | 海外平台和品牌矩阵仍可补 |
| `acc_jiajia` | 家家悦集团股份有限公司 | 家家悦 | 零售消费 | 商超便利 | 连锁零售 | retail_multi_store | L3 | B | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 区域连锁商超属性明确，可作为多门店零售次级样本。 | 第八至第九批关键账户强核验 | 区域经营颗粒度仍可补 |
| `acc_chubang` | 中炬高新技术实业（集团）股份有限公司 | 厨邦 / 美味鲜 | 零售消费 | 调味品 | 品牌消费品 | retail_high_sku_brand | L3 | B | 自然堂,君乐宝,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 调味品品牌矩阵和全国渠道经营属性成立，可作为高 SKU 品牌消费品次级样本。 | 第十至第十一批关键账户强核验 | 供应链协同颗粒度仍可补 |
| `acc_yuanzu` | 元祖股份有限公司 | 元祖 | 零售消费 | 烘焙零售 | 连锁零售 | retail_multi_store | L3 | B | 鲜丰水果,来伊份,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 烘焙礼品零售网络与区域经营特征成立，可作为多门店零售次级样本。 | 第十一至第十二批关键账户强核验 | 门店网络颗粒度仍可补 |
| `acc_klg` | 开润股份有限公司 | 开润股份 | 跨境电商 | 品牌出海 | 品牌出海 | cbec_multi_platform_brand | L3 | B | 乐其 SmallRig | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 海外业务和消费品品牌经营成立，可作为品牌出海次级样本。 | 第十一至第十二批关键账户强核验 | 海外平台结构和品牌边界仍可补 |

## 7. 本轮迁移完成后的结构

当前 `external_target_account_pool_v2` 首版真实内容已覆盖：

- `59` 家高质量层账户
- `3` 条主线
- `7` 个 active 画像
- 可挂接 `12` 条知识资产

## 8. 下一步迁移顺序建议

建议下一步继续按以下顺序推进：

1. 优先迁 `L4-中可信候选`
2. 再批量迁 `L5-放量候选`
3. 每迁一轮，都同步补：
   - `account_evidence_log_v1`
   - `account_review_queue_v1`

## 9. 关联文档

- [external_target_account_pool_v2-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-字段模板-v1.md)
- [track_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/track_registry_v1-首版真实内容-v0.1.md)
- [persona_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/persona_registry_v1-首版真实内容-v0.1.md)
- [knowledge_asset_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/knowledge_asset_registry_v1-首版真实内容-v0.1.md)
- [外部目标客户池-v1.0-总池汇总视图-v0.7.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-总池汇总视图-v0.7.md)
