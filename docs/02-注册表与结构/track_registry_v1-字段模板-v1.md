# `track_registry_v1` 字段模板 v1

## 1. 文档目的

本文件定义 `track_registry_v1` 的字段结构、填写规则和样例。

这张表是未来新增行业和维护主线边界的入口表，不允许绕过它直接往账户池里塞新行业。

## 2. 表定义

- 表名：`track_registry_v1`
- 粒度：一行代表一条主线
- 当前初始记录：`零售消费`、`跨境电商`、`先进制造`

## 3. 字段清单

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `track_id` | 主线 ID | 文本 | 是 | 建议使用稳定英文 snake_case |
| `track_name` | 主线名称 | 文本 | 是 | 中文显示名 |
| `status` | 状态 | 枚举 | 是 | `active / draft / deprecated` |
| `priority_level` | 优先级 | 枚举 | 是 | `P0 / P1 / P2 / P3` |
| `maturity_level` | 成熟度 | 枚举 | 是 | `高 / 中 / 低 / 探索` |
| `description` | 主线定义 | 长文本 | 是 | 说明这条主线是什么 |
| `entry_criteria_summary` | 入池标准摘要 | 长文本 | 是 | 说明什么样的公司能进入该主线 |
| `non_fit_boundary_summary` | 非适配边界摘要 | 长文本 | 是 | 说明什么样的公司虽然相邻但不纳入 |
| `seed_persona_ids` | 初始画像列表 | 文本 | 否 | 逗号分隔或数组格式 |
| `seed_account_refs` | 标尺样本账户 | 文本 | 否 | 逗号分隔或数组格式 |
| `seed_knowledge_refs` | 初始知识资产 | 文本 | 否 | 逗号分隔或数组格式 |
| `typical_jtbd_summary` | 典型 JTBD 摘要 | 长文本 | 否 | 当前主线高频任务 |
| `owner_note` | 维护备注 | 长文本 | 否 | 维护判断、边界提醒 |
| `created_at` | 创建时间 | 日期时间 | 否 | 记录时间 |
| `last_reviewed_at` | 最近复核时间 | 日期时间 | 否 | 最近一次主线复盘时间 |

## 4. 枚举口径

### `status`

- `active`：已启用，可正式扩池
- `draft`：已立项研究，但不允许正式放量建池
- `deprecated`：不再新增，但保留历史记录

### `priority_level`

- `P0`：当前公司战略主线
- `P1`：重点拓展主线
- `P2`：储备主线
- `P3`：观察主线

## 5. 空值策略

- `seed_persona_ids`、`seed_account_refs`、`seed_knowledge_refs` 在新主线刚创建时允许为空
- 但主线要从 `draft` 升到 `active` 前，这三项至少要补齐前两项中的一项，且建议三项都有

## 6. 启用规则

任何新主线从 `draft -> active` 前，必须满足：

1. `description` 完整
2. `entry_criteria_summary` 完整
3. `non_fit_boundary_summary` 完整
4. 至少定义 `2-5` 个初始画像
5. 至少具备 `3-10` 个标尺样本或 `3-10` 条初始知识资产

## 7. 推荐空表表头

```text
track_id,track_name,status,priority_level,maturity_level,description,entry_criteria_summary,non_fit_boundary_summary,seed_persona_ids,seed_account_refs,seed_knowledge_refs,typical_jtbd_summary,owner_note,created_at,last_reviewed_at
```

## 8. 样例记录

| track_id | track_name | status | priority_level | maturity_level | description | entry_criteria_summary |
| --- | --- | --- | --- | --- | --- | --- |
| retail_consumer | 零售消费 | active | P0 | 高 | 品牌零售、连锁零售、品牌消费品与连锁服务类经营主体 | 多门店、多区域、多渠道、高 SKU、总部经营分析和一线动作闭环需求明显 |
| cross_border_ecommerce | 跨境电商 | active | P1 | 中 | 品牌出海、多平台卖家、跨境供应链型经营主体 | 多平台、多店铺、多国家、多币种、利润核算和供需平衡复杂 |
| advanced_manufacturing | 先进制造 | active | P1 | 中 | 离散制造、技术型制造、多工厂制造集团 | 多工厂、多事业部、LTC 与经营驾驶舱需求明显 |
| healthcare | 医药医疗 | draft | P2 | 探索 | 预留主线示例 | 尚未启用，仅用于说明未来接入方式 |

## 9. 与其他表的关系

- `persona_registry_v1.track_id` 必须引用本表
- `knowledge_asset_registry_v1.track_ids` 应引用本表
- `external_target_account_pool_v2.primary_track` 应引用本表中的 `track_name`
