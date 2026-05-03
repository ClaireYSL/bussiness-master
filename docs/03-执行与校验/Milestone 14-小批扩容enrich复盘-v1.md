# milestone14_small_batch_enrich_v1 enrich复盘-v1

## 批次概览

- 目标：`Milestone 14：小批扩容 L5->L3 enrich 非写回复核`
- 样本数：`15`
- 可进入 promote：`0`
- 候选类型：`formal_candidate=0 / observation=15`
- 最小事实：`pass=0 / partial=0 / fail=15`
- 官方源状态：`available=14 / missing=1`
- 写回治理：`queue_items_created=0 / evidence_items_created=0`

## 分对象复盘

### 烟台艾迪精密机械股份有限公司 / `acc_aidi`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=missing`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：烟台艾迪精密机械股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：业务结构、全球经营与客户协同仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 缺少可定位的官方或高可信来源。

### 爱慕股份有限公司 / `acc_aimer`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：爱慕股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：渠道结构、品牌矩阵与会员经营仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 安记食品股份有限公司 / `acc_anji`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：安记食品股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：渠道结构、库存协同与品牌矩阵仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 安井食品集团股份有限公司 / `acc_anjingfood`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：安井食品集团股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：渠道结构、供应链与库存颗粒度仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 奥飞娱乐股份有限公司 / `acc_aofei`

- 主线 / 画像：`零售消费 / retail_high_sku_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：奥飞娱乐股份有限公司 enrich 完成：主画像=retail_high_sku_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：业务结构与消费品牌占比仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 箭牌家居集团股份有限公司 / `acc_arrowhome`

- 主线 / 画像：`零售消费 / retail_multi_store`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=3`
- 结论：箭牌家居集团股份有限公司 enrich 完成：主画像=retail_multi_store，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：直营网 / 经销网络与区域经营颗粒度仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 深圳市傲基创新科技股份有限公司 / `acc_aukey`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=0`
- 结论：深圳市傲基创新科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：当前主体有效性、经营阶段与品牌结构仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 浙江嘉益保温科技股份有限公司 / `acc_cayi`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=0`
- 结论：浙江嘉益保温科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：海外经营规模与平台结构仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 江苏天奈科技股份有限公司 / `acc_cnano`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：江苏天奈科技股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：业务链路与组织复杂度仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 浙江大自然户外用品股份有限公司 / `acc_daziran`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=0`
- 结论：浙江大自然户外用品股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：海外平台结构、品牌矩阵、区域经营仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 浙江鼎力机械股份有限公司 / `acc_dingli`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：浙江鼎力机械股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：制造基地、区域经营与客户结构仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 深圳市易仓科技有限公司 / `acc_eccang`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=0`
- 结论：深圳市易仓科技有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：平台业务边界、客户结构与场景范围仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。

### 江苏先锋精密科技股份有限公司 / `acc_focusprecision`

- 主线 / 画像：`先进制造 / mfg_rnd_sales_complex`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：江苏先锋精密科技股份有限公司 enrich 完成：主画像=mfg_rnd_sales_complex，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：主体强证据与经营复杂度仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 入池理由仍偏画像模板。
- 仅有 1 条较强来源，仍偏薄。

### 杭州巨星科技股份有限公司 / `acc_greatstar`

- 主线 / 画像：`跨境电商 / cbec_multi_platform_brand`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=0`
- 结论：杭州巨星科技股份有限公司 enrich 完成：主画像=cbec_multi_platform_brand，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：海外渠道结构、品牌矩阵、平台颗粒度仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 入池理由仍偏画像模板。
- 仅有 1 条较强来源，仍偏薄。

### 宁波海天精工股份有限公司 / `acc_haitianjg`

- 主线 / 画像：`先进制造 / mfg_multi_factory_group`；次级画像=0
- 层级建议：`L5 -> L5`
- enrich 判定：`observation`，`minimum_fact=fail`，`official_source=available`，`ready_for_promote=False`
- review 状态：`pending_review`；建议队列=`verification`
- 知识挂接：`knowledge_assets=5 / talk_tracks=1`
- 结论：宁波海天精工股份有限公司 enrich 完成：主画像=mfg_multi_factory_group，次级画像=0，知识资产=5，可进入 promote=False。
- 待验证项：工厂布局、业务条线与全球经营仍需补。
- 阻塞项：
- 公司产品与服务概述 不能为空。
- 商业模式概述 不能为空。
- 风险项：
- 仅有 1 条较强来源，仍偏薄。
