# Milestone 11-warn质量解阻执行说明-v1

## 1. 执行目标

本轮承接 Milestone 7 状态口径修复后的 6R 样本，目标不是强行升层，而是消除可通过补证和字段重写解决的 warn。

基线：

1. `allow=0 / warn=12 / block=0`
2. `evidence_thin=10`
3. `generic_product=6`
4. `generic_admission=1`
5. `persona_boundary_unstable=12`

验收口径：

1. `evidence_thin` 明显下降
2. `generic_product` 明显下降
3. `generic_admission` 降为 0
4. 剩余 warn 能解释为画像边界待复核

## 2. 输入与配置

候选：

- `deliveries/archive/repairs/milestone6r_trust_candidates_reselect_20260419.json`

补证包：

- `configs/execution_batches/milestone11_warn_quality_facts_v1.json`

执行配置：

- `configs/execution_batches/milestone11_warn_quality_registry_v1.json`
- `configs/promote_batches/milestone11_warn_quality_promote_v1.json`

执行命令口径：

```bash
STATIC_POOL_ROOT="/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池" \
python3 scripts/run_execution_batch.py \
  --config-file configs/execution_batches/milestone11_warn_quality_registry_v1.json \
  --phase report_only \
  --candidate-file deliveries/archive/repairs/milestone6r_trust_candidates_reselect_20260419.json
```

## 3. 闭环步骤

本轮继续使用固定闭环：

1. `select`
2. `report_only`
3. `gate_check`
4. `write_back --require-report-baseline`
5. `post_integrity`

说明：

- 当前补证包作为 promote 评估输入叠加，用于验证质量问题是否下降。
- 因本轮结果仍为 `warn=12`，正式写回阶段不会升层，也不会把 warn 样本写成 allow 结果。

## 4. 预期结果

预期：

1. `evidence_thin: 10 -> 0`
2. `generic_product: 6 -> 0`
3. `generic_admission: 1 -> 0`
4. `persona_boundary_unstable: 12 -> 12`

若结果符合预期，说明可补证质量问题已被消除，下一轮应聚焦画像稳定性复核，而不是继续做状态或字段口径修复。
