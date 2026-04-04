# `knowledge_asset_registry_v1` 首版真实内容 v0.1

## 1. 文档目的

本文件基于已经学习过的内部/外部客户案例、解决方案材料和映射事实，给出 `knowledge_asset_registry_v1` 的第一版真实内容。

本文件不是字段规范，字段规范见：

- [knowledge_asset_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/knowledge_asset_registry_v1-字段模板-v1.md)

## 2. 首版真实内容设计原则

首版不追求“把所有材料一次性抽完”，而是先抽 `12` 条高价值知识资产，覆盖：

- 零售消费主阵地
- 跨境电商重点拓展
- 先进制造重点拓展
- 品牌/主体映射事实

## 3. 首版真实知识资产

### 3.1 零售消费

#### `ka_case_naturehall_ai_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_naturehall_ai_v1` |
| `asset_type` | `customer_case` |
| `title` | `自然堂全渠道数字化创新与 AI 实践` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace/geo-content/sources/L1客户案例/自然堂全渠道数字化创新和AI实践.docx` |
| `source_origin` | `internal` |
| `track_ids` | `retail_consumer` |
| `persona_ids` | `retail_high_sku_brand` |
| `customer_refs` | `自然堂,伽蓝集团` |
| `jtbd_tags` | `渠道动销分析,商品与库存优化,AI+BI 升级` |
| `complexity_tags` | `高 SKU,多渠道,品牌消费品` |
| `summary` | 该资产支撑高 SKU 品牌消费品如何从全渠道数字化与 AI 实践切入，说明品牌消费品的商品、渠道、库存和智能洞察诉求具备稳定可复制性。 |
| `key_signals` | 高 SKU、多渠道、品牌消费品；观远不是只做报表，而是做全渠道经营分析与 AI 实践。 |
| `recommended_usage` | 入池判断、画像解释、样本映射、用户建议生成。 |
| `confidence_level` | `高` |

#### `ka_case_xianfeng_retail_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_xianfeng_retail_v1` |
| `asset_type` | `customer_case` |
| `title` | `鲜丰水果等连锁零售经营分析样本` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/archive/外部目标客户池-v1.0/外部目标客户池-v1.0-画像映射表示例.md` |
| `source_origin` | `internal` |
| `track_ids` | `retail_consumer` |
| `persona_ids` | `retail_multi_store` |
| `customer_refs` | `鲜丰水果,来伊份,博士眼镜` |
| `jtbd_tags` | `总部经营透视,门店经营健康度,区域差异分析` |
| `complexity_tags` | `多门店,多区域,总部强管理` |
| `summary` | 该资产沉淀了多门店连锁零售的样本锚点，可用于判断哪些零售企业属于总部强管理、多区域、多门店、高频复盘型对象。 |
| `key_signals` | 多门店、多区域、门店动作闭环；适合做连锁零售经营分析平台型切入。 |
| `recommended_usage` | 多门店连锁零售入池判断、画像校准、上移比对。 |
| `confidence_level` | `高` |

#### `ka_case_laiyifen_replenishment_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_laiyifen_replenishment_v1` |
| `asset_type` | `scenario_pack` |
| `title` | `来伊份加盟选品与补货难点场景` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0501-电商客户典型案例/9｜电商代运营（TP_DP）/来伊份的补货场景预期的难点.md` |
| `source_origin` | `internal` |
| `track_ids` | `retail_consumer` |
| `persona_ids` | `retail_multi_store,retail_high_sku_brand` |
| `customer_refs` | `来伊份` |
| `jtbd_tags` | `加盟选品,补货决策,降低加盟门槛` |
| `complexity_tags` | `加盟体系,商品复杂,补货复杂` |
| `summary` | 该资产说明客户口头说的“库存调拨/补货”背后，真实任务可能是加盟扩张下如何降低选品与补货决策门槛。 |
| `key_signals` | 不只看功能词，要看经营阶段和加盟扩张背景。 |
| `recommended_usage` | 画像边界修正、入池理由深化、用户建议生成。 |
| `confidence_level` | `高` |

#### `ka_case_chatbi_frontline_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_chatbi_frontline_v1` |
| `asset_type` | `sales_narrative` |
| `title` | `ChatBI 在督导、店长、一线场景中的应用叙事` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0501-电商客户典型案例/9｜电商代运营（TP_DP）/督导巡店、门店管理不用愁：观远ChatBI在一线业务场景中的实战应用.md` |
| `source_origin` | `internal` |
| `track_ids` | `retail_consumer` |
| `persona_ids` | `retail_multi_store,retail_chain_fnb` |
| `customer_refs` | `` |
| `jtbd_tags` | `一线问数,督导巡店,店长动作闭环` |
| `complexity_tags` | `一线动作密集,总部到门店链路长` |
| `summary` | 该资产说明观远的 AI+BI 能力可以下沉到督导、店长和一线业务动作，不只服务总部报表。 |
| `key_signals` | 一线角色是 AI+BI 的新突破口；适合给前线解释为什么这类连锁企业值得入池。 |
| `recommended_usage` | 用户建议生成、画像解释、AI+BI 匹配判断。 |
| `confidence_level` | `高` |

