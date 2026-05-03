# 交接快照

- 生成时间(UTC): `2026-04-27T02:33:11.677417+00:00`
- 分支: `codex/milestone12-persona-stability`
- 提交: `693a0e4`
- 工作区是否干净: `no`

## 修复基线

- main_id_repair coverage: `1.0`
- main_id_repair generated_rows: `138`
- workbook_integrity ok: `True`

## 最近执行摘要

- `deliveries/archive/milestones/milestone14_small_batch_expansion/milestone14_small_batch_run_summary_v1.json` | status=`success` mode=`report_only` allow/warn/block=`0/0/15` lock=`False`
- `deliveries/archive/milestones/milestone13_persona_boundary_rules/milestone13_persona_boundary_run_summary_v1.json` | status=`success` mode=`report_only` allow/warn/block=`0/12/0` lock=`False`
- `deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_run_summary_v1.json` | status=`success` mode=`report_only` allow/warn/block=`0/12/0` lock=`False`
- `deliveries/archive/milestones/milestone11_warn_quality/milestone11_warn_quality_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`0/12/0` lock=`True`
- `deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`0/12/0` lock=`True`
- `deliveries/archive/milestones/milestone6r_trust/milestone6r_trust_lock_probe_run_summary_v1.json` | status=`fail` mode=`write_back` allow/warn/block=`0/0/0` lock=`False`
- `deliveries/archive/milestones/milestone6_supply/milestone6_supply_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`0/0/6` lock=`None`
- `deliveries/archive/milestones/milestone6/milestone6_run_summary_v1.json` | status=`success` mode=`write_back` allow/warn/block=`10/2/0` lock=`None`

## 关键配置(最近)

- `configs/execution_batches/milestone14_small_batch_registry_v1.json` | milestone=`milestone14_small_batch_expansion` batch=`milestone14_small_batch_expansion_v1`
- `configs/enrich_batches/milestone14_small_batch_enrich_v1.json` | milestone=`` batch=`milestone14_small_batch_enrich_v1`
- `configs/promote_batches/milestone14_small_batch_promote_v1.json` | milestone=`` batch=`milestone14_small_batch_promote_v1`
- `configs/execution_batches/milestone13_2_manual_persona_review_template_v1.json` | milestone=`` batch=`milestone13_2_manual_persona_review_template_v1`
- `configs/execution_batches/milestone13_persona_boundary_registry_v1.json` | milestone=`milestone13_persona_boundary_rules` batch=`milestone13_persona_boundary_batch_v1`
- `configs/promote_batches/milestone13_persona_boundary_promote_v1.json` | milestone=`` batch=`milestone13_persona_boundary_promote_v1`
- `configs/execution_batches/milestone13_persona_boundary_queue_v1.json` | milestone=`` batch=`milestone13_persona_boundary_queue_v1`
- `configs/execution_batches/milestone13_persona_boundary_facts_v1.json` | milestone=`` batch=`milestone13_persona_boundary_facts_v1`
- `configs/execution_batches/milestone13_persona_boundary_rules_v1.json` | milestone=`milestone13_persona_boundary_rules` batch=`milestone13_persona_boundary_rules_v1`
- `configs/execution_batches/milestone12_persona_stability_registry_v1.json` | milestone=`milestone12_persona_stability` batch=`milestone12_persona_stability_batch_v1`
- `configs/execution_batches/milestone12_persona_stability_queue_v1.json` | milestone=`` batch=`milestone12_persona_stability_queue_v1`
- `configs/execution_batches/milestone12_persona_stability_facts_v1.json` | milestone=`` batch=`milestone12_persona_stability_facts_v1`

## 接力建议

- 先执行 `git pull` 并确认分支与本快照一致。
- 统一从 `configs/*` 驱动执行，避免手工拼命令。
- 保持 `report_only -> write_back` 顺序，并启用 `--require-report-baseline`。
- 写回前后各跑一次完整性检查。
