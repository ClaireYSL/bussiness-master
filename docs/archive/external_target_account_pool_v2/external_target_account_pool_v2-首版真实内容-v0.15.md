# `external_target_account_pool_v2` 首版真实内容 v0.15

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.14.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.14.md) 基础上，完成第十三轮 `L5` 结构化迁移。

## 2. 本轮迁移范围

### 已有基础

- `v0.14` 主表覆盖：`353`

### 本轮新增

- 第十三轮 `L5` 迁移：`20`
  - 零售消费：`10`
  - 跨境电商：`5`
  - 先进制造：`5`

### 本轮完成后

- 主表覆盖提升到 `373`

## 3. 第十三轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_dengkang` | 登康口腔护理用品股份有限公司 | 冷酸灵 | 零售消费 | 个护消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 贝泰妮,自然堂 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 个护品牌属性明确，适合作为高 SKU 品牌消费品候选。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与会员经营仍需补。 |
| `acc_bull` | 公牛集团股份有限公司 | 公牛 | 零售消费 | 消费电子 / 家居电工 | 品牌消费品 | retail_high_sku_brand | L5 | A | 小熊电器,飞科电器 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 消费电子与家居电工品牌属性强，商品与渠道分析空间明确。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_flyco` | 飞科电器股份有限公司 | 飞科 | 零售消费 | 小家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 小熊电器,公牛集团 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 小家电品牌属性明确，符合高 SKU 品牌消费品画像。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_bear` | 广东小熊电器股份有限公司 | 小熊电器 | 零售消费 | 小家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 飞科电器,公牛集团 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 小家电品牌经营属性明确，适合作为品牌消费品候选。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与会员经营仍需补。 |
| `acc_laiyifen_legal` | 上海来伊份股份有限公司 | 来伊份 | 零售消费 | 连锁零食零售 | 连锁零售 | retail_multi_store | L5 | A | 老乡鸡,绝味食品 | 总部经营透视 / 门店经营分析 | ka_case_laiyifen_replenishment_v1,ka_case_chatbi_frontline_v1 | 连锁零食零售与门店网络特征强，适合总部经营透视画像。 | 第十六批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_jinzi` | 金字火腿股份有限公司 | 金字火腿 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 仲景食品,安记食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 食品品牌与商品经营属性成立，适合作为品牌消费品候选。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_gaishi` | 盖世食品股份有限公司 | 盖世食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 味知香,千味央厨 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 食品品牌与预制食品属性明确，商品与渠道画像成立。 | 第十六批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_maiquer` | 麦趣尔集团股份有限公司 | 麦趣尔 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 光明乳业,三元食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 乳制品与烘焙消费品双属性成立。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_guifaxiang` | 天津桂发祥十八街麻花食品股份有限公司 | 桂发祥 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 五芳斋,良品铺子 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 传统食品品牌与零售经营属性并存。 | 第十六批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_yedao` | 海南椰岛（集团）股份有限公司 | 椰岛 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 李子园,欢乐家 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 饮品与健康食品品牌属性成立，适合作为品牌消费品候选。 | 第十六批放量候选池 v0.1 | 品牌经营边界、渠道结构与库存协同仍需补。 |
| `acc_longood` | 朗科智能电气股份有限公司 | 朗科智能 | 跨境电商 | 智能控制出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 杰美特,正裕工业 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 智能控制与出口属性并存，复杂跨境经营画像成立。 | 第十六批放量候选池 v0.1 | 海外客户结构、业务边界与经营颗粒度仍需补。 |
| `acc_mengtian_wood` | 浙江梦天木作家居有限公司 | 梦天木作 | 跨境电商 | 家居出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 匠心家居,慕容家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居产品与海外经营特征成立，适合作为复杂跨境经营候选。 | 第十六批放量候选池 v0.1 | 海外经营规模、品牌边界与渠道结构仍需补。 |
| `acc_enpack` | 英联股份有限公司 | 英联股份 | 跨境电商 | 包装材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 华瓷股份,英科再生 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 包装材料与海外经营属性成立，复杂跨境经营画像成立。 | 第十六批放量候选池 v0.1 | 海外客户结构、业务边界与经营颗粒度仍需补。 |
| `acc_yiyi` | 依依股份有限公司 | 依依股份 | 跨境电商 | 宠物用品出海 | 品牌出海 | cbec_brand_outbound | L5 | B | 匠心家居,哈尔斯 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 宠物护理用品与海外经营属性明确，品牌出海画像相邻。 | 第十六批放量候选池 v0.1 | 海外渠道、品牌矩阵与经营颗粒度仍需补。 |
| `acc_nbfd` | 宁波富达股份有限公司 | 宁波富达 | 跨境电商 | 家居/消费制造出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 浙江永强,凯迪股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居 / 消费制造与海外经营属性相邻，适合作为复杂跨境经营候选。 | 第十六批放量候选池 v0.1 | 海外经营边界、客户结构与业务颗粒度仍需补。 |
| `acc_efort` | 埃夫特智能装备股份有限公司 | 埃夫特 | 先进制造 | 工业机器人制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 新松机器人,拓斯达 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工业机器人与智能装备制造属性明确，多工厂画像相邻。 | 第十六批放量候选池 v0.1 | 工厂布局、业务条线与客户结构仍需补。 |
| `acc_maxwell` | 迈为股份有限公司 | 迈为股份 | 先进制造 | 新能源 / 泛半导体装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 先导智能,海目星 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 泛半导体与新能源装备制造协同属性成立。 | 第十六批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |
| `acc_neway_cnc` | 纽威数控装备（苏州）股份有限公司 | 纽威数控 | 先进制造 | 数控机床制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海天精工,亚威股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 数控机床与装备制造属性成立，多工厂画像相邻。 | 第十六批放量候选池 v0.1 | 工厂布局、事业部与区域经营仍需补。 |
| `acc_siasun` | 沈阳新松机器人自动化股份有限公司 | 机器人 | 先进制造 | 自动化装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 埃夫特,拓斯达 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工业机器人与自动化装备制造属性明确。 | 第十六批放量候选池 v0.1 | 工厂布局、业务条线与经营颗粒度仍需补。 |
| `acc_shandongweida` | 山东威达机械股份有限公司 | 山东威达 | 先进制造 | 机械制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海天精工,中信重工 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 机械制造与多业务协同特征明显，多工厂画像相邻。 | 第十六批放量候选池 v0.1 | 工厂布局、业务条线与经营颗粒度仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.14

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=280`
- 合计 `353`

### v0.15

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=300`
- 合计 `373`