### 3.2 跨境电商

#### `ka_case_smallrig_outbound_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_smallrig_outbound_v1` |
| `asset_type` | `customer_case` |
| `title` | `乐其 SmallRig 出海样本` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/客户案例与合作主体映射-v1.md` |
| `source_origin` | `internal` |
| `track_ids` | `cross_border_ecommerce` |
| `persona_ids` | `cbec_multi_platform_brand` |
| `customer_refs` | `乐其 SmallRig` |
| `jtbd_tags` | `品牌出海,多平台经营,海外业务分析` |
| `complexity_tags` | `品牌出海,多平台,多国家` |
| `summary` | 该资产作为现有出海样本锚点，用于解释品牌出海型企业为何属于观远可打的跨境画像。 |
| `key_signals` | 品牌化出海、多平台经营、海外业务复杂度。 |
| `recommended_usage` | 样本映射、账户解释、跨境画像校准。 |
| `confidence_level` | `中` |

#### `ka_solution_cbec_profit_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_solution_cbec_profit_v1` |
| `asset_type` | `solution_playbook` |
| `title` | `跨境 T+1 利润分析与业财一体化打法` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/additional_folder/跨境电商/跨境电商出海吧🚢.md` |
| `source_origin` | `internal` |
| `track_ids` | `cross_border_ecommerce` |
| `persona_ids` | `cbec_multi_platform_brand,cbec_supply_chain_complex` |
| `customer_refs` | `` |
| `jtbd_tags` | `T+1 利润分析,业财一体化,库存与供需平衡` |
| `complexity_tags` | `多平台,多店铺,利润核算复杂` |
| `summary` | 该资产凝练了跨境电商最关键的解决方案抓手：市场洞察与选品、多平台精细化运营、库存与供需平衡、T+1 利润分析。 |
| `key_signals` | 跨境电商不是泛行业，而是围绕利润、库存、平台经营复杂度来判断。 |
| `recommended_usage` | 入池理由生成、方案匹配、用户建议生成。 |
| `confidence_level` | `高` |

#### `ka_insight_cbec_abm_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_insight_cbec_abm_v1` |
| `asset_type` | `industry_insight` |
| `title` | `跨境电商 ABM 物料与 ICP 洞察` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/additional_folder/跨境电商/跨境电商 - ABM物料.md` |
| `source_origin` | `internal` |
| `track_ids` | `cross_border_ecommerce` |
| `persona_ids` | `cbec_multi_platform_brand,cbec_supply_chain_complex` |
| `customer_refs` | `` |
| `jtbd_tags` | `ABM,行业敲门砖,样板客户复制` |
| `complexity_tags` | `中腰部高复杂度` |
| `summary` | 该资产说明跨境电商已经不是“研究阶段”，而是已具备 ABM 物料、Top 案例和相对明确的 ICP。 |
| `key_signals` | 优先找多平台、多店铺、有 IT/数据能力、利润和库存问题显性化的中腰部客户。 |
| `recommended_usage` | 行业扩充、用户建议生成、账户筛选收口。 |
| `confidence_level` | `高` |

#### `ka_insight_cbec_jtbd_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_insight_cbec_jtbd_v1` |
| `asset_type` | `industry_insight` |
| `title` | `跨境电商核心 JTBD 洞察` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/内部客户案例系统学习-2026-03-28.md` |
| `source_origin` | `internal` |
| `track_ids` | `cross_border_ecommerce` |
| `persona_ids` | `cbec_multi_platform_brand,cbec_supply_chain_complex` |
| `customer_refs` | `` |
| `jtbd_tags` | `市场洞察与选品,多平台运营,库存与供需平衡,T+1 利润分析` |
| `complexity_tags` | `多平台,多店铺,多国家,多币种` |
| `summary` | 该资产把跨境电商的核心任务收敛为市场洞察与选品、多平台精细化运营、库存与供需平衡、T+1 利润分析四条主线。 |
| `key_signals` | 找跨境潜客时，不该只写“跨境企业”，而应看平台经营、利润核算和库存协同是否复杂。 |
| `recommended_usage` | 新账户入池、画像解释、用户建议生成。 |
| `confidence_level` | `高` |

### 3.3 先进制造

