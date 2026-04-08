# Milestone 2.1-3个observation主画像收敛专项-执行说明-v1

## 目的

本轮只处理 `3` 个在 `Milestone 2` 中仍处于 `observation + 空主画像` 的对象：

- `acc_popmart`
- `acc_loctek`
- `acc_jereh`

目标不是升层，而是把它们从“主画像待定”推进到“主画像可判”。

## 配置与结果位置

批次配置：

- [milestone2_1_observation_persona_resolution_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_1_observation_persona_resolution_v1.json)

事实补强包：

- [milestone2_1_observation_persona_resolution_facts_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_1_observation_persona_resolution_facts_v1.json)

rectification 包：

- [milestone2_1_observation_persona_resolution_rectification_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2_1/milestone2_1_observation_persona_resolution_rectification_v1.json)

结果包：

- [milestone2_1_observation_persona_resolution_enrich_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2_1/milestone2_1_observation_persona_resolution_enrich_v1.json)
- [milestone2_1_observation_persona_resolution_promote_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2_1/milestone2_1_observation_persona_resolution_promote_v1.json)
- [milestone2_1_observation_persona_resolution_summary_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2_1/milestone2_1_observation_persona_resolution_summary_v1.json)

## 本轮动作

1. 对 `3` 家样本追加 persona 收敛所需事实补强
2. 分别为 `retail_fashion_group / cbec_multi_platform_brand / mfg_multi_factory_group` 补充收敛用 evidence
3. 通过 rectification 包把主画像结论固定为标准 persona
4. 重跑 enrich 并做定向回写
5. 用 enrich 结果驱动 promote
6. 产出前后对比 summary

## 本轮结果

### enrich

- `result_count = 3`
- `ready_for_promote = 3`
- `observation = 0`

### promote

- `allow = 0`
- `warn = 3`
- `block = 0`

### summary

- `observation_promoted_to_formal = 3`
- `persona_resolved = 3`

## 主画像收敛结果

- `acc_popmart`
  - `待定 -> retail_fashion_group`
- `acc_loctek`
  - `待定 -> cbec_multi_platform_brand`
- `acc_jereh`
  - `待定 -> mfg_multi_factory_group`

## 写回结果

本轮 enrich 写回前自动备份了外部工作簿：

- `潜客档案库.enrich_backup_20260408_230024.xlsx`
- `内部运营-静态潜客池-共享版.enrich_backup_20260408_230024.xlsx`
- `治理与证据.enrich_backup_20260408_230024.xlsx`

写回摘要：

- `profile_updates = 3`
- `main_shared_updates = 3`
- `queue_items_created = 1`
- `evidence_items_created = 0`

说明：

- 本轮没有把 `3` 家推进到 `allow`
- 但已经把“空主画像 observation”收敛为“有主画像的 formal candidate + warn”
