# `account_evidence_log_v1` 首版真实内容 v0.1

## 1. 文档目的

本文件为当前已迁入 [external_target_account_pool_v2-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.1.md) 的 `59` 家高质量层账户补齐首版结构化证据链。

本轮目标是先把证据链建起来，而不是一次性把每个账户的所有强证据补满。

## 2. 覆盖范围

- `L1=8`
- `L2=36`
- `L3=15`
- 合计 `59`

本轮口径：

- 每个账户至少 `1` 条证据
- `L1` 全部使用官方官网 / IR / 年报级主证据
- `L2/L3` 优先引用已完成的强核验文档，并尽量连接现有知识资产

## 3. L1 高可信母样本证据

| evidence_id | account_id | evidence_type | source_locator | evidence_strength | supports_dimension | summary | related_asset_ids | checked_by | checked_at | owner_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ev_acc_kidswant_ar_2024` | `acc_kidswant` | `annual_report` | `https://static.cninfo.com.cn/finalpage/2025-04-03/1222991960.pdf` | `S` | `主线,画像,上移` | 孩子王 2024 年报可确认其母婴零售主体、持续扩店与多业态布局，足以支撑其作为零售消费 `L1` 母样本。 | `ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1` | `codex_llm` | `2026-03-28` | `仍可补更细的区域经营证据。` |
| `ev_acc_miniso_ir_2024` | `acc_miniso` | `investor_relations` | `https://ir.miniso.com/2025-03-21-MINISO-Group-Announces-December-Quarter-and-Full-Year-of-2024-Unaudited-Financial-Results` | `A` | `主线,画像,上移` | 名创优品 IR 材料可确认其海内外门店规模、全球化连锁经营与门店网络复杂度，足以支撑 `L1`。 | `ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1` | `codex_llm` | `2026-03-28` | `中国经营主体与国内组织结构可继续补。` |
| `ev_acc_anker_official_about` | `acc_anker` | `official_website` | `https://www.anker.com.cn/pages/5-about` | `A` | `主线,画像,上移` | 安克官网可确认其全球消费电子品牌出海属性与全球市场覆盖，支撑其作为跨境品牌出海 `L1` 锚点。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `平台矩阵和区域经营颗粒度可继续补。` |
| `ev_acc_autel_ar_2024` | `acc_autel` | `annual_report` | `https://big5.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-03-29/688208_20250329_XJAN.pdf` | `S` | `主线,画像,上移` | 道通科技年报可确认其全球销售覆盖、多产品线经营和复杂渠道结构，支撑其作为复杂跨境经营型 `L1` 样本。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `主切入更偏跨境经营还是全球化制造仍可补。` |
| `ev_acc_luxshare_official_profile` | `acc_luxshare` | `official_website` | `https://www.luxshare-ict.com/about/company-profile.html` | `A` | `主线,画像,上移` | 立讯精密官网公司概况可确认其多基地、一体化制造和全球业务据点，支撑其作为多工厂制造 `L1` 锚点。 | `ka_case_zerorun_self_service_v1,ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `工厂和事业部颗粒度可继续补。` |
| `ev_acc_inovance_ar_2024` | `acc_inovance` | `annual_report` | `https://static.cninfo.com.cn/finalpage/2025-04-29/1223371383.PDF` | `S` | `主线,画像,上移` | 汇川技术年报可确认其多业务线与全球经营布局，支撑其作为先进制造经营型 BI `L1` 母样本。 | `ka_case_haozhi_dashboard_v1,ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `多工厂与渠道协同颗粒度可继续补。` |
| `ev_acc_mindray_ar_2024` | `acc_mindray` | `annual_report` | `https://www.mindray.com/content/dam/xpace/zh/investor-relations/financialinformation/2024/mindray-2024-yearly-report-cn.pdf` | `S` | `主线,画像,上移` | 迈瑞年报可确认其全球经营、复杂业务体系和研产销协同特征，支撑其作为技术型制造 `L1` 样本。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `更细的组织与渠道结构仍可补。` |
| `ev_acc_uih_ar_2024` | `acc_uih` | `annual_report` | `https://global.united-imaging.com/-/media/uih/pdf/investor/20250430-cn/united-imaging-healthcare-annual-report-for-2024.pdf` | `S` | `主线,画像,上移` | 联影医疗年报可确认其高端医疗设备与全球经营复杂度，支撑其作为技术型制造 `L1` 样本。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `集团协同切入颗粒度仍可补。` |

## 4. L2 高可信补充样本证据

