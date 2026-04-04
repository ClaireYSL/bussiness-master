# `account_review_queue_v1` 补充内容 v0.7

## 1. 文档目的

本文件为 [external_target_account_pool_v2-首版真实内容-v0.10.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.10.md) 新迁入的第八轮 `L5` 账户补充结构化工作队列。

## 2. 本轮新增队列项

| queue_item_id | queue_type | account_id | priority | status | owner | reason_summary | target_action | due_hint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `q_verify_zhongjing_v1` | `verification` | `acc_zhongjing` | `high` | `open` | `codex_llm` | 仲景食品高 SKU 品牌消费品画像稳定，适合优先补渠道与库存协同证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_xidamen_v1` | `verification` | `acc_xidamen` | `high` | `open` | `codex_llm` | 西大门材料出口画像明确，适合优先补海外占比与品牌边界证据。 | `补第2条强证据并复核是否可进入 L4/L3 上移候选` | `next_cycle` |
| `q_verify_zdleader_v1` | `verification` | `acc_zdleader` | `high` | `open` | `codex_llm` | 中大力德自动化 / 传动部件画像稳定，适合优先补业务结构与客户颗粒度证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_wanma_v1` | `verification` | `acc_wanma` | `high` | `open` | `codex_llm` | 万马股份线缆与新材料制造协同属性明确，适合优先补客户协同证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_verify_hanzhong_v1` | `verification` | `acc_hanzhong` | `high` | `open` | `codex_llm` | 汉钟精机高端设备制造画像明确，适合优先补全球经营与业务条线证据。 | `补第2条强证据并准备 promotion_review` | `next_cycle` |
| `q_promo_zhongjing_v1` | `promotion_review` | `acc_zhongjing` | `medium` | `open` | `codex_llm` | 仲景食品与食品饮料高 SKU 样本相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_promo_megain_v1` | `promotion_review` | `acc_megain` | `medium` | `open` | `codex_llm` | 麦加芯彩与新材料出口画像相邻，补证据后可评估上移。 | `补证据后评估是否从 L5 升到 L4` | `after_verification` |
| `q_boundary_inteco_v1` | `boundary_review` | `acc_mustangbat` | `medium` | `open` | `codex_llm` | 野马电池处于电池出口和品牌经营边界之间，需要持续校准复杂跨境经营画像。 | `复核品牌经营边界与主画像归属` | `before_promotion` |
| `q_knowledge_foodbrand_v1` | `knowledge_extraction` | `acc_zhongjing` | `medium` | `open` | `codex_llm` | 当前调味品 / 乳品 / 烘焙品牌消费品知识资产仍可继续增厚。 | `补抽食品饮料品牌消费品、渠道与库存协同相关知识资产` | `next_month` |
| `q_cleanup_material_export_v1` | `cleanup_review` | `acc_megain` | `low` | `open` | `codex_llm` | 材料出口与复杂跨境经营画像在主表中占比上升，需要持续检查边界是否过宽。 | `月度复盘时检查材料出口类账户的画像边界` | `monthly_review` |

## 3. 本轮完成情况

- 新增 `10` 条队列项
- 当前第八轮 L5 迁移后的重点核验对象已进入显式工作队列

## 4. 关联文档

- [account_review_queue_v1-补充内容-v0.6.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/account_review_queue_v1-补充内容-v0.6.md)
- [external_target_account_pool_v2-首版真实内容-v0.10.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/external_target_account_pool_v2-首版真实内容-v0.10.md)
