# Milestone 58R：静态潜客池 L1-L5 口径纠偏与动态边界隔离

## Summary

M58R 已将 L1-L5 从“经营优先级/人工反馈”口径纠偏为“静态 ICP 匹配 + 证据成熟度 + 信息完整度”。静态潜客池只回答是不是 ICP、为什么、证据是什么、可信到什么程度；不回答是否现在经营、由谁跟进、何时触达。

## 结果

- 当前 L1 ICP 强匹配档案：`0`
- 当前 L2 正式潜客档案：`8`
- 当前 L3 摘要卡：`20`
- 当前 L5 线索：`30`
- 静态 L1 ready：`0`
- 保留 L2：`8`
- 状态：`PASS_M58R_STATIC_BOUNDARY_CORRECTED`

## 产物

- 静态 L1 准入包：`deliveries/archive/milestones/milestone58r_static_pool_boundary_correction/static_l1_admission_package_v1.json`
- 静态 readiness score：`deliveries/archive/milestones/milestone58r_static_pool_boundary_correction/l1_static_readiness_score_v1.json`
- 动态边界 no-write/no-dynamic proof：`deliveries/archive/milestones/milestone58r_static_pool_boundary_correction/static_boundary_no_dynamic_proof_v1.json`
- M58R closure：`deliveries/archive/milestones/milestone58r_static_pool_boundary_correction/milestone58r_static_pool_boundary_correction_closure_v1.json`

## 边界

- 不写旧主表。
- 不写知识资产。
- 不改 persona registry。
- 不生成动态跟进任务。
- M57R 反馈模板已降级为 optional external feedback，不参与 L1/L2 静态分级。
