# milestone6_supply_enrich_v1 enrich复盘-v1

## 批次概览

- 目标：`Milestone 6 Supply：L5到L4供给附带批次（6家） enrich`
- 样本数：`6`
- 可进入 promote：`4`
- 候选类型：`formal_candidate=4 / observation=2`
- 最小事实：`pass=4 / partial=2 / fail=0`
- 官方源状态：`available=6 / missing=0`
- 写回治理：`queue_items_created=0 / evidence_items_created=0`

## 分对象复盘

### 公牛集团股份有限公司 / `acc_bull`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：公牛集团股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 东山精密制造股份有限公司 / `acc_dsbj`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：东山精密制造股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 入池理由仍偏画像模板。
- 当前仍处于观察/边界状态。

### 焦点科技股份有限公司 / `acc_focus`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：焦点科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 入池理由仍偏画像模板。
- 当前仍处于观察/边界状态。

### 上海克来机电自动化工程股份有限公司 / `acc_kelai`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：上海克来机电自动化工程股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 三全食品股份有限公司 / `acc_sanquan`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：三全食品股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 依依股份有限公司 / `acc_yiyi`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：依依股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
