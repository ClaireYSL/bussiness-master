# `external_target_account_pool_v2` 首版真实内容 v0.7

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.6.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.6.md) 基础上，继续完成第五轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 家居零售、品牌消费品与门店网络较清晰的零售对象
2. 家居 / 消费电子 / 日用品相邻的品牌出海与复杂跨境经营对象
3. 电子制造、新材料、半导体设备和高技术制造相邻对象

## 2. 本轮迁移范围

### 已有基础

- `v0.6` 主表覆盖：`182`

### 本轮新增

- 第五轮 `L5` 迁移：`28`
  - 零售消费：`10`
  - 跨境电商：`7`
  - 先进制造：`11`

### 本轮完成后

- 主表覆盖提升到 `210`

## 3. 第五轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_tineco` | 添可智能科技有限公司 | 添可 | 零售消费 | 智能家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 石头科技,科沃斯 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 家电消费品牌与品类矩阵特征明显，符合高 SKU 品牌消费品画像。 | 第四批放量候选池 v0.1 | 经营主体、渠道颗粒度与供应链切入仍需补。 |
| `acc_freda` | 福瑞达生物股份有限公司 | 福瑞达 | 零售消费 | 美妆个护 | 品牌消费品 | retail_high_sku_brand | L5 | B | 华熙生物,自然堂 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 美妆与消费品属性明确，适合作为高 SKU 品牌消费品候选。 | 第四批放量候选池 v0.1 | 品牌矩阵、渠道与库存复杂度仍需补。 |
| `acc_wanpy` | 中宠股份有限公司 | 顽皮 | 零售消费 | 宠物消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 乖宝宠物,佩蒂股份 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 宠物消费品品牌与 SKU、渠道动销空间明显。 | 第四批放量候选池 v0.1 | 品牌矩阵、渠道结构与海外占比仍需补。 |
| `acc_kuka` | 顾家家居股份有限公司 | 顾家家居 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 居然之家,红星美凯龙 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 品牌零售与终端网络特征成立，符合多门店连锁零售画像。 | 第四批放量候选池 v0.1 | 门店网络、区域经营与直营网比例仍需补。 |
| `acc_lafang` | 拉芳家化股份有限公司 | 拉芳家化 | 零售消费 | 日化用品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 华熙生物,润本 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 日化消费品牌与渠道经营特征明显，符合高 SKU 品牌消费品画像。 | 第五批放量候选池 v0.1 | 品牌矩阵、渠道与库存复杂度仍需补。 |
| `acc_suofeiya` | 索菲亚家居股份有限公司 | 索菲亚 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 居然之家,顾家家居 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居零售与终端网络特征明显，符合多门店连锁零售画像。 | 第五批放量候选池 v0.1 | 门店 / 终端网络与区域结构仍需补。 |
| `acc_spzp` | 广州尚品宅配家居股份有限公司 | 尚品宅配 | 零售消费 | 家居零售 | 连锁零售 | retail_multi_store | L5 | B | 索菲亚,志邦家居 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 家居定制零售与终端经营特征成立，符合多门店连锁零售画像。 | 第五批放量候选池 v0.1 | 区域终端网络与经营结构仍需补。 |
| `acc_vatsliquor` | 华致酒行连锁管理股份有限公司 | 华致酒行 | 零售消费 | 酒类零售 | 连锁零售 | retail_multi_store | L5 | B | 来伊份,锅圈 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 酒类零售连锁属性成立，适合总部经营透视画像。 | 第六批放量候选池 v0.1 | 门店网络与终端经营结构仍需补。 |
| `acc_mlily` | 梦百合家居科技股份有限公司 | 梦百合 | 零售消费 | 家居消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 顾家家居,罗莱生活 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 家居品牌与全球零售属性并存，符合高 SKU 品牌消费品画像。 | 第六批放量候选池 v0.1 | 零售渠道与海外经营比例仍需补。 |
| `acc_mobi` | 牧高笛户外用品股份有限公司 | 牧高笛 | 零售消费 | 户外消费品 | 品牌消费品 | retail_high_sku_brand | L5 | B | 三夫户外,浙江自然 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 户外消费品与品牌零售属性并存，适合作为高 SKU 品牌消费品候选。 | 第六批放量候选池 v0.1 | 渠道结构与库存协同仍需补。 |
| `acc_jemet` | 深圳市杰美特科技股份有限公司 | 杰美特 | 跨境电商 | 消费电子出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 安克创新,绿联科技 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 消费电子配件与品牌经营属性成立，符合品牌出海画像。 | 第五批放量候选池 v0.1 | 海外平台结构与品牌矩阵仍需补。 |
| `acc_motern` | 匠心家居股份有限公司 | 匠心家居 | 跨境电商 | 家居出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 致欧家居,乐歌 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 家居品牌出海画像相邻，适合作为品牌出海候选。 | 第五批放量候选池 v0.1 | 海外渠道、品牌与经营结构仍需补。 |
| `acc_cayi` | 浙江嘉益保温科技股份有限公司 | 嘉益股份 | 跨境电商 | 消费品出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 哈尔斯,致欧家居 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 保温器皿出海属性明显，符合品牌出海画像。 | 第六批放量候选池 v0.1 | 海外经营规模与平台结构仍需补。 |
| `acc_sleemon` | 麒盛科技股份有限公司 | 麒盛科技 | 跨境电商 | 智能家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 恒林股份,建霖家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 智能家居与海外经营属性并存，适合作为复杂跨境经营候选。 | 第六批放量候选池 v0.1 | 海外业务占比与品牌结构仍需补。 |
| `acc_yotrio` | 浙江永强集团股份有限公司 | 浙江永强 | 跨境电商 | 家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 恒林股份,麒盛科技 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 户外休闲家居出口属性明显，符合复杂跨境经营画像。 | 第六批放量候选池 v0.1 | 海外渠道结构与经营阶段仍需补。 |
| `acc_jialian` | 宁波家联科技股份有限公司 | 家联科技 | 跨境电商 | 日用品出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 致欧家居,双枪科技 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居日用品出口属性明确，可沿复杂跨境经营画像纳入。 | 第六批放量候选池 v0.1 | 品牌化程度与经营复杂度仍需补。 |
| `acc_origin` | 宁波创源文化发展股份有限公司 | 创源股份 | 跨境电商 | 文创出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 家联科技,致欧家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 海外市场与出口属性明显，适合作为复杂跨境经营候选。 | 第六批放量候选池 v0.1 | 品牌化程度与经营结构仍需补。 |
| `acc_neway` | 苏州纽威阀门股份有限公司 | 纽威阀门 | 先进制造 | 装备制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中信重工,海天精工 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 技术型制造属性明确，符合装备 / 工业制造画像。 | 第四批放量候选池 v0.1 | 研产销协同与全球经营颗粒度仍需补。 |
| `acc_shuanghuan` | 浙江双环传动机械股份有限公司 | 双环传动 | 先进制造 | 汽车零部件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 伯特利,德赛西威 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 汽车零部件与技术制造属性明显，符合技术型制造画像。 | 第四批放量候选池 v0.1 | 全球经营与组织复杂度仍需补。 |
| `acc_deye` | 宁波德业科技股份有限公司 | 德业股份 | 先进制造 | 多元装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 三一重工,柳工股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 多产品线制造与全球经营属性明显，符合多工厂制造画像。 | 第四批放量候选池 v0.1 | 多工厂和事业部复杂度仍需补。 |
| `acc_topband` | 深圳拓邦股份有限公司 | 拓邦股份 | 先进制造 | 智能控制制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,和而泰 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 智能控制与制造协同属性成立，符合技术型制造画像。 | 第五批放量候选池 v0.1 | 经营复杂度与多业务结构仍需补。 |
| `acc_yuyue` | 江苏鱼跃医疗设备股份有限公司 | 鱼跃医疗 | 先进制造 | 医疗设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 迈瑞医疗,开立医疗 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 医疗设备与消费医疗器械协同属性明显，符合技术型制造画像。 | 第五批放量候选池 v0.1 | 业务结构与制造协同仍需补。 |
| `acc_ronbay` | 宁波容百新能源科技股份有限公司 | 容百科技 | 先进制造 | 新材料制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 当升科技,恩捷股份 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 新能源材料制造画像成立，适合作为技术型制造候选。 | 第六批放量候选池 v0.1 | 业务协同与全球经营颗粒度仍需补。 |
| `acc_piotech` | 拓荆科技股份有限公司 | 拓荆科技 | 先进制造 | 半导体设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 北方华创,中微公司 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 半导体装备制造画像成立，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 业务结构与全球经营仍需补。 |
| `acc_scientech` | 中科飞测科技股份有限公司 | 中科飞测 | 先进制造 | 检测设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 精测电子,中微公司 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高端检测设备与技术型制造画像相邻。 | 第六批放量候选池 v0.1 | 经营链路与业务颗粒度仍需补。 |
| `acc_scc` | 生益电子股份有限公司 | 生益电子 | 先进制造 | 电子材料制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 鹏鼎控股,沪士电子 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 电子材料 / 制造属性成立，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 经营协同与客户结构仍需补。 |
| `acc_faratronic` | 厦门法拉电子股份有限公司 | 法拉电子 | 先进制造 | 电子元器件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 立讯精密,瑞可达 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 电子元器件制造画像成立，符合技术型制造画像。 | 第六批放量候选池 v0.1 | 业务结构与协同链路仍需补。 |
| `acc_recodeal` | 瑞可达连接系统股份有限公司 | 瑞可达 | 先进制造 | 连接器制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 立讯精密,法拉电子 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 连接器制造与多行业客户协同特征成立。 | 第六批放量候选池 v0.1 | 组织复杂度与全球经营仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.6

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=109`
- 合计 `182`

### v0.7

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=137`
- 合计 `210`

## 5. 下一步建议

1. 为本轮新增 `28` 家账户补第一条结构化证据
2. 优先强核验：
   - 顾家家居
   - 嘉益股份
   - 纽威阀门
   - 拓荆科技
   - 瑞可达
3. 后续第六轮 `L5` 迁移可继续优先：
   - 家居零售与个护消费品
   - 家居 / 材料出海
   - 新材料、精密制造与医疗设备相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.6.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.6.md)
- [外部目标客户池-v1.0-第四批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第五批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第五批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第六批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第六批放量候选池-v0.1.md)
