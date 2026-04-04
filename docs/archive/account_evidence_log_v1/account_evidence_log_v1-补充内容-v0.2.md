# `account_evidence_log_v1` 补充内容 v0.2

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.3.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.3.md) 新迁入的 `30` 家 `L5` 账户补第一条结构化证据。

本轮仍采用“最小可用证据链”策略：

- 每家先补 `1` 条证据
- 证据强度以 `B` 为主
- 先支撑主线成立、主画像成立和正式入池理由

## 2. 本轮新增证据记录

| evidence_id | account_id | evidence_type | source_locator | evidence_strength | supports_dimension | summary | related_asset_ids | checked_by | checked_at | owner_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ev_acc_mercuryhome_l5_intake` | `acc_mercuryhome` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确水星家纺的家纺品牌消费品属性及 SKU、渠道、库存协同分析空间，足以支撑其进入 `L5`。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `后续可补官网或年报级证据。` |
| `ev_acc_robam_l5_intake` | `acc_robam` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确老板电器的厨电品牌消费品属性和渠道经营复杂度。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `后续补渠道与库存协同强证据。` |
| `ev_acc_supor_l5_intake` | `acc_supor` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确苏泊尔小家电品牌消费品属性与商品、渠道分析空间。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `后续补品类矩阵与供应链证据。` |
| `ev_acc_joyoung_l5_intake` | `acc_joyoung` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确九阳品牌消费品画像与商品、渠道、库存分析空间。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `后续补线上线下渠道颗粒度。` |
| `ev_acc_huangshanghuang_l5_intake` | `acc_huangshanghuang` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确煌上煌卤味休闲食品品牌属性及全渠道动销分析空间。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `后续补加盟 / 直营网比例。` |
| `ev_acc_qianweiyangchu_l5_intake` | `acc_qianweiyangchu` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确千味央厨的食品品牌与供应链协同双属性。 | `ka_case_laiyifen_replenishment_v1` | `codex_llm` | `2026-03-28` | `后续补渠道边界与供应链强证据。` |
| `ev_acc_anjingfood_l5_intake` | `acc_anjingfood` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确安井食品的冷冻食品与预制菜品牌属性。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `后续补渠道结构与库存颗粒度。` |
| `ev_acc_laiyifen_l5_intake` | `acc_laiyifen` | `internal_mapping` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十二批候选与现有来伊份场景资产共同支撑其零食连锁零售与总部经营透视画像。 | `ka_case_laiyifen_replenishment_v1,ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `后续补门店网络与直营网 / 加盟结构强证据。` |
| `ev_acc_chj_l5_intake` | `acc_chj` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十二批候选已明确潮宏基珠宝品牌零售与终端网络特征。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `后续补直营网 / 加盟结构与区域经营证据。` |
| `ev_acc_wfj_l5_intake` | `acc_wfj` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十二批候选已明确王府井百货与购物中心经营网络特征。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `后续补商场层级和业态边界证据。` |
| `ev_acc_greatstar_l5_intake` | `acc_greatstar` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确巨星科技的工具与消费品海外经营属性，适合作为复杂跨境经营候选。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `后续补海外渠道结构与平台颗粒度。` |
| `ev_acc_jeep_bike_l5_intake` | `acc_jeep_bike` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确久祺股份自行车出海与海外经营属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `后续补海外平台与品牌矩阵证据。` |
| `ev_acc_uechairs_l5_intake` | `acc_uechairs` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确永艺家具家居品牌出海与海外经营属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `后续补海外平台与客户结构。` |
| `ev_acc_impulse_l5_intake` | `acc_impulse` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确英派斯运动器材出海与品牌出海属性。 | `ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1` | `codex_llm` | `2026-03-28` | `后续补海外平台结构与品牌矩阵。` |
| `ev_acc_petstar_l5_intake` | `acc_petstar` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确源飞宠物海外经营与品牌出海属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `后续补品牌经营颗粒度。` |
| `ev_acc_hlin_l5_intake` | `acc_hlin` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十批候选已明确恒林股份家居出海与海外经营特征。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `后续补海外渠道与品牌经营颗粒度。` |
| `ev_acc_morhome_l5_intake` | `acc_morhome` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十二批候选已明确慕容家居品牌出海与海外经营属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `后续补品牌矩阵和经营主体映射。` |
| `ev_acc_jiayi_l5_intake` | `acc_jiayi` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十二批候选已明确嘉益股份保温器皿品牌出海属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `后续补平台结构与经营颗粒度。` |
| `ev_acc_saite_l5_intake` | `acc_saite` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十二批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十二批候选已明确赛特新材材料出口与海外经营属性。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `后续补海外经营规模与业务边界。` |
| `ev_acc_daziran_l5_intake` | `acc_daziran` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十一批候选已明确大自然户外用品与海外经营属性。 | `ka_case_smallrig_outbound_v1,ka_insight_cbec_abm_v1` | `codex_llm` | `2026-03-28` | `后续补平台结构、品牌矩阵与区域经营。` |
| `ev_acc_junsheng_l5_intake` | `acc_junsheng` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确均胜电子汽车电子与全球制造协同属性。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补工厂布局与经营口径强证据。` |
| `ev_acc_yinlun_l5_intake` | `acc_yinlun` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确银轮股份热管理与零部件制造属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补全球经营与客户协同颗粒度。` |
| `ev_acc_eefo_l5_intake` | `acc_eefo` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确新易盛光通信高技术制造属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补组织颗粒度与客户结构。` |
| `ev_acc_jifeng_l5_intake` | `acc_jifeng` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第七批候选已明确继峰股份汽车零部件与全球工厂布局属性。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补工厂网络与事业部结构。` |
| `ev_acc_hangcha_l5_intake` | `acc_hangcha` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确杭叉集团工业车辆与多基地制造特征。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补区域经营与事业部结构。` |
| `ev_acc_ikd_l5_intake` | `acc_ikd` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第八批候选已明确爱柯迪汽车零部件全球制造属性。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补工厂布局与全球经营颗粒度。` |
| `ev_acc_xcmg_l5_intake` | `acc_xcmg` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第九批候选已明确徐工机械工程机械与全球经营协同属性。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补工厂布局、事业部与经营结构。` |
| `ev_acc_jingsheng_l5_intake` | `acc_jingsheng` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第九批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第九批候选已明确晶盛机电半导体 / 光伏装备与高技术制造属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补业务条线与全球经营颗粒度。` |
| `ev_acc_haitianjg_l5_intake` | `acc_haitianjg` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十一批候选已明确海天精工高端机床与制造协同属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补工厂布局、业务条线与全球经营。` |
| `ev_acc_citic_hic_l5_intake` | `acc_citic_hic` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一批放量候选池-v0.1.md` | `B` | `主线,画像,入池` | 第十一批候选已明确中信重工重型装备与多业务协同特征。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `后续补工厂布局、业务条线与全球经营颗粒度。` |

## 3. 本轮完成情况

- 本轮新迁入的 `30` 家 `L5` 账户均已补上首条结构化证据
- 所有证据都可回溯到既有批次文档或已沉淀知识资产
- 主表、证据表、队列表三者开始形成同步闭环

## 4. 下一步建议

1. 优先为 `来伊份、嘉益股份、均胜电子、徐工机械、晶盛机电、海天精工` 补第二条更强的官方证据
2. 第二轮 `L5` 迁移继续优先挑选：
   - 零售中的连锁餐饮 / 茶饮样本
   - 跨境中的品牌出海强相邻对象
   - 制造中的工程机械 / 高技术装备强相邻对象

## 5. 关联文档

- [account_evidence_log_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_evidence_log_v1-首版真实内容-v0.1.md)
- [external_target_account_pool_v2-首版真实内容-v0.3.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.3.md)
