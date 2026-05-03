# Milestone 6R block 解阻优先级清单-v1

## 1. 当前结论（基于 Milestone 7 状态兼容后回归）

- 样本范围：`milestone6r_trust` 当前候选 12 家（3 条主线各 4 家）
- 修复前 promote 结果：`allow=0 / warn=0 / block=12`
- 修复后 promote 结果：`allow=0 / warn=12 / block=0`
- 原 block 主因：`invalid_review_status`（12/12，100%）
- 当前结论：状态口径阻塞已解除，剩余问题转为 warn 级补证与画像稳定性风险

原始状态分布（12 家）：

1. `auto_ingested`：10 家
2. `promotion_completed`：2 家

以上两类状态已通过规则层映射为 `pending_review`，不再触发 `invalid_review_status`。

## 2. 优先级分组

### P0（已完成）：review_status 口径统一

目标：先把“状态口径不兼容”从系统性阻塞降为可评估状态。

已完成动作：

1. 已做状态映射决议：
   - `auto_ingested -> pending_review`
   - `promotion_completed -> pending_review`
2. 采用代码兼容，不批量改表
3. 重跑 `report_only` 验证已解除 `invalid_review_status`

受影响账号：

1. `auto_ingested`（10 家）
   - `acc_cn_000768`
   - `acc_cn_002074`
   - `acc_cn_002281`
   - `acc_cn_002511`
   - `acc_cn_002626`
   - `acc_cn_002640`
   - `acc_cn_300592`
   - `acc_cn_301110`
   - `acc_cn_600185`
   - `acc_cn_688082`
2. `promotion_completed`（2 家）
   - `acc_dreame`
   - `acc_tomtop`

### P1（已完成）：候选与基线重锁定

目标：避免“修过状态但候选/基线旧快照”导致准入失败。

已完成动作：

1. 已重跑 `select_execution_candidates.py --strict`
2. 已重跑 `run_execution_batch.py --phase report_only`
3. 已重新生成并确认 baseline 候选签名一致

验收结果：

1. `invalid_review_status` 已不再是 block 主因
2. 三份产物计数一致：`enrich.result_count == promote.result_count == promote.results_count`

### P2（已完成）：闸门复核 + 串行执行

目标：在状态解阻后再进入写回，避免无效写回。

已完成动作：

1. 已运行 `pre_writeback_gate_check.py`
2. 已确认 5 个闸门全部 PASS
3. 已执行 `--phase write_back --require-report-baseline`

验收结果：

1. `promote_write_back_enabled=true`
2. 本轮结果仍为 `skipped=12`，因为 12 家均为 warn，不进入 allow 升层
3. 写回后 workbook integrity 仍为 `ok=true`

### P3（下一步）：warn 级问题分层补证

当前 warn 主因：

1. `persona_boundary_unstable`：12 家
2. `evidence_thin`：10 家
3. `generic_product`：6 家
4. `generic_admission`：1 家

建议下一轮优先处理：

1. 给 10 家 `evidence_thin` 补至少 1 条强来源 evidence
2. 给 6 家 `generic_product` 重写更具体的产品与服务字段
3. 对 12 家 `persona_boundary_unstable` 做一次主画像稳定性复核

## 3. 建议执行顺序（最短路径）

1. 先处理 `evidence_thin`
2. 再处理 `generic_product / generic_admission`
3. 最后复核 `persona_boundary_unstable`
4. 重跑 `report_only -> gate_check -> write_back`

## 4. 风险提示

1. 状态口径问题已经解除，但不代表 12 家已经可以升层。
2. 当前全量 warn 是合理保守结果，应先补证再追求 allow。
3. 后续每轮仍需保留 baseline 与 gate check，避免候选漂移。
