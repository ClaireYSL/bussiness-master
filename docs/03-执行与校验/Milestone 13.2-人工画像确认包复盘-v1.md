# Milestone 13.2-人工画像确认包复盘-v1

## 1. 摘要

- 样本数：`12`
- 规则决策分布：`{'keep_pending_review': 12}`
- 当前默认人工决策：`全部 pending_manual_review`

## 2. 使用方式

本包不写回工作簿。若后续需要转 active，请在 template JSON 中把对应账户 `decision` 改为 `confirm_active`，再重新运行 M13 规则脚本。

## 3. 明细

### 中航西飞（acc_cn_000768）

- persona：`mfg_rnd_sales_complex`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 国轩高科（acc_cn_002074）

- persona：`mfg_rnd_sales_complex`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 光迅科技（acc_cn_002281）

- persona：`mfg_multi_factory_group`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 中顺洁柔（acc_cn_002511）

- persona：`retail_high_sku_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 金达威（acc_cn_002626）

- persona：`retail_high_sku_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 跨境通（acc_cn_002640）

- persona：`cbec_multi_platform_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 华凯易佰（acc_cn_300592）

- persona：`cbec_multi_platform_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 青木科技（acc_cn_301110）

- persona：`cbec_multi_platform_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：补足缺失维度或保持 keep_pending。

### 珠免集团（acc_cn_600185）

- persona：`retail_multi_store`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 盛美上海（acc_cn_688082）

- persona：`mfg_rnd_sales_complex`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：补足缺失维度或保持 keep_pending。

### 追觅创新科技（苏州）有限公司（acc_dreame）

- persona：`retail_high_sku_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。

### 深圳市通拓科技有限公司（acc_tomtop）

- persona：`cbec_multi_platform_brand`
- 规则判断：`keep_pending_review`
- 强 evidence：`2`
- 待人工确认：是否确认该对象的主画像已稳定，足以从 pending_review 转 active？
- 建议：人工复核后可考虑 confirm_active；若无法确认，保持 keep_pending。
