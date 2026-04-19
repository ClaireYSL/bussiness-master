# 交接快照

- 生成时间(UTC): `2026-04-19T06:34:45.919814+00:00`
- 分支: `codex/execution-layer-foundation`
- 提交: `674ae4e`
- 工作区是否干净: `no`

## 修复基线

- main_id_repair coverage: `1.0`
- main_id_repair generated_rows: `138`
- workbook_integrity ok: `True`

## 最近执行摘要

- `deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`0/5/4` lock=`True`
- `deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_lock_probe_run_summary_v1.json` | status=`fail` mode=`write_back` allow/warn/block=`0/0/0` lock=`False`
- `deliveries/archive/milestones/milestone6_supply/milestone6_supply_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`0/0/6` lock=`None`
- `deliveries/archive/milestones/milestone6/milestone6_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`10/2/0` lock=`None`
- `deliveries/archive/milestones/milestone5/milestone5_execution_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`7/0/0` lock=`None`
- `deliveries/archive/milestones/milestone5_supply/milestone5a_supply_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`7/0/0` lock=`None`

## 关键配置(最近)

- `configs/execution_batches/milestone6r_trust_candidates_v1.json` | milestone=`` batch=`milestone6r_trust_batch_v1`
- `configs/enrich_batches/milestone6r_trust_enrich_v1.json` | milestone=`` batch=`milestone6r_trust_enrich_v1`
- `configs/promote_batches/milestone6r_trust_promote_v1.json` | milestone=`` batch=`milestone6r_trust_promote_v1`
- `configs/execution_batches/milestone6r_trust_registry_v1.json` | milestone=`milestone6r_trust` batch=`milestone6r_trust_batch_v1`
- `configs/execution_batches/milestone6_supply_candidates_v1.json` | milestone=`` batch=`milestone6_supply_batch_v1`
- `configs/execution_batches/milestone6_candidates_v1.json` | milestone=`` batch=`milestone6_main_batch_v1`
- `configs/promote_batches/milestone6_supply_promote_v1.json` | milestone=`` batch=`milestone6_supply_promote_v1`
- `configs/enrich_batches/milestone6_supply_enrich_v1.json` | milestone=`` batch=`milestone6_supply_enrich_v1`
- `configs/execution_batches/milestone6_supply_registry_v1.json` | milestone=`milestone6_supply` batch=`milestone6_supply_batch_v1`
- `configs/promote_batches/milestone6_promote_v1.json` | milestone=`` batch=`milestone6_promote_v1`
- `configs/enrich_batches/milestone6_enrich_v1.json` | milestone=`` batch=`milestone6_enrich_v1`
- `configs/execution_batches/milestone6_registry_v1.json` | milestone=`milestone6` batch=`milestone6_main_batch_v1`

## 接力建议

- 先执行 `git pull` 并确认分支与本快照一致。
- 统一从 `configs/*` 驱动执行，避免手工拼命令。
- 保持 `report_only -> write_back` 顺序，并启用 `--require-report-baseline`。
- 写回前后各跑一次完整性检查。
