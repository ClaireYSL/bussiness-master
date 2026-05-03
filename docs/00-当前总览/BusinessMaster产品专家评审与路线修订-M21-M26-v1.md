# BusinessMaster 产品专家评审与路线修订 M21-M26 v1

## 1. 评审结论

产品专家评审认为：BusinessMaster 当前系统设计方向成立，但下一阶段计划仍偏“工程治理视角”，需要更快切到“增长产品经营视角”。

原 M21-M26 的主要问题不是顺序完全错误，而是业务反馈进入太晚。如果先继续做 M21 的内部画像确认，再做 M22 写回，最后才做 M23 业务反馈，项目可能会把“系统内部可解释”误认为“业务真实可用”。

因此，本次路线修订采纳产品专家建议：

1. 将 `M23A 首批15家L3业务反馈快跑` 前置为 P0。
2. M21 保持 P0，但必须和 M23A 并行，并把业务价值字段纳入画像确认模板。
3. M22 只有在出现 `confirm_active_high_value` 时才进入写回准入。
4. M24 先做最小知识资产，不做全量规则体系。
5. M25 继续暂缓，扩容前必须证明 L3 样本有业务行动价值。

## 2. 核心风险

### 2.1 P0：画像确认可能仍是内部规则确认

M21 把 `persona_boundary_unstable=30` 转成 `confirm_active / keep_pending / hold / persona_adjust` 是必要的，但如果确认依据只来自 evidence、产品描述和本地规则，就仍然是系统内部自洽。

B2B 潜客池的核心不是“像不像画像”，而是“是否值得业务继续投入动作”。

### 2.2 P0：业务反馈进入太晚

当前已有 `15` 家 L3 可消费对象，这是项目最宝贵的真实验证样本。它们已经经过真实写回、证据补强和 share 包生成。

如果不先验证这 15 家是否真的被业务认为值得看，后续继续推进 30 家，只是在扩大内部定义的合格池。

### 2.3 P0：成功指标偏工程化

当前已有指标包括：

1. `allow/warn/block`
2. `gate PASS`
3. `workbook integrity ok=true`
4. `promoted/skipped`

这些是治理指标，不是产品成功指标。

下一阶段必须补充增长产品指标：

1. `business_reviewed_count`
2. `accepted_by_business_count`
3. `rejected_by_business_count`
4. `next_action_defined_count`
5. `positive_fit_rate`
6. `disqualification_reason_coverage`

### 2.4 P0：L3 可消费定义还不够产品化

当前 `l3_share_ready=15` 说明这些对象字段完整、证据可解释、share package 可读。

但产品上还需要回答：

1. 谁消费？
2. 在哪里消费？
3. 消费后做什么？
4. 多久反馈？
5. 反馈字段如何回流？

如果没有消费场景闭环，L3 只是漂亮的数据层级，不是业务资产。

## 3. 路线修订

### 3.1 修订前排序

1. M21：30 家画像确认与写回准入包，P0。
2. M22：第二批 L3 写回试点，P0/P1。
3. M23：业务反馈闭环，P1。
4. M24：知识库与画像规则资产化，P1。
5. M25：扩容到 50-100 家候选，P2。
6. M26：长期运行与交接固化，P2。

### 3.2 修订后排序

1. M23A：首批 15 家 L3 业务反馈快跑，P0。
2. M21：30 家画像确认与写回准入包，P0，和 M23A 并行。
3. M22：第二批 L3 写回试点，P0/P1，仅接收高价值确认对象。
4. M24：最小知识资产沉淀，P1，依赖 M23A/M21 反馈。
5. M25：50-100 家扩容，P2，继续暂缓。
6. M26：长期运行与交接固化，P2，小步整理，不压过业务验证。

## 4. 新增 M23A：首批15家L3业务反馈快跑

### 4.1 目标

用 M18 的 `15` 家 L3 可消费对象，快速验证 BusinessMaster 产出的对象是否真的具备业务行动价值。

### 4.2 输入

1. M18 L3 operational package。
2. M17 写回结果。
3. 每家公司 share 摘要、证据摘要、画像和风险说明。

### 4.3 输出

每家公司一条业务反馈记录，字段包括：

