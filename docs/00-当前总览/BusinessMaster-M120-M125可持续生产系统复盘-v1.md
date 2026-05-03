# BusinessMaster M120-M125 可持续生产系统复盘 v1

## 结论

M120-M125 将 BusinessMaster 从“验证性 milestone 产物”推进到“可持续生产系统底座”。本轮没有追求新增潜客数量，而是把知识资产、画像 registry、证据采集、trusted pool、vault 交付和运行守护串成稳定闭环。

## 当前状态

- 系统状态：`PASS_M125R_SUSTAINABLE_PRODUCTION_SYSTEM_READY`
- canonical trusted pool：`61` 家，其中 `L1=35 / L2=25 / L4=1`
- canonical knowledge asset registry：`40` 条正式可用知识资产
- canonical persona registry：`8` 个 active supported 画像
- evidence acquisition task：`26` 条
- learning/customer-case exclusion：`35` 条，避免把学习素材或客户案例误转为潜客
- trusted pool report-only candidate：`0`，原因是本轮只生成证据采集任务，尚未采集可定位强来源

## 关键变化

- 新增 canonical 承载：`deliveries/canonical/businessmaster/knowledge_asset_registry_v1.json`
- 新增 canonical 承载：`deliveries/canonical/businessmaster/persona_registry_v1.json`
- 新增学习资产与画像引用桥：`deliveries/canonical/businessmaster/learning_persona_reference_map_v1.json`
- 统一入口增加 `production` 模式：`python3 scripts/businessmaster_pipeline.py --mode production`
- M121 将学习素材标题拆分为证据采集任务和排除清单，避免潜客产出污染知识/画像

## 边界

- 不写旧 Excel
- 不从潜客写知识资产
- 不从潜客写 persona registry
- 不写 vault 正区
- 不引入动态经营字段
- LLM 只可辅助摘要、分类、草稿和缺口建议，不作为 evidence

## 下一步

下一轮应优先执行证据采集，而不是继续扩池：

1. 从 `milestone121r_evidence_acquisition_engine/evidence_collection_task_queue_v1.json` 选取 10-20 条任务。
2. 为每条任务补可定位强来源：official_owned、platform_operating_fact、authoritative_third_party 或 regulatory_or_capital_market。
3. 生成 evidence patch 和 source trace。
4. 跑 M122 report-only，若出现 L3/L2/L1 候选，再 guarded update trusted pool。
5. 通过 vault preview 后再写 vault 正区。
