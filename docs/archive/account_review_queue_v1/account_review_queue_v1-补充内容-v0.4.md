# `account_review_queue_v1` 补充内容 v0.4

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.7.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.7.md) 新迁入的第五轮 `L5` 账户补充结构化工作队列。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | reason_summary | target_action | due_hint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_kuka_v1` | `verification` | `acc_kuka` | `high` | `open` | `codex_llm` | 顾家家居已进入主表，但门店网络与直营网比例仍需补强。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_cayi_v1` | `verification` | `acc_cayi` | `high` | `open` | `codex_llm` | 嘉益股份与现有品牌出海样本相邻，适合优先补平台与经营规模证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_neway_v1` | `verification` | `acc_neway` | `high` | `open` | `codex_llm` | 纽威阀门技术型制造画像清晰，适合优先补研产销协同证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_piotech_v1` | `verification` | `acc_piotech` | `high` | `open` | `codex_llm` | 拓荆科技高技术制造画像明确，适合优先补业务结构与全球经营证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_recodeal_v1` | `verification` | `acc_recodeal` | `high` | `open` | `codex_llm` | 瑞可达与连接器制造画像相邻，适合优先补客户协同与全球经营证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_promo_tineco_v1` | `promotion_review` | `acc_tineco` | `medium` | `open` | `codex_llm` | 添可和石头 / 科沃斯画像相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_jemet_v1` | `promotion_review` | `acc_jemet` | `medium` | `open` | `codex_llm` | 杰美特与安克 / 绿联画像相邻，适合作为品牌出海补充样本。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_boundary_mlily_v1` | `boundary_review` | `acc_mlily` | `medium` | `open` | `codex_llm` | 梦百合兼具家居品牌与海外经营属性，需继续校准主画像归属。 | `复核零售消费主线与跨境经营边界` | `before_promotion` |
| `q_knowledge_home_retail_v1` | `knowledge_extraction` | `acc_suofeiya` | `medium` | `open` | `codex_llm` | 当前家居零售总部经营透视相关知识资产仍偏薄。 | `补抽家居零售与区域经营相关知识资产` | `next_month` |
| `q_cleanup_l5_batch5_v1` | `cleanup_review` | `acc_origin` | `low` | `open` | `codex_llm` | 随着 L5 扩张，需要持续检查跨境经营主体的去重和 canonical 归一。 | `迁移后清理边界重合和重复 canonical 风险` | `monthly_review` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前第五轮 L5 迁移后的重点核验对象已进入显式工作队列

## 4. 关联文档

- [account_review_queue_v1-补充内容-v0.3.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-补充内容-v0.3.md)
- [external_target_account_pool_v2-首版真实内容-v0.7.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.7.md)