1. `business_fit_rating`
2. `worth_following`
3. `recommended_next_action`
4. `target_scenario`
5. `disqualify_reason`
6. `priority_rank`
7. `feedback_owner`
8. `feedback_date`
9. `feedback_notes`

### 4.4 成功口径

1. `business_reviewed_count >= 15`，或明确记录未完成原因。
2. `next_action_defined_count` 可统计。
3. `accepted_by_business_count / rejected_by_business_count` 可统计。
4. 每条 rejected 都有淘汰原因。
5. 至少形成一版画像/候选选择修正建议。

## 5. 修订 M21：画像确认加入业务价值维度

### 5.1 原分类

1. `confirm_active`
2. `keep_pending`
3. `hold`
4. `persona_adjust`

### 5.2 新分类

1. `confirm_active_high_value`
2. `confirm_active_low_priority`
3. `keep_pending_need_business_context`
4. `persona_adjust`
5. `hold_not_icp`

### 5.3 新成功口径

1. 每家公司都有画像判断和业务价值判断。
2. 每家公司都有建议下一步动作。
3. `confirm_active_high_value` 数量可统计。
4. 如果 `confirm_active_high_value_rate < 30%`，暂停 M22 写回，回到画像定义和候选选择策略。
5. 默认不写回，真实写回仍需单独确认。

## 6. 修订 M22：第二批写回只接收高价值确认对象

M22 不再以 `promoted > 0` 作为主要成功口径。

M22 的写回准入条件改为：

1. 规则层通过。
2. evidence 可信。
3. 画像明确。
4. 业务场景清楚。
5. 下一步动作明确。
6. M21 分类为 `confirm_active_high_value`。

M22 的成功口径改为：

1. `promoted > 0`。
2. `skipped=0`。
3. workbook integrity PASS。
4. `business_value_confirmed_count == promoted_count`。
5. share/action card 更新。

## 7. 北极星指标

下一阶段建议采用北极星指标：`可行动静态潜客数`。

定义：同时满足以下条件的公司数量：

1. 证据可信。
2. 画像明确。
3. 业务场景清楚。
4. 下一步动作明确。
5. 可被业务侧接收或继续判断。

当前 `l3_share_ready=15` 只能说明 share ready，不自动等于 actionable ready。

## 8. M24 最小知识资产范围

M24 不应一开始做大而全的规则知识体系。

第一版只沉淀四类：

1. 画像正例。
2. 画像反例。
3. 业务淘汰原因。
4. 强 evidence 判定样例。

这些知识资产必须吸收 M23A 和 M21 的真实反馈，而不是只来自 promote/gate 结果。

## 9. M25 扩容前置条件

M25 暂缓，直到满足以下条件：

1. M23A 证明首批 L3 中存在明确业务行动价值。
2. M21 产出一定比例的 `confirm_active_high_value`。
3. M24 已沉淀最小正例/反例/淘汰原因。
4. 候选扩容加入商业优先级排序。

商业优先级排序建议字段：

1. `icp_fit`
2. `business_scenario_clarity`
3. `reachability`
4. `industry_priority`
5. `evidence_strength`
6. `recent_trigger_signal`

## 10. 下一步执行建议

下一步不应单独推进 M21，而应执行：

1. 先生成 M23A 的 15 家业务反馈快跑包。
2. 同步生成 M21 的 30 家画像确认包，并加入业务价值字段。
3. 用 M23A 反馈修正 M21 判断标准。
4. 只有出现 `confirm_active_high_value`，才进入 M22 写回准入。
5. 用 M23A/M21 的正反例进入 M24 最小知识资产沉淀。

## 11. 不做事项

当前明确不做：

1. 不扩大到 100+。
2. 不追求 L2。
3. 不继续为所有 pending 做深补证。
4. 不把所有规则产品化。
5. 不用 LLM 输出直接决定 active 或写回。

## 12. 修订后的产品判断

BusinessMaster 当前不是缺工程能力，而是到了必须证明业务使用价值的节点。

下一阶段真正的产品拐点不是再写回多少家公司，而是证明：这些公司被业务看见后，是否真的能产生判断、行动和反馈。
