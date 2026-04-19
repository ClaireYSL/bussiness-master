# milestone6r_trust_enrich_v1 enrich复盘-v1

## 批次概览

- 目标：`Milestone 6R：可信增强首轮12家 enrich`
- 样本数：`9`
- 可进入 promote：`4`
- 候选类型：`formal_candidate=4 / observation=5`
- 最小事实：`pass=4 / partial=5 / fail=0`
- 官方源状态：`available=9 / missing=0`
- 写回治理：`queue_items_created=0 / evidence_items_created=0`

## 分对象复盘

### 中炬高新技术实业（集团）股份有限公司 / `acc_chubang`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：中炬高新技术实业（集团）股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 产品与服务字段仍偏模板句。
- 当前仍处于观察/边界状态。

### 重庆登康口腔护理用品股份有限公司 / `acc_dencare`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：重庆登康口腔护理用品股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 产品与服务字段仍偏模板句。

### 英派斯健康科技股份有限公司 / `acc_impulse`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：英派斯健康科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 久祺股份有限公司 / `acc_jeep_bike`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：久祺股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 嘉益股份有限公司 / `acc_jiayi`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：嘉益股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 绝味食品股份有限公司 / `acc_juewei`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：绝味食品股份有限公司 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 入池理由仍偏画像模板。
- 当前仍处于观察/边界状态。

### 上海晨光文具股份有限公司 / `acc_mgstationery`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：上海晨光文具股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 产品与服务字段仍偏模板句。
- 当前仍处于观察/边界状态。

### 源飞宠物用品股份有限公司 / `acc_petstar`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：源飞宠物用品股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 广东拓斯达科技股份有限公司 / `acc_topstar`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`observation`，`minimum_fact=partial`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：广东拓斯达科技股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
- 风险项：
- 入池理由仍偏画像模板。
