# Milestone 12-主画像稳定性复核执行说明-v1

## 1. 目标

Milestone 12 处理 Milestone 11 后剩余的 `persona_boundary_unstable=12`。

本轮不追求粗暴把全部对象改成 `active`，而是逐一确认：

1. 当前主画像是否成立
2. 是否需要切换主画像或保留次级画像
3. 是否有足够证据支持从 `pending_review` 转为 `active`
4. 若继续 warn，真实业务原因是什么

## 2. 输入

固定回归样本：Milestone 6R/11 的 12 家候选。

主要输入文件：

1. `deliveries/archive/milestones/milestone11_warn_quality/milestone11_warn_quality_promote_v1_report_only_L2_1.json`
2. `deliveries/archive/repairs/milestone6r_trust_candidates_reselect_20260419.json`
3. 本机静态池工作簿，通过 `STATIC_POOL_ROOT` / `STATIC_POOL_*_FILE` 解析

## 3. LLM 委派边界

LLM 只处理抽象输入包。

允许发送：

1. 公司名称、主线、画像标签
2. 产品与服务概述、商业模式概述、入池理由
3. 证据摘要、来源类型、证据强度、支持维度
4. 当前 promote 结果和 warn code

不允许发送：

1. 原始长文素材
2. 未抽象的本地档案全文
3. 未经筛选的外部来源全文
4. 任何真实 API key 或本机隐私路径

LLM 输出只能作为画像复核草稿，不能直接写回。

## 4. 标准流程

```bash
python3 scripts/build_persona_stability_review_package.py \
  --promote-result-file deliveries/archive/milestones/milestone11_warn_quality/milestone11_warn_quality_promote_v1_report_only_L2_1.json \
  --output-file deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_abstract_input_v1.json \
  --review-file docs/03-执行与校验/Milestone 12-主画像稳定性复核草稿-v1.md
```

```bash
python3 scripts/llm_delegate.py \
  --system-file prompts/delegate/persona_stability_system.md \
  --user-file prompts/delegate/persona_stability_user.md \
  --input-file deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_abstract_input_v1.json \
  --input-source-tag abstracted_persona_review_package \
  --format json \
  --max-tokens 4000 \
  --timeout 240 \
  --output-file deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_llm_review_v1.json
```

LLM 结果复核后，才允许整理为后续 `fact_patch_file` 或人工复核清单。

## 5. 验收口径

1. 12 家均有画像稳定性判断
2. 每家公司都有 `keep_persona / change_persona / keep_pending_review / hold` 之一
3. 画像判断必须引用证据摘要或明确说明证据不足
4. 若建议转 `active`，必须说明为什么不再属于边界状态
5. 下一轮 `report_only` 中 `persona_boundary_unstable` 应明显下降
6. 若仍 `skipped=12`，复盘中必须解释剩余 warn 的真实业务原因

## 6. 当前首轮委派结果

已生成首轮抽象输入包和 LLM 复核草稿：

1. `deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_abstract_input_v1.json`
2. `deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_llm_review_v1.json`
3. `docs/03-执行与校验/Milestone 12-LLM画像复核结果草稿-v1.md`

首轮 LLM 草稿结论偏保守：12 家均建议继续 `pending_review`，核心剩余风险集中在官网、年报、IR、公告等更强一手证据不足。

因此 M12 后续不应直接批量转 `active`，应先补足能收束画像边界的强 evidence，再重跑 promote。

## 7. 行动包生成

首轮 LLM 复核结果需要先转换为安全行动包，不能直接写回。

```bash
python3 scripts/build_persona_stability_action_package.py
```

当前生成结果：

1. `deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_action_package_v1.json`
2. `configs/execution_batches/milestone12_persona_stability_facts_v1.json`
3. `configs/execution_batches/milestone12_persona_stability_queue_v1.json`
4. `docs/03-执行与校验/Milestone 12-画像稳定性行动包复盘-v1.md`

当前首轮行动包的安全结论：

1. `fact_patch_allowed_count=0`
2. `queue_patch_count=12`
3. `validation_error_count=0`

因此本轮 M12 下一步是强证据补证，而不是状态转正写回。

## 8. 最终闭环结果

本轮已完成 M12 首轮完整闭环：

1. 强 evidence patch：`configs/execution_batches/milestone12_persona_stability_evidence_patch_v1.json`
2. 合并 fact patch：`configs/execution_batches/milestone12_persona_stability_facts_v1.json`
3. report baseline：`deliveries/archive/milestones/milestone12_persona_stability/milestone12_persona_stability_report_baseline_v1.json`
4. gate check：`deliveries/archive/repairs/milestone12_persona_stability_gate_check_v1.json`
5. 最终复盘：`docs/03-执行与校验/Milestone 12-画像稳定性最终复盘-v1.md`

最终结果：

1. `allow=0 / warn=12 / block=0`
2. `persona_boundary_unstable=12`
3. `gate_check=PASS`
4. `status_patch_allowed_count=0`
5. 当前不执行 write_back

结论：M12 已完成“画像稳定性补证与闸门闭环”的工程闭环，但业务上仍需要人工画像复核或 M13 规则沉淀，才能决定哪些对象可从 `pending_review` 转为 `active`。
