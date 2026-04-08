# `external_target_account_pool_v2` L5 入池模板 v1.0

## 1. 文档目的

本文件用于在 `Milestone 2` 的最小机制下，给后续新增静态潜客提供一个统一、可直接复用的 `L5` 入池模板。

目标只有两个：

1. 让新增账户可以稳定进入 `L5`
2. 确保新增不会继续污染清洗后的事实主表

## 2. 入池前检查顺序

任何新账户正式进入 `L5` 前，必须按以下顺序检查：

1. 查询 [account_alias_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/account_alias_registry_v1-首版真实内容-v0.1.md)
2. 查询 [external_target_account_pool_v2-清洗后事实主表-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-清洗后事实主表-v1.0.md)
3. 对照老客映射与合作主体映射，做老客排除
4. 明确主线
5. 明确主画像
6. 写一句话入池理由
7. 补最小证据
8. 标记待验证项
9. 回填 `信息扎实度 / ICP匹配概率 / 静态潜客记录成熟度`
10. 才允许进入 `L5`

## 3. L5 最低必填字段

| 字段名 | 必填 | 说明 |
| --- | --- | --- |
| `account_id` | 是 | 稳定主键，命名规范与现有主表一致 |
| `account_canonical_name` | 是 | 归一主体名 |
| `brand_name` | 否 | 市场常用名 |
| `group_name` | 否 | 集团名 |
| `primary_track` | 是 | `零售消费 / 跨境电商 / 先进制造` |
| `industry_l1` | 是 | 一级行业 |
| `industry_l2` | 是 | 二级行业 |
| `business_model` | 是 | 业务模式 |
| `persona_tag` | 是 | 主画像 |
| `complexity_tag` | 是 | 一句话复杂度标签 |
| `primary_jtbd` | 是 | 主业务任务 |
| `current_business_problem` | 是 | 当前业务问题 |
| `admission_reason_summary` | 是 | 入池理由摘要 |
| `case_type_match` | 是 | 对应案例类型 |
| `existing_customer_reference` | 是 | 样本客户引用 |
| `solution_match` | 是 | 对应方案或打法 |
| `信息扎实度` | 是 | 默认建议 `中低` 或 `中` |
| `ICP匹配概率` | 是 | 默认建议 `中` 或 `中高` |
| `静态潜客记录成熟度` | 是 | 固定填 `L5` |
| `static_priority` | 是 | `A / B / C` |
| `dedupe_status` | 是 | 默认应为 `passed` 或 `pending` |
| `legacy_customer_check_status` | 是 | 默认 `passed` 或 `pending` |
| `review_status` | 是 | 默认 `active` 或 `pending_review` |
| `source_note` | 是 | 主要来源 |
| `validation_gap` | 是 | 当前待验证项 |

## 4. 最小证据要求

新账户进入 `L5` 时，至少要同步新增 `1` 条证据记录，并满足：

1. 证据类型明确
2. 来源明确
3. 至少能支撑：
   - 主线
   - 主画像
   - 入池理由

推荐证据强度：

- `B`：权威媒体 / 行业榜单 / 协会名录
- `C`：初步人工判断或弱外部资料

说明：

- `L5` 可接受 `B/C`
- 但不能没有证据直接入池
- `L5` 仅表示“该记录已满足最低入池标准”，不代表动态机会更高

## 5. 不允许直接入 L5 的情况

以下情况不允许直接进入正式 `L5`：

1. `account_alias_registry_v1` 已明确映射到现有 canonical account
2. 清洗后主表中已存在同一 canonical 主体
3. 明显疑似老客但未做排除确认
4. 没有主画像
5. 没有一句话入池理由
6. 没有任何证据

遇到上述情况，优先进入：

- `cleanup_review`
- 或 `verification`

而不是直接并入主表。

## 6. 建议写法模板

### 6.1 入池理由摘要模板

```text
该公司属于【主画像】，在【主线】下具备【经营复杂度 / 业务模式】特征，与现有【样本客户 / 案例类型】高度相邻，当前信息下判断其具备较高 ICP 相邻性，适合作为【静态潜客记录成熟度】候选纳入静态池，但仍需进一步验证【待验证项】。
```

### 6.2 当前业务问题模板

```text
公司在【渠道 / 门店 / 平台 / 工厂 / 事业部】协同上具备明显复杂度，当前更可能关心【主 JTBD】，符合观远在【方案类型】上的已验证打法。
```

### 6.3 待验证项模板

```text
待进一步确认其【主体映射 / 复杂度颗粒度 / 数据能力 / 经营链路细节 / 官方证据强度】。
```

## 7. 示例记录

| 字段 | 示例值 |
| --- | --- |
| `account_id` | `acc_example_brand` |
| `account_canonical_name` | `某某股份有限公司` |
| `brand_name` | `某某品牌` |
| `primary_track` | `零售消费` |
| `industry_l1` | `消费零售` |
| `industry_l2` | `品牌零售` |
| `business_model` | `多门店品牌零售` |
| `persona_tag` | `retail_multi_store` |
| `complexity_tag` | `多门店、多区域、总部强管控` |
| `primary_jtbd` | `总部经营分析与门店透视` |
| `current_business_problem` | `门店经营与区域差异分析复杂，总部到一线的经营动作闭环需求成立。` |
| `admission_reason_summary` | `该公司属于多门店连锁零售画像，在零售消费主线下与孩子王、名创优品等样本相邻，可先作为 L5 静态潜客纳入，但仍需验证其总部数字化成熟度。` |
| `case_type_match` | `连锁零售经营分析` |
| `existing_customer_reference` | `孩子王；名创优品` |
| `solution_match` | `门店经营分析 + AI 问数` |
| `信息扎实度` | `中低` |
| `ICP匹配概率` | `中高` |
| `静态潜客记录成熟度` | `L5` |
| `static_priority` | `B` |
| `dedupe_status` | `passed` |
| `legacy_customer_check_status` | `passed` |
| `review_status` | `active` |
| `source_note` | `官网 + 行业榜单` |
| `validation_gap` | `待确认门店规模区间与数据团队成熟度。` |

## 8. 关联文档

- [external_target_account_pool_v2-字段模板-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-字段模板-v1.md)
- [external_target_account_pool_v2-清洗后事实主表-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-清洗后事实主表-v1.0.md)
- [external_target_account_pool_v2-去重治理规则-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-去重治理规则-v1.0.md)
- [account_alias_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/account_alias_registry_v1-首版真实内容-v0.1.md)
- [静态潜客池-持续扩展最小机制-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/静态潜客池-持续扩展最小机制-v1.0.md)
