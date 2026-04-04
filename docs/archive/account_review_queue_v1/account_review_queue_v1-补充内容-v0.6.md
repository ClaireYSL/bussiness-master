# `account_review_queue_v1` 补充内容 v0.6

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.9.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.9.md) 新迁入的第七轮 `L5` 账户补充结构化工作队列。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | reason_summary | target_action | due_hint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_lancy_v1` | `verification` | `acc_lancy` | `high` | `open` | `codex_llm` | 朗姿股份兼具服饰零售与多品牌经营属性，适合优先补业务边界和门店网络证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_hailide_v1` | `verification` | `acc_hailide` | `high` | `open` | `codex_llm` | 海利得材料出口与全球经营画像稳定，适合优先补海外占比与客户结构证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_zhongding_v1` | `verification` | `acc_zhongding` | `high` | `open` | `codex_llm` | 中鼎股份与汽车零部件多工厂制造画像相邻，适合优先补事业部与多工厂证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_moons_v1` | `verification` | `acc_moons` | `high` | `open` | `codex_llm` | 鸣志电器高技术制造画像明确，适合优先补业务条线和客户协同证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_mingyang_v1` | `verification` | `acc_mingyang` | `high` | `open` | `codex_llm` | 明阳智能风电装备和多工厂制造画像较强，适合优先补工厂布局与事业部证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_promo_aofei_v1` | `promotion_review` | `acc_aofei` | `medium` | `open` | `codex_llm` | 奥飞娱乐和泡泡玛特 / 实丰文化画像相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_ccgrass_v1` | `promotion_review` | `acc_ccgrass` | `medium` | `open` | `codex_llm` | 共创草坪与材料出口画像相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_boundary_lancy_v1` | `boundary_review` | `acc_lancy` | `medium` | `open` | `codex_llm` | 朗姿股份存在服饰零售与医美多品牌并存边界，需要持续校准主画像归属。 | `复核业务边界与 canonical 画像归属` | `before_promotion` |
| `q_knowledge_toy_v1` | `knowledge_extraction` | `acc_aofei` | `medium` | `open` | `codex_llm` | 当前潮玩 / 文创消费品画像相关知识资产仍偏少。 | `补抽潮玩 / 文创品牌经营与渠道分析相关知识资产` | `next_month` |
| `q_cleanup_cbec_boundary_v2` | `boundary_review` | `acc_xidamen` | `low` | `open` | `codex_llm` | 跨境主线仍存在材料 / 产业品出口边界主体，需要继续清理与画像校准。 | `月度复盘时检查复杂跨境经营画像的边界是否过宽` | `monthly_review` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前第七轮 L5 迁移后的重点核验对象已进入显式工作队列

## 4. 关联文档

- [account_review_queue_v1-补充内容-v0.5.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-补充内容-v0.5.md)
- [external_target_account_pool_v2-首版真实内容-v0.9.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.9.md)
