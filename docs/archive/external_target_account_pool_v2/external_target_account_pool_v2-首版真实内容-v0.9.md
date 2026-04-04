# `external_target_account_pool_v2` 首版真实内容 v0.9

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.8.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.8.md) 基础上，继续完成第七轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 潮玩 / 服饰 / 家居零售等边界稳定的品牌消费品与连锁零售对象
2. 材料 / 家居 / 产业品出口属性较清晰的复杂跨境经营对象
3. 新能源、自动化、高端零部件与多工厂制造相邻对象

## 2. 本轮迁移范围

### 已有基础

- `v0.8` 主表覆盖：`230`

### 本轮新增

- 第七轮 `L5` 迁移：`22`
  - 零售消费：`8`
  - 跨境电商：`5`
  - 先进制造：`9`

### 本轮完成后

- 主表覆盖提升到 `252`

## 3. 第七轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_aofei` | 奥飞娱乐股份有限公司 | 奥飞娱乐 | 零售消费 | 潮玩文创 | 品牌消费品 | retail_high_sku_brand | L5 | B | 泡泡玛特,实丰文化 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 潮玩 / 内容衍生消费品属性成立，符合高 SKU 品牌消费品画像。 | 第五批放量候选池 v0.1 | 业务结构与消费品牌占比仍需补。 |
| `acc_shifengculture` | 实丰文化发展股份有限公司 | 实丰文化 | 零售消费 | 潮玩文创 | 品牌消费品 | retail_high_sku_brand | L5 | B | 奥飞娱乐,泡泡玛特 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 玩具 / 潮玩消费品属性成立，符合品牌消费品画像。 | 第五批放量候选池 v0.1 | SKU 与渠道结构仍需补。 |
| `acc_sanfo` | 三夫户外用品股份有限公司 | 三夫户外 | 零售消费 | 户外零售 | 连锁零售 | retail_multi_store | L5 | B | 牧高笛,浙江自然 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 户外零售门店网络与品牌经营成立，符合多门店连锁零售画像。 | 第六批放量候选池 v0.1 | 门店规模与区域经营结构仍需补。 |
| `acc_lancy` | 朗姿股份有限公司 | 朗姿股份 | 零售消费 | 服饰零售 | 连锁零售 | retail_multi_store | L5 | B | 报喜鸟,锦泓时装 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 时尚服饰 / 医美多品牌经营并存，品牌零售与区域经营特征成立。 | 第七批放量候选池 v0.1 | 业务边界、门店网络与品牌矩阵仍需补。 |
| `acc_vgrass` | 锦泓时装集团股份有限公司 | VGRASS / TEENIE WEENIE | 零售消费 | 服饰零售 | 连锁零售 | retail_multi_store | L5 | B | 朗姿股份,九牧王 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 多品牌服饰零售特征明显，符合多门店连锁零售画像。 | 第七批放量候选池 v0.1 | 品牌矩阵、渠道结构与终端网络仍需补。 |
| `acc_joeone` | 九牧王股份有限公司 | 九牧王 | 零售消费 | 服饰零售 | 连锁零售 | retail_multi_store | L5 | B | 报喜鸟,海澜之家 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 服饰零售品牌与门店网络特征明确。 | 第七批放量候选池 v0.1 | 门店网络、直营网与加盟结构仍需补。 |
| `acc_arrowhome` | 箭牌家居集团股份有限公司 | ARROW 箭牌 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 顾家家居,索菲亚 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居品牌与终端网络特征明显，符合多门店连锁零售画像。 | 第七批放量候选池 v0.1 | 直营网 / 经销网络与区域经营颗粒度仍需补。 |
| `acc_haoxiangni` | 好想你健康食品股份有限公司 | 好想你 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 良品铺子,三只松鼠 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 休闲食品品牌属性成立，SKU 与全渠道动销分析空间明显。 | 第七批放量候选池 v0.1 | SKU 颗粒度、渠道结构与库存协同仍需补。 |
| `acc_xidamen` | 西大门新材料股份有限公司 | 西大门 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 海利得,明新旭腾 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 海外业务与材料出口属性成立，符合复杂跨境经营画像。 | 第七批放量候选池 v0.1 | 品牌化程度与海外渠道结构仍需补。 |
| `acc_ccgrass` | 共创草坪股份有限公司 | 共创草坪 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 海利得,西大门 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 海外销售和出口导向特征明确，适合作为复杂跨境经营候选。 | 第七批放量候选池 v0.1 | 海外客户结构与品牌经营颗粒度仍需补。 |
| `acc_haojiang` | 豪江智能科技股份有限公司 | 豪江智能 | 跨境电商 | 智能家居出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 麒盛科技,恒林股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 智能家居部件出口与海外经营特征成立。 | 第七批放量候选池 v0.1 | 海外经营规模与品牌化程度仍需补。 |
| `acc_hailide` | 浙江海利得新材料股份有限公司 | 海利得 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 西大门,明新旭腾 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 新材料出口与全球经营属性成立。 | 第九批放量候选池 v0.1 | 海外经营占比、客户结构与业务边界仍需补。 |
| `acc_mingxin` | 浙江明新旭腾新材料股份有限公司 | 明发集团 / 明新旭腾 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 海利得,西大门 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 汽车内饰新材料与海外经营特征成立。 | 第九批放量候选池 v0.1 | 海外客户结构、经营边界仍需补。 |
| `acc_zhongding` | 安徽中鼎密封件股份有限公司 | 中鼎股份 | 先进制造 | 汽车零部件制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 双环传动,德赛西威 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 汽车零部件与全球经营并存，符合多工厂制造画像。 | 第七批放量候选池 v0.1 | 事业部结构与多工厂协同颗粒度仍需补。 |
| `acc_juyi` | 合肥巨一科技股份有限公司 | 巨一科技 | 先进制造 | 智能装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 先导智能,埃斯顿 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 智能装备与新能源链条协同特征成立。 | 第七批放量候选池 v0.1 | 制造基地、业务条线与经营复杂度仍需补。 |
| `acc_cnano` | 江苏天奈科技股份有限公司 | 天奈科技 | 先进制造 | 新材料制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 容百科技,当升科技 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 新材料与新能源制造协同属性成立。 | 第七批放量候选池 v0.1 | 业务链路与组织复杂度仍需补。 |
| `acc_tfc` | 苏州天孚光通信股份有限公司 | 天孚通信 | 先进制造 | 光通信器件 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 华工科技,中际旭创 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 光器件制造与多业务协同特征成立。 | 第七批放量候选池 v0.1 | 业务结构与全球经营颗粒度仍需补。 |
| `acc_moons` | 上海鸣志电器股份有限公司 | 鸣志电器 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 和而泰,雷赛智能 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 运动控制与驱动产品技术型制造属性明确。 | 第八批放量候选池 v0.1 | 业务条线、全球经营与客户协同颗粒度仍需补。 |
| `acc_invt` | 深圳市英威腾电气股份有限公司 | 英威腾 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,新时达 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 工业自动化和电气控制产品属性明显。 | 第八批放量候选池 v0.1 | 业务条线、组织复杂度与全球经营仍需补。 |
| `acc_yawei` | 江苏亚威机床股份有限公司 | 亚威股份 | 先进制造 | 机床装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海天精工,秦川机床 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 机床装备与多业务协同特征明确，符合多工厂制造画像。 | 第十一批放量候选池 v0.1 | 工厂布局、事业部结构与经营颗粒度仍需补。 |
| `acc_sino-seals` | 中密控股股份有限公司 | 中密控股 | 先进制造 | 高端零部件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 纽威阀门,瑞可达 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 流体机械密封与高端制造协同属性成立。 | 第十二批放量候选池 v0.1 | 业务条线、客户结构与全球经营颗粒度仍需补。 |
| `acc_mingyang` | 明阳智慧能源集团股份公司 | 明阳智能 | 先进制造 | 新能源装备 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 金风科技,运达股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 风电与新能源装备制造特征明显，符合多工厂制造画像。 | 第十二批放量候选池 v0.1 | 工厂布局、事业部与经营颗粒度仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.8

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=157`
- 合计 `230`

### v0.9

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=179`
- 合计 `252`

## 5. 下一步建议

1. 为本轮新增 `22` 家账户补第一条结构化证据
2. 优先强核验：
   - 朗姿股份
   - 海利得
   - 中鼎股份
   - 鸣志电器
   - 明阳智能
3. 后续第八轮 `L5` 迁移可继续优先：
   - 食品饮料高 SKU 品牌消费品
   - 边界较清晰的复杂跨境经营材料与产业品出口对象
   - 自动化控制、新材料与高端零部件相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.8.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.8.md)
- [外部目标客户池-v1.0-第七批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第八批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第九批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十一批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十二批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md)
