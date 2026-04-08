# Milestone 2-跨主线6家真实纠偏批次-执行说明-v1

## 目的

本轮不继续扩新 `expand provider`，而是用 `6` 家跨主线代表样本，压实当前执行层的真实纠偏闭环：

`事实补强 -> enrich -> promote -> 定向回写`

主目标不是追求更多 `allow`，而是让判定更可信。

## 主验收样本

### 零售消费

- `acc_popmart` / 北京泡泡玛特文化创意有限公司
- `acc_threesquirrels` / 三只松鼠股份有限公司

### 跨境电商

- `acc_loctek` / 乐歌人体工学科技股份有限公司
- `acc_jihong` / 厦门吉宏科技股份有限公司

### 先进制造

- `acc_jereh` / 烟台杰瑞石油服务集团股份有限公司
- `acc_bozon` / 博众精工科技股份有限公司

## 配置与入口

本轮固定配置：

- [milestone2_cross_track_rectification_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_cross_track_rectification_v1.json)

事实补强包：

- [milestone2_cross_track_rectification_facts_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_cross_track_rectification_facts_v1.json)

执行入口仍只使用：

- [scripts/enrich_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/enrich_static_pool.py)
- [scripts/promote_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/promote_static_pool.py)

辅助脚本：

- [scripts/apply_milestone2_fact_patch.py](/Users/clairaipartner/Codex/bussiness-master/scripts/apply_milestone2_fact_patch.py)
- [scripts/build_milestone2_rectification_summary.py](/Users/clairaipartner/Codex/bussiness-master/scripts/build_milestone2_rectification_summary.py)

## 本轮执行顺序

1. 用事实补强包补 `公司产品与服务概述 / 商业模式概述 / 核心客户客群 / official_source_count / primary_source_refs`
2. 向 `evidence_log` 写入 `12` 条官方源事实 evidence
3. 重跑 `enrich`
4. 对 `6` 家做定向回写
5. 用 enrich 结果包驱动 `promote`
6. 产出 milestone 汇总结果包

## 本轮结果包

事实补强结果：

- [milestone2_cross_track_rectification_fact_patch_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2/milestone2_cross_track_rectification_fact_patch_v1.json)

enrich 结果：

- [milestone2_cross_track_rectification_enrich_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2/milestone2_cross_track_rectification_enrich_v1.json)

promote 结果：

- [milestone2_cross_track_rectification_promote_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2/milestone2_cross_track_rectification_promote_v1.json)

总汇总：

- [milestone2_cross_track_rectification_summary_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2/milestone2_cross_track_rectification_summary_v1.json)

## 本轮摘要

事实补强：

- `profile_updates = 6`
- `main_shared_updates = 6`
- `evidence_rows_created = 12`

enrich：

- `result_count = 6`
- `ready_for_promote = 3`
- `observation = 3`

promote：

- `allow = 0`
- `warn = 3`
- `block = 3`

总汇总：

- `observation_kept = 3`
- `observation_promoted_to_formal = 0`
- `control_kept_warn = 3`
- `official_source_repaired = 3`

## 执行口径

本轮实际收紧了两个关键口径：

1. `enrich` 不再只复读 rectification 包中的 `official_source_missing / minimum_fact_decision`，而是回到事实层实时读取字段和 evidence 状态。
2. `promote` 继续以 enrich 结果为前置，不允许 observation 或 enrich 未就绪对象被误放进 `allow`。

## 定向回写结果

本轮 enrich 写回前自动备份了外部工作簿：

- `潜客档案库.enrich_backup_20260408_223828.xlsx`
- `内部运营-静态潜客池-共享版.enrich_backup_20260408_223828.xlsx`
- `治理与证据.enrich_backup_20260408_223828.xlsx`

写回摘要：

- `profile_updates = 6`
- `main_shared_updates = 6`
- `queue_items_created = 0`
- `evidence_items_created = 0`

说明：

- 当前队列和治理项复用原有 open 项，没有出现重复污染。
