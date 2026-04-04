# `account_review_queue_v1` 补充内容 v0.10

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.13.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.13.md) 新迁入账户补首版队列项。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | created_at | reason_summary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `q_v10_winnermedical_verify` | `verification` | `acc_winnermedical` | `high` | `open` | `codex_llm` | `2026-03-28` | `稳健医疗兼具品牌消费品与渠道经营属性，需补品牌矩阵与库存协同强证据。` |
| `q_v10_botanee_verify` | `verification` | `acc_botanee` | `high` | `open` | `codex_llm` | `2026-03-28` | `贝泰妮静态优先级为 A，需补会员经营与品牌矩阵强证据。` |
| `q_v10_qiaqia_verify` | `verification` | `acc_qiaqia` | `high` | `open` | `codex_llm` | `2026-03-28` | `洽洽食品静态优先级为 A，需补渠道结构与品牌矩阵强证据。` |
| `q_v10_focus_verify` | `verification` | `acc_focus` | `high` | `open` | `codex_llm` | `2026-03-28` | `焦点科技平台型跨境经营属性强，需补平台业务边界与客户结构强证据。` |
| `q_v10_haitian_prec_verify` | `verification` | `acc_haitian_prec` | `high` | `open` | `codex_llm` | `2026-03-28` | `海天精工可作为机床装备多工厂制造样本，需补工厂布局与事业部证据。` |
| `q_v10_dsbj_verify` | `verification` | `acc_dsbj` | `high` | `open` | `codex_llm` | `2026-03-28` | `东山精密可作为精密制造多基地样本，需补事业部与区域经营证据。` |
| `q_v10_focus_promo` | `promotion_review` | `acc_focus` | `medium` | `open` | `codex_llm` | `2026-03-28` | `若补齐平台业务边界与客户结构证据，可评估从 L5 上移。` |
| `q_v10_haitian_prec_promo` | `promotion_review` | `acc_haitian_prec` | `medium` | `open` | `codex_llm` | `2026-03-28` | `若补齐多基地经营证据，可评估从 L5 上移。` |
| `q_v10_beauty_asset_gap` | `knowledge_extraction` | `acc_botanee` | `medium` | `open` | `codex_llm` | `2026-03-28` | `当前美妆个护品牌消费品画像知识资产仍偏薄，建议补抽取相邻案例资产。` |
| `q_v10_jewelry_chain_gap` | `knowledge_extraction` | `acc_zhouliufu` | `medium` | `open` | `codex_llm` | `2026-03-28` | `当前珠宝连锁零售画像知识资产仍偏薄，建议补抽取相邻案例资产。` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前队列继续覆盖：
  - `verification`
  - `promotion_review`
  - `knowledge_extraction`
