# `account_review_queue_v1` 补充内容 v0.8

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.11.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.11.md) 新迁入的第九轮 `L5` 账户补充结构化工作队列。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | reason_summary | target_action | due_hint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_liziyuan_v1` | `verification` | `acc_liziyuan` | `high` | `open` | `codex_llm` | 李子园饮品品牌画像稳定，适合优先补品牌矩阵与供应链颗粒度证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_hengbo_v1` | `verification` | `acc_hengbo` | `high` | `open` | `codex_llm` | 恒勃股份产业品出口画像较稳，适合优先补海外经营规模与客户结构证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_xinje_v1` | `verification` | `acc_xinje` | `high` | `open` | `codex_llm` | 信捷电气自动化控制产品画像明确，适合优先补业务结构与全球经营证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_chuangshiji_v1` | `verification` | `acc_chuangshiji` | `high` | `open` | `codex_llm` | 创世纪机床与智能装备制造画像稳定，适合优先补工厂布局与事业部证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_victory_v1` | `verification` | `acc_victory` | `high` | `open` | `codex_llm` | 运达股份风电装备和多工厂制造画像较强，适合优先补工厂布局与全球经营证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_promo_hengbo_v1` | `promotion_review` | `acc_hengbo` | `medium` | `open` | `codex_llm` | 恒勃股份与产业品出口 / 复杂跨境经营画像相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_zhongjing_v2` | `promotion_review` | `acc_zhongjing` | `medium` | `open` | `codex_llm` | 仲景食品与食品饮料高 SKU 样本相邻，补证据后适合上移评估。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_boundary_pengwei_v1` | `boundary_review` | `acc_pengwei` | `medium` | `open` | `codex_llm` | 品渥食品兼具进口消费品经营属性，需要继续校准主画像边界。 | `复核进口消费品经营边界与主画像归属` | `before_promotion` |
| `q_knowledge_condiment_v1` | `knowledge_extraction` | `acc_tianwei` | `medium` | `open` | `codex_llm` | 当前调味品 / 休闲食品品牌消费品知识资产仍可继续增厚。 | `补抽调味品、烘焙、乳品品牌经营与渠道分析相关知识资产` | `next_month` |
| `q_cleanup_export_boundary_v3` | `boundary_review` | `acc_hengbo` | `low` | `open` | `codex_llm` | 产业品出口类复杂跨境经营账户越来越多，需要持续检查画像边界是否过宽。 | `月度复盘时检查复杂跨境经营画像的产业品出口边界` | `monthly_review` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前第九轮 L5 迁移后的重点核验对象已进入显式工作队列

## 4. 关联文档

- [account_review_queue_v1-补充内容-v0.7.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-补充内容-v0.7.md)
- [external_target_account_pool_v2-首版真实内容-v0.11.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.11.md)
