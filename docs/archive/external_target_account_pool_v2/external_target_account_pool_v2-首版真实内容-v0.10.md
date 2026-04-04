# `external_target_account_pool_v2` 首版真实内容 v0.10

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.9.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.9.md) 基础上，继续完成第八轮 `L5` 放量候选的结构化迁移。

这一轮继续优先：

1. 食品饮料与乳品烘焙等高 SKU 品牌消费品
2. 材料 / 家居 / 产业品出口属性较清晰的复杂跨境经营对象
3. 自动化控制、高端零部件、风电链条与装备制造相邻对象

## 2. 本轮迁移范围

### 已有基础

- `v0.9` 主表覆盖：`252`

### 本轮新增

- 第八轮 `L5` 迁移：`21`
  - 零售消费：`8`
  - 跨境电商：`5`
  - 先进制造：`8`

### 本轮完成后

- 主表覆盖提升到 `273`

## 3. 第八轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_zhongjing` | 仲景食品股份有限公司 | 仲景食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 天味食品,良品铺子 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 调味品品牌属性成立，符合高 SKU 品牌消费品画像。 | 第八批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_keming` | 克明食品股份有限公司 | 五谷道场 / 陈克明 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 三全食品,桃李面包 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 食品品牌与多品类经营特征明显，适合作为品牌消费品候选。 | 第八批放量候选池 v0.1 | 品牌矩阵、渠道结构与供应链切入仍需补。 |
| `acc_weizhixiang` | 上海味知香食品股份有限公司 | 味知香 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 三全食品,海欣食品 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 预制食品品牌属性成立，适合作为高 SKU 品牌消费品候选。 | 第八批放量候选池 v0.1 | 渠道结构、库存协同与直营网程度仍需补。 |
| `acc_youyou` | 有友食品股份有限公司 | 有友 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 好想你,良品铺子 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 休闲食品品牌属性成立，SKU 与渠道分析空间明显。 | 第九批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_tolybread` | 桃李面包股份有限公司 | 桃李面包 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 一鸣食品,立高食品 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 烘焙食品品牌属性强，符合高 SKU 品牌消费品画像。 | 第九批放量候选池 v0.1 | 渠道结构、库存与供应链切入仍需补。 |
| `acc_milkground` | 上海妙可蓝多食品科技股份有限公司 | 妙可蓝多 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 三元食品,一鸣食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 奶酪品牌与渠道经营特征明显，适合作为高 SKU 品牌消费品候选。 | 第九批放量候选池 v0.1 | SKU 结构、渠道颗粒度与库存协同仍需补。 |
| `acc_jiaheshipin` | 佳禾食品工业股份有限公司 | 佳禾食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 南侨食品,西王食品 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 食品与饮品相关消费品属性成立。 | 第十一批放量候选池 v0.1 | 品牌经营边界、渠道结构与供应链切入仍需补。 |
| `acc_namchow` | 南侨食品集团（上海）股份有限公司 | 南侨食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 佳禾食品,立高食品 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 烘焙油脂与食品品牌画像相邻，符合品牌消费品画像。 | 第十一批放量候选池 v0.1 | 品牌经营边界、渠道结构与供应链颗粒度仍需补。 |
| `acc_yayi` | 浙江雅艺金属科技股份有限公司 | 雅艺科技 | 跨境电商 | 家居出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 恒林股份,浙江永强 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 户外家居出口属性明确，符合复杂跨境经营画像。 | 第八批放量候选池 v0.1 | 海外业务占比与品牌经营边界仍需补。 |
| `acc_skshu` | 星徽股份有限公司 | 星徽股份 | 跨境电商 | 家居 / 电商出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 匠心家居,恒林股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居 / 电商出海经营属性成立，适合作为复杂跨境经营候选。 | 第八批放量候选池 v0.1 | 当前业务结构、品牌化程度与海外经营颗粒度仍需补。 |
| `acc_washin` | 浙江华生科技股份有限公司 | 华生科技 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 海利得,西大门 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 新材料出口与海外经营特征成立。 | 第十批放量候选池 v0.1 | 海外客户结构与业务边界仍需补。 |
| `acc_megain` | 麦加芯彩新材料科技（上海）股份有限公司 | 麦加芯彩 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 海利得,西大门 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 新材料与海外经营特征明确，适合作为复杂跨境经营候选。 | 第十一批放量候选池 v0.1 | 海外业务占比、客户结构与业务边界仍需补。 |
| `acc_mustangbat` | 浙江野马电池股份有限公司 | 野马电池 | 跨境电商 | 电池出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 恒威电池,嘉益股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 电池产品出口与海外经营特征成立。 | 第十一批放量候选池 v0.1 | 海外经营规模、品牌边界与客户结构仍需补。 |
| `acc_zdleader` | 宁波中大力德智能传动股份有限公司 | 中大力德 | 先进制造 | 传动与控制部件 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 鸣志电器,雷赛智能 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 传动与控制部件制造属性成立，符合技术型制造画像。 | 第八批放量候选池 v0.1 | 业务结构、研产销协同与客户颗粒度仍需补。 |
| `acc_kinco` | 上海步科自动化股份有限公司 | 步科股份 | 先进制造 | 工业自动化 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,鸣志电器 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 工业自动化与控制产品技术型制造画像成立。 | 第八批放量候选池 v0.1 | 经营链路、客户结构与全球经营仍需补。 |
| `acc_haomai` | 豪迈科技股份有限公司 | 豪迈科技 | 先进制造 | 高端装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 中信重工,杰瑞股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 高端装备制造与复杂客户协同特征成立。 | 第八批放量候选池 v0.1 | 多基地布局、业务条线与经营颗粒度仍需补。 |
| `acc_xusheng` | 宁波旭升集团股份有限公司 | 旭升集团 | 先进制造 | 新能源零部件制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 中鼎股份,双环传动 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 铝合金零部件与新能源链条协同明显。 | 第八批放量候选池 v0.1 | 制造基地、业务条线与客户结构仍需补。 |
| `acc_wanma` | 浙江万马股份有限公司 | 万马股份 | 先进制造 | 新材料 / 线缆制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 厦钨新能,上海新阳 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 线缆与新材料制造协同属性成立。 | 第十一批放量候选池 v0.1 | 业务结构、客户协同与经营颗粒度仍需补。 |
| `acc_newspring` | 五洲新春集团股份有限公司 | 五洲新春 | 先进制造 | 精密零部件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 瑞可达,中密控股 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 轴承与精密零部件制造协同属性成立。 | 第十二批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |
| `acc_hanzhong` | 汉钟精机股份有限公司 | 汉钟精机 | 先进制造 | 压缩机与真空设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 纽威阀门,中密控股 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 压缩机与真空设备制造属性明确。 | 第十二批放量候选池 v0.1 | 业务条线、客户协同与全球经营仍需补。 |
| `acc_yingliu` | 应流机电股份有限公司 | 应流股份 | 先进制造 | 高端零部件制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 中密控股,瑞可达 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高端零部件与装备制造协同特征成立。 | 第十二批放量候选池 v0.1 | 业务结构、全球经营与客户协同仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.9

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=179`
- 合计 `252`

### v0.10

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=200`
- 合计 `273`

## 5. 下一步建议

1. 为本轮新增 `21` 家账户补第一条结构化证据
2. 优先强核验：
   - 仲景食品
   - 西大门
   - 中大力德
   - 万马股份
   - 汉钟精机
3. 后续第九轮 `L5` 迁移可继续优先：
   - 乳品 / 调味品 / 休闲食品高 SKU 品牌消费品
   - 宠物用品、陶瓷家居、家居电机等复杂跨境经营对象
   - 机床装备、风电链条与高端零部件相邻对象

## 6. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.9.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.9.md)
- [外部目标客户池-v1.0-第八批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第九批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十一批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十二批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md)
