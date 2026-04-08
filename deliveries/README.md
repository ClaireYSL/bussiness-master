# Deliveries

本目录只保留当前仍有复用价值的结果包、模板和最近执行产物。

默认原则已收口为：

1. `expand / enrich / promote` 日常执行不应默认往 repo 顶层落 JSON
2. 未显式指定 `--output-file` 时，结果默认写到 `/tmp/codex-static-pool-runs/`
3. 只有 milestone / 专项验收批次，才应显式落盘并进入 repo

当前优先保留：

- `phase1_*`
- `calibration_batch_*`
- `promote_batch_*`
- 当前仍在复用的 `expand_*`
- `templates/`

已结束的一次性批次结果已迁入：

- `/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/`

其中 milestone 级批次结果已集中到：

- `/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/`

其中客户档案逐批修复的历史 JSON 已集中到：

- `/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/customer_archive_repair_batches/`
