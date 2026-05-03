# BusinessMaster 下一阶段规划-M41R-M48R-evidence-first可信潜客池-v1

## 阶段结论

M41R-M48R 已完成从 legacy 迁出后的第一轮 evidence-first 新可信潜客池闭环：先盘点真实学习素材，再校准画像来源支撑，随后落地 intake schema、首批 20 家可信潜客试运行、质量抽样、独立承载设计、产品化导出与长期运行机制。

本阶段没有写旧主表、没有写正式知识资产、没有修改画像 registry。旧主表/档案/共享版继续只作为 legacy/reference/export，不作为新可信事实源。

## 已完成产物

- M41R：完成原素材 inventory，覆盖 `744` 个素材文件，其中正文/文档学习队列 `166` 条，附件 `491` 条仅作索引。
- M42R：完成 15 个画像的 evidence map，`7` 个画像已有来源支撑，`1` 个需补源验证，`7` 个存在 source gap。
- M43R：完成新可信潜客 intake schema、evidence patch schema、summary card schema 和门禁校验。
- M44R：产出首批 `20` 家新可信潜客候选，`20/20 trusted_match_ready`，每家公司至少 1 条 official/strong evidence。
- M45R：抽样 `15` 张卡做可读性质量检查，`15/15 pass`；无人为反馈时保持 pending，不伪造业务认可。
- M46R：明确新可信池不复用旧 Excel 作为主存储，建议独立 `trusted_prospect_pool_v1`。
- M47R：形成 `trusted_prospect_pool_v1`、share view、persona dashboard、source trace index。
- M48R：形成扩容阈值、批次 runbook、quality gate 和 handoff snapshot。

## 当前状态

当前状态面板：`PASS_M48R_EVIDENCE_FIRST_RUNBOOK_READY`。

关键路径：

```text
真实学习素材 -> 画像来源支撑 -> 新 intake schema -> evidence-first 候选 -> 可信摘要卡 -> 独立可信池 -> 扩容阈值
```

## 下一步建议

进入 M49R：按 M48R 阈值做第二批 `30-50` 家扩容候选发现与 evidence-first 采集。

M49R 仍建议默认不写正式工作簿，先产出独立 trusted pool 增量包、share view 和来源索引。只有当新可信池承载方式确认后，再考虑新建正式工作簿或导入钉钉 AI 表格。

## 边界

- 潜客产出不能反向覆盖知识资产。
- 知识资产只能来自真实客户案例、解决方案、行业研究或权威材料。
- 旧主表/档案字段不能自动继承到新可信池。
- LLM 可辅助摘要和复核草稿，但不能直接决定 trusted status。
- 真实 write_back、新建正式工作簿、覆盖知识资产或画像 registry 都需要单独确认。
