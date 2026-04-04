# `persona_registry_v1` 首版真实内容 v0.1

## 1. 文档目的

本文件基于现有画像规则、真实建池结果和内部案例学习，给出 `persona_registry_v1` 的第一版真实注册内容。

本文件不是字段规范，字段规范见：

- [persona_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/persona_registry_v1-字段模板-v1.md)

## 2. 当前建议启用的首版画像

当前建议先启用 `7` 个画像：

1. `retail_multi_store`
2. `retail_high_sku_brand`
3. `retail_chain_fnb`
4. `cbec_multi_platform_brand`
5. `cbec_supply_chain_complex`
6. `mfg_multi_factory_group`
7. `mfg_rnd_sales_complex`

## 3. 首版真实记录

### 3.1 `retail_multi_store`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `retail_multi_store` |
| `persona_version` | `v1` |
| `persona_name` | `多门店连锁零售` |
| `track_id` | `retail_consumer` |
| `status` | `active` |
| `definition` | 总部管理半径大、门店和区域经营差异显著、需要从总部到区域到门店做经营穿透和动作闭环的连锁零售企业。 |
| `fit_criteria` | 连锁零售/商超便利/连锁服务；多门店、多区域、总部强管理；门店经营复盘频繁。 |
| `non_fit_boundary` | 单店或少量门店的小品牌；主要依赖单一电商渠道、没有明显线下管理半径的公司。 |
| `typical_jtbd` | 总部经营透视、门店经营健康度、区域差异分析、一线动作闭环。 |
| `complexity_signals` | 多门店、多区域、多层级管理、总部到门店协同。 |
| `reference_customers` | `鲜丰水果,来伊份,博士眼镜,7-Eleven` |
| `reference_cases` | `鲜丰水果类案例,来伊份补货场景,ChatBI 一线场景材料` |
| `reference_solutions` | `连锁零售经营分析平台,总部到门店经营穿透,门店经营健康度与动作闭环场景` |
| `admission_hint` | 优先识别全国或区域性连锁零售集团、商超便利、连锁服务品牌，不能只看行业名，要看管理半径。 |
| `promotion_hint` | 若有官方资料明确门店网络、区域经营和总部管理结构，可较快上移。 |

### 3.2 `retail_high_sku_brand`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `retail_high_sku_brand` |
| `persona_version` | `v1` |
| `persona_name` | `高 SKU 品牌消费品` |
| `track_id` | `retail_consumer` |
| `status` | `active` |
| `definition` | SKU 多、渠道复杂、库存与动销压力大，需要围绕商品、渠道、库存和业财供协同做经营分析的品牌消费品企业。 |
| `fit_criteria` | 美妆个护、食品饮料、母婴宠物、品牌消费品；高 SKU；多渠道；库存和补货决策复杂。 |
| `non_fit_boundary` | SKU 极少、渠道极简单、主要依赖单一销售路径的品牌。 |
| `typical_jtbd` | 商品与库存优化、渠道与动销分析、业财供协同、补货与分货决策。 |
| `complexity_signals` | 高 SKU、多渠道、库存压力大、商品经营复杂。 |
| `reference_customers` | `自然堂,君乐宝,王小卤,元气森林` |
| `reference_cases` | `自然堂 AI 实践,品牌消费品和美妆个护案例集` |
| `reference_solutions` | `渠道/商品/动销增长分析,业财供协同,补货与库存场景` |
| `admission_hint` | 不只看消费品标签，要看 SKU 复杂度、渠道复杂度和库存联动压力。 |
| `promotion_hint` | 若能找到官方或年报级资料支撑渠道结构、SKU 复杂度和库存/动销场景，可快速从 L5 往上提。 |