| evidence_id | account_id | evidence_type | source_locator | evidence_strength | supports_dimension | summary | related_asset_ids | checked_by | checked_at | owner_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ev_acc_chowtaiseng_vfy` | `acc_chowtaiseng` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.2-首轮核验版.md` | `B` | `画像,上移` | 首轮核验已确认其珠宝零售终端网络与连锁经营特征，可支撑作为零售多门店补充标尺。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `区域经营颗粒度仍可补。` |
| `ev_acc_ecovacs_vfy` | `acc_ecovacs` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.2-首轮核验版.md` | `B` | `画像,上移` | 首轮核验已确认科沃斯全球品牌与海外经营特征，支撑其作为品牌出海补充标尺。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `平台结构仍可补。` |
| `ev_acc_syoung_vfy` | `acc_syoung` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.3-第二轮核验版.md` | `B` | `画像,上移` | 第二轮核验已确认水羊高 SKU、美妆个护、多渠道经营属性，支撑其作为品牌消费品补充标尺。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `渠道结构颗粒度仍可补。` |
| `ev_acc_songmics_vfy` | `acc_songmics` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.3-第二轮核验版.md` | `B` | `画像,上移` | 第二轮核验已确认致欧家居家居出海链路长、平台和区域经营复杂，支撑 `L2`。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1` | `codex_llm` | `2026-03-28` | `海外仓与平台颗粒度仍可补。` |
| `ev_acc_zhonghangoptic_vfy` | `acc_zhonghangoptic` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.3-第二轮核验版.md` | `B` | `画像,上移` | 第二轮核验已确认中航光电高技术制造与复杂客户协同特征，支撑技术型制造 `L2`。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `全球经营颗粒度仍可补。` |
| `ev_acc_roborock_vfy` | `acc_roborock` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.4-第三轮核验版.md` | `B` | `画像,上移` | 第三轮核验已确认石头科技全球消费电子品牌与海外经营特征，支撑 `L2`。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `平台经营颗粒度仍可补。` |
| `ev_acc_bestore_vfy` | `acc_bestore` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L4中可信候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L4 首轮强核验已确认良品铺子多品类零食品牌、SKU 体系与全渠道经营特征。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `渠道与供应链颗粒度仍可补。` |
| `ev_acc_suntime_vfy` | `acc_suntime` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L4中可信候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L4 首轮强核验已确认赛维时代多平台、多品牌和复杂跨境经营结构。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `品牌化程度仍可补。` |
| `ev_acc_insta360_vfy` | `acc_insta360` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L5 首轮强核验已确认影石创新消费电子品牌出海属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `平台与区域颗粒度仍可补。` |
| `ev_acc_ecoflow_vfy` | `acc_ecoflow` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-第二轮强核验-v0.1.md` | `B` | `画像,上移` | L5 第二轮强核验已确认正浩海外消费科技品牌和全球经营特征。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1` | `codex_llm` | `2026-03-28` | `平台矩阵颗粒度仍可补。` |
| `ev_acc_supcon_vfy` | `acc_supcon` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-第二轮强核验-v0.1.md` | `B` | `画像,上移` | L5 第二轮强核验已确认中控技术的自动化与技术型制造属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `业务条线颗粒度仍可补。` |
| `ev_acc_easyhome_vfy` | `acc_easyhome` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四至第六批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第四至第六批强核验已确认居然之家家居零售网络与总部管理半径。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `商场层级与区域结构仍可补。` |
| `ev_acc_jackery_vfy` | `acc_jackery` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四至第六批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第四至第六批强核验已确认华宝新能海外品牌与全球经营属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `平台矩阵颗粒度仍可补。` |
| `ev_acc_lens_vfy` | `acc_lens` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四至第六批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第四至第六批强核验已确认蓝思科技多基地制造与复杂协同。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `工厂布局颗粒度仍可补。` |
| `ev_acc_sunwoda_vfy` | `acc_sunwoda` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四至第六批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第四至第六批强核验已确认欣旺达多基地与产业链协同特征。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `事业部颗粒度仍可补。` |
| `ev_acc_catl_vfy` | `acc_catl` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四至第六批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第四至第六批强核验已确认宁德时代全球新能源制造与多基地协同。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `组织与基地颗粒度仍可补。` |
| `ev_acc_naura_vfy` | `acc_naura` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第四至第六批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第四至第六批强核验已确认北方华创高技术装备与复杂经营协同属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `业务条线颗粒度仍可补。` |
| `ev_acc_shokz_vfy` | `acc_shokz` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第七批强核验已确认韶音全球消费电子品牌与海外市场经营属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1,ka_insight_cbec_abm_v1` | `codex_llm` | `2026-03-28` | `区域经营颗粒度仍可补。` |
| `ev_acc_cfmoto_vfy` | `acc_cfmoto` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第七批强核验已确认春风动力海外品牌经营特征。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `平台经营颗粒度仍可补。` |
| `ev_acc_dsbj_vfy` | `acc_dsbj` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第七批强核验已确认东山精密多基地制造与全球客户协同。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `事业部颗粒度仍可补。` |
| `ev_acc_sanhua_vfy` | `acc_sanhua` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第七批强核验已确认三花智控热管理与控制部件业务复杂度。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `业务条线颗粒度仍可补。` |
| `ev_acc_tuopu_vfy` | `acc_tuopu` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第七批强核验已确认拓普集团多基地制造与全球协同。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `工厂颗粒度仍可补。` |
| `ev_acc_yonghui_vfy` | `acc_yonghui` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八至第九批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第八至第九批强核验已确认永辉商超网络与总部管理半径。 | `ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1` | `codex_llm` | `2026-03-28` | `直营网/合作经营结构仍可补。` |
| `ev_acc_bosideng_vfy` | `acc_bosideng` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八至第九批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第八至第九批强核验已确认波司登全国零售网络与品牌服饰经营属性。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `中国主体映射与直营网结构仍可补。` |
| `ev_acc_wolong_vfy` | `acc_wolong` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八至第九批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第八至第九批强核验已确认卧龙电驱多基地制造与全球经营。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `事业部颗粒度仍可补。` |
| `ev_acc_btl_vfy` | `acc_btl` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八至第九批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第八至第九批强核验已确认伯特利汽车零部件与复杂客户协同属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `全球经营颗粒度仍可补。` |
| `ev_acc_zhongji_vfy` | `acc_zhongji` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八至第九批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第八至第九批强核验已确认中际旭创光通信制造与全球客户协同特征。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `事业部颗粒度仍可补。` |
| `ev_acc_xtep_vfy` | `acc_xtep` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十至第十一批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十至第十一批强核验已确认特步全国零售网络和品牌矩阵。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `直营网/经销结构仍可补。` |
| `ev_acc_threesquirrels_vfy` | `acc_threesquirrels` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十至第十一批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十至第十一批强核验已确认三只松鼠多 SKU 与全渠道经营特征。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `渠道与库存颗粒度仍可补。` |
| `ev_acc_huali_vfy` | `acc_huali` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十至第十一批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十至第十一批强核验已确认华利集团全球鞋履制造与复杂海外客户协同。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `平台经营颗粒度仍可补。` |
| `ev_acc_sany_vfy` | `acc_sany` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十至第十一批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十至第十一批强核验已确认三一重工多基地制造和全球经营。 | `ka_case_zerorun_self_service_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `工厂布局与事业部颗粒度仍可补。` |
| `ev_acc_desay_vfy` | `acc_desay` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十至第十一批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十至第十一批强核验已确认德赛西威汽车电子与全球客户协同。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `业务条线颗粒度仍可补。` |
| `ev_acc_zhouheiya_vfy` | `acc_zhouheiya` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一至第十二批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十一至第十二批强核验已确认周黑鸭连锁网络和区域经营特征。 | `ka_case_xianfeng_retail_v1,ka_case_chatbi_frontline_v1` | `codex_llm` | `2026-03-28` | `中国经营主体和直营网结构仍可补。` |
| `ev_acc_mengtianhome_vfy` | `acc_mengtianhome` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一至第十二批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十一至第十二批强核验已确认梦天家居海外经营与供应链协同特征。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `海外客户结构和品牌边界仍可补。` |
| `ev_acc_siasun_vfy` | `acc_siasun` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一至第十二批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十一至第十二批强核验已确认机器人股份自动化装备和多业务协同属性。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `制造基地与业务线颗粒度仍可补。` |
| `ev_acc_timeselectric_vfy` | `acc_timeselectric` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一至第十二批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十一至第十二批强核验已确认时代电气轨交电气与高技术制造协同特征。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `全球经营与业务条线颗粒度仍可补。` |

## 5. L3 中高可信补充样本证据

| evidence_id | account_id | evidence_type | source_locator | evidence_strength | supports_dimension | summary | related_asset_ids | checked_by | checked_at | owner_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ev_acc_mgstationery_vfy` | `acc_mgstationery` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.2-首轮核验版.md` | `B` | `画像,上移` | 首轮核验已确认晨光文具品类与渠道复杂度，支撑其作为品牌消费品 `L3` 样本。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `渠道与库存颗粒度仍可补。` |
| `ev_acc_ugreen_vfy` | `acc_ugreen` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.3-第二轮核验版.md` | `B` | `画像,上移` | 第二轮核验已确认绿联品牌出海方向成立。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `海外平台与组织颗粒度仍可补。` |
| `ev_acc_biemlfdlkk_vfy` | `acc_biemlfdlkk` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.4-第三轮核验版.md` | `B` | `画像,上移` | 第三轮核验已确认比音勒芬零售网络和品牌服饰经营属性。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `区域和组织颗粒度仍可补。` |
| `ev_acc_hangke_vfy` | `acc_hangke` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第二批扩展候选池-v0.4-第三轮核验版.md` | `B` | `画像,上移` | 第三轮核验已确认杭可科技新能源装备与海外布局特征。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `研产销协同颗粒度仍可补。` |
| `ev_acc_botanee_vfy` | `acc_botanee` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L5 首轮强核验已确认贝泰妮美妆个护与品牌消费品属性。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `渠道与供应链颗粒度仍可补。` |
| `ev_acc_hymson_vfy` | `acc_hymson` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L5 首轮强核验已确认海目星装备制造方向和多工厂制造画像。 | `ka_case_haozhi_dashboard_v1,ka_insight_mfg_value_stream_v1` | `codex_llm` | `2026-03-28` | `工厂与业务线颗粒度仍可补。` |
| `ev_acc_dji_vfy` | `acc_dji` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-第二轮强核验-v0.1.md` | `B` | `画像,上移` | L5 第二轮强核验已确认 DJI 全球品牌和海外经营特征。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `平台与主体结构仍可补。` |
| `ev_acc_dencare_vfy` | `acc_dencare` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L5放量候选-第二轮强核验-v0.1.md` | `B` | `画像,上移` | L5 第二轮强核验已确认登康口腔品牌消费品与渠道经营属性。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `渠道与库存颗粒度仍可补。` |
| `ev_acc_hla_vfy` | `acc_hla` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L4中可信候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L4 首轮强核验已确认海澜之家多品牌服饰零售集团属性与线下网络特征。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `加盟/直营网颗粒度仍可补。` |
| `ev_acc_easyhome_hkyb_vfy` | `acc_easyhome_hkyb` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-L4中可信候选-首轮强核验-v0.1.md` | `B` | `画像,上移` | L4 首轮强核验已确认华凯易佰多平台多店铺经营成立。 | `ka_solution_cbec_profit_v1,ka_insight_cbec_jtbd_v1` | `codex_llm` | `2026-03-28` | `品牌化程度仍可补。` |
| `ev_acc_taotao_vfy` | `acc_taotao` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第七批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第七批强核验已确认涛涛车业出行类品牌出海方向。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `海外平台和品牌矩阵仍可补。` |
| `ev_acc_jiajia_vfy` | `acc_jiajia` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第八至第九批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第八至第九批强核验已确认家家悦区域连锁商超属性。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `区域经营颗粒度仍可补。` |
| `ev_acc_chubang_vfy` | `acc_chubang` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十至第十一批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十至第十一批强核验已确认中炬高新调味品品牌矩阵和全国渠道经营属性。 | `ka_case_naturehall_ai_v1` | `codex_llm` | `2026-03-28` | `供应链协同颗粒度仍可补。` |
| `ev_acc_yuanzu_vfy` | `acc_yuanzu` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一至第十二批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十一至第十二批强核验已确认元祖烘焙礼品零售网络与区域经营特征。 | `ka_case_xianfeng_retail_v1` | `codex_llm` | `2026-03-28` | `门店网络颗粒度仍可补。` |
| `ev_acc_klg_vfy` | `acc_klg` | `manual_note` | `/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/外部目标客户池-v1.0-第十一至第十二批关键账户强核验-v0.1.md` | `B` | `画像,上移` | 第十一至第十二批强核验已确认开润股份海外业务和消费品品牌经营属性。 | `ka_case_smallrig_outbound_v1,ka_solution_cbec_profit_v1` | `codex_llm` | `2026-03-28` | `海外平台结构和品牌边界仍可补。` |

## 6. 当前完成情况

- 当前 `59` 家高质量层账户均已有至少 `1` 条证据记录
- `L1` 全部具备 `A/S` 级官方证据
- `L2/L3` 已具备首版结构化证据，可支持后续解释、上移复核和知识资产挂接

## 7. 下一步建议

1. 优先为 `validation_gap` 仍大的 `L2/L3` 账户补第二条强证据
2. 在迁移 `L4` 的同时，为最接近上移的账户同步挂第一条证据
3. 后续迁移 `L5` 时，继续沿用“至少一条最小证据”的首版策略

## 8. 关联文档

- [account_evidence_log_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_evidence_log_v1-字段模板-v1.md)
- [external_target_account_pool_v2-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.1.md)
- [knowledge_asset_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/knowledge_asset_registry_v1-首版真实内容-v0.1.md)
