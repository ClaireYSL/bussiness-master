# M64R trusted pool 长期运行手册 v1

## 默认主线

source/persona -> candidate discovery -> enrich_static_facts -> attach_icp_references -> collect_strong_evidence -> static_promote -> static_gap_queue -> update_trusted_pool -> vault cards/dossiers。

## 运行命令

```bash
python3 scripts/trusted_pool_runner.py \
  --output-file deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/trusted_pool_runner_v2_report_v1.json \
  --write-baseline

python3 scripts/trusted_pool_runner.py \
  --output-file deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/trusted_pool_runner_v2_report_v1.json \
  --require-baseline
```

## 边界

- 默认不写旧 Excel。
- 默认不写知识资产。
- 默认不改 persona registry。
- 静态 L1-L5 不表达经营优先级、团队跟进或触达时间。
