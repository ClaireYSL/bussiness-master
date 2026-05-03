# Milestone 13-画像边界规则评估复盘-v1

## 1. 摘要

- 样本数：`12`
- 决策分布：`{'keep_pending_review': 12}`
- 强 evidence 合计：`24`
- active fact patch 数：`0`

## 2. 规则结论

本轮没有对象满足 active_candidate 条件；原因主要是缺少人工或 LLM 转正确认。

## 3. 明细

### 中航西飞（acc_cn_000768）

- persona：`mfg_rnd_sales_complex`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认研产销协同、高技术制造或复杂产品经营链路。

### 国轩高科（acc_cn_002074）

- persona：`mfg_rnd_sales_complex`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认研产销协同、高技术制造或复杂产品经营链路。

### 光迅科技（acc_cn_002281）

- persona：`mfg_multi_factory_group`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认制造协同、多基地、多产线或集团化经营复杂度。

### 中顺洁柔（acc_cn_002511）

- persona：`retail_high_sku_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认多 SKU/多品类品牌经营，而不是只有单一产品或泛消费品描述。

### 金达威（acc_cn_002626）

- persona：`retail_high_sku_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable, promotion_review_missing`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认多 SKU/多品类品牌经营，而不是只有单一产品或泛消费品描述。

### 跨境通（acc_cn_002640）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

### 华凯易佰（acc_cn_300592）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

### 青木科技（acc_cn_301110）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`persona_required_dimensions_missing, active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

### 珠免集团（acc_cn_600185）

- persona：`retail_multi_store`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认门店/零售网络/区域经营结构，而不是只有零售行业标签。

### 盛美上海（acc_cn_688082）

- persona：`mfg_rnd_sales_complex`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable`
- reasons：`persona_required_dimensions_missing, active_confirmation_missing`
- active_confirmation_hint：需要能确认研产销协同、高技术制造或复杂产品经营链路。

### 追觅创新科技（苏州）有限公司（acc_dreame）

- persona：`retail_high_sku_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable, promotion_review_missing`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认多 SKU/多品类品牌经营，而不是只有单一产品或泛消费品描述。

### 深圳市通拓科技有限公司（acc_tomtop）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- suggested_review_status：`pending_review`
- strong_evidence_count：`2`
- warning_codes：`persona_boundary_unstable, promotion_review_missing`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。
