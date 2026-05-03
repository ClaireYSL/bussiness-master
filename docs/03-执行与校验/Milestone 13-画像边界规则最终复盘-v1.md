# Milestone 13-画像边界规则最终复盘-v1

## 1. 批次结论

- 状态：`report_only完成，gate_check=PASS，未执行write_back`
- 目标：把 M12 的 `persona_boundary_unstable` 转成可执行画像边界规则。
- 规则评估：`{'keep_pending_review': 12}`
- promote：`allow=0 / warn=12 / block=0`
- gate_check：`PASS`

## 2. 规则沉淀

本轮沉淀出的核心规则：

1. 强 evidence 是转正必要条件，但不是充分条件。
2. `review_status=active` 需要强 evidence、标准 persona、无本地 block、且有人工或明确复核确认。
3. LLM 单独建议不得触发 active；当前 LLM 建议为 `keep_pending_review`，因此全部保持 pending。
4. 允许的剩余 warn 只包括 `persona_boundary_unstable` 与 `promotion_review_missing`；其他质量 warn 必须先回到 M11/M12 补证。

## 3. 当前结果

- 样本数：`12`
- 强 evidence 合计：`24`
- active_candidate：`0`
- keep_pending_review：`12`
- hold_review：`0`

## 4. 明细

### 中航西飞（acc_cn_000768）

- persona：`mfg_rnd_sales_complex`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认研产销协同、高技术制造或复杂产品经营链路。

### 国轩高科（acc_cn_002074）

- persona：`mfg_rnd_sales_complex`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认研产销协同、高技术制造或复杂产品经营链路。

### 光迅科技（acc_cn_002281）

- persona：`mfg_multi_factory_group`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认制造协同、多基地、多产线或集团化经营复杂度。

### 中顺洁柔（acc_cn_002511）

- persona：`retail_high_sku_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认多 SKU/多品类品牌经营，而不是只有单一产品或泛消费品描述。

### 金达威（acc_cn_002626）

- persona：`retail_high_sku_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认多 SKU/多品类品牌经营，而不是只有单一产品或泛消费品描述。

### 跨境通（acc_cn_002640）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

### 华凯易佰（acc_cn_300592）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

### 青木科技（acc_cn_301110）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`persona_required_dimensions_missing, active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

### 珠免集团（acc_cn_600185）

- persona：`retail_multi_store`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认门店/零售网络/区域经营结构，而不是只有零售行业标签。

### 盛美上海（acc_cn_688082）

- persona：`mfg_rnd_sales_complex`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`persona_required_dimensions_missing, active_confirmation_missing`
- active_confirmation_hint：需要能确认研产销协同、高技术制造或复杂产品经营链路。

### 追觅创新科技（苏州）有限公司（acc_dreame）

- persona：`retail_high_sku_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认多 SKU/多品类品牌经营，而不是只有单一产品或泛消费品描述。

### 深圳市通拓科技有限公司（acc_tomtop）

- persona：`cbec_multi_platform_brand`
- boundary_decision：`keep_pending_review`
- strong_evidence_count：`2`
- reasons：`active_confirmation_missing`
- active_confirmation_hint：需要能确认跨境或多平台经营结构，而不是只有互联网电商或代运营标签。

## 5. 写回判断

本轮不执行 write_back。原因：

1. `active_candidate_count=0`。
2. M13 fact patch 未生成任何 `review_status=active` 字段。
3. 规则验证的目标是沉淀可复用边界，而不是强行转正。

## 6. 下一步

建议进入 M13.2：对 12 家做人工画像确认清单。若人工确认某家公司满足画像边界，可通过 manual review file 重新运行 M13 规则，并进入 `report_only -> gate_check -> write_back`。
