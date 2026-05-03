# Milestone 7-10-执行闭环稳定化路线-v1

## 1. 阶段定位

本阶段目标是把静态潜客池执行层从“能跑”推进到“可重复、可解释、可迁移、可防漂移”。

当前主线继续固定为：

`知识库 -> 画像 -> L5 候选 -> enrich 补强 -> promote 上移 -> writeback 治理 -> share 消费`

本阶段不把大面积档案修复作为默认主线。档案修复只在阻碍上移判断或共享消费时作为支持动作进入。

## 2. Milestone 7：状态口径与准入规则收口

目标：

1. 把历史状态纳入规则层兼容映射
2. 避免候选因为旧状态字段被系统性 `invalid_review_status` 阻断
3. 保持未知状态的保守拦截

当前规则：

1. `active`：正式可评估
2. `pending_review`：观察/待核验可评估
3. `queued -> pending_review`
4. `auto_ingested -> pending_review`
5. `promotion_completed -> pending_review`
6. `hold / removed / 未知状态`：不进入上移评估

验收：

1. Milestone 6R 重跑后，`invalid_review_status` 不再是 12/12 主因
2. 未知状态仍会被 block

## 3. Milestone 8：批次执行闭环标准化

目标：

把每轮上移批次固定为五步：

1. `select`
2. `report_only`
3. `gate_check`
4. `write_back --require-report-baseline`
5. `post_integrity`

每轮必须产出：

1. 候选快照
2. run summary
3. report baseline
4. gate check JSON / Markdown
5. 写回后 integrity report

验收：

1. 候选签名与 baseline 一致
2. `enrich.result_count == promote.result_count == promote.results_count`
3. 工作簿完整性 `ok=true`
4. 写回锁可获取

## 4. Milestone 9：候选重选与上移结果复核

目标：

在状态兼容后重跑 Milestone 6R，比较修复前后的判断分布。

对比指标：

1. `allow / warn / block`
2. `promoted / skipped`
3. `profile_updates / main_updates / evidence_created / promotion_review_resolved`
4. block 主因是否从状态口径问题转为真实业务问题

验收：

1. 不再出现“全量状态口径 block”
2. 若仍 block，应能归因到证据薄、字段缺失、画像不稳或治理队列未完成

## 5. Milestone 10：执行层迁移与交接固化

目标：

让另一个 agent 或另一台机器能按固定流程恢复运行。

固定项：

1. `STATIC_POOL_ROOT` / `STATIC_POOL_*_FILE` 路径优先级
2. 工作簿完整性检查
3. handoff snapshot
4. 候选、baseline、gate check 的批次证据链

验收：

1. 新环境能完成 `py_compile`
2. 新环境能完成 workbook integrity
3. 新环境能完成一轮 `report_only`
4. 新环境能生成 handoff snapshot
