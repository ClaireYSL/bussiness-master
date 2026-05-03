# Milestone 12-主画像稳定性复核草稿-v1

## 1. 批次概览

- batch_id：`milestone12_persona_stability_review_v1`
- 生成时间：`2026-04-27T01:39:32.733528+00:00`
- 样本数：`12`
- 当前 promote：`allow=0 / warn=12 / block=0`
- persona_boundary_unstable：`12`

## 2. 复核口径

本文件是 LLM/人工画像复核前的抽象输入草稿，不是写回结果。

建议动作只能落入：`keep_persona`、`change_persona`、`keep_pending_review`、`hold`。

## 3. 公司清单

### 追觅创新科技（苏州）有限公司（acc_dreame）

- 主线 / 当前画像：`零售消费 / retail_high_sku_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营智能家电相关产品或品牌业务，属于高 SKU、多渠道经营的品牌消费品主体。
- 入池理由：智能家电品牌与 SKU 复杂度明显，符合高 SKU 品牌消费品画像。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 深圳市通拓科技有限公司（acc_tomtop）

- 主线 / 当前画像：`跨境电商 / cbec_multi_platform_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营跨境品牌出海相关业务，属于多平台经营的跨境品牌或供应链出海主体。
- 入池理由：跨境电商经营属性明确，适合作为品牌出海相邻候选。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 珠免集团（acc_cn_600185）

- 主线 / 当前画像：`零售消费 / retail_multi_store`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营零售渠道、百货、连锁卖场或区域零售网络业务，具备多门店经营复杂度。
- 入池理由：珠免集团 具备零售消费主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 金达威（acc_cn_002626）

- 主线 / 当前画像：`零售消费 / retail_high_sku_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营品牌消费品、个护、家居、食品或耐用品等多 SKU 产品，具备较强商品与渠道复杂度。
- 入池理由：金达威 具备零售消费主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 中顺洁柔（acc_cn_002511）

- 主线 / 当前画像：`零售消费 / retail_high_sku_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营品牌消费品、个护、家居、食品或耐用品等多 SKU 产品，具备较强商品与渠道复杂度。
- 入池理由：中顺洁柔 具备零售消费主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 跨境通（acc_cn_002640）

- 主线 / 当前画像：`跨境电商 / cbec_multi_platform_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营跨境品牌消费品业务，具备多平台、多国家、多产品线经营复杂度。
- 入池理由：跨境通 具备跨境电商主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 青木科技（acc_cn_301110）

- 主线 / 当前画像：`跨境电商 / cbec_multi_platform_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营跨境品牌消费品业务，具备多平台、多国家、多产品线经营复杂度。
- 入池理由：青木科技 具备跨境电商主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 华凯易佰（acc_cn_300592）

- 主线 / 当前画像：`跨境电商 / cbec_multi_platform_brand`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营跨境品牌消费品业务，具备多平台、多国家、多产品线经营复杂度。
- 入池理由：华凯易佰 具备跨境电商主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 光迅科技（acc_cn_002281）

- 主线 / 当前画像：`先进制造 / mfg_multi_factory_group`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营多工厂、多基地制造业务，具备集团化制造协同复杂度。
- 入池理由：光迅科技 具备先进制造主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 中航西飞（acc_cn_000768）

- 主线 / 当前画像：`先进制造 / mfg_rnd_sales_complex`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营技术型设备、材料、工业产品或高复杂制造业务，具备研产销协同复杂度。
- 入池理由：中航西飞 具备先进制造主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 盛美上海（acc_cn_688082）

- 主线 / 当前画像：`先进制造 / mfg_rnd_sales_complex`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营技术型设备、材料、工业产品或高复杂制造业务，具备研产销协同复杂度。
- 入池理由：盛美上海 具备先进制造主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。

### 国轩高科（acc_cn_002074）

- 主线 / 当前画像：`先进制造 / mfg_rnd_sales_complex`
- 当前状态：`pending_review`
- 当前 promote：`warn`
- warn：`persona_boundary_unstable`
- 产品与服务：主营技术型设备、材料、工业产品或高复杂制造业务，具备研产销协同复杂度。
- 入池理由：国轩高科 具备先进制造主线下的典型经营复杂度，已补到公开主体名单、行业分类与上市公司公开披露层，满足 L3 静态样本门槛。
- 待复核问题：当前主画像是否已经稳定到足以从 pending_review 转为 active，或是否应继续 pending/hold/调整画像。