### 3.3 `retail_chain_fnb`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `retail_chain_fnb` |
| `persona_version` | `v1` |
| `persona_name` | `连锁餐饮 / 茶饮 / 咖啡` |
| `track_id` | `retail_consumer` |
| `status` | `active` |
| `definition` | 门店运营高度标准化、总部强管理、多区域扩张明显，需要从总部到区域到门店做经营、商品、会员和督导动作分析的连锁餐饮/茶饮/咖啡品牌。 |
| `fit_criteria` | 连锁餐饮、茶饮、咖啡；多门店、多区域、总部强运营；门店经营频次高、督导动作密集。 |
| `non_fit_boundary` | 单店餐饮、区域单点品牌、仅靠轻量 POS 报表即可满足经营管理的主体。 |
| `typical_jtbd` | 门店经营透视、区域赛马、督导与店长动作闭环、商品与活动复盘。 |
| `complexity_signals` | 多门店、多区域、高频复盘、一线动作密集。 |
| `reference_customers` | `老乡鸡,奈雪的茶` |
| `reference_cases` | `老乡鸡数字化转型案例,ChatBI 一线应用材料` |
| `reference_solutions` | `连锁门店运营分析,一线问数与巡店场景,总部经营驾驶舱` |
| `admission_hint` | 应优先找连锁规模已成型、总部管控强、复盘节奏高的品牌，而不是泛餐饮。 |
| `promotion_hint` | 如果能找到门店规模、区域扩张和总部经营分析诉求的明确信号，可进入高质量补充样本层。 |

### 3.4 `cbec_multi_platform_brand`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `cbec_multi_platform_brand` |
| `persona_version` | `v1` |
| `persona_name` | `多平台品牌出海型` |
| `track_id` | `cross_border_ecommerce` |
| `status` | `active` |
| `definition` | 在多个跨境平台和多个国家市场运营，需要在市场洞察、选品、平台经营和利润分析之间建立统一分析框架的品牌出海企业。 |
| `fit_criteria` | 品牌出海；多平台；多店铺；多国家；海外业务体量较大。 |
| `non_fit_boundary` | 只在单平台、单区域、小规模试水的跨境卖家。 |
| `typical_jtbd` | 多平台精细化运营、T+1 利润分析、市场洞察与选品、海外业务经营驾驶舱。 |
| `complexity_signals` | 多平台、多店铺、多国家、多币种。 |
| `reference_customers` | `乐其 SmallRig,安克创新,致欧家居` |
| `reference_cases` | `出海标杆客户案例集（东南亚）,跨境 ABM 物料` |
| `reference_solutions` | `跨境利润分析,市场洞察与选品,多平台经营分析` |
| `admission_hint` | 优先识别品牌化程度高、多平台多区域经营成熟的主体，不泛抓所有跨境卖家。 |
| `promotion_hint` | 若能找到官方资料明确平台结构、国家分布和海外经营复杂度，可作为稳定扩池标尺。 |

### 3.5 `cbec_supply_chain_complex`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `cbec_supply_chain_complex` |
| `persona_version` | `v1` |
| `persona_name` | `供应链复杂的跨境经营型企业` |
| `track_id` | `cross_border_ecommerce` |
| `status` | `active` |
| `definition` | 跨境履约链路长、库存和供需平衡复杂、利润核算和业财协同压力大的跨境经营主体。 |
| `fit_criteria` | 海外仓、跨境供应链、履约链路长、利润核算复杂、供需平衡显性化。 |
| `non_fit_boundary` | 仅做轻量跨境分销、没有明显库存/履约/利润复杂度的公司。 |
| `typical_jtbd` | 库存与供需平衡、业财一体化、履约链路分析、T+1 利润分析。 |
| `complexity_signals` | 长物流链路、海外仓、利润核算复杂、供需协同复杂。 |
| `reference_customers` | `赛维时代,华凯易佰,正浩 EcoFlow` |
| `reference_cases` | `跨境电商拓展材料,跨境 JTBD 总结,跨境 ABM 物料` |
| `reference_solutions` | `跨境供应链经营分析,库存与利润联动分析,业财一体化` |
| `admission_hint` | 重点看利润、库存、履约复杂度，不只看跨境规模。 |
| `promotion_hint` | 若能明确海外仓、履约链路和财务协同复杂度，可上移为中高可信或高可信补充样本。 |

