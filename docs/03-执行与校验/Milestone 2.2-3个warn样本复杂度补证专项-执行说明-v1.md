# Milestone 2.2-3个warn样本复杂度补证专项-执行说明-v1

## 目的

本轮只处理 `Milestone 2.1` 中已经完成主画像收敛、但 `promote` 仍为 `warn` 的 `3` 家样本：

- `acc_popmart`
- `acc_loctek`
- `acc_jereh`

本轮目标不是改主画像，而是把它们从：

- `formal_candidate + warn`

推进到：

- `formal_candidate + allow`

## 配置与结果位置

批次配置：

- [milestone2_2_warn_complexity_resolution_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_2_warn_complexity_resolution_v1.json)

事实补强包：

- [milestone2_2_warn_complexity_resolution_facts_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_2_warn_complexity_resolution_facts_v1.json)

promotion_review 队列补丁：

- [milestone2_2_warn_complexity_resolution_queue_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/archive/enrich_batches/milestone2_2_warn_complexity_resolution_queue_v1.json)

结果包：

- [milestone2_2_warn_complexity_resolution_promote_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2_2/milestone2_2_warn_complexity_resolution_promote_v1.json)
- [milestone2_2_warn_complexity_resolution_summary_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/archive/milestones/milestone2_2/milestone2_2_warn_complexity_resolution_summary_v1.json)

## 本轮动作

1. 为 `3` 家样本追加复杂度颗粒度 evidence
2. 更新 `validation_gap`，把“后续再补”收敛为“已具备 promotion_review 基础”
3. 打开或重用 `promotion_review` 队列项
4. 重跑 `promote`
5. 输出 summary

## 本轮结果

### promote

- `allow = 3`
- `warn = 0`
- `block = 0`

### summary

- `control_to_allow = 3`

## 三家结果

- `acc_popmart`
  - `L4 warn -> L4 allow`
- `acc_loctek`
  - `L3 warn -> L3 allow`
- `acc_jereh`
  - `L3 warn -> L3 allow`

## 补丁摘要

事实补强：

- `profile_updates = 3`
- `main_shared_updates = 3`
- `evidence_rows_created = 3`

队列补丁：

- `created = 1`
- `reopened_or_updated = 2`

说明：

- 本轮真正消除的阻塞是 `promotion_review_missing`
- 当前系统已从“主画像收敛”推进到“可作为建议推进对象”
