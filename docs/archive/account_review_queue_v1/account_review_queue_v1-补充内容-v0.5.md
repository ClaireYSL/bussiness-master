# `account_review_queue_v1` 补充内容 v0.5

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.8.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.8.md) 新迁入的第六轮 `L5` 账户补充结构化工作队列。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | reason_summary | target_action | due_hint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_luolai_v1` | `verification` | `acc_luolai` | `high` | `open` | `codex_llm` | 罗莱生活家纺品牌消费品画像清晰，适合优先补渠道与库存协同证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_lanhe_v1` | `verification` | `acc_lanhe` | `high` | `open` | `codex_llm` | 蓝禾品牌出海方向明确，适合优先补海外平台与经营规模证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_xtcnew_v1` | `verification` | `acc_xtcnew` | `high` | `open` | `codex_llm` | 厦钨新能新材料制造画像清晰，适合优先补经营链路与组织颗粒度证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_hetai_v1` | `verification` | `acc_hetai` | `high` | `open` | `codex_llm` | 和而泰与现有智能控制样本相邻，适合优先补全球客户协同证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_scimee_v1` | `verification` | `acc_scimee` | `high` | `open` | `codex_llm` | 芯源微半导体设备画像稳定，适合优先补业务与组织复杂度证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_promo_freda_v1` | `promotion_review` | `acc_freda` | `medium` | `open` | `codex_llm` | 福瑞达与华熙生物、自然堂画像相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_xtcnew_v1` | `promotion_review` | `acc_xtcnew` | `medium` | `open` | `codex_llm` | 厦钨新能与新材料样本相邻，适合作为技术型制造补充样本。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_boundary_mlily_v2` | `boundary_review` | `acc_mlily` | `medium` | `open` | `codex_llm` | 梦百合仍兼具家居品牌和海外经营属性，需要持续校准主画像归属。 | `复核零售消费主线与跨境经营边界` | `before_promotion` |
| `q_knowledge_petcare_v1` | `knowledge_extraction` | `acc_peti` | `medium` | `open` | `codex_llm` | 宠物消费品画像相关知识资产仍偏少。 | `补抽宠物消费品、品牌矩阵与渠道经营相关知识资产` | `next_month` |
| `q_cleanup_cbec_c_v1` | `boundary_review` | `acc_lanhe` | `low` | `open` | `codex_llm` | 跨境主线剩余 C 级主体未入主表，需要在后续清理与边界复盘中单独处理。 | `复核万得福 / 建发等边界主体是否永久保留在候选层` | `monthly_review` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前第六轮 L5 迁移后的重点核验对象已进入显式工作队列

## 4. 关联文档

- [account_review_queue_v1-补充内容-v0.4.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-补充内容-v0.4.md)
- [external_target_account_pool_v2-首版真实内容-v0.8.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.8.md)
