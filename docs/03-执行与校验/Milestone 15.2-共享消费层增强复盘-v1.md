# Milestone 15.2-共享消费层增强复盘-v1

## 1. 摘要

- 可进入人工消费对象：`15`
- 高价值 pending：`12`
- 待入池补丁对象：`0`
- 暂不共享对象：`0`
- 状态分布：`{'high_value_pending': 12, 'ready_for_human_review': 15}`

## 2. 共享对象

### 中航西飞（acc_cn_000768）

- 画像：`mfg_rnd_sales_complex`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 国轩高科（acc_cn_002074）

- 画像：`mfg_rnd_sales_complex`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 光迅科技（acc_cn_002281）

- 画像：`mfg_multi_factory_group`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 中顺洁柔（acc_cn_002511）

- 画像：`retail_high_sku_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 金达威（acc_cn_002626）

- 画像：`retail_high_sku_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 跨境通（acc_cn_002640）

- 画像：`cbec_multi_platform_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 华凯易佰（acc_cn_300592）

- 画像：`cbec_multi_platform_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 青木科技（acc_cn_301110）

- 画像：`cbec_multi_platform_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：persona_required_dimensions_missing,active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 珠免集团（acc_cn_600185）

- 画像：`retail_multi_store`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 盛美上海（acc_cn_688082）

- 画像：`mfg_rnd_sales_complex`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：persona_required_dimensions_missing,active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 追觅创新科技（苏州）有限公司（acc_dreame）

- 画像：`retail_high_sku_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 深圳市通拓科技有限公司（acc_tomtop）

- 画像：`cbec_multi_platform_brand`
- 状态：`high_value_pending`
- 为什么值得看：已具备 2 条强 evidence，画像维度基本齐备，但仍需人工确认是否可 active。
- 剩余风险：active_confirmation_missing
- 下一步：人工确认画像边界；若确认 active，再进入 report_only/gate/writeback。

### 烟台艾迪精密机械股份有限公司（acc_aidi）

- 画像：`mfg_rnd_sales_complex`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 爱慕股份有限公司（acc_aimer）

- 画像：`retail_high_sku_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 安记食品股份有限公司（acc_anji）

- 画像：`retail_high_sku_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 安井食品集团股份有限公司（acc_anjingfood）

- 画像：`retail_high_sku_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 奥飞娱乐股份有限公司（acc_aofei）

- 画像：`retail_high_sku_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 箭牌家居集团股份有限公司（acc_arrowhome）

- 画像：`retail_multi_store`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 深圳市傲基创新科技股份有限公司（acc_aukey）

- 画像：`cbec_multi_platform_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 浙江嘉益保温科技股份有限公司（acc_cayi）

- 画像：`cbec_multi_platform_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 江苏天奈科技股份有限公司（acc_cnano）

- 画像：`mfg_rnd_sales_complex`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 浙江大自然户外用品股份有限公司（acc_daziran）

- 画像：`cbec_multi_platform_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 浙江鼎力机械股份有限公司（acc_dingli）

- 画像：`mfg_multi_factory_group`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 深圳市易仓科技有限公司（acc_eccang）

- 画像：`cbec_multi_platform_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 江苏先锋精密科技股份有限公司（acc_focusprecision）

- 画像：`mfg_rnd_sales_complex`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 杭州巨星科技股份有限公司（acc_greatstar）

- 画像：`cbec_multi_platform_brand`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

### 宁波海天精工股份有限公司（acc_haitianjg）

- 画像：`mfg_multi_factory_group`
- 状态：`ready_for_human_review`
- 为什么值得看：小批扩容候选，已完成 report_only 预检。
- 剩余风险：待人工确认画像边界和真实业务优先级。
- 下一步：规则层已可执行；进入 M17 写回准入材料，但真实 write_back 仍需单独确认。

## 3. 待补和暂不共享对象
