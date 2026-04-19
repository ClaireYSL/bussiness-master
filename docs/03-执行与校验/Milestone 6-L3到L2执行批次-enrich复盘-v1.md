# milestone6_enrich_v1 enrich复盘-v1

## 批次概览

- 目标：`Milestone 6：L3到L2主闭环（12家） enrich`
- 样本数：`12`
- 可进入 promote：`10`
- 候选类型：`formal_candidate=10 / observation=2`
- 最小事实：`pass=10 / partial=2 / fail=0`
- 官方源状态：`available=12 / missing=0`
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

### 深圳市大疆创新科技有限公司 / `acc_dji`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：深圳市大疆创新科技有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 惠州亿纬锂能股份有限公司 / `acc_eve`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：惠州亿纬锂能股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 家家悦集团股份有限公司 / `acc_jiajia`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：家家悦集团股份有限公司 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 广西柳工机械股份有限公司 / `acc_liugong`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：广西柳工机械股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

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

### 明阳智慧能源集团股份公司 / `acc_mingyang`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：明阳智慧能源集团股份公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 涛涛车业股份有限公司 / `acc_taotao`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：涛涛车业股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 深圳市绿联科技股份有限公司 / `acc_ugreen`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：深圳市绿联科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 徐工集团工程机械股份有限公司 / `acc_xcmg`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：徐工集团工程机械股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 元祖股份有限公司 / `acc_yuanzu`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：元祖股份有限公司 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 子不语集团有限公司 / `acc_zibuyu`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L2 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：子不语集团有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：需补主体、组织结构与经营复杂度官方证据，待补promotion_review队列项
