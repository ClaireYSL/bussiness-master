# `external_target_account_pool_v2` 首版真实内容 v0.3

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.2.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.2.md) 基础上，完成第一轮 `L5` 放量候选的结构化迁移。

本轮迁移坚持两个原则：

1. 不一次性机械平移全部 `L5=281`
2. 只优先迁移与现有 `L1/L2/L3` 最接近、画像边界最稳定的一批

## 2. 本轮迁移范围

### 已有基础

- `v0.1` 已迁入：`59`
- `v0.2` 新增迁入 `L4=14`
- 当前主表覆盖：`73`

### 本轮新增

- 首轮 `L5` 迁移：`30`
  - 零售消费：`10`
  - 跨境电商：`10`
  - 先进制造：`10`

### 本轮完成后

- 主表覆盖提升到 `103`

## 3. 首轮 L5 迁移策略

优先迁入以下几类对象：

1. 与已有 `L1/L2/L3` 标尺样本最接近的对象
2. 画像边界清晰、入池理由稳定的对象
3. 已有相对明确入池理由，但尚未进入高质量层的对象

暂不优先迁入：

- 边界更偏产业链经营、消费品牌经营不够明确的零售对象
- 更偏制造出口、品牌化程度不够清楚的跨境对象
- 更偏普通工厂或经营协同复杂度不足的制造对象

