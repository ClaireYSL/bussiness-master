# Milestone 43R-新可信潜客intake schema与采集器-v1

## 结论

- intake required fields：`9`
- evidence required fields：`7`
- trusted status 枚举：`['trusted_match_ready', 'evidence_pending', 'persona_pending_review', 'not_icp']`
- 空样本校验错误数：`0`
- no-write proof：`True`

## 门禁

- 无强 evidence 的候选不能进入 `trusted_match_ready`。
- 旧档案字段不得自动继承。
- LLM 只做摘要草稿，不决定可信状态。
- 本轮只产出 schema 和校验报告，不生成潜客、不写工作簿。
