# `external_target_account_pool_v2` 首版真实内容 v0.13

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.12.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.12.md) 基础上，完成第十一轮 `L5` 结构化迁移。

本轮优先回收早期候选文档中尚未完成结构化迁移、但画像边界稳定的一批对象。

## 2. 本轮迁移范围

### 已有基础

- `v0.12` 主表覆盖：`313`

### 本轮新增

- 第十一轮 `L5` 迁移：`20`
  - 零售消费：`8`
  - 跨境电商：`5`
  - 先进制造：`7`

### 本轮完成后

- 主表覆盖提升到 `333`

## 3. 第十一轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_winnermedical` | 稳健医疗用品股份有限公司 | 稳健医疗 / 全棉时代 | 零售消费 | 医疗消费品 | 品牌消费品 | retail_high_sku_brand | L5 | A | 自然堂,贝泰妮 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 医疗消费品与品牌经营双属性并存，适合作为高 SKU 品牌消费品高优先级候选。 | 第十四批放量候选池 v0.1 | 品牌矩阵、渠道结构与库存协同仍需补。 |
| `acc_zhouliufu` | 周六福珠宝股份有限公司 | 周六福 | 零售消费 | 珠宝零售 | 连锁零售 | retail_multi_store | L5 | B | 周大生,潮宏基 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 珠宝零售网络属性明确，符合多门店连锁零售画像。 | 第十四批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_chinagold` | 中国黄金集团黄金珠宝股份有限公司 | 中国黄金 | 零售消费 | 珠宝零售 | 连锁零售 | retail_multi_store | L5 | B | 周大生,老凤祥 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 珠宝零售终端网络特征成立，适合作为总部零售候选。 | 第十四批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_botanee` | 贝泰妮集团股份有限公司 | 薇诺娜 | 零售消费 | 美妆个护 | 品牌消费品 | retail_high_sku_brand | L5 | A | 自然堂,花西子 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 美妆个护品牌属性强，适合作为高 SKU 品牌消费品高优先级候选。 | 第十四批放量候选池 v0.1 | 渠道结构、品牌矩阵与会员经营仍需补。 |
| `acc_jinzai` | 劲仔食品集团股份有限公司 | 劲仔 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 盐津铺子,良品铺子 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 休闲食品品牌与多 SKU 经营特征明确。 | 第十四批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_ganyuan` | 甘源食品股份有限公司 | 甘源 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 盐津铺子,洽洽食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 休闲食品品牌属性明显，商品与渠道分析空间成立。 | 第十四批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_qiaqia` | 洽洽食品股份有限公司 | 洽洽 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | A | 三只松鼠,盐津铺子 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 坚果零食品牌与多产品经营属性强，适合高 SKU 品牌消费品画像。 | 第十四批放量候选池 v0.1 | 渠道结构、库存协同与品牌矩阵仍需补。 |
| `acc_pandarb` | 熊猫乳品集团股份有限公司 | 熊猫乳品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 光明乳业,妙可蓝多 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 乳品品牌属性明确，SKU 与渠道经营特征明显。 | 第十四批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_focus` | 焦点科技股份有限公司 | 中国制造网 | 跨境电商 | 跨境平台服务 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | A | 赛维时代,致欧家居 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 平台型出海服务与跨境经营属性明确，适合作为复杂跨境经营高优先级候选。 | 第十四批放量候选池 v0.1 | 平台业务边界、客户结构与海外经营颗粒度仍需补。 |
| `acc_intco_medical` | 英科医疗科技股份有限公司 | 英科医疗 | 跨境电商 | 医疗耗材出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 英科再生,稳健医疗 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 医疗耗材与海外经营属性并存，复杂跨境经营画像成立。 | 第十四批放量候选池 v0.1 | 海外业务占比、客户结构与品牌边界仍需补。 |
| `acc_intco_recycling` | 英科再生资源股份有限公司 | 英科再生 | 跨境电商 | 再生材料出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 华生科技,麦加芯彩 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 再生材料与海外经营属性成立，符合复杂跨境经营画像。 | 第十四批放量候选池 v0.1 | 海外经营规模、客户结构与业务边界仍需补。 |
| `acc_huaci` | 华瓷股份有限公司 | 华瓷股份 | 跨境电商 | 日用陶瓷出海 | 品牌出海 | cbec_brand_outbound | L5 | B | 匠心家居,哈尔斯 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 日用陶瓷与海外经营属性明确，品牌出海画像相邻。 | 第十四批放量候选池 v0.1 | 海外渠道、品牌矩阵与平台结构仍需补。 |
| `acc_kaidi` | 常州凯迪电器股份有限公司 | 凯迪股份 | 跨境电商 | 家电配套出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 富佳股份,乐歌股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 家电配套与出口属性成立，符合复杂跨境经营画像。 | 第十四批放量候选池 v0.1 | 海外客户结构、品牌边界与经营颗粒度仍需补。 |
| `acc_hymson` | 海目星激光科技集团股份有限公司 | 海目星 | 先进制造 | 激光装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 先导智能,杭可科技 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 激光装备与新能源链条制造协同属性成立。 | 第十四批放量候选池 v0.1 | 工厂布局、业务条线与客户结构仍需补。 |
| `acc_yiheda` | 怡合达自动化股份有限公司 | 怡合达 | 先进制造 | 自动化零部件 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,中大力德 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 自动化零部件与平台化供给属性并存，技术型制造画像成立。 | 第十四批放量候选池 v0.1 | 业务结构、客户协同与经营颗粒度仍需补。 |
| `acc_haitian_prec` | 海天精工股份有限公司 | 海天精工 | 先进制造 | 机床装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 创世纪,亚威股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 机床装备与多基地制造属性明显，多工厂画像成立。 | 第十四批放量候选池 v0.1 | 工厂布局、事业部与区域经营仍需补。 |
| `acc_hangke` | 杭可科技股份有限公司 | 杭可科技 | 先进制造 | 锂电设备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 先导智能,海目星 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 锂电设备制造与多基地经营属性成立。 | 第十四批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |
| `acc_dsbj` | 东山精密制造股份有限公司 | 东山精密 | 先进制造 | 精密制造 | 多工厂制造 | mfg_multi_factory_group | L5 | A | 立讯精密,蓝思科技 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 精密制造与多基地协同属性强，适合作为多工厂制造高优先级候选。 | 第十四批放量候选池 v0.1 | 工厂布局、事业部与区域经营仍需补。 |
| `acc_sinomach_precision` | 国机精工集团股份有限公司 | 国机精工 | 先进制造 | 精密功能材料 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 上海新阳,中密控股 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 精密功能材料与高端制造协同属性成立。 | 第十四批放量候选池 v0.1 | 业务结构、客户协同与经营颗粒度仍需补。 |
| `acc_rifa` | 浙江日发精密机械股份有限公司 | 日发精机 | 先进制造 | 精密机械制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海天精工,创世纪 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 机床与精密机械制造属性明确，多工厂画像相邻。 | 第十四批放量候选池 v0.1 | 工厂布局、业务条线与区域经营仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.12

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=240`
- 合计 `313`

### v0.13

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=260`
- 合计 `333`

## 5. 下一步建议

1. 为本轮新增 `20` 家账户补第一条结构化证据
2. 优先强核验：
   - 稳健医疗
   - 贝泰妮
   - 洽洽
   - 焦点科技
   - 海天精工
   - 东山精密
