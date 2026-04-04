# `track_registry_v1` 首版真实内容 v0.1

## 1. 文档目的

本文件基于当前已完成的案例学习、静态潜客建池和公司战略背景，给出 `track_registry_v1` 的第一版真实注册内容。

本文件不是字段规范，字段规范见：

- [track_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/track_registry_v1-字段模板-v1.md)

## 2. 当前启用主线

当前建议正式注册并启用以下 3 条主线：

1. `零售消费`
2. `跨境电商`
3. `先进制造`

## 3. 首版真实记录

### 3.1 `retail_consumer`

| 字段 | 内容 |
| --- | --- |
| `track_id` | `retail_consumer` |
| `track_name` | `零售消费` |
| `status` | `active` |
| `priority_level` | `P0` |
| `maturity_level` | `高` |
| `description` | 以品牌零售、连锁零售、品牌消费品、连锁餐饮/茶饮/咖啡为核心的经营主体，典型特征是多门店、多区域、多渠道、高 SKU、高频经营复盘。 |
| `entry_criteria_summary` | 必须能映射到零售消费主阵地画像之一，如多门店连锁零售、高 SKU 品牌消费品、连锁餐饮/茶饮/咖啡；且经营复杂度、JTBD 与观远既有案例和方案存在明显相邻性。 |
| `non_fit_boundary_summary` | 不纳入单店/少店小品牌、纯单一线上销售且管理半径弱的主体，也不纳入只有一般报表需求、缺乏经营复杂度的零售公司。 |
| `seed_persona_ids` | `retail_multi_store,retail_high_sku_brand,retail_chain_fnb` |
| `seed_account_refs` | `名创优品,孩子王,来伊份,鲜丰水果,博士眼镜,周黑鸭,元祖` |
| `seed_knowledge_refs` | `ka_case_xianfeng_retail_v1,ka_case_laiyifen_replenishment_v1,ka_case_chatbi_frontline_v1,ka_case_naturehall_ai_v1` |
| `typical_jtbd_summary` | 总部经营透视、门店经营健康度、区域差异分析、商品与库存优化、加盟选品与补货、渠道动销与业财供协同、一线问数与动作闭环。 |
| `owner_note` | 当前样本、案例和画像最成熟，应继续承担主要命中率验证任务，同时维持边扩池边上移的节奏。 |

### 3.2 `cross_border_ecommerce`

| 字段 | 内容 |
| --- | --- |
| `track_id` | `cross_border_ecommerce` |
| `track_name` | `跨境电商` |
| `status` | `active` |
| `priority_level` | `P1` |
| `maturity_level` | `中` |
| `description` | 以品牌出海、多平台卖家、跨境供应链型经营主体为核心，典型特征是多平台、多店铺、多国家、多币种，市场洞察、选品、利润分析和供需平衡复杂。 |
| `entry_criteria_summary` | 必须能映射到多平台品牌出海型或供应链复杂的跨境经营型画像；且海外业务复杂度、利润核算复杂度或平台运营复杂度已显性化。 |
| `non_fit_boundary_summary` | 不纳入单平台、单区域、小规模试水的卖家，也不纳入只有“出海概念”但没有明显跨境经营复杂度的公司。 |
| `seed_persona_ids` | `cbec_multi_platform_brand,cbec_supply_chain_complex` |
| `seed_account_refs` | `安克创新,致欧家居,赛维时代,华凯易佰,正浩 EcoFlow,科沃斯` |
| `seed_knowledge_refs` | `ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1,ka_insight_cbec_jtbd_v1,ka_case_smallrig_outbound_v1` |
| `typical_jtbd_summary` | 市场洞察与选品、多平台精细化运营、T+1 利润分析、库存与供需平衡、业财一体化、海外业务经营驾驶舱。 |
| `owner_note` | 2026 重点拓展方向，现有打法已具备 ABM 物料和样本，但仍需持续补高质量案例和强标尺。 |

### 3.3 `advanced_manufacturing`

| 字段 | 内容 |
| --- | --- |
| `track_id` | `advanced_manufacturing` |
| `track_name` | `先进制造` |
| `status` | `active` |
| `priority_level` | `P1` |
| `maturity_level` | `中` |
| `description` | 以离散制造、技术型制造、多工厂制造集团为核心，典型特征是多工厂、多产线、多事业部，LTC、计划协同、经营驾驶舱和集团透明化需求明显。 |
| `entry_criteria_summary` | 必须能映射到多工厂离散制造集团或研产销协同复杂的技术型制造企业画像；且企业具备明显经营协同复杂度，不是单纯工厂控制型需求。 |
| `non_fit_boundary_summary` | 不纳入单工厂、单事业部、链路简单的普通工厂型企业，也不以 MES/SCADA 替代为切入目标。 |
| `seed_persona_ids` | `mfg_multi_factory_group,mfg_rnd_sales_complex` |
| `seed_account_refs` | `汇川技术,立讯精密,迈瑞医疗,联影医疗,中航光电,时代电气` |
| `seed_knowledge_refs` | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1,ka_case_zerorun_self_service_v1` |
| `typical_jtbd_summary` | 集团经营驾驶舱、多工厂计划协同、LTC、财务/生产/质量/存货联动、渠道效率与技术品牌经营透明化。 |
| `owner_note` | 2026 重点拓展方向，应坚持“经营型 BI”切入，不因行业战略重要而泛铺制造企业。 |

## 4. 当前未启用但可预留的候选主线

以下主线可以保留为 `draft` 候选，但当前不建议正式启用：

- `医药医疗`
- `金融`
- `企业服务`
- `物流供应链`

原因：

- 当前虽有相邻案例或客户，但画像、样本、知识资产和静态潜客池厚度都还不够支撑正式扩池。

## 5. 当前使用建议

1. 账户入池时，`primary_track` 只能从当前 `active` 主线中选。
2. 新行业若要进入正式扩池，必须先补 `track_registry_v1` 的真实记录，再补画像和知识资产。
3. 月度复盘时，应至少复核一次每条主线的：
   - 样本厚度
   - 案例覆盖
   - 画像健康度
   - 边界是否需要收紧或扩展

## 6. 关联文档

- [持续扩展高质量潜客池的运营机制设计-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/持续扩展高质量潜客池的运营机制设计-v1.md)
- [track_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/track_registry_v1-字段模板-v1.md)
- [内部客户案例系统学习-2026-03-28.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/04-研究与方法/内部客户案例系统学习-2026-03-28.md)
