# `account_review_queue_v1` 补充内容 v0.9

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.12.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.12.md) 新迁入账户补首版队列项。

本轮重点建立：

- 新增高价值账户的 `verification`
- 可上移对象的 `promotion_review`
- 新增画像缺口对应的 `knowledge_extraction`

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | created_at | reason_summary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `q_v09_yanjin_verify` | `verification` | `acc_yanjinshop` | `high` | `open` | `codex_llm` | `2026-03-28` | `盐津铺子静态优先级为 A，需补渠道结构与库存协同强证据。` |
| `q_v09_sanquan_verify` | `verification` | `acc_sanquan` | `high` | `open` | `codex_llm` | `2026-03-28` | `三全食品静态优先级为 A，需补品牌矩阵与渠道结构强证据。` |
| `q_v09_juewei_verify` | `verification` | `acc_juewei` | `high` | `open` | `codex_llm` | `2026-03-28` | `绝味食品连锁网络特征强，需补门店网络与直营网/加盟结构证据。` |
| `q_v09_loctek_verify` | `verification` | `acc_loctek` | `high` | `open` | `codex_llm` | `2026-03-28` | `乐歌股份品牌出海属性强，需补海外平台结构与品牌矩阵证据。` |
| `q_v09_liugong_verify` | `verification` | `acc_liugong` | `high` | `open` | `codex_llm` | `2026-03-28` | `柳工股份可作为多工厂制造高价值样本，需补多基地与事业部证据。` |
| `q_v09_jereh_verify` | `verification` | `acc_jereh` | `high` | `open` | `codex_llm` | `2026-03-28` | `杰瑞股份可作为高端装备制造样本，需补全球经营与业务条线证据。` |
| `q_v09_sinyang_verify` | `verification` | `acc_sinyang` | `medium` | `open` | `codex_llm` | `2026-03-28` | `上海新阳需补半导体材料业务结构与客户协同证据。` |
| `q_v09_liugong_promo` | `promotion_review` | `acc_liugong` | `medium` | `open` | `codex_llm` | `2026-03-28` | `若补齐多基地经营证据，可评估从 L5 上移至 L4/L3。` |
| `q_v09_loctek_promo` | `promotion_review` | `acc_loctek` | `medium` | `open` | `codex_llm` | `2026-03-28` | `若补齐海外渠道与品牌矩阵证据，可评估上移。` |
| `q_v09_food_brand_asset_gap` | `knowledge_extraction` | `acc_yanjinshop` | `medium` | `open` | `codex_llm` | `2026-03-28` | `当前休闲食品/速冻食品品牌消费品知识资产仍偏单薄，建议补抽取相关案例资产。` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前队列继续覆盖：
  - `verification`
  - `promotion_review`
  - `knowledge_extraction`

## 4. 关联文档

- [external_target_account_pool_v2-首版真实内容-v0.12.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.12.md)
- [account_evidence_log_v1-补充内容-v0.10.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_evidence_log_v1-补充内容-v0.10.md)
