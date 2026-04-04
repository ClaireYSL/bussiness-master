# `external_target_account_pool_v2` 首版真实内容 v0.8

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.7.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.7.md) 基础上，继续完成第六轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 家纺家居、户外与个护品牌消费品
2. 边界较清晰的消费电子配件品牌出海对象
3. 新材料、精密制造、半导体设备与技术型制造相邻对象

本轮明确不纳入：

- `深圳市万得福电子商务有限公司`
- `厦门建发股份有限公司`

原因是两者当前仍处于 `C` 级边界判断，不适合在本轮直接进入结构化主表。

## 2. 本轮迁移范围

### 已有基础

- `v0.7` 主表覆盖：`210`

### 本轮新增

- 第六轮 `L5` 迁移：`20`
  - 零售消费：`8`
  - 跨境电商：`1`
  - 先进制造：`11`

### 本轮完成后

- 主表覆盖提升到 `230`

## 3. 第六轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_peti` | 佩蒂动物营养科技股份有限公司 | 佩蒂 | 零售消费 | 宠物消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 中宠股份,乖宝宠物 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 宠物消费品画像相邻，适合作为高 SKU 品牌消费品候选。 | 第四批放量候选池 v0.1 | 品牌经营与渠道颗粒度仍需补。 |
| `acc_luolai` | 罗莱生活科技股份有限公司 | 罗莱生活 | 零售消费 | 家纺消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 富安娜,梦百合 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 家纺消费品牌与 SKU、渠道分析空间明显。 | 第五批放量候选池 v0.1 | 渠道颗粒度与库存协同仍需补。 |
| `acc_fuanna` | 深圳市富安娜家居用品股份有限公司 | 富安娜 | 零售消费 | 家纺消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 罗莱生活,梦百合 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 家纺品牌消费品画像成立，适合作为高 SKU 品牌消费品候选。 | 第五批放量候选池 v0.1 | SKU 与渠道结构仍需补。 |
| `acc_zbom` | 志邦家居股份有限公司 | 志邦家居 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 索菲亚,尚品宅配 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居零售画像相邻，可沿终端经营与区域管理切入。 | 第五批放量候选池 v0.1 | 门店与直营网结构仍需补。 |
| `acc_goldenhome` | 金牌厨柜家居科技股份有限公司 | 金牌厨柜 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 索菲亚,志邦家居 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居零售和渠道经营特征明显，符合多门店连锁零售画像。 | 第五批放量候选池 v0.1 | 渠道结构与终端网络仍需补。 |
| `acc_holike` | 好莱客创意家居股份有限公司 | 好莱客 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 索菲亚,尚品宅配 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居定制零售画像成立，适合作为多门店零售候选。 | 第五批放量候选池 v0.1 | 门店网络与区域经营颗粒度仍需补。 |
| `acc_haoyue` | 豪悦护理用品股份有限公司 | 豪悦护理 | 零售消费 | 个护消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 润本,拉芳家化 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 个护消费品与品牌供应链属性成立，符合高 SKU 品牌消费品画像。 | 第六批放量候选池 v0.1 | 品类矩阵与渠道经营复杂度仍需补。 |
| `acc_zjnature` | 浙江自然户外用品股份有限公司 | 浙江自然 | 零售消费 | 户外消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 牧高笛,三夫户外 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 户外消费品画像成立，适合作为品牌消费品候选。 | 第六批放量候选池 v0.1 | 品牌经营与渠道颗粒度仍需补。 |
| `acc_lanhe` | 深圳市蓝禾技术有限公司 | 蓝禾 | 跨境电商 | 消费电子出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 绿联科技,杰美特 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 消费电子 / 配件品牌出海方向成立，符合品牌出海画像。 | 第五批放量候选池 v0.1 | 海外经营规模与平台结构仍需补。 |
| `acc_xtcnew` | 厦门厦钨新能源材料股份有限公司 | 厦钨新能 | 先进制造 | 新材料制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 容百科技,当升科技 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 新材料与新能源制造属性成立，符合技术型制造画像。 | 第四批放量候选池 v0.1 | 经营链路与组织颗粒度仍需补。 |
| `acc_focusprecision` | 江苏先锋精密科技股份有限公司 | 先锋精密 | 先进制造 | 精密制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 长盈精密,瑞可达 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 精密制造属性成立，适合作为技术型制造候选。 | 第四批放量候选池 v0.1 | 主体强证据与经营复杂度仍需补。 |
| `acc_weixingmeter` | 浙江伟星智能仪表股份有限公司 | 伟星智能 | 先进制造 | 仪表制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,新时达 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 仪表制造与技术型制造画像相邻。 | 第四批放量候选池 v0.1 | 经营链路与组织协同颗粒度仍需补。 |
| `acc_hetai` | 深圳和而泰智能控制股份有限公司 | 和而泰 | 先进制造 | 智能控制制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 拓邦股份,汇川技术 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 智能控制与全球客户协同特征明显，符合技术型制造画像。 | 第五批放量候选池 v0.1 | 经营链路与组织颗粒度仍需补。 |
| `acc_leisai` | 深圳市雷赛智能控制股份有限公司 | 雷赛智能 | 先进制造 | 智能控制制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 和而泰,拓邦股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 控制类技术型制造画像相邻。 | 第五批放量候选池 v0.1 | 组织结构与全球经营仍需补。 |
| `acc_opt` | 奥普特科技股份有限公司 | 奥普特 | 先进制造 | 机器视觉 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 华工科技,精测电子 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 机器视觉与高技术制造协同属性成立。 | 第五批放量候选池 v0.1 | 经营链路与协同复杂度仍需补。 |
| `acc_kelai` | 上海克来机电自动化工程股份有限公司 | 克来机电 | 先进制造 | 自动化装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 拓斯达,赛腾股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化装备与技术型制造画像成立。 | 第五批放量候选池 v0.1 | 协同链路与组织复杂度仍需补。 |
| `acc_easpring` | 北京当升材料科技股份有限公司 | 当升科技 | 先进制造 | 新材料制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 容百科技,恩捷股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 材料制造与产业链协同特征明显，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 经营结构与研产销切入仍需补。 |
| `acc_scimee` | 沈阳芯源微电子设备股份有限公司 | 芯源微 | 先进制造 | 半导体设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 北方华创,中微公司 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 半导体设备制造与技术型制造画像相邻。 | 第六批放量候选池 v0.1 | 经营链路与组织复杂度仍需补。 |
| `acc_wus` | 沪士电子股份有限公司 | 沪士电子 | 先进制造 | PCB制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 鹏鼎控股,生益电子 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | PCB 制造与全球客户协同特征明显。 | 第六批放量候选池 v0.1 | 业务颗粒度与组织复杂度仍需补。 |
| `acc_sinyang` | 上海新阳半导体材料股份有限公司 | 上海新阳 | 先进制造 | 半导体材料 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 华海清科,当升科技 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 半导体材料制造画像成立。 | 第六批放量候选池 v0.1 | 经营链路与全球经营颗粒度仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.7

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=137`
- 合计 `210`

### v0.8

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=157`
- 合计 `230`

## 5. 下一步建议

1. 为本轮新增 `20` 家账户补第一条结构化证据
2. 优先强核验：
   - 罗莱生活
   - 蓝禾
   - 厦钨新能
   - 和而泰
   - 芯源微
3. 后续第七轮 `L5` 迁移可继续优先：
   - 潮玩 / 文创消费品
   - 材料 / 供应链复杂跨境经营对象
   - 半导体设备与精密制造相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.7.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.7.md)
- [外部目标客户池-v1.0-第四批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第五批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第五批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第六批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第六批放量候选池-v0.1.md)
