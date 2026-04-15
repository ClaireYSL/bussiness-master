# execution批次编排说明-v1

## 目的

把现行执行层从“手工串命令”收口为“统一批次编排”：

1. `enrich`
2. `promote`
3. 批次级 `summary/review`

对应入口脚本：

- [run_execution_batch.py](/Users/clairaipartner/Codex/bussiness-master/scripts/run_execution_batch.py)

## 配置入口

批次配置目录：

- `configs/execution_batches/`

模板：

- [template_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/execution_batches/template_v1.json)

## 配置结构

固定包含：

1. `batch_id`
2. `goal`
3. `mode`（`report_only` 或 `write_back`）
4. `enrich` 阶段配置
5. `promote` 阶段配置
6. `run_output`（run-level summary/review）

### enrich 阶段最小字段

1. `config_file`
2. `output_file`
3. `summary_file`
4. `review_file`

### promote 阶段最小字段

1. `config_file`
2. `output_file`
3. `summary_file`
4. `review_file`
5. `enrich_result_source`（推荐 `from_current_enrich`）

### run_output 最小字段

1. `summary_file`
2. `review_file`

## 使用方式

### report-only

```bash
python3 scripts/run_execution_batch.py --config-file configs/execution_batches/template_v1.json --report-only
```

### write-back

```bash
python3 scripts/run_execution_batch.py --config-file configs/execution_batches/template_v1.json --write-back
```

## 模式优先级

1. CLI 参数优先（`--report-only` / `--write-back`）
2. 批次配置 `mode`
3. 默认 `report_only`

## 输出产物

统一生成：

1. enrich result / summary / review
2. promote result / summary / review
3. execution run summary / run review

run summary 至少包含：

1. `batch_id`
2. `mode`
3. `status`
4. enrich 阶段执行状态与产物路径
5. promote 阶段执行状态与产物路径
6. `allow/warn/block` 汇总
7. 错误阶段与错误信息（若失败）

## 失败策略

1. enrich 失败则 promote 不执行
2. promote 失败则记录失败阶段并返回非 0
3. run summary/review 始终落盘，便于复盘

## 当前边界

1. runner 只编排现有 `enrich_static_pool.py` 与 `promote_static_pool.py`
2. 不改变 enrich/promote 判定规则本身
3. 历史 `scripts/legacy/` 不纳入统一编排入口
