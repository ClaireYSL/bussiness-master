# `account_review_queue_v1` 补充内容 v0.2

## 1. 文档目的

本文件补充第一轮 `L5` 迁移后的新增工作队列，重点覆盖：

1. 本轮新迁入 `30` 家 `L5` 的补证据任务
2. 从 `L5` 继续上移的优先核验队列
3. 第二轮 `L5` 迁移前的画像补抽取任务

## 2. 新增队列项

| queue_item_id | queue_type | account_id | related_track_id | related_persona_id | priority | status | owner | reason_summary | expected_action | source_context | created_at | resolved_at | resolution_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_l5_laiyifen` | `verification` | `acc_laiyifen` | `retail_consumer` | `retail_multi_store` | `高` | `open` | `codex_llm` | 来伊份已迁入 `L5`，且已有较强场景资产，应尽快补第一条强证据。 | 补门店网络、直营网 / 加盟和区域经营强证据。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_verify_l5_chj` | `verification` | `acc_chj` | `retail_consumer` | `retail_multi_store` | `中` | `open` | `codex_llm` | 潮宏基零售画像成立，但珠宝零售网络和直营网 / 加盟结构证据仍不足。 | 补门店网络与区域经营证据。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_verify_l5_jiayi` | `verification` | `acc_jiayi` | `cross_border_ecommerce` | `cbec_multi_platform_brand` | `高` | `open` | `codex_llm` | 嘉益股份品牌出海方向明确，适合优先补海外平台与品牌矩阵证据。 | 补平台结构、品牌矩阵与经营颗粒度证据。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_verify_l5_junsheng` | `verification` | `acc_junsheng` | `advanced_manufacturing` | `mfg_multi_factory_group` | `高` | `open` | `codex_llm` | 均胜电子与现有多工厂制造标尺最接近，适合尽快补强证据。 | 补工厂布局、业务条线与经营口径强证据。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_verify_l5_xcmg` | `verification` | `acc_xcmg` | `advanced_manufacturing` | `mfg_multi_factory_group` | `高` | `open` | `codex_llm` | 徐工机械是工程机械主线里最接近高质量层的对象之一。 | 补多基地、事业部和全球经营强证据。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_verify_l5_jingsheng` | `verification` | `acc_jingsheng` | `advanced_manufacturing` | `mfg_rnd_sales_complex` | `高` | `open` | `codex_llm` | 晶盛机电高技术制造画像稳定，适合作为优先上移候选。 | 补业务条线、全球经营与经营颗粒度证据。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_promote_l5_laiyifen` | `promotion_review` | `acc_laiyifen` | `retail_consumer` | `retail_multi_store` | `高` | `open` | `codex_llm` | 来伊份已具备内部场景资产与清晰主画像，是本轮 `L5` 中最接近上移的零售对象。 | 补强证据后评估是否可升 `L4/L3`。 | `ka_case_laiyifen_replenishment_v1` | `2026-03-28` |  |  |
| `q_promote_l5_jiayi` | `promotion_review` | `acc_jiayi` | `cross_border_ecommerce` | `cbec_multi_platform_brand` | `高` | `open` | `codex_llm` | 嘉益股份是本轮新迁入的品牌出海候选里最适合作为次级样本的对象之一。 | 补强证据后评估是否可升 `L4/L3`。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_promote_l5_junsheng` | `promotion_review` | `acc_junsheng` | `advanced_manufacturing` | `mfg_multi_factory_group` | `高` | `open` | `codex_llm` | 均胜电子与德赛西威、立讯精密的相邻度高，适合作为优先上移候选。 | 补强多工厂与全球协同证据后评估上移。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_extract_retail_jewelry_assets` | `knowledge_extraction` |  | `retail_consumer` | `retail_multi_store` | `中` | `open` | `codex_llm` | 珠宝零售画像目前已有周大生，但潮宏基等相邻对象增多，知识资产仍偏薄。 | 补抽珠宝零售网络、直营网 / 加盟与区域经营相关资产。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_extract_outdoor_brand_assets` | `knowledge_extraction` |  | `cross_border_ecommerce` | `cbec_multi_platform_brand` | `中` | `open` | `codex_llm` | 户外 / 出行 / 工具类品牌出海对象增多，但现有知识资产仍偏消费电子。 | 补抽春风动力、涛涛车业、英派斯、大自然等相邻品牌出海资产。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |
| `q_extract_engineering_mfg_assets` | `knowledge_extraction` |  | `advanced_manufacturing` | `mfg_multi_factory_group` | `中` | `open` | `codex_llm` | 工程机械与重工装备对象开始增多，但现有制造资产更偏自动化与高技术制造。 | 补抽徐工、三一、中信重工、海天精工等经营协同资产。 | `external_target_account_pool_v2-v0.3` | `2026-03-28` |  |  |

## 3. 本轮意义

本轮补充队列把第一轮 `L5` 迁移后的工作路径具体化为：

1. 先补第一条强证据
2. 再选最有代表性的账户做上移核验
3. 同时补薄弱画像的知识资产

## 4. 关联文档

- [account_review_queue_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-首版真实内容-v0.1.md)
- [external_target_account_pool_v2-首版真实内容-v0.3.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.3.md)
