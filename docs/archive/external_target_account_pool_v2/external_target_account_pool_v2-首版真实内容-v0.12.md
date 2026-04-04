# `external_target_account_pool_v2` 首版真实内容 v0.12

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.11.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.11.md) 基础上，完成第十轮 `L5` 增量扩池的结构化迁移。

这一轮的迁移来源不再是“旧批次剩余待迁”，而是来自新增的 [外部目标客户池-v1.0-第十三批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十三批放量候选池-v0.1.md)。

## 2. 本轮迁移范围

### 已有基础

- `v0.11` 主表覆盖：`293`

### 本轮新增

- 第十轮 `L5` 迁移：`20`
  - 零售消费：`8`
  - 跨境电商：`5`
  - 先进制造：`7`

### 本轮完成后

- 主表覆盖提升到 `313`

## 3. 第十轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_brightdairy` | 光明乳业股份有限公司 | 光明乳业 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 三元食品,妙可蓝多 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 乳品品牌与多产品经营属性明确，符合高 SKU 品牌消费品画像。 | 第十三批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_yanjinshop` | 盐津铺子食品股份有限公司 | 盐津铺子 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | A | 良品铺子,三只松鼠 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 休闲食品品牌与多 SKU 经营特征强，适合作为高 SKU 品牌消费品候选。 | 第十三批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_babi` | 中饮巴比食品股份有限公司 | 巴比食品 | 零售消费 | 连锁餐饮 | 连锁零售 | retail_multi_store_chain | L5 | B | 老乡鸡,来伊份 | 总部经营透视 / 门店经营分析 | ka_case_laiyifen_replenishment_v1,ka_case_chatbi_frontline_v1 | 连锁餐饮零售属性明确，符合多门店连锁零售画像。 | 第十三批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_lecom` | 立高食品股份有限公司 | 立高食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 南侨食品,桃李面包 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 烘焙相关消费品品牌属性成立，适合作为高 SKU 候选。 | 第十三批放量候选池 v0.1 | 渠道结构、品牌矩阵与供应链协同仍需补。 |
| `acc_sanquan` | 三全食品股份有限公司 | 三全食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | A | 桃李面包,味知香 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 速冻食品品牌属性强，商品与渠道分析空间明确。 | 第十三批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_qianweiyangchu` | 郑州千味央厨食品股份有限公司 | 千味央厨 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 味知香,巴比食品 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 预制食品与餐饮供应双属性并存，商品与供应链画像成立。 | 第十三批放量候选池 v0.1 | 客户结构、渠道颗粒度与库存协同仍需补。 |
| `acc_haixinfood` | 海欣食品股份有限公司 | 海欣食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 三全食品,味知香 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 预制食品与速冻食品品牌属性明确。 | 第十三批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_juewei` | 绝味食品股份有限公司 | 绝味食品 | 零售消费 | 连锁餐饮 | 连锁零售 | retail_multi_store_chain | L5 | A | 老乡鸡,来伊份 | 总部经营透视 / 门店经营分析 | ka_case_laiyifen_replenishment_v1,ka_case_chatbi_frontline_v1 | 卤味连锁网络特征强，适合总部经营透视与门店经营分析。 | 第十三批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_uxi` | 匠心家居股份有限公司 | 匠心家居 | 跨境电商 | 家居出海 | 品牌出海 | cbec_brand_outbound | L5 | B | 致欧家居,赛维时代 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 家居品牌出海属性明确，适合作为品牌出海型候选。 | 第十三批放量候选池 v0.1 | 海外渠道结构、品牌矩阵与平台颗粒度仍需补。 |
| `acc_yotrio` | 浙江永强集团股份有限公司 | 浙江永强 | 跨境电商 | 家居出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 匠心家居,恒林股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 户外家居与海外经营属性并存，符合复杂跨境经营画像。 | 第十三批放量候选池 v0.1 | 海外业务占比、客户结构与品牌边界仍需补。 |
| `acc_haers` | 浙江哈尔斯真空器皿股份有限公司 | 哈尔斯 | 跨境电商 | 消费品出海 | 品牌出海 | cbec_brand_outbound | L5 | B | 嘉益股份,安克创新 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 保温器皿品牌出海属性明确，品牌出海画像相邻。 | 第十三批放量候选池 v0.1 | 海外渠道、品牌矩阵与经营颗粒度仍需补。 |
| `acc_loctek` | 乐歌人体工学科技股份有限公司 | 乐歌股份 | 跨境电商 | 家居出海 | 品牌出海 | cbec_brand_outbound | L5 | A | 致欧家居,安克创新 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 人体工学家居与海外品牌经营属性强，符合品牌出海画像。 | 第十三批放量候选池 v0.1 | 海外平台结构、品牌矩阵与区域经营仍需补。 |
| `acc_jame` | 深圳市杰美特科技股份有限公司 | 杰美特 | 跨境电商 | 消费电子配件出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 绿联科技,蓝禾 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 消费电子配件与海外经营属性成立，符合复杂跨境经营画像。 | 第十三批放量候选池 v0.1 | 海外客户结构、品牌边界与经营颗粒度仍需补。 |
| `acc_liugong` | 广西柳工机械股份有限公司 | 柳工股份 | 先进制造 | 工程机械制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 三一重工,山推股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工程机械制造与多基地经营特征强，多工厂画像成立。 | 第十三批放量候选池 v0.1 | 工厂布局、事业部与区域经营颗粒度仍需补。 |
| `acc_jereh` | 烟台杰瑞石油服务集团股份有限公司 | 杰瑞股份 | 先进制造 | 高端装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 中信重工,豪迈科技 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 高端装备与能源装备制造协同属性明显。 | 第十三批放量候选池 v0.1 | 多基地布局、业务条线与全球经营仍需补。 |
| `acc_yawei` | 江苏亚威机床股份有限公司 | 亚威股份 | 先进制造 | 机床与智能装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 海天精工,创世纪 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 机床与智能制造装备属性明确，符合技术型制造画像。 | 第十三批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |
| `acc_ruikeda` | 苏州瑞可达连接系统股份有限公司 | 瑞可达 | 先进制造 | 精密连接器制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中航光电,上海新阳 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 精密连接器与高端制造协同特征成立。 | 第十三批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |
| `acc_leisai` | 深圳市雷赛智能控制股份有限公司 | 雷赛智能 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,信捷电气 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 运动控制与自动化产品属性明确，技术型制造画像成立。 | 第十三批放量候选池 v0.1 | 业务条线、客户协同与全球经营仍需补。 |
| `acc_sinyang` | 上海新阳半导体材料股份有限公司 | 上海新阳 | 先进制造 | 半导体材料 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 北方华创,德赛西威 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 半导体材料与高技术制造协同属性成立。 | 第十三批放量候选池 v0.1 | 业务结构、客户协同与经营颗粒度仍需补。 |
| `acc_neway` | 纽威阀门股份有限公司 | 纽威股份 | 先进制造 | 工业阀门制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中密控股,汉钟精机 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 阀门与工业装备零部件制造属性明确。 | 第十三批放量候选池 v0.1 | 业务条线、客户结构与全球经营仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.11

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=220`
- 合计 `293`

### v0.12

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=240`
- 合计 `313`

## 5. 下一步建议

1. 为本轮新增 `20` 家账户补第一条结构化证据
2. 优先强核验：
   - 盐津铺子
   - 三全食品
   - 乐歌股份
   - 柳工股份
   - 杰瑞股份
   - 上海新阳
