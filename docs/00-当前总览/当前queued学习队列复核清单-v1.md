# 当前 queued 学习队列复核清单-v1

## 1. 文档目的

本文件用于只读复核当前仍处于 `queued` 的学习队列项。

这份清单只回答：

1. 当前还剩哪些 `queued`
2. 它们分别是什么
3. 哪些是真实待学习素材
4. 哪些只是流程入口或占位

本文件不做：

- 启动新的知识学习
- 修改 `learning_queue` 状态
- 新增正式知识资产

---

## 2. 数据来源

本次复核基于：

- [知识资产注册表.xlsx](/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/知识资产注册表.xlsx)
  - sheet：`learning_queue`

当前 `extraction_status = queued` 数量：

- `11`

---

## 3. 复核结论总览

当前 `11` 条 `queued` 可以分成两类：

### 3.1 手工入口 / 非具体素材

- `1` 条

### 3.2 已验真的真实待学习素材

- `10` 条

结论：

- 当前 `queued` 并不是杂乱失控
- 除 `klq_003` 之外，其余 10 条都已经指向具体原始材料
- 它们应被理解为“已登记但尚未继续吃”的待处理素材，而不是脏队列

---

## 4. 手工入口项

### `klq_003`

- 标题：`团队提供的新学习素材待接入`
- 路径：`待补充`
- `material_origin`：`internal`
- `material_type`：`new_material`
- `trigger_scene`：`manual_ingest`
- `priority`：`P1`
- `source_verified`：`no`
- `ready_for_registry`：`no`

当前判断：

- 这不是一条具体原始素材
- 它只是“团队新素材入口”
- 不能直接进入学习
- 也不能被当成可抽取的真实材料

---

## 5. 当前 10 条真实待学习素材

## 5.1 跨境电商方向

### `klq_051`

- 标题：`乐其 SmallRig 跨境电商数据分析体系案例`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace/geo-content/sources/L1客户案例/走近乐其SmallRig，观远数据携手共建跨境电商数据分析体系.docx`
- 主线：`cross_border_ecommerce`
- 画像：`cbec_multi_platform_brand, mgmt_profit_improvement`
- 拟产出：`customer_case`
- 拟标题：`乐其 SmallRig 跨境经营分析案例`
- 优先级：`P1`

### `klq_052`

- 标题：`碧橙 TP/DP BI 数据应用平台方案`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0102-消费品_客制方案『仅内部，不可外发』/碧橙_BI数据应用平台项目方案_观远数据（202305）.pdf`
- 主线：`cross_border_ecommerce`
- 画像：`cbec_multi_platform_brand, mgmt_hq_operating_visibility`
- 拟产出：`solution_playbook`
- 拟标题：`TP/DP 运营数据平台打法`
- 优先级：`P1`

### `klq_053`

- 标题：`倍思 BI 案例分享`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0501-电商客户典型案例/7｜3C家电/「倍思」BI案例分享.pdf`
- 主线：`cross_border_ecommerce`
- 画像：`cbec_multi_platform_brand, mgmt_profit_improvement`
- 拟产出：`customer_case`
- 拟标题：`倍思跨境品牌经营分析案例`
- 优先级：`P1`

### `klq_054`

- 标题：`有棵树 BI 案例分享`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0501-电商客户典型案例/8｜鞋服/「有棵树」BI案例分享.pdf`
- 主线：`cross_border_ecommerce`
- 画像：`cbec_multi_platform_brand, mgmt_profit_improvement`
- 拟产出：`customer_case`
- 拟标题：`有棵树跨境鞋服经营案例`
- 优先级：`P2`

## 5.2 先进制造方向

### `klq_055`

