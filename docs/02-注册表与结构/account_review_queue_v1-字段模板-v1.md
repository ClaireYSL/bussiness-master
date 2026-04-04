# `account_review_queue_v1` 字段模板 v1

## 1. 文档目的

本文件定义 `account_review_queue_v1` 的字段结构和持续滚动运营的队列口径。

这张表用于把“随时新增、持续核验、持续清池、按需抽知识”从临时动作变成标准工作流。

## 2. 表定义

- 表名：`account_review_queue_v1`
- 粒度：一行代表一个待处理工作项

## 3. 队列类型

`queue_type` 可选值：

- `new_intake`
- `verification`
- `promotion_review`
- `boundary_review`
- `knowledge_extraction`
- `cleanup_review`

## 4. 字段清单

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `queue_item_id` | 队列项 ID | 文本 | 是 | 稳定主键 |
| `queue_type` | 队列类型 | 枚举 | 是 | 见上文 |
| `account_id` | 账户 ID | 文本 | 否 | 某些知识抽取项可为空 |
| `related_track_id` | 相关主线 | 文本 | 否 | 新行业或边界复核可填 |
| `related_persona_id` | 相关画像 | 文本 | 否 | 画像扩展或边界复核可填 |
| `priority` | 队列优先级 | 枚举 | 是 | `高 / 中 / 低` |
| `status` | 队列状态 | 枚举 | 是 | `open / in_progress / resolved / dropped` |
| `owner` | 当前负责人 | 文本 | 否 | 人或 LLM 标识 |
| `reason_summary` | 入队原因 | 长文本 | 是 | 为什么进入队列 |
| `expected_action` | 期望动作 | 长文本 | 否 | 需要补证据、判断上移、清池等 |
| `source_context` | 来源上下文 | 长文本 | 否 | 哪个批次、哪个用户请求、哪份文档触发 |
| `created_at` | 创建时间 | 日期时间 | 否 | 创建时间 |
| `resolved_at` | 完成时间 | 日期时间 | 否 | 完成时间 |
| `resolution_note` | 处理结果 | 长文本 | 否 | 处理结论 |

## 5. 使用场景

### `new_intake`

- 新账户进入系统但尚未完成最低入池检查

### `verification`

- 已入 `L5/L4`，需要补证据做强核验
- 对 `L5` 观察对象，如果方向大致成立但事实仍薄，也进入此队列继续补证

### `promotion_review`

- 当前证据已较强，待判断是否上移
- 第一阶段采用“渐进提示”口径：程序给出 `allow / warn / block`，但暂不硬拦截写入

### `boundary_review`

- 主线、画像、老客映射或 canonical 存在边界疑问
- 对 `L5` 新入池对象，若主线 / 画像不稳，应优先进入此队列而不是直接视作正式候选

### `knowledge_extraction`

- 某份材料需要按需抽取为知识资产

### `cleanup_review`

- 待清理重复项、弱依据项、已失效项

## 6. 推荐空表表头

```text
queue_item_id,queue_type,account_id,related_track_id,related_persona_id,priority,status,owner,reason_summary,expected_action,source_context,created_at,resolved_at,resolution_note
```

## 7. 样例记录

| queue_item_id | queue_type | account_id | priority | status | reason_summary |
| --- | --- | --- | --- | --- | --- |
| q_verify_anker | verification | acc_anker | 高 | open | 该账户具备高标尺价值，需要补强年报级证据并确认是否维持 L1。 |
| q_boundary_alias_711 | boundary_review |  | 中 | open | 7-Eleven 相关主体映射存在品牌、签约主体、集团归属三层关系，待继续复核。 |
| q_extract_cbec_pack | knowledge_extraction |  | 中 | open | 新增跨境材料可能改变现有品牌出海画像边界，需要抽取知识资产。 |

## 8. 与其他表的关系

- `external_target_account_pool_v2.review_status` 可由本表驱动更新
- 推荐配套口径：
  - `review_status=active` 对应正式候选
  - `review_status=pending_review` 对应观察 / 边界对象
- `knowledge_asset_registry_v1` 的按需抽取工作可从本表进入
- 月度运营复盘应统计本表的新增、完成、积压情况
