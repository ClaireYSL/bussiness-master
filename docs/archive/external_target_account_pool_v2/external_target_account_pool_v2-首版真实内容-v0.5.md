# `external_target_account_pool_v2` 首版真实内容 v0.5

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.4.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.4.md) 基础上，继续完成第三轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 商超 / 百货等多门店零售画像相邻对象
2. 材料 / 纺织 / 家居等复杂跨境经营对象
3. 重工装备、自动化与高技术制造画像相邻对象

## 2. 本轮迁移范围

### 已有基础

- `v0.4` 主表覆盖：`127`

### 本轮新增

- 第三轮 `L5` 迁移：`25`
  - 零售消费：`8`
  - 跨境电商：`8`
  - 先进制造：`9`

### 本轮完成后

- 主表覆盖提升到 `152`

## 3. 第三轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_zhongbai` | 中百控股集团股份有限公司 | 中百集团 | 零售消费 | 商超便利 | 连锁零售 | retail_multi_store | L5 | B | 永辉超市,家家悦 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 商超网络与区域经营特征成立，适合总部经营透视画像。 | 第九批放量候选池 v0.1 | 门店网络、区域层级与直营网结构仍需补。 |
| `acc_eurasia` | 欧亚集团股份有限公司 | 欧亚集团 | 零售消费 | 百货零售 | 连锁零售 | retail_multi_store | L5 | B | 王府井,居然之家 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 百货零售与区域经营网络成立，符合多门店零售画像。 | 第九批放量候选池 v0.1 | 业态结构、商场层级与区域经营颗粒度仍需补。 |
| `acc_bbg` | 步步高商业连锁股份有限公司 | 步步高 | 零售消费 | 商超便利 | 连锁零售 | retail_multi_store | L5 | B | 永辉超市,中百集团 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 连锁商超与区域经营特征明确，符合多门店零售画像。 | 第九批放量候选池 v0.1 | 门店网络、区域层级和直营网结构仍需补。 |
| `acc_hqls` | 红旗连锁股份有限公司 | 红旗连锁 | 零售消费 | 商超便利 | 连锁零售 | retail_multi_store | L5 | B | 永辉超市,家家悦 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 便利零售与门店网络特征明显，符合多门店零售画像。 | 第九批放量候选池 v0.1 | 门店网络、区域经营与直营网结构仍需补。 |
| `acc_lolo` | 承德露露股份公司 | 承德露露 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 中炬高新,三只松鼠 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 饮品品牌属性明确，适合商品与渠道分析，符合高 SKU 品牌消费品画像。 | 第十一批放量候选池 v0.1 | 渠道结构、库存协同、品牌矩阵仍需补。 |
| `acc_yiming` | 浙江一鸣食品股份有限公司 | 一鸣食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 来伊份,五芳斋 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 乳品与烘焙品牌双属性并存，SKU 与渠道经营特征明显。 | 第十一批放量候选池 v0.1 | 渠道结构、品牌矩阵、供应链颗粒度仍需补。 |
| `acc_ligao` | 广州立高食品股份有限公司 | 立高食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 海融科技,安井食品 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 烘焙食品品牌与渠道经营特征成立，符合高 SKU 品牌消费品画像。 | 第十一批放量候选池 v0.1 | 渠道结构、品牌矩阵与供应链协同仍需补。 |
| `acc_haixinfood` | 海欣食品股份有限公司 | 海欣食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 良品铺子,安井食品 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 速冻食品品牌属性明确，适合作为商品与渠道协同分析候选。 | 第十一批放量候选池 v0.1 | 渠道结构、库存与供应链颗粒度仍需补。 |
| `acc_furi` | 孚日集团股份有限公司 | 孚日集团 | 跨境电商 | 家纺出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 盛泰集团,建霖家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家纺出口与海外经营属性明确，适合作为复杂跨境经营候选。 | 第九批放量候选池 v0.1 | 品牌化程度、海外客户结构、平台颗粒度仍需补。 |
| `acc_luthai` | 鲁泰纺织股份有限公司 | 鲁泰纺织 | 跨境电商 | 纺织出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 盛泰集团,华利集团 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 纺织服装出口和全球经营特征成立，符合复杂跨境经营画像。 | 第九批放量候选池 v0.1 | 海外客户结构、品牌经营边界仍需补。 |
| `acc_jiansheng` | 健盛集团股份有限公司 | 健盛集团 | 跨境电商 | 纺织出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 华利集团,鲁泰纺织 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 纺织服饰出口与海外经营属性明显，符合复杂跨境经营画像。 | 第九批放量候选池 v0.1 | 品牌化程度、海外经营规模仍需补。 |
| `acc_haixiang` | 海象新材料股份有限公司 | 海象新材 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 赛特新材,玉马遮阳 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 新材料出口与海外经营特征成立，符合复杂跨境经营画像。 | 第九批放量候选池 v0.1 | 海外客户结构、业务边界仍需补。 |
| `acc_kanglongda` | 康隆达特种防护科技集团股份有限公司 | 康隆达 | 跨境电商 | 防护用品出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 恒辉安防,英科医疗 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 防护用品与海外经营属性明确，适合作为复杂跨境经营候选。 | 第九批放量候选池 v0.1 | 海外渠道、品牌经营边界、客户结构仍需补。 |
| `acc_suncha` | 双枪科技股份有限公司 | 双枪科技 | 跨境电商 | 家居日用品出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 建霖家居,恒林股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居日用品与出口特征明显，适合作为复杂跨境经营候选。 | 第九批放量候选池 v0.1 | 海外经营规模、品牌矩阵与平台结构仍需补。 |
| `acc_taipeng` | 泰鹏智能家居股份有限公司 | 泰鹏智能 | 跨境电商 | 智能家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 建霖家居,巨星科技 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 智能家居与出口经营属性成立，适合作为复杂跨境经营候选。 | 第九批放量候选池 v0.1 | 海外客户结构、品牌化程度仍需补。 |
| `acc_xinghua` | 星华新材股份有限公司 | 星华新材 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 海利得,赛特新材 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 新材料出口与海外经营属性明确，符合复杂跨境经营画像。 | 第九批放量候选池 v0.1 | 海外客户结构、品牌化程度仍需补。 |
| `acc_jereh` | 杰瑞石油服务集团股份有限公司 | 杰瑞股份 | 先进制造 | 装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 中信重工,海天精工 | 集团经营驾驶舱与计划协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 装备制造与多业务协同特征明显，符合多工厂制造画像。 | 第九批放量候选池 v0.1 | 制造基地、事业部结构与全球经营仍需补。 |
| `acc_boshi` | 哈尔滨博实自动化股份有限公司 | 博实股份 | 先进制造 | 自动化装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中控技术,机器人股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化装备与复杂客户协同特征成立，符合技术型制造画像。 | 第九批放量候选池 v0.1 | 业务条线、经营颗粒度与客户结构仍需补。 |
| `acc_weichuang` | 苏州伟创电气科技股份有限公司 | 伟创电气 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中控技术,汇川技术 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化控制产品技术型制造画像成立。 | 第九批放量候选池 v0.1 | 业务结构、全球经营与客户协同仍需补。 |
| `acc_liugong` | 广西柳工机械股份有限公司 | 柳工 | 先进制造 | 工程机械 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 三一重工,徐工机械 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工程机械与全球经营特征成立，符合多工厂制造画像。 | 第九批放量候选池 v0.1 | 制造基地、事业部与全球经营颗粒度仍需补。 |
| `acc_aidi` | 烟台艾迪精密机械股份有限公司 | 艾迪精密 | 先进制造 | 液压部件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 恒立液压,伯特利 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 液压与工程机械部件制造画像相邻，符合技术型制造画像。 | 第九批放量候选池 v0.1 | 业务结构、全球经营与客户协同仍需补。 |
| `acc_softcontrol` | 软控股份有限公司 | 软控股份 | 先进制造 | 装备制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 海天精工,中信重工 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 装备制造与工业系统协同属性成立，符合技术型制造画像。 | 第十一批放量候选池 v0.1 | 业务条线、客户协同与经营颗粒度仍需补。 |
| `acc_dalianheavy` | 大连华锐重工集团股份有限公司 | 大连重工 | 先进制造 | 重工装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 中信重工,金风科技 | 集团经营驾驶舱与计划协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 重工装备与多基地制造特征成立，符合多工厂制造画像。 | 第十一批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |
| `acc_lanjian` | 兰剑智能科技股份有限公司 | 兰剑智能 | 先进制造 | 智能物流装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 江苏北人,机器人股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 智能物流装备与技术型制造属性成立，符合技术型制造画像。 | 第十一批放量候选池 v0.1 | 客户结构、业务条线与经营颗粒度仍需补。 |
| `acc_jsbr` | 江苏北人智能制造科技股份有限公司 | 江苏北人 | 先进制造 | 智能制造装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 兰剑智能,机器人股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 智能制造装备与复杂客户协同特征成立，符合技术型制造画像。 | 第十一批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.4

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=54`
- 合计 `127`

### v0.5

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=79`
- 合计 `152`

## 5. 下一步建议

1. 为本轮新增 `25` 家账户补第一条结构化证据
2. 优先强核验：
   - 中百集团
   - 建盛集团 / 鲁泰纺织二选一
   - 杰瑞股份
   - 软控股份
   - 兰剑智能
3. 后续第四轮 `L5` 迁移可继续优先：
   - 零售中的饮品 / 烘焙品牌消费品
   - 跨境中的材料与防护用品出口画像
   - 制造中的机床、电气与新能源材料相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.4.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.4.md)
- [外部目标客户池-v1.0-第九批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十一批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md)
