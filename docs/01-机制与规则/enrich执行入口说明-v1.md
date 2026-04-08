# enrich执行入口说明-v1

## 目的

`enrich` 是当前执行层的独立增强入口，职责不是升层，而是把潜客对象补到“可进入 promote 判断”的状态。

它负责三件事：

1. 补强事实层
2. 重算主画像 / 次级画像
3. 动态回挂强相关知识资产

## 当前脚本入口

- [enrich_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/enrich_static_pool.py)
- [enrich_engine.py](/Users/clairaipartner/Codex/bussiness-master/shared/static_pool/enrich_engine.py)

## enrich 输入

当前脚本支持：

- `--account-id`
- `--batch-file`
- `--track`
- `--from-level`
- `--rectification-file`
- `--report-only`
- `--write-back`
- `--output-file`

## enrich 输出

默认策略：

- 未显式指定 `--output-file` 时，结果默认写到 `/tmp/codex-static-pool-runs/`
- 只有 milestone / 专项验收批次，才应显式落 repo 结果包

每个对象至少输出：

- `persona_tag`
- `secondary_persona_tags`
- `knowledge_asset_refs`
- `talk_track_refs`
- `minimum_fact_status`
- `official_source_status`
- `candidate_type`
- `review_status`
- `validation_gap`
- `enrich_ready_for_promote`

## enrich 的当前边界

当前 enrich 允许：

1. 消费既有主表 / 档案库 / 治理与证据 / 知识资产注册表 / 画像注册表
2. 结合 `Phase 1` 纠偏结果重算主画像与次级画像
3. 生成知识资产强相关引用
4. 对指定样本做小范围定向回写

当前 enrich 不允许：

1. 新增知识资产
2. 新增 persona 定义
3. 直接基于档案长文倒推事实
4. 把知识资产引用当成事实增强证据

## 当前写回范围

`--write-back` 仅用于小样本定向回写，目前写到：

1. [潜客档案库.xlsx](/Users/clairaipartner/Documents/Obsidian-Codex/%E6%BD%9C%E5%AE%A2%E6%B1%A0/%E6%BD%9C%E5%AE%A2%E6%A1%A3%E6%A1%88%E5%BA%93.xlsx) 的 `account_profiles`
2. [内部运营-静态潜客池-共享版.xlsx](/Users/clairaipartner/Documents/Obsidian-Codex/%E6%BD%9C%E5%AE%A2%E6%B1%A0/%E5%86%85%E9%83%A8%E8%BF%90%E8%90%A5-%E9%9D%99%E6%80%81%E6%BD%9C%E5%AE%A2%E6%B1%A0-%E5%85%B1%E4%BA%AB%E7%89%88.xlsx) 的 `全量主表`
3. [治理与证据.xlsx](/Users/clairaipartner/Documents/Obsidian-Codex/%E6%BD%9C%E5%AE%A2%E6%B1%A0/%E6%B2%BB%E7%90%86%E4%B8%8E%E8%AF%81%E6%8D%AE.xlsx) 的 `review_queue` 与 `evidence_log`

## 与 promote 的关系

`enrich` 的输出是 `promote` 的前置输入，不应反过来被理解成上移动作本身。

正确顺序是：

1. `expand` 找人和最小入池增强
2. `enrich` 补事实、重算画像、回挂知识
3. `promote` 消费 enrich 结果，做 `allow / warn / block`
