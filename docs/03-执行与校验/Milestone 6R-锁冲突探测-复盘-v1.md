# milestone6r_trust_lock_probe_v1 execution复盘-v1

## 批次概览

- 目标：`Milestone 6R：主工作簿修复与可信度增强（12家）`
- 模式：`write_back`
- 状态：`fail`
- 开始：`2026-04-18T12:39:08.852039+00:00`
- 结束：`2026-04-18T12:39:09.952856+00:00`

## 阶段结果

- enrich：`status=failed`，`result_count=0`，`output=deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_enrich_v1.json`
- promote：`status=skipped`，`result_count=0`，`output=`

## 执行摘要

- promote 判定：`allow=0 / warn=0 / block=0`
- 写回：`enrich_enabled=False / promote_enabled=False`
- 写回锁：`acquired=False / wait_seconds=0.0`
- 完整性检查：`ok=None`
- run summary：`deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_lock_probe_run_summary_v1.json`
- enrich summary/review：`deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_enrich_summary_v1.json` / `docs/03-执行与校验/Milestone 6R-主表修复与可信增强-enrich复盘-v1.md`
- promote summary/review：`` / ``

## 失败信息

- error_stage：`enrich`
- error_message：workbook write lock is busy after 0.000s: /tmp/codex_static_pool_workbook_writeback.lock
