# `account_review_queue_v1` 补充内容 v0.3

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.6.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.6.md) 新迁入的第四轮 `L5` 账户补充结构化工作队列。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | reason_summary | target_action | due_hint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_redstar_v1` | `verification` | `acc_redstar` | `high` | `open` | `codex_llm` | 红星美凯龙已进入主表，但商场层级与平台经营边界仍待补强。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_70mai_v1` | `verification` | `acc_70mai` | `high` | `open` | `codex_llm` | 70迈品牌出海画像清晰，适合优先补海外平台与经营主体证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_leadtrend_v1` | `verification` | `acc_leadtrend` | `high` | `open` | `codex_llm` | 领益智造与现有高质量电子制造样本相邻，适合优先补组织结构证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_eve_v1` | `verification` | `acc_eve` | `high` | `open` | `codex_llm` | 亿纬锂能多工厂制造画像成立，适合优先补全球经营与事业部颗粒度。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_amec_v1` | `verification` | `acc_amec` | `high` | `open` | `codex_llm` | 中微公司高技术制造画像清晰，适合优先补业务协同与官方强证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_promo_narwal_v1` | `promotion_review` | `acc_narwal` | `medium` | `open` | `codex_llm` | 云鲸与现有清洁家电样本相邻，若补齐渠道与经营主体证据可考虑上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_laifen_v1` | `promotion_review` | `acc_laifen` | `medium` | `open` | `codex_llm` | 徕芬与安克 / 正浩 / 影石画像相邻，适合作为品牌出海补充样本。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_henglin_v1` | `promotion_review` | `acc_henglin` | `medium` | `open` | `codex_llm` | 恒林家居与致欧 / 建霖家居画像相邻，适合补强后进入上移评估。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_boundary_yatsen_v1` | `boundary_review` | `acc_yatsen` | `medium` | `open` | `codex_llm` | 逸仙电商存在主体、集团和品牌矩阵边界问题，需要先校准。 | `复核主体与品牌边界，确认 canonical 口径` | `before_promotion` |
| `q_boundary_aukey_v1` | `boundary_review` | `acc_aukey` | `medium` | `open` | `codex_llm` | 傲基当前主体有效性与经营阶段仍需谨慎确认。 | `复核主体有效性与老客排除状态` | `before_promotion` |
| `q_knowledge_retail_beauty_v1` | `knowledge_extraction` | `acc_bloomage` | `medium` | `open` | `codex_llm` | 当前美妆个护品牌消费品知识资产仍偏少。 | `补抽与美妆品牌矩阵、渠道经营相关知识资产` | `next_month` |
| `q_cleanup_l5_batch4to6_v1` | `cleanup_review` | `acc_sailvan` | `low` | `open` | `codex_llm` | 随着 L5 扩张，需要继续检查跨境综合经营主体的去重和边界。 | `迁移后清理边界重合和重复 canonical 风险` | `monthly_review` |

## 3. 本轮完成情况

- 新增 `12` 条队列项
- 覆盖 `verification / promotion_review / boundary_review / knowledge_extraction / cleanup_review`
- 当前第四轮 L5 迁移后的重点核验对象已进入显式工作队列

## 4. 关联文档

- [account_review_queue_v1-补充内容-v0.2.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-补充内容-v0.2.md)
- [external_target_account_pool_v2-首版真实内容-v0.6.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.6.md)
