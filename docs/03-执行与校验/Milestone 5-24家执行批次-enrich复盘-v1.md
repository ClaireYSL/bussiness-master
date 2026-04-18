# milestone5_execution_enrich_v1 enrich复盘-v1

## 批次概览

- 目标：`Milestone 5：24家样本 enrich 批次`
- 样本数：`24`
- 可进入 promote：`24`
- 候选类型：`formal_candidate=24 / observation=0`
- 最小事实：`pass=24 / partial=0 / fail=0`
- 官方源状态：`available=24 / missing=0`
- 写回治理：`queue_items_created=0 / evidence_items_created=0`

## 分对象复盘

### 深圳市七十迈数字科技有限公司 / `acc_70mai`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：深圳市七十迈数字科技有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营颗粒度与平台结构细表。

### 上海爱婴室商务服务股份有限公司 / `acc_ays`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=1
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：上海爱婴室商务服务股份有限公司 enrich 完成：主画像=retail_multi_store，次级画像=1，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。需补充直营/加盟结构与区域经营颗粒度细节，明确persona边界

### 柏楚电子科技股份有限公司 / `acc_boci`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：柏楚电子科技股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 哈尔滨博实自动化股份有限公司 / `acc_boshi`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：哈尔滨博实自动化股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 博众精工科技股份有限公司 / `acc_bozon`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=1
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：博众精工科技股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=1，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。LTC链路、组织复杂度细节待补充

### 四川百茶百道实业股份有限公司 / `acc_chabaidao`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：四川百茶百道实业股份有限公司 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 华凯易佰科技股份有限公司 / `acc_cn_300592`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：华凯易佰科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 广东新宝电器股份有限公司 / `acc_donlim`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：广东新宝电器股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

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

### 宁波均胜电子股份有限公司 / `acc_junsheng`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：宁波均胜电子股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 开润股份有限公司 / `acc_klg`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：开润股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 全新好 / `acc_l5_000007`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：全新好 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营和渠道结构细表。

### 天音控股 / `acc_l5_000829`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：天音控股 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营和渠道结构细表。

### 爱施德 / `acc_l5_002416`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：爱施德 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营和渠道结构细表。

### 吉峰科技 / `acc_l5_300022`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：吉峰科技 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营和渠道结构细表。

### 博士眼镜 / `acc_l5_300622`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：博士眼镜 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营和门店网络细表。

### 农夫山泉股份有限公司 / `acc_nongfuspring`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：农夫山泉股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 源飞宠物用品股份有限公司 / `acc_petstar`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：源飞宠物用品股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 三柏硕健康科技股份有限公司 / `acc_sunsbike`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L4 -> L4`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：三柏硕健康科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已完成最小事实补齐；后续补区域经营颗粒度与平台结构细表。

### 江苏联赢激光股份有限公司 / `acc_uwlaser`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：江苏联赢激光股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 厦门厦钨新能源材料股份有限公司 / `acc_xtcnew`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L3 -> L3`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：厦门厦钨新能源材料股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L3；后续继续补官网、年报、IR和财报口径字段，再评估是否进入L2。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。

### 中联重科股份有限公司 / `acc_zhonglian`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L2 -> L2`
- enrich 判定：`formal_candidate`，`minimum_fact=pass`，`official_source=available`，`ready_for_promote=True`
- review 状态：`active`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=2`
- 结论：中联重科股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=True。
- 待验证项：已进入L2；后续继续补官网、年报、IR和财报口径字段。收入规模、利润状态、营收增长仍需回到更强来源继续补齐。
