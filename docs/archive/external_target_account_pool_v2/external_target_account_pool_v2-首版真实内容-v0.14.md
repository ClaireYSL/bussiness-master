# `external_target_account_pool_v2` 首版真实内容 v0.14

## 1. 文档目的

本文件在 [external_target_account_pool_v2-首版真实内容-v0.13.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.13.md) 基础上，完成第十二轮 `L5` 结构化迁移。

本轮继续优先回收早期候选文档中尚未完成结构化迁移、但画像边界稳定的一批对象。

## 2. 本轮迁移范围

### 已有基础

- `v0.13` 主表覆盖：`333`

### 本轮新增

- 第十二轮 `L5` 迁移：`20`
  - 零售消费：`8`
  - 跨境电商：`5`
  - 先进制造：`7`

### 本轮完成后

- 主表覆盖提升到 `353`

## 3. 第十二轮新增迁入的 L5 账户

| account_id | account_canonical_name | brand_name | primary_track | industry_l2 | business_model | persona_tag | pool_layer | static_priority | existing_customer_reference | solution_match | knowledge_asset_refs | admission_reason_summary | source_note | validation_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `acc_laofengxiang` | 老凤祥股份有限公司 | 老凤祥 | 零售消费 | 珠宝零售 | 连锁零售 | retail_multi_store | L5 | B | 周大生,中国黄金 | 连锁零售经营分析平台 | ka_case_xianfeng_retail_v1 | 珠宝零售终端网络特征明确，符合多门店连锁零售画像。 | 第十五批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_aimer` | 爱慕股份有限公司 | 爱慕 | 零售消费 | 服饰零售 | 品牌消费品 | retail_high_sku_brand | L5 | B | 海澜之家,赢家时尚 | 商品 / 渠道 / 品牌经营分析 | ka_case_naturehall_ai_v1 | 服饰内衣品牌与多 SKU 经营属性明确。 | 第十五批放量候选池 v0.1 | 渠道结构、品牌矩阵与会员经营仍需补。 |
| `acc_eeka` | 赢家时尚控股有限公司 | 赢家时尚 | 零售消费 | 服饰零售 | 连锁零售 | retail_multi_store | L5 | B | 海澜之家,森马服饰 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 多品牌服饰零售网络属性成立，适合总部经营透视画像。 | 第十五批放量候选池 v0.1 | 门店网络、品牌矩阵与区域经营仍需补。 |
| `acc_toread` | 探路者控股集团股份有限公司 | 探路者 | 零售消费 | 户外零售 | 连锁零售 | retail_multi_store | L5 | B | 孩子王,名创优品 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 户外品牌零售与直营网点属性成立。 | 第十五批放量候选池 v0.1 | 门店网络、直营网/加盟结构与区域经营仍需补。 |
| `acc_cofco_sugar` | 中粮糖业控股股份有限公司 | 中粮糖业 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 李子园,西王食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 糖类消费品经营属性成立，适合作为品牌消费品候选。 | 第十五批放量候选池 v0.1 | 品牌经营边界、渠道结构与库存协同仍需补。 |
| `acc_xinhe` | 欣贺股份有限公司 | JORYA / ANNAKRO | 零售消费 | 服饰零售 | 连锁零售 | retail_multi_store | L5 | B | 赢家时尚,爱慕 | 总部经营透视与区域经营分析 | ka_case_xianfeng_retail_v1 | 多品牌女装零售网络特征明显。 | 第十五批放量候选池 v0.1 | 门店网络、品牌矩阵与区域经营仍需补。 |
| `acc_xiwang` | 西王食品股份有限公司 | 西王食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 光明乳业,三元食品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 食用油与健康食品品牌属性明确。 | 第十五批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_sanyuan` | 北京三元食品股份有限公司 | 三元食品 | 零售消费 | 食品饮料 | 品牌消费品 | retail_high_sku_brand | L5 | B | 光明乳业,熊猫乳品 | 商品 / 渠道 / 动销增长分析 | ka_case_naturehall_ai_v1 | 乳品品牌与渠道经营属性明确。 | 第十五批放量候选池 v0.1 | 渠道结构、品牌矩阵与库存协同仍需补。 |
| `acc_comix` | 深圳齐心集团股份有限公司 | 齐心集团 | 跨境电商 | 办公用品出海 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 焦点科技,乐歌股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 办公用品与海外经营属性并存，符合复杂跨境经营画像。 | 第十五批放量候选池 v0.1 | 海外经营规模、客户结构与业务边界仍需补。 |
| `acc_tomtop` | 深圳市通拓科技有限公司 | 通拓科技 | 跨境电商 | 跨境品牌出海 | 品牌出海 | cbec_brand_outbound | L5 | B | 赛维时代,有棵树 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 跨境电商经营属性明确，适合作为品牌出海相邻候选。 | 第十五批放量候选池 v0.1 | 平台结构、品牌矩阵与经营颗粒度仍需补。 |
| `acc_eccang` | 深圳市易仓科技有限公司 | 易仓科技 | 跨境电商 | 跨境平台服务 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 焦点科技,吉宏股份 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 跨境经营工具与平台服务属性成立，复杂跨境经营画像相邻。 | 第十五批放量候选池 v0.1 | 平台业务边界、客户结构与场景范围仍需补。 |
| `acc_youkeshu` | 深圳市有棵树科技股份有限公司 | 有棵树 | 跨境电商 | 跨境品牌出海 | 品牌出海 | cbec_brand_outbound | L5 | B | 赛维时代,华凯易佰 | 品牌出海经营分析 | ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1 | 多平台跨境经营属性明确，适合作为品牌出海型候选。 | 第十五批放量候选池 v0.1 | 平台结构、品牌矩阵与经营主体映射仍需补。 |
| `acc_zhengyu` | 浙江正裕工业股份有限公司 | 正裕工业 | 跨境电商 | 汽车零部件出口 | 复杂跨境经营 | cbec_supply_chain_complex | L5 | B | 恒勃股份,拓普集团 | 复杂跨境经营分析 | ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1 | 汽车零部件与海外经营属性成立，复杂跨境经营画像成立。 | 第十五批放量候选池 v0.1 | 海外客户结构、品牌边界与经营颗粒度仍需补。 |
| `acc_donlim` | 广东新宝电器股份有限公司 | 新宝电器 | 先进制造 | 小家电制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 德业股份,富佳股份 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 小家电制造与多基地经营属性成立。 | 第十五批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |
| `acc_slac` | 苏州斯莱克精密设备股份有限公司 | 斯莱克 | 先进制造 | 精密设备制造 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 海目星,先导智能 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 精密设备与高端制造协同属性明确。 | 第十五批放量候选池 v0.1 | 业务结构、客户协同与全球经营仍需补。 |
| `acc_uwlaser` | 江苏联赢激光股份有限公司 | 联赢激光 | 先进制造 | 激光装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海目星,杭可科技 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 激光焊接装备与新能源链条制造协同属性成立。 | 第十五批放量候选池 v0.1 | 工厂布局、业务条线与客户结构仍需补。 |
| `acc_injet` | 英杰电气股份有限公司 | 英杰电气 | 先进制造 | 电源控制设备 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 汇川技术,雷赛智能 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 电源控制与高技术制造协同属性成立。 | 第十五批放量候选池 v0.1 | 业务结构、客户协同与经营颗粒度仍需补。 |
| `acc_boci` | 柏楚电子科技股份有限公司 | 柏楚电子 | 先进制造 | 工控软件与控制系统 | 技术型制造 | mfg_rnd_sales_complex | L5 | B | 雷赛智能,信捷电气 | 技术型制造经营协同 | ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1 | 工业软件与控制系统属性成立，技术型制造画像相邻。 | 第十五批放量候选池 v0.1 | 软件与设备边界、客户结构与经营颗粒度仍需补。 |
| `acc_pioneer_tech` | 先惠技术股份有限公司 | 先惠技术 | 先进制造 | 智能装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 海目星,联赢激光 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 智能装备与新能源制造协同属性成立。 | 第十五批放量候选池 v0.1 | 工厂布局、业务条线与客户结构仍需补。 |
| `acc_topstar` | 拓斯达科技股份有限公司 | 拓斯达 | 先进制造 | 自动化装备制造 | 多工厂制造 | mfg_multi_factory_group | L5 | B | 汇川技术,怡合达 | 集团经营驾驶舱与计划协同 | ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1 | 自动化与智能制造装备属性明确，多工厂画像相邻。 | 第十五批放量候选池 v0.1 | 工厂布局、业务条线与全球经营仍需补。 |

## 4. 迁移后主表覆盖变化

### v0.13

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=260`
- 合计 `333`

### v0.14

- `L1=8`
- `L2=36`
- `L3=15`
- `L4=14`
- `L5(累计已迁移)=280`
- 合计 `353`

## 5. 下一步建议

1. 为本轮新增 `20` 家账户补第一条结构化证据
2. 优先强核验：
   - 稳健医疗
   - 焦点科技
   - 海天精工
   - 东山精密
   - 新宝电器
   - 联赢激光