- 标题：`SAP PCE 对接技术白皮书`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/additional_folder/泛制造/价值主张与支撑案例/【修订】观远BI与SAP PCE系统数据对接技术白皮书.md`
- 主线：`advanced_manufacturing`
- 画像：`mfg_multi_factory_group, mgmt_group_coordination`
- 拟产出：`solution_playbook`
- 拟标题：`制造企业 SAP PCE 对接打法`
- 优先级：`P1`

### `klq_056`

- 标题：`兆驰集团多工厂多产线经营效能案例`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/additional_folder/泛制造/价值主张与支撑案例/多工厂多产线高效管控！兆驰集团携手观远数据实现企业“效能跃升”.md`
- 主线：`advanced_manufacturing`
- 画像：`mfg_multi_factory_group, mgmt_group_coordination`
- 拟产出：`customer_case`
- 拟标题：`兆驰集团多工厂协同案例`
- 优先级：`P1`

## 5.3 零售消费方向

### `klq_057`

- 标题：`LLLM 采销供应链数据化解决方案`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0102-消费品_客制方案『仅内部，不可外发』/LLLM采销供应链数据化解决方案.pdf`
- 主线：`retail_consumer`
- 画像：`retail_high_sku_brand, mgmt_inventory_supply_coordination`
- 拟产出：`solution_playbook`
- 拟标题：`消费品采销供应链数据化打法`
- 优先级：`P2`

### `klq_058`

- 标题：`CJ Foods 需求计划数字化平台方案`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0102-消费品_客制方案『仅内部，不可外发』/[GuanData] CJ Foods Damand Planning Digital Management Platform PROPOSAL_2309.pdf`
- 主线：`retail_consumer`
- 画像：`retail_high_sku_brand, mgmt_inventory_supply_coordination`
- 拟产出：`solution_playbook`
- 拟标题：`消费品需求计划数字化平台打法`
- 优先级：`P1`

### `klq_059`

- 标题：`鲜丰水果数据智能化应用方案`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace-main/dingtalk_docs/2026-03-28/0102-消费品_客制方案『仅内部，不可外发』/鲜丰水果数据智能化应用汇报交流-观远数据-完整版v1.2.pdf`
- 主线：`retail_consumer`
- 画像：`retail_multi_store, mgmt_hq_operating_visibility`
- 拟产出：`customer_case`
- 拟标题：`鲜丰水果门店零售经营案例`
- 优先级：`P2`

### `klq_060`

- 标题：`7-Eleven 终端经营透视案例`
- 路径：
  `/Users/clairaipartner/.openclaw/workspace/geo-content/sources/L1客户案例/数据驱动零售新生态：7-Eleven携手观远数据打造终端经营“透视镜”.docx`
- 主线：`retail_consumer`
- 画像：`retail_multi_store, mgmt_hq_operating_visibility`
- 拟产出：`customer_case`
- 拟标题：`7-Eleven 终端经营透视案例`
- 优先级：`P2`

---

## 6. 当前只读判断

本次不启动学习，只做复核。当前可得出以下只读判断：

1. `klq_003` 不是学习对象，而是流程入口
2. `klq_051-060` 是真实待学习素材
3. 这 10 条素材覆盖方向明确：
   - 跨境电商
   - 先进制造
   - 零售消费
4. 优先级也已经被标过，不需要重新做一轮粗分

---

## 7. 当前不做的事

这份清单明确不做：

1. 不把任何 `queued` 改成 `converted`
2. 不把任何 `queued` 改成 `rejected`
3. 不生成新的 `knowledge_assets`
4. 不补写学习摘要

也就是说，当前只是“看清”，不是“继续吃”。

---

## 8. 当前结论

当前 `queued` 队列并不混乱，真正需要注意的是：

1. 真实待学习素材只有 `10` 条
2. 另有 `1` 条手工入口占位，不应被误算成真实素材
3. 若后续恢复知识学习，最自然的恢复点就是：
   - `P1` 的 `klq_051 / 052 / 053 / 055 / 056 / 058`

但本文件不触发该动作。

---

## 9. 关联文档

- [知识库原素材位置与学习进展总览-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/00-当前总览/知识库原素材位置与学习进展总览-v1.md)
- [原素材物理目录分布总览-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/00-当前总览/原素材物理目录分布总览-v1.md)
