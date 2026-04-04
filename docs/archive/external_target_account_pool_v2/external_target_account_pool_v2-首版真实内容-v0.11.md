# `external_target_account_pool_v2` 首版真实内容 v0.11

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.10.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.10.md) 基础上，继续完成第九轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 食品饮料与乳品烘焙等高 SKU 品牌消费品
2. 家居 / 宠物用品 / 家化与产业品出口属性较清晰的复杂跨境经营对象
3. 机床装备、自动化控制、风电链条与多工厂制造相邻对象

## 2. 本轮迁移范围

### 已有基础

- `v0.10` 主表覆盖：`273`

### 本轮新增

- 第九轮 `L5` 迁移：`20`
  - 零售消费：`8`
  - 跨境电商：`5`
  - 先进制造：`7`

### 本轮完成后

- 主表覆盖提升到 `293`

## 3. 第九轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_zuming` | 祖名豆制品股份有限公司 | 祖名 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 仲景食品,克明食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 食品品牌与多品类经营特征明确，符合高 SKU 品牌消费品画像。 | 第九批放量候选池 v0.1 | 渠道结构、供应链与库存颗粒度仍需补。 |
| `acc_huanlejia` | 欢乐家食品集团股份有限公司 | 欢乐家 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 李子园,仲景食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 饮料与罐头品牌画像成立，适合作为高 SKU 品牌消费品候选。 | 第九批放量候选池 v0.1 | 品牌矩阵、渠道颗粒度与库存协同仍需补。 |
| `acc_liziyuan` | 李子园食品股份有限公司 | 李子园 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 一鸣食品,妙可蓝多 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 饮品品牌属性明确，符合高 SKU 品牌消费品画像。 | 第九批放量候选池 v0.1 | 渠道结构、品牌矩阵与供应链颗粒度仍需补。 |
| `acc_anji` | 安记食品股份有限公司 | 安记食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 仲景食品,天味食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 调味品品牌属性明确，SKU 与渠道经营特征明显。 | 第十批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_richen` | 日辰食品集团股份有限公司 | 日辰食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 仲景食品,南侨食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 复合调味料与食品品牌属性成立。 | 第十批放量候选池 v0.1 | 渠道结构、品牌矩阵与供应链协同仍需补。 |
| `acc_seamild` | 西麦食品股份有限公司 | 西麦 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 桂发祥,仲景食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 谷物早餐品牌属性明确，适合作为高 SKU 品牌消费品候选。 | 第十批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_tianwei` | 天味食品股份有限公司 | 天味食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 仲景食品,安记食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 调味品品牌与多 SKU 经营特征成立。 | 第十批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_pengwei` | 品渥食品股份有限公司 | 品渥食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 南侨食品,佳禾食品 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 食品品牌与进口消费品经营属性成立。 | 第十一批放量候选池 v0.1 | 品牌矩阵、渠道结构与库存协同仍需补。 |
| `acc_hengbo` | 恒勃控股股份有限公司 | 恒勃股份 | 跨境电商 | 产业品出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 正裕工业,野马电池 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 汽车与机车相关出口属性成立，符合复杂跨境经营画像。 | 第八批放量候选池 v0.1 | 海外经营规模、客户结构与品牌化程度仍需补。 |
| `acc_fujia` | 宁波富佳实业股份有限公司 | 富佳股份 | 跨境电商 | 小家电出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 蓝禾,70迈 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 小家电出口与海外经营特征成立。 | 第八批放量候选池 v0.1 | 海外渠道结构、品牌化程度与经营复杂度仍需补。 |
| `acc_hengwei` | 浙江恒威电池股份有限公司 | 恒威电池 | 跨境电商 | 电池出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 野马电池,嘉益股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 电池产品出口与海外经营属性成立。 | 第八批放量候选池 v0.1 | 海外客户结构与品牌经营边界仍需补。 |
| `acc_jiaheng` | 嘉亨家化股份有限公司 | 嘉亨家化 | 跨境电商 | 家化出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 蓝禾,拉芳家化 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家化与海外经营属性成立，适合作为复杂跨境经营候选。 | 第十一批放量候选池 v0.1 | 品牌经营边界与海外客户结构仍需补。 |
| `acc_bestar` | 贝仕达克股份有限公司 | 贝仕达克 | 跨境电商 | 电子出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 蓝禾,杰美特 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 电子与智能控制类出口经营属性成立。 | 第十一批放量候选池 v0.1 | 海外经营规模、客户结构与品牌边界仍需补。 |
| `acc_xinje` | 无锡信捷电气股份有限公司 | 信捷电气 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,步科股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化控制产品技术型制造画像相邻。 | 第八批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |
| `acc_heli` | 安徽合力股份有限公司 | 安徽合力 | 先进制造 | 工业车辆制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 诺力股份,柳工股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工业车辆与全球经营属性并存，符合多工厂制造画像。 | 第八批放量候选池 v0.1 | 工厂网络、业务条线与经营颗粒度仍需补。 |
| `acc_shantui` | 山推工程机械股份有限公司 | 山推股份 | 先进制造 | 工程机械制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 三一重工,柳工股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工程机械制造与全球经营特征成立。 | 第十批放量候选池 v0.1 | 制造基地、业务条线与全球经营仍需补。 |
| `acc_dingli` | 浙江鼎力机械股份有限公司 | 浙江鼎力 | 先进制造 | 高空作业平台制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 山推股份,安徽合力 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 高空作业平台制造与全球经营属性明显。 | 第十批放量候选池 v0.1 | 制造基地、区域经营与客户结构仍需补。 |
| `acc_noblelift` | 诺力智能装备股份有限公司 | 诺力股份 | 先进制造 | 工业车辆 / 智能装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 安徽合力,山推股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 智能装备与工业车辆制造属性成立。 | 第十批放量候选池 v0.1 | 工厂布局、事业部结构与经营颗粒度仍需补。 |
| `acc_chuangshiji` | 广东创世纪智能装备集团股份有限公司 | 创世纪 | 先进制造 | 机床与智能装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海天精工,亚威股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 机床与智能装备制造属性明显，符合多工厂制造画像。 | 第十批放量候选池 v0.1 | 工厂布局、事业部与经营结构仍需补。 |
| `acc_victory` | 运达能源科技集团股份有限公司 | 运达股份 | 先进制造 | 新能源装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 明阳智能,金风科技 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 风电装备与新能源制造协同属性成立。 | 第十二批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.10

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=200`
- 合计 `273`

### v0.11

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=220`
- 合计 `293`

## 5. 下一步建议

1. 为本轮新增 `20` 家账户补第一条结构化证据
2. 优先强核验：
   - 李子园
   - 恒勃股份
   - 信捷电气
   - 创世纪
   - 运达股份
3. 后续第十轮 `L5` 迁移可继续优先：
   - 乳品 / 调味品 / 休闲食品高 SKU 品牌消费品
   - 陶瓷家居 / 宠物用品 / 家电配套复杂跨境经营对象
   - 机床装备、船海装备与高端零部件相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.10.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.10.md)
- [外部目标客户池-v1.0-第八批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第九批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十一批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十二批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md)
