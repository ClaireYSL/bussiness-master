# `external_target_account_pool_v2` 首版真实内容 v0.4

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.3.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.3.md) 基础上，继续完成第二轮 `L5` 放量候选的结构化迁移。

本轮继续遵循：

1. 不一次性迁完全部 `L5`
2. 继续优先迁移画像边界稳定、与现有高质量层相邻度高的一批

## 2. 本轮迁移范围

### 已有基础

- `v0.3` 主表覆盖：`103`

### 本轮新增

- 第二轮 `L5` 迁移：`24`
  - 零售消费：`8`
  - 跨境电商：`8`
  - 先进制造：`8`

### 本轮完成后

- 主表覆盖提升到 `127`

## 3. 第二轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_guangzhourestaurant` | 广州酒家集团股份有限公司 | 广州酒家 | 零售消费 | 餐饮零售 | 连锁餐饮 | retail_chain_fnb | L5 | B | 老乡鸡,周黑鸭 | 连锁门店经营透视与一线动作闭环 | ka_case_chatbi_frontline_v1 | 餐饮连锁与食品品牌双属性并存，可沿连锁餐饮画像纳入，适合作为餐饮零售候选。 | 第七批放量候选池 v0.1 | 餐饮门店网络与食品业务边界仍需补。 |
| `acc_babi` | 巴比食品集团有限公司 | 巴比食品 | 零售消费 | 连锁餐饮 | 连锁餐饮 | retail_chain_fnb | L5 | B | 老乡鸡,茶百道 | 连锁餐饮经营分析 | ka_case_chatbi_frontline_v1 | 餐饮连锁与食品零售双属性成立，可沿连锁餐饮画像纳入。 | 第八批放量候选池 v0.1 | 门店网络、加盟结构与食品业务边界仍需补。 |
| `acc_quanjude` | 中国全聚德（集团）股份有限公司 | 全聚德 | 零售消费 | 连锁餐饮 | 连锁餐饮 | retail_chain_fnb | L5 | B | 老乡鸡,周黑鸭 | 连锁餐饮经营分析 | ka_case_chatbi_frontline_v1 | 餐饮连锁品牌属性明确，可沿连锁餐饮画像纳入。 | 第十批放量候选池 v0.1 | 门店网络、直营 / 加盟结构、食品业务边界仍需补。 |
| `acc_ziyan` | 紫燕食品股份有限公司 | 紫燕百味鸡 | 零售消费 | 连锁食品零售 | 连锁零售 | retail_multi_store | L5 | B | 周黑鸭,来伊份 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 卤味连锁零售属性明确，可沿多门店零售画像纳入。 | 第十二批放量候选池 v0.1 | 门店网络、直营网 / 加盟结构、区域经营仍需补。 |
| `acc_hiro` | 海融科技股份有限公司 | 海融科技 | 零售消费 | 食品原料消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 良品铺子,中炬高新 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 烘焙原料与消费品经营属性成立，适合作为高 SKU 品牌消费品候选。 | 第十二批放量候选池 v0.1 | 品牌经营边界、渠道结构、供应链协同仍需补。 |
| `acc_wufangzhai` | 五芳斋实业股份有限公司 | 五芳斋 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 来伊份,良品铺子 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 食品品牌与零售经营双属性并存，适合商品与渠道分析。 | 第十二批放量候选池 v0.1 | 渠道结构、门店网络与库存颗粒度仍需补。 |
| `acc_fiyta` | 飞亚达精密科技股份有限公司 | 飞亚达 | 零售消费 | 品牌零售 | 连锁零售 | retail_multi_store | L5 | B | 周大生,潮宏基 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 手表品牌零售与直营网点特征成立，符合多门店连锁零售画像。 | 第十二批放量候选池 v0.1 | 品牌经营边界、门店网络与区域结构仍需补。 |
| `acc_sanjiang` | 三江购物俱乐部股份有限公司 | 三江购物 | 零售消费 | 商超便利 | 连锁零售 | retail_multi_store | L5 | B | 永辉超市,家家悦 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 区域连锁商超特征成立，适合作为多门店零售候选。 | 第九批放量候选池 v0.1 | 门店网络、区域经营与组织结构仍需补。 |
| `acc_dechangmotor` | 宁波德昌电机股份有限公司 | 德昌电机 | 跨境电商 | 制造出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 吉宏股份,华利集团 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 出口制造与海外经营特征明显，适合跨境经营型画像。 | 第七批放量候选池 v0.1 | 品牌化程度、海外经营规模、平台颗粒度仍需补。 |
| `acc_runner` | 建霖家居股份有限公司 | 建霖家居 | 跨境电商 | 家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 致欧家居,恒林股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居卫浴出口与海外经营特征明显，适合作为复杂跨境经营候选。 | 第七批放量候选池 v0.1 | 海外客户结构、品牌经营边界仍需补。 |
| `acc_patio` | 浙江正特股份有限公司 | 正特股份 | 跨境电商 | 户外家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 慕容家居,永艺家具 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 户外休闲用品出口与海外经营特征明显，适合作为跨境经营型候选。 | 第八批放量候选池 v0.1 | 品牌化程度、海外渠道结构、客户颗粒度仍需补。 |
| `acc_yuma` | 玉马遮阳科技股份有限公司 | 玉马遮阳 | 跨境电商 | 材料出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 赛特新材,海利得 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 功能材料与海外经营属性成立，可作为复杂跨境经营候选。 | 第八批放量候选池 v0.1 | 海外客户结构、业务边界仍需补。 |
| `acc_shengtai` | 浙江盛泰服装集团股份有限公司 | 盛泰集团 | 跨境电商 | 服装出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 华利集团,鲁泰纺织 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 服装制造与海外经营属性明显，适合作为跨境经营型候选。 | 第十批放量候选池 v0.1 | 海外客户结构、品牌经营边界仍需补。 |
| `acc_sunsbike` | 三柏硕健康科技股份有限公司 | 三柏硕 | 跨境电商 | 运动器材出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 英派斯,春风动力 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 健身器材与品牌出海属性相邻，符合品牌出海画像。 | 第十批放量候选池 v0.1 | 海外平台结构、品牌矩阵与区域经营仍需补。 |
| `acc_hengansecurity` | 江苏恒辉安防股份有限公司 | 恒辉安防 | 跨境电商 | 防护用品出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 康隆达,英科医疗 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 防护用品出口与海外经营特征明确，适合作为复杂跨境经营候选。 | 第十批放量候选池 v0.1 | 海外经营规模、品牌边界仍需补。 |
| `acc_dechangshares` | 德昌股份有限公司 | 德昌股份 | 跨境电商 | 制造出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 德昌电机,富佳股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 制造出口与海外经营属性明确，适合作为复杂跨境经营候选。 | 第十批放量候选池 v0.1 | 海外经营规模、品牌边界与客户结构仍需补。 |
| `acc_zhonglian` | 中联重科股份有限公司 | 中联重科 | 先进制造 | 工程机械 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 三一重工,徐工机械 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工程机械与多基地制造、全球经营特征明显，符合多工厂制造画像。 | 第九批放量候选池 v0.1 | 工厂布局、事业部与区域经营颗粒度仍需补。 |
| `acc_henglihyd` | 江苏恒立液压股份有限公司 | 恒立液压 | 先进制造 | 液压部件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 伯特利,三花智控 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 液压部件制造与全球客户协同属性明确，符合技术型制造画像。 | 第九批放量候选池 v0.1 | 业务条线、全球经营与客户结构仍需补。 |
| `acc_jiejia` | 深圳市捷佳伟创新能源装备股份有限公司 | 捷佳伟创 | 先进制造 | 光伏装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 晶盛机电,海目星 | 多工厂经营驾驶舱 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 光伏装备与复杂制造协同特征成立，符合多工厂制造画像。 | 第九批放量候选池 v0.1 | 工厂布局、业务条线与经营颗粒度仍需补。 |
| `acc_kedali` | 深圳市科达利实业股份有限公司 | 科达利 | 先进制造 | 新能源零部件 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 宁德时代,欣旺达 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 新能源零部件与多基地制造特征明显，符合多工厂制造画像。 | 第九批放量候选池 v0.1 | 工厂布局、事业部结构与全球经营仍需补。 |
| `acc_hongya` | 弘亚数控机械股份有限公司 | 弘亚数控 | 先进制造 | 数控装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 海天精工,时代电气 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 数控装备与技术型制造画像成立，适合作为技术型制造候选。 | 第十批放量候选池 v0.1 | 业务结构、客户协同与经营颗粒度仍需补。 |
| `acc_qinchuan` | 秦川机床工具集团股份公司 | 秦川机床 | 先进制造 | 高端机床 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海天精工,中信重工 | 多工厂经营驾驶舱 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 机床工具与多基地制造特征明确，符合多工厂制造画像。 | 第十批放量候选池 v0.1 | 制造基地、事业部结构与全球经营仍需补。 |
| `acc_haopeng` | 深圳市豪鹏科技股份有限公司 | 豪鹏科技 | 先进制造 | 电池制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 欣旺达,宁德时代 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 电池与电子制造协同属性成立，符合技术型制造画像。 | 第十批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |
| `acc_goldwind` | 金风科技股份有限公司 | 金风科技 | 先进制造 | 风电装备 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 三一重工,徐工机械 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 风电装备与全球制造协同属性强，符合多工厂制造画像。 | 第十二批放量候选池 v0.1 | 工厂布局、事业部与区域经营颗粒度仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.3

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(首轮迁移)=30`
- 合计 `103`

### v0.4

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=54`
- 合计 `127`

## 5. 下一步建议

1. 为本轮新增 `24` 家账户补第一条结构化证据
2. 优先强核验：
   - 广州酒家
   - 建霖家居
   - 中联重科
   - 恒立液压
   - 金风科技
3. 第三轮 `L5` 迁移可继续优先：
   - 零售中的商超便利 / 百货零售边界样本
   - 跨境中的材料出口与家居出海样本
   - 制造中的重工装备与新能源装备样本

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.3.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.3.md)
- [外部目标客户池-v1.0-第七批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第八批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第九批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十一批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十二批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md)