#### `ka_case_haozhi_dashboard_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_haozhi_dashboard_v1` |
| `asset_type` | `customer_case` |
| `title` | `昊志机电经营驾驶舱与战略升级叙事` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0501-电商客户典型案例/9｜电商代运营（TP_DP）/为高速战机装上“数字驾驶舱”：昊志机电如何驾驭数据，实现战略升级.md` |
| `source_origin` | `internal` |
| `track_ids` | `advanced_manufacturing` |
| `persona_ids` | `mfg_multi_factory_group,mfg_rnd_sales_complex` |
| `customer_refs` | `昊志机电` |
| `jtbd_tags` | `经营驾驶舱,价值流管理,战略升级` |
| `complexity_tags` | `研产销协同,集团管理,经营透明化` |
| `summary` | 该资产证明制造业方向的强项不是工厂控制替代，而是经营驾驶舱、价值流管理和管理标准化复制。 |
| `key_signals` | 制造业要从经营型 BI 切入，而不是泛智慧工厂。 |
| `recommended_usage` | 先进制造画像解释、上移核验、行业建议。 |
| `confidence_level` | `高` |

#### `ka_case_zerorun_self_service_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_case_zerorun_self_service_v1` |
| `asset_type` | `customer_case` |
| `title` | `零跑汽车自助式数据服务体系` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace/geo-content/sources/L1客户案例/不用3年只需3个月，零跑汽车建立「自助餐式」数据服务体系.docx` |
| `source_origin` | `internal` |
| `track_ids` | `advanced_manufacturing` |
| `persona_ids` | `mfg_multi_factory_group` |
| `customer_refs` | `零跑汽车` |
| `jtbd_tags` | `自助分析,经营协同,数据服务体系` |
| `complexity_tags` | `多组织协同,制造+经营联动` |
| `summary` | 该资产作为先进制造和复杂经营协同样本，可用于说明技术型制造和汽车相关复杂经营主体具备观远可复制的自助分析与经营协同需求。 |
| `key_signals` | 自助分析体系和经营协同能力，可外推到多事业部、多工厂类制造集团。 |
| `recommended_usage` | 样本映射、账户解释、上移核验。 |
| `confidence_level` | `高` |

#### `ka_insight_mfg_value_stream_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_insight_mfg_value_stream_v1` |
| `asset_type` | `industry_insight` |
| `title` | `制造业从商业价值流切入的行业洞察` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/additional_folder/泛制造/制造业拓展2026（持续更新中）.md` |
| `source_origin` | `internal` |
| `track_ids` | `advanced_manufacturing` |
| `persona_ids` | `mfg_multi_factory_group,mfg_rnd_sales_complex` |
| `customer_refs` | `` |
| `jtbd_tags` | `LTC,计划协同,价值流管理` |
| `complexity_tags` | `多工厂,多事业部,价值链长` |
| `summary` | 该资产明确了先进制造拓展的基本方向：不是做智慧工厂替代，而是做商业价值流、经营协同和计划协同。 |
| `key_signals` | 多工厂、多产线、多事业部、渠道链条复杂、IPO/全球化阶段的企业更适配。 |
| `recommended_usage` | 新账户入池、画像边界收紧、行业扩展建议。 |
| `confidence_level` | `高` |

### 3.4 映射事实

#### `ka_mapping_brand_to_legal_v1`

| 字段 | 内容 |
| --- | --- |
| `asset_id` | `ka_mapping_brand_to_legal_v1` |
| `asset_type` | `mapping_fact` |
| `title` | `客户案例品牌名与合作主体映射事实集` |
| `source_path_or_url` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/客户案例与合作主体映射-v1.md` |
| `source_origin` | `internal` |
| `track_ids` | `retail_consumer,cross_border_ecommerce,advanced_manufacturing` |
| `persona_ids` | `` |
| `customer_refs` | `自然堂,老乡鸡,零跑汽车,来伊份,鲜丰水果,7-Eleven` |
| `jtbd_tags` | `` |
| `complexity_tags` | `主体归一,集团映射` |
| `summary` | 该资产沉淀了品牌名、集团名、签约主体之间的映射关系，是去重、老客排除和样本引用统一的基础。 |
| `key_signals` | 不能把案例标题里的品牌名直接当作客户主体；必须区分签约主体、经营主体、市场品牌。 |
| `recommended_usage` | 去重、老客排除、账户归一、证据补充。 |
| `confidence_level` | `高` |

## 4. 当前首版覆盖范围说明

首版 `12` 条知识资产，主要覆盖：

- 3 条主线的核心切入叙事
- 7 个画像中的主要判断锚点
- 典型样本客户
- 关键映射事实

当前还没有系统抽取但后续应补的资产包括：

- 更多零售消费子行业案例
- 更多跨境电商样板客户
- 更多先进制造的年报级和 IR 级支撑资产

## 5. 当前使用建议

1. 新账户入池时，优先从本文件中找可引用的知识资产，而不是每次从长文档现找。
2. 新画像从 `draft -> active` 前，至少应引用本文件中的一条相关资产，或新增一条新资产。
3. 月度复盘时，应检查：
   - 哪条主线的知识资产最薄
   - 哪个画像缺少高置信度资产
   - 哪些长文档值得再抽一轮

## 6. 关联文档

- [knowledge_asset_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/knowledge_asset_registry_v1-字段模板-v1.md)
- [内部客户案例系统学习-2026-03-28.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/内部客户案例系统学习-2026-03-28.md)
- [客户案例与合作主体映射-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/客户案例与合作主体映射-v1.md)
- [持续扩展高质量潜客池的运营机制设计-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/持续扩展高质量潜客池的运营机制设计-v1.md)
