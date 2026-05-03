# `knowledge_asset_registry_v1` 字段模板 v1

## 1. 文档目的

本文件定义 `knowledge_asset_registry_v1` 的字段结构、最小知识抽取要求和复用口径。

这张表是把已学习的大量客户案例、解决方案、画像知识持续发挥作用的关键中间层。

## 2. 表定义

- 表名：`knowledge_asset_registry_v1`
- 粒度：一行代表一条可复用知识资产

补充：

- 当前工作簿 `/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/知识资产注册表.xlsx`
  现在同时承载：
  - `raw_material_inventory`：原始素材盘点表
  - `knowledge_assets`：正式知识资产表
  - `learning_queue`：学习队列 / 待抽取素材入口

## 3. 资产类型

`asset_type` 可选值：

- `customer_case`
- `solution_playbook`
- `scenario_pack`
- `industry_insight`
- `sales_narrative`
- `mapping_fact`

## 4. 字段清单

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `asset_id` | 资产 ID | 文本 | 是 | 稳定主键 |
| `asset_type` | 资产类型 | 枚举 | 是 | 见上文 |
| `title` | 资产标题 | 文本 | 是 | 知识对象名称 |
| `source_path_or_url` | 原始来源 | 文本 | 是 | 本地路径或公开链接 |
| `source_origin` | 来源属性 | 枚举 | 是 | `internal / external / public_web` |
| `track_ids` | 适用主线 | 文本 | 是 | 逗号分隔或数组 |
| `persona_ids` | 适用画像 | 文本 | 否 | 可为空，后续补 |
| `customer_refs` | 对应客户 | 文本 | 否 | 已服务客户或案例主体 |
| `jtbd_tags` | JTBD 标签 | 文本 | 否 | 逗号分隔或数组 |
| `complexity_tags` | 复杂度标签 | 文本 | 否 | 逗号分隔或数组 |
| `summary` | 摘要 | 长文本 | 是 | 3-8 句摘要 |
| `key_signals` | 关键判断信号 | 长文本 | 是 | 这条知识能支撑哪些判断 |
| `recommended_usage` | 推荐使用场景 | 长文本 | 否 | 行业扩充、入池判断、上移核验等 |
| `confidence_level` | 置信度 | 枚举 | 是 | `高 / 中 / 低` |
| `last_reviewed_at` | 最近复核时间 | 日期时间 | 否 | 最近更新时间 |
| `owner_note` | 维护备注 | 长文本 | 否 | 抽取范围、边界等 |

## 5. 最小抽取要求

每条知识资产至少要回答：

1. 它属于哪条主线
2. 它支撑哪些画像或至少支撑哪类判断
3. 它支撑哪些 JTBD 或复杂度信号
4. 它能怎么被调用
5. 它的置信度如何

## 6. 推荐空表表头

```text
asset_id,asset_type,title,source_path_or_url,source_origin,track_ids,persona_ids,customer_refs,jtbd_tags,complexity_tags,summary,key_signals,recommended_usage,confidence_level,last_reviewed_at,owner_note
```

## 7. 样例记录

| asset_id | asset_type | title | track_ids | persona_ids | confidence_level | recommended_usage |
| --- | --- | --- | --- | --- | --- | --- |
| ka_case_naturehall_v1 | customer_case | 自然堂全渠道数字化与 AI 实践 | retail_consumer | retail_high_sku_brand | 高 | 高 SKU 品牌消费品入池判断、样本映射、用户解释 |
| ka_solution_cbec_profit_v1 | solution_playbook | 跨境 T+1 利润分析打法 | cross_border_ecommerce | cbec_multi_platform_brand | 高 | 跨境账户入池理由生成、上移核验、方案匹配说明 |
| ka_industry_mfg_dashboard_v1 | industry_insight | 制造业经营驾驶舱切入洞察 | advanced_manufacturing | mfg_multi_factory_group | 中 | 先进制造行业扩展、账户解释、上移比对 |
| ka_mapping_7eleven_v1 | mapping_fact | 7-Eleven 与牛奶公司/惠康集团映射 | retail_consumer |  | 中 | 品牌主体归一、老客排除、集团映射判断 |

## 8. 调用节点要求

未来以下场景应优先调用本表，而不是让 LLM 临时自由发挥：

1. 新行业接入
2. 新画像扩展
3. 账户入池理由生成
4. 账户上移核验
5. 用户建议生成

## 9. 与其他表的关系

- `external_target_account_pool_v2.knowledge_asset_refs` 应引用本表
- `account_evidence_log_v1.related_asset_ids` 可引用本表
- 新画像从 `draft -> active` 时，建议至少引用一条本表资产

## 10. 原始素材盘点说明

为了防止后续只靠记忆或只靠 `learning_queue` 理解素材池，当前工作簿额外增加：

- sheet：`raw_material_inventory`

它记录原始 PDF / DOCX / MD 素材的全量盘点，并标注每条素材当前处于：

- `已转正式资产`
- `已入学习队列`
- `待评估`
- `明确不学`
- `已驳回`

这层负责回答：

1. 还有哪些原始素材没吃
2. 为什么还没吃
3. 哪些只是暂时不学，而不是不存在

## 11. 学习队列说明

为了保证知识库可以持续学习扩展，当前工作簿额外增加：

- sheet：`learning_queue`

它的作用不是替代正式知识资产表，而是承接：

1. 新接入材料
2. 上移后的样本反哺
3. 重点公司 / 专题包中形成的新共性

标准原则：

- 新素材先入 `learning_queue`
- 通过筛选后再进入 `knowledge_assets`
- 不允许把模型整理结果直接跳过真实来源校验，写成正式知识资产
- 不允许把潜客档案页、重点公司 note、专题包、主表摘要或模型总结本身写成 `learning_queue.material_path_or_url`
- 样本反哺只允许触发“查找并补回原始素材”，不允许把阅读层产物直接当学习素材源
- `L1 / L2 / L3` 样本只能提示“哪些原始素材方向还缺”，不能反向决定知识库主要学习范围

## 12. 潜客产出与知识资产的隔离边界

潜客批次、可信潜客摘要卡、promote/report-only 结果和 L3/L5 档案都不是正式知识资产来源。

允许：

- 作为 `candidate_observation` 记录“哪些画像边界需要复核”。
- 作为 `source_gap` 触发补源：寻找真实客户案例、内部解决方案、行业研究、公开权威材料。
- 作为 evidence 说明某家公司本身的信息可信度，例如官网、年报、IR、CNINFO。

禁止：

- 把潜客公司写成 `customer_case`。
- 把潜客匹配结果写成画像正例或反例。
- 把候选摘要、档案页、批次复盘、LLM 总结直接写入 `knowledge_assets`。
- 用 M21R/M22R 的 `trusted_match_ready` 反向证明画像定义正确。

正确链路是：

`潜客观察 -> learning_queue 补源任务 -> 真实素材/案例验证 -> 人工评审 -> 正式 knowledge_assets`。