### 3.6 `mfg_multi_factory_group`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `mfg_multi_factory_group` |
| `persona_version` | `v1` |
| `persona_name` | `多工厂离散制造集团` |
| `track_id` | `advanced_manufacturing` |
| `status` | `active` |
| `definition` | 拥有多个工厂、产线和事业部，需要通过经营驾驶舱和计划协同实现集团级管理透明化的制造企业。 |
| `fit_criteria` | 离散制造；多工厂；多事业部；集团化经营；管理协同链条长。 |
| `non_fit_boundary` | 单工厂、单事业部、经营链路简单的制造企业；仅强调底层生产控制而不强调经营协同的工厂型项目。 |
| `typical_jtbd` | 集团经营驾驶舱、多工厂计划协同、LTC 与经营透明化。 |
| `complexity_signals` | 多工厂、多事业部、集团化经营、协同链条长。 |
| `reference_customers` | `零跑汽车,汇川技术,立讯精密` |
| `reference_cases` | `零跑汽车自助式数据服务体系,昊志机电经营驾驶舱类材料` |
| `reference_solutions` | `制造业经营驾驶舱,LTC,多工厂计划协同` |
| `admission_hint` | 应优先找多工厂、多事业部、集团管理透明化诉求明显的制造集团。 |
| `promotion_hint` | 若存在年报级集团经营结构和制造复杂度证据，可较快上移。 |

### 3.7 `mfg_rnd_sales_complex`

| 字段 | 内容 |
| --- | --- |
| `persona_id` | `mfg_rnd_sales_complex` |
| `persona_version` | `v1` |
| `persona_name` | `研产销协同复杂的技术型制造企业` |
| `track_id` | `advanced_manufacturing` |
| `status` | `active` |
| `definition` | 研发、生产、销售和渠道链路长，且经营透明化、渠道效率、项目型协同压力显著的技术型制造企业。 |
| `fit_criteria` | 技术型制造、医疗器械/设备/高端装备、研产销协同复杂、渠道链条长。 |
| `non_fit_boundary` | 单一加工型工厂、缺乏经营协同和渠道复杂度的普通制造主体。 |
| `typical_jtbd` | 财务/生产/质量/存货联动、渠道效率分析、项目型经营透明化、集团经营协同。 |
| `complexity_signals` | 研产销链路长、项目型交付、渠道链条复杂、高端制造属性。 |
| `reference_customers` | `迈瑞医疗,联影医疗,中航光电,时代电气` |
| `reference_cases` | `昊志机电战略升级材料,制造业拓展 2026 材料` |
| `reference_solutions` | `经营型 BI,价值流分析,业财产销协同` |
| `admission_hint` | 不按“是否制造业”粗抓，而看是否具备技术型制造和经营协同复杂度。 |
| `promotion_hint` | 若能找到年报、官网或 IR 对复杂产品线、事业部、渠道和协同结构的强证据，可上移。 |

## 4. 当前不建议直接启用的新画像

以下方向可以研究，但当前不建议直接设为 `active`：

- 零售消费中的 `商超便利深分画像`
- 先进制造中的 `CDMO 专用画像`
- 医药医疗主线下新画像

原因：

- 当前已有画像还能覆盖主要入池判断，新的细分画像会让首版注册表过早膨胀。

## 5. 当前使用建议

1. `external_target_account_pool_v2` 首版迁移时，账户只能先挂这 7 个 `active` 画像之一。
2. 如果某账户同时像多个画像，先定主画像，其他画像留到补充说明或知识资产中。
3. 新画像先走 `draft`，不要先在账户表里临时发明名称。

## 6. 关联文档

- [persona_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/persona_registry_v1-字段模板-v1.md)
- [外部目标客户池-v1.0-画像映射规则.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/archive/外部目标客户池-v1.0/外部目标客户池-v1.0-画像映射规则.md)
- [外部目标客户池-v1.0-画像映射表示例.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/archive/外部目标客户池-v1.0/外部目标客户池-v1.0-画像映射表示例.md)
