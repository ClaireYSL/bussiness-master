# `external_target_account_pool_v2` 首版真实内容 v0.6

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.5.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.5.md) 基础上，继续完成第四轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 与现有零售消费高质量样本最相邻的品牌消费品与连锁零售对象
2. 与现有跨境高质量样本最相邻的品牌出海与复杂跨境经营对象
3. 与现有先进制造高质量样本最相邻的电子制造、新能源与高技术制造对象

## 2. 本轮迁移范围

### 已有基础

- `v0.5` 主表覆盖：`152`

### 本轮新增

- 第四轮 `L5` 迁移：`30`
  - 零售消费：`10`
  - 跨境电商：`8`
  - 先进制造：`12`

### 本轮完成后

- 主表覆盖提升到 `182`

## 3. 第四轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_narwal` | 深圳市云鲸智能创新有限公司 | 云鲸 | 零售消费 | 智能清洁家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 石头科技,科沃斯 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 智能清洁消费品牌与产品矩阵成立，适合作为高 SKU 品牌消费品候选。 | 第四批放量候选池 v0.1 | 全渠道结构、库存协同与海外经营比例仍需补。 |
| `acc_dreame` | 追觅创新科技（苏州）有限公司 | 追觅 | 零售消费 | 智能家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 石头科技,科沃斯 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 智能家电品牌与 SKU 复杂度明显，符合高 SKU 品牌消费品画像。 | 第四批放量候选池 v0.1 | 中国经营主体、全渠道结构与库存协同仍需补。 |
| `acc_yatsen` | 广州逸仙电子商务有限公司 | 完美日记 / 逸仙电商 | 零售消费 | 美妆个护 | 品牌消费品 | retail_high_sku_brand | L5 | B | 花西子,自然堂 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 美妆品牌矩阵与渠道经营特征成立，适合高 SKU 品牌消费品画像。 | 第四批放量候选池 v0.1 | 主体与集团边界、品牌矩阵与渠道结构仍需补。 |
| `acc_gubei` | 乖宝宠物食品集团股份有限公司 | 麦富迪 | 零售消费 | 宠物消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 中宠股份,佩蒂股份 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 宠物消费品品牌与渠道经营复杂度较高，符合高 SKU 品牌消费品画像。 | 第四批放量候选池 v0.1 | 渠道结构、品牌矩阵与供应链协同仍需补。 |
| `acc_bloomage` | 华熙生物科技股份有限公司 | 华熙生物 | 零售消费 | 美妆个护 | 品牌消费品 | retail_high_sku_brand | L5 | B | 福瑞达,自然堂 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 美妆与功能护肤品牌矩阵成立，适合作为高 SKU 品牌消费品候选。 | 第五批放量候选池 v0.1 | 品牌矩阵、渠道结构与供应链协同仍需补。 |
| `acc_saintangelo` | 报喜鸟控股股份有限公司 | 报喜鸟 | 零售消费 | 服饰鞋帽 | 连锁零售 | retail_multi_store | L5 | B | 海澜之家,森马 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 男装品牌零售与门店网络特征明确，符合多门店连锁零售画像。 | 第五批放量候选池 v0.1 | 门店网络、直营网与加盟结构仍需补。 |
| `acc_redstar` | 红星美凯龙家居集团股份有限公司 | 红星美凯龙 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | A | 居然之家,顾家家居 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居零售平台与商场网络特征强，适合作为多门店零售候选。 | 第五批放量候选池 v0.1 | 商场层级、区域经营与平台经营边界仍需补。 |
| `acc_darryring` | 迪阿股份有限公司 | DR | 零售消费 | 珠宝零售 | 连锁零售 | retail_multi_store | L5 | B | 周大生,潮宏基 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 珠宝品牌零售与终端网络特征成立，符合多门店连锁零售画像。 | 第六批放量候选池 v0.1 | 门店网络、直营网与区域结构仍需补。 |
| `acc_candr` | 中顺洁柔纸业股份有限公司 | 洁柔 | 零售消费 | 日化用品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 拉芳家化,润本 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 日用品消费品牌与渠道经营特征成立，符合高 SKU 品牌消费品画像。 | 第六批放量候选池 v0.1 | 渠道结构、品牌矩阵与供应链协同仍需补。 |
| `acc_runben` | 润本生物技术股份有限公司 | 润本 | 零售消费 | 个护消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 拉芳家化,华熙生物 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 个护消费品牌画像成立，SKU 与渠道经营分析空间明显。 | 第六批放量候选池 v0.1 | SKU 结构、渠道矩阵与供应链颗粒度仍需补。 |
| `acc_laifen` | 深圳市徕芬电子科技有限公司 | 徕芬 | 跨境电商 | 消费电子出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 安克创新,韶音科技 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 消费电子品牌出海属性明确，和安克、正浩、影石画像相邻。 | 第四批放量候选池 v0.1 | 海外平台结构、经营规模与组织颗粒度仍需补。 |
| `acc_sailvan` | 深圳市赛维网络科技有限公司 | 赛维网络 | 跨境电商 | 跨境综合经营 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 赛维时代,华凯易佰 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 跨境经营属性较强，可沿供应链复杂型跨境画像纳入。 | 第四批放量候选池 v0.1 | 经营规模、组织结构与主体有效性仍需补。 |
| `acc_santai` | 深圳市三态电子商务股份有限公司 | 三态股份 | 跨境电商 | 跨境综合经营 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 赛维时代,华凯易佰 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 跨境电商经营属性明确，符合复杂跨境经营画像。 | 第五批放量候选池 v0.1 | 品牌化程度、业务结构与经营复杂度仍需补。 |
| `acc_loctek` | 乐歌人体工学科技股份有限公司 | 乐歌 | 跨境电商 | 家居出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 致欧家居,匠心家居 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 人体工学产品出海属性成立，海外经营特征明显。 | 第五批放量候选池 v0.1 | 海外平台、渠道结构与品牌矩阵仍需补。 |
| `acc_aukey` | 深圳市傲基创新科技股份有限公司 | 傲基 | 跨境电商 | 跨境综合经营 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 赛维时代,华凯易佰 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 跨境经营与供应链协同属性较强，符合复杂跨境经营画像。 | 第五批放量候选池 v0.1 | 当前主体有效性、经营阶段与品牌结构仍需补。 |
| `acc_70mai` | 深圳市七十迈数字科技有限公司 | 70迈 | 跨境电商 | 消费电子出海 | 品牌出海 | cbec_multi_platform_brand | L5 | A | 安克创新,正浩创新 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 消费电子品牌出海属性强，和安克、正浩、影石画像相邻。 | 第六批放量候选池 v0.1 | 经营主体、海外平台与品牌矩阵仍需补。 |
| `acc_haers` | 浙江哈尔斯真空器皿股份有限公司 | 哈尔斯 | 跨境电商 | 消费品出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 嘉益股份,致欧家居 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 消费品出口与品牌经营属性成立，符合品牌出海画像。 | 第六批放量候选池 v0.1 | 海外渠道、品牌矩阵与平台结构仍需补。 |
| `acc_henglin` | 恒林家居股份有限公司 | 恒林股份 | 跨境电商 | 家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 建霖家居,致欧家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居出海与海外经营属性成立，适合作为复杂跨境经营候选。 | 第六批放量候选池 v0.1 | 海外占比、渠道颗粒度与品牌边界仍需补。 |
| `acc_leadtrend` | 领益智造股份有限公司 | 领益智造 | 先进制造 | 电子制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 立讯精密,东山精密 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 电子制造与多业务协同明显，符合多工厂制造画像。 | 第五批放量候选池 v0.1 | 组织结构、事业部与全球经营颗粒度仍需补。 |
| `acc_zhending` | 鹏鼎控股（深圳）股份有限公司 | 鹏鼎控股 | 先进制造 | 电子制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 立讯精密,东山精密 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 电子制造与全球经营属性强，符合多工厂制造画像。 | 第五批放量候选池 v0.1 | 多工厂与业务协同颗粒度仍需补。 |
| `acc_huagong` | 华工科技产业股份有限公司 | 华工科技 | 先进制造 | 高端装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中控技术,汇川技术 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 激光与高端制造属性成立，符合技术型制造画像。 | 第五批放量候选池 v0.1 | 业务协同结构与制造颗粒度仍需补。 |
| `acc_kaili` | 深圳开立生物医疗科技股份有限公司 | 开立医疗 | 先进制造 | 医疗设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 迈瑞医疗,联影医疗 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 医疗设备制造与研产销协同属性明确，符合技术型制造画像。 | 第五批放量候选池 v0.1 | 研产销协同链路与全球经营颗粒度仍需补。 |
| `acc_xinshida` | 上海新时达电气股份有限公司 | 新时达 | 先进制造 | 工业自动化 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 汇川技术,埃斯顿 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工业自动化与多业务协同成立，可沿多工厂制造画像纳入。 | 第五批放量候选池 v0.1 | 多工厂和经营复杂度仍需补。 |
| `acc_saiteng` | 苏州赛腾精密电子股份有限公司 | 赛腾股份 | 先进制造 | 自动化装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 博众精工,拓斯达 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 装备制造与消费电子链路相邻，符合多工厂制造画像。 | 第五批放量候选池 v0.1 | 多工厂和客户结构仍需补。 |
| `acc_eve` | 惠州亿纬锂能股份有限公司 | 亿纬锂能 | 先进制造 | 新能源制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 宁德时代,欣旺达 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多工厂与新能源制造属性明显，符合多工厂制造画像。 | 第六批放量候选池 v0.1 | 全球经营、业务协同与事业部颗粒度仍需补。 |
| `acc_semcorp` | 云南恩捷新材料股份有限公司 | 恩捷股份 | 先进制造 | 新材料制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 当升科技,容百科技 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 新材料制造与下游产业协同特征明显，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 经营链路与组织复杂度仍需补。 |
| `acc_amec` | 中微半导体设备（上海）股份有限公司 | 中微公司 | 先进制造 | 半导体设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | A | 北方华创,拓荆科技 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高端半导体设备制造画像成立，适合作为技术型制造候选。 | 第六批放量候选池 v0.1 | 经营协同与业务颗粒度仍需补。 |
| `acc_hwatsing` | 华海清科股份有限公司 | 华海清科 | 先进制造 | 半导体设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 北方华创,中微公司 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高技术装备制造属性成立，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 研产销协同颗粒度仍需补。 |
| `acc_precision` | 武汉精测电子集团股份有限公司 | 精测电子 | 先进制造 | 检测设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中控技术,华工科技 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 检测设备制造与多业务协同成立，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 业务协同与组织复杂度仍需补。 |
| `acc_everwin` | 深圳市长盈精密技术股份有限公司 | 长盈精密 | 先进制造 | 精密制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 立讯精密,蓝思科技 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 精密制造与消费电子制造协同属性强，符合多工厂制造画像。 | 第六批放量候选池 v0.1 | 多工厂与全球经营颗粒度仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.5

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=79`
- 合计 `152`

### v0.6

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=109`
- 合计 `182`

## 5. 下一步建议

1. 为本轮新增 `30` 家账户补第一条结构化证据
2. 优先强核验：
   - 红星美凯龙
   - 70迈
   - 领益智造
   - 亿纬锂能
   - 中微公司
3. 后续第五轮 `L5` 迁移可继续优先：
   - 美妆个护与家纺家居品牌消费品
   - 家居 / 消费电子品牌出海
   - 半导体设备、新材料与精密制造相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.5.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.5.md)
- [外部目标客户池-v1.0-第四批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第五批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第五批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第六批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第六批放量候选池-v0.1.md)