## 4. 本轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_mercuryhome` | 水星家纺股份有限公司 | 水星家纺 | 零售消费 | 家纺家居 | 品牌消费品 | retail_high_sku_brand | L5 | B | 自然堂,良品铺子,三只松鼠 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 家纺品牌消费品属性明确，SKU、渠道与库存协同分析空间明显，符合高 SKU 品牌消费品画像。 | 第七批放量候选池 v0.1 | 渠道结构、零售终端网络、库存颗粒度仍需补强。 |
| `acc_robam` | 杭州老板电器股份有限公司 | 老板电器 | 零售消费 | 厨电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 自然堂,晨光文具 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 厨电品牌消费品属性明确，品类矩阵和渠道经营复杂度较强，符合高 SKU 品牌消费品画像。 | 第七批放量候选池 v0.1 | 渠道结构、库存协同、海外经营占比仍需补。 |
| `acc_supor` | 浙江苏泊尔股份有限公司 | 苏泊尔 | 零售消费 | 小家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 自然堂,晨光文具 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 小家电品牌消费品属性强，SKU 与渠道动销分析空间明显，适合作为高 SKU 品牌消费品候选。 | 第七批放量候选池 v0.1 | 品类矩阵、渠道结构、供应链切入仍需补。 |
| `acc_joyoung` | 九阳股份有限公司 | 九阳 | 零售消费 | 小家电 | 品牌消费品 | retail_high_sku_brand | L5 | B | 自然堂,晨光文具 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 小家电消费品牌画像成立，适合商品、渠道与库存分析，符合高 SKU 品牌消费品画像。 | 第七批放量候选池 v0.1 | 线上线下渠道颗粒度、库存协同仍需补。 |
| `acc_huangshanghuang` | 煌上煌集团食品股份有限公司 | 煌上煌 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 良品铺子,三只松鼠,王小卤 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 卤味休闲食品品牌属性明确，SKU 与全渠道动销分析空间明显，符合高 SKU 品牌消费品画像。 | 第八批放量候选池 v0.1 | 渠道结构、库存协同、加盟 / 直营网比例仍需补。 |
| `acc_qianweiyangchu` | 千味央厨食品股份有限公司 | 千味央厨 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 良品铺子,来伊份 | 商品 / 渠道 / 供应链协同分析 | ka_case_laiyifen_replenishment_v1 | 餐饮供应链与食品品牌双属性并存，适合商品与供应链协同画像，符合高 SKU 品牌消费品相邻画像。 | 第八批放量候选池 v0.1 | 渠道边界、品牌经营与供应链颗粒度仍需补。 |
| `acc_anjingfood` | 安井食品集团股份有限公司 | 安井食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 良品铺子,三只松鼠 | 商品 / 渠道 / 供应链协同分析 | ka_case_naturehall_ai_v1 | 冷冻食品与预制菜品牌画像成立，适合商品与渠道分析，符合品牌消费品画像。 | 第八批放量候选池 v0.1 | 渠道结构、供应链与库存颗粒度仍需补。 |
| `acc_laiyifen` | 上海来伊份股份有限公司 | 来伊份 | 零售消费 | 食品零售 | 连锁零售 | retail_multi_store | L5 | A | 鲜丰水果,周黑鸭,元祖 | 连锁零售经营分析平台 | ka_case_laiyifen_replenishment_v1,ka_case_xianfeng_retail_v1 | 零食连锁零售与商品经营特征强，适合总部经营透视与加盟选品 / 补货画像。 | 第十二批放量候选池 v0.1 | 门店网络、直营网 / 加盟结构与区域经营颗粒度仍需补。 |
| `acc_chj` | 潮宏基珠宝股份有限公司 | 潮宏基 | 零售消费 | 珠宝零售 | 连锁零售 | retail_multi_store | L5 | B | 周大生,博士眼镜 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 珠宝品牌零售与终端网络特征明显，符合多门店连锁零售画像。 | 第十二批放量候选池 v0.1 | 门店网络、直营网 / 加盟结构与区域经营仍需补。 |
| `acc_wfj` | 王府井集团股份有限公司 | 王府井 | 零售消费 | 百货零售 | 连锁零售 | retail_multi_store | L5 | B | 居然之家,名创优品 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 百货与购物中心经营网络特征成立，适合作为总部零售候选，符合多门店连锁零售画像。 | 第十二批放量候选池 v0.1 | 商场层级、区域经营与业态边界仍需补。 |
| `acc_greatstar` | 杭州巨星科技股份有限公司 | WORKPRO 等 | 跨境电商 | 工具出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 安克创新,赛维时代 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 工具与消费品海外经营属性明显，适合作为供应链复杂型跨境经营候选。 | 第七批放量候选池 v0.1 | 海外渠道结构、品牌矩阵、平台颗粒度仍需补。 |
| `acc_jeep_bike` | 久祺股份有限公司 | 久祺股份 | 跨境电商 | 出行出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 春风动力,涛涛车业 | 海外品牌经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 自行车出海与海外经营属性明确，品牌出海画像相邻。 | 第七批放量候选池 v0.1 | 海外平台结构、渠道网络、品牌矩阵仍需补。 |
| `acc_uechairs` | 永艺家具股份有限公司 | 永艺 | 跨境电商 | 家居出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 致欧家居,梦天家居 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 家居品牌出海与海外经营属性成立，符合品牌出海画像。 | 第七批放量候选池 v0.1 | 海外平台与客户结构、品牌经营颗粒度仍需补。 |
| `acc_impulse` | 英派斯健康科技股份有限公司 | 英派斯 | 跨境电商 | 运动器材出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 韶音,春风动力 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 运动器材出海与海外经营属性明确，品牌出海画像相邻。 | 第八批放量候选池 v0.1 | 海外平台结构、品牌矩阵、区域经营仍需补。 |
| `acc_petstar` | 源飞宠物用品股份有限公司 | 源飞宠物 | 跨境电商 | 宠物出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 乐其 SmallRig,安克创新 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 宠物用品出海与海外经营属性明确，符合品牌出海画像。 | 第八批放量候选池 v0.1 | 海外平台矩阵、品牌经营颗粒度仍需补。 |
| `acc_hlin` | 浙江恒林椅业股份有限公司 | 恒林股份 | 跨境电商 | 家居出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 致欧家居,梦天家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家居出海与海外经营特征明确，可作为跨境经营型候选。 | 第十批放量候选池 v0.1 | 海外渠道与品牌经营颗粒度仍需补。 |
| `acc_morhome` | 慕容家居控股有限公司 | 慕容家居 | 跨境电商 | 家居出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 致欧家居,梦天家居 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 家居品牌与海外经营属性并存，品牌出海画像相邻。 | 第十二批放量候选池 v0.1 | 海外渠道、品牌矩阵与经营主体映射仍需补。 |
| `acc_jiayi` | 嘉益股份有限公司 | 嘉益股份 | 跨境电商 | 保温器皿出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 安克创新,开润股份 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1 | 保温器皿品牌出海属性明确，品牌出海画像相邻。 | 第十二批放量候选池 v0.1 | 海外平台结构、品牌矩阵与经营颗粒度仍需补。 |
| `acc_saite` | 福建赛特新材股份有限公司 | 赛特新材 | 跨境电商 | 材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 吉宏股份,华利集团 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 材料出口与海外经营属性成立，适合作为复杂跨境经营候选。 | 第十二批放量候选池 v0.1 | 海外经营规模、客户结构与业务边界仍需补。 |
| `acc_daziran` | 浙江大自然户外用品股份有限公司 | 大自然 | 跨境电商 | 户外出海 | 品牌出海 | cbec_multi_platform_brand | L5 | B | 韶音,春风动力 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 户外用品与海外经营属性成立，品牌出海画像相邻。 | 第十一批放量候选池 v0.1 | 海外平台结构、品牌矩阵、区域经营仍需补。 |
| `acc_junsheng` | 宁波均胜电子股份有限公司 | 均胜电子 | 先进制造 | 汽车电子 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 德赛西威,立讯精密 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 汽车电子与全球制造协同属性强，多工厂制造画像成立。 | 第七批放量候选池 v0.1 | 业务条线、区域工厂与经营口径仍需补。 |
| `acc_yinlun` | 浙江银轮机械股份有限公司 | 银轮股份 | 先进制造 | 汽车零部件 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 伯特利,三花智控 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 热管理与零部件制造属性明确，技术型制造画像成立。 | 第七批放量候选池 v0.1 | 业务结构、全球经营与客户协同颗粒度仍需补。 |
| `acc_eefo` | 深圳新易盛通信技术股份有限公司 | 新易盛 | 先进制造 | 光通信制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | A | 中际旭创,天孚通信 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 光通信高技术制造属性明确，技术型制造画像成立。 | 第七批放量候选池 v0.1 | 组织颗粒度、全球经营与客户结构仍需补。 |
| `acc_jifeng` | 宁波继峰汽车零部件股份有限公司 | 继峰股份 | 先进制造 | 汽车零部件 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 拓普集团,伯特利 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 汽车零部件与全球工厂布局属性明显，多工厂画像成立。 | 第七批放量候选池 v0.1 | 工厂网络、事业部结构与经营颗粒度仍需补。 |
| `acc_hangcha` | 杭叉集团股份有限公司 | 杭叉集团 | 先进制造 | 工业车辆 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 卧龙电驱,徐工机械 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工业车辆与多基地制造特征明显，多工厂画像成立。 | 第八批放量候选池 v0.1 | 制造基地、区域经营与事业部结构仍需补。 |
| `acc_ikd` | 爱柯迪股份有限公司 | 爱柯迪 | 先进制造 | 汽车零部件 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 拓普集团,伯特利 | 多工厂经营驾驶舱 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 汽车零部件全球制造属性明显，多工厂画像成立。 | 第八批放量候选池 v0.1 | 工厂布局、事业部结构与全球经营仍需补。 |
| `acc_xcmg` | 徐工集团工程机械股份有限公司 | 徐工机械 | 先进制造 | 工程机械 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 三一重工,中联重科 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 工程机械与全球经营协同属性强，多工厂制造画像成立。 | 第九批放量候选池 v0.1 | 工厂布局、事业部与经营结构仍需补。 |
| `acc_jingsheng` | 浙江晶盛机电股份有限公司 | 晶盛机电 | 先进制造 | 半导体 / 光伏装备 | 技术型制造 | mfg_rnd_sales_complex | L5 | A | 北方华创,海天精工 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 半导体 / 光伏装备制造与高技术制造属性强，技术型制造画像成立。 | 第九批放量候选池 v0.1 | 业务条线、全球经营与经营颗粒度仍需补。 |
| `acc_haitianjg` | 宁波海天精工股份有限公司 | 海天精工 | 先进制造 | 高端机床 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 时代电气,秦川机床 | 多工厂经营驾驶舱 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 高端机床与制造协同属性明显，多工厂画像成立。 | 第十一批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |
| `acc_citic_hic` | 中信重工机械股份有限公司 | 中信重工 | 先进制造 | 重工装备 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 三一重工,机器人股份 | 集团经营驾驶舱与计划协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 重型装备与多业务协同特征明显，多工厂画像成立。 | 第十一批放量候选池 v0.1 | 工厂布局、业务条线与全球经营颗粒度仍需补。 |

## 5. 迁移后主表覆盖变化

### v0.2

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- 合计 `73`

### v0.3

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(首轮迁移)=30`
- 合计 `103`

## 6. 下一步建议

1. 为本轮新增的 `30` 家 `L5` 账户补第一条结构化证据
2. 从这 `30` 家中优先进入强核验的对象建议为：
   - 来伊份
   - 嘉益股份
   - 均胜电子
   - 徐工机械
   - 晶盛机电
   - 海天精工
3. 第二轮 `L5` 迁移继续优先：
   - 连锁餐饮 / 茶饮画像
   - 品牌出海画像
   - 多工厂制造与高技术制造画像

## 7. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.2.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.2.md)
- [account_review_queue_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-首版真实内容-v0.1.md)
- [外部目标客户池-v1.0-第七批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第八批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第九批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十一批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md)
- [外部目标客户池-v1.0-第十二批放量候选池-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md)
