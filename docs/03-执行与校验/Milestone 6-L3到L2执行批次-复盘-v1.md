# milestone6_main_batch_v1 execution复盘-v1

## 批次概览

- 目标：`Milestone 6：L3到L2主闭环（12家）`
- 模式：`write_back`
- 状态：`success`

## 阶段结果

- enrich：`status=success`，`result_count=12`，`output=deliveries/archive/milestones/milestone6/milestone6_enrich_v1.json`
- promote：`status=success`，`result_count=12`，`output=deliveries/archive/milestones/milestone6/milestone6_promote_v1.json`

## 执行摘要

- promote 判定：`allow=10 / warn=2 / block=0`
- 写回：`promoted=10 / skipped=2 / evidence_created=10`
- 验收结论：
  - 样本结构：`4/4/4` 达成
  - 通过率阈值：`10/12 = 83.3%`，高于 `50%`
  - 每条主线均有推进对象和保守对象

## 关键产物

- run summary：`deliveries/archive/milestones/milestone6/milestone6_run_summary_v1.json`
- enrich summary/review：`deliveries/archive/milestones/milestone6/milestone6_enrich_summary_v1.json` / `docs/03-执行与校验/Milestone 6-L3到L2执行批次-enrich复盘-v1.md`
- promote summary/review：`deliveries/archive/milestones/milestone6/milestone6_summary_v1.json` / `docs/03-执行与校验/Milestone 6-L3到L2执行批次-promote复盘-v1.md`

