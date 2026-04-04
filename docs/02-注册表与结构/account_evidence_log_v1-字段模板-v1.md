# `account_evidence_log_v1` 字段模板 v1

## 1. 文档目的

本文件定义 `account_evidence_log_v1` 的字段结构和证据强度口径。

这张表用于回答三个核心问题：

1. 为什么这个账户能进池
2. 为什么这个账户能上移
3. 为什么我们知道某个背景字段或档案结论成立

## 2. 表定义

- 表名：`account_evidence_log_v1`
- 粒度：一行代表一条证据记录

## 3. 字段清单

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `evidence_id` | 证据 ID | 文本 | 是 | 稳定主键 |
| `account_id` | 账户 ID | 文本 | 是 | 引用 `external_target_account_pool_v2.account_id` |
| `evidence_type` | 证据类型 | 枚举 | 是 | 见下方枚举 |
| `source_locator` | 来源定位 | 文本 | 是 | URL、文件路径或明确出处 |
| `evidence_strength` | 证据强度 | 枚举 | 是 | `S / A / B / C` |
| `supports_dimension` | 支撑维度 | 文本 | 是 | 主线、画像、JTBD、复杂度、上移等 |
| `summary` | 证据摘要 | 长文本 | 是 | 1-3 句说明证据内容 |
| `related_asset_ids` | 关联知识资产 | 文本 | 否 | 关联 `knowledge_asset_registry_v1` |
| `checked_by` | 核验人 | 文本 | 否 | 人或 LLM 标识 |
| `checked_at` | 核验时间 | 日期时间 | 否 | 核验时间 |
| `owner_note` | 备注 | 长文本 | 否 | 边界说明或补充说明 |
| `field_name` | 对应字段名 | 文本 | 否 | 若该证据直接支撑某个背景字段或档案字段，则填写字段名 |
| `field_value` | 对应字段值 | 文本 | 否 | 若该证据直接支撑某个背景字段或档案字段，则填写当前阶段性值 |

## 4. 证据类型枚举

- `official_website`
- `annual_report`
- `prospectus`
- `investor_relations`
- `industry_ranking`
- `association_member`
- `media_interview`
- `marketplace_or_platform`
- `internal_mapping`
- `manual_note`

## 5. 证据强度枚举

- `S`：官方年报、招股书、强官方披露
- `A`：官网、IR、强官方资料
- `B`：权威媒体、行业榜单、协会名录
- `C`：初步人工判断、弱公开资料

## 6. 使用规则

### 入 `L5`

- 至少有 `1` 条 `B/C` 级有效证据

### 升到 `L3`

- 至少有 `1` 条 `B` 级及以上有效证据

### 升到 `L2/L1`

- 至少有 `1` 条 `A/S` 级主证据
- 建议至少再有 `1` 条辅助证据

## 7. 推荐空表表头

```text
evidence_id,account_id,evidence_type,source_locator,evidence_strength,supports_dimension,summary,related_asset_ids,checked_by,checked_at,owner_note,field_name,field_value
```

## 8. 样例记录

| evidence_id | account_id | evidence_type | evidence_strength | supports_dimension | summary |
| --- | --- | --- | --- | --- | --- |
| ev_anker_ar_2024 | acc_anker | annual_report | S | 主线,画像,复杂度,上移 | 年报显示其跨境经营结构和业务复杂度，足以支撑其作为跨境品牌出海型高可信样本。 |
| ev_miniso_ir | acc_miniso | investor_relations | A | 主线,画像 | IR 材料能支撑其多门店、多区域零售经营特征，与多门店连锁零售画像高度一致。 |
| ev_case_mapping_lx | acc_inovance | internal_mapping | B | 样本映射,案例匹配 | 内部制造业案例与现有样本映射，支撑其作为先进制造经营型 BI 切入对象。 |

## 9. 与其他表的关系

- 本表为 `external_target_account_pool_v2` 提供入池和上移的证据基础
- 本表应与 `knowledge_asset_registry_v1` 配合使用，避免每次都重新解释同一类材料
- 本表与 `潜客档案库.xlsx` 配合使用：
  - 档案层存“已经知道了什么”
  - evidence 层存“这些信息从哪来”
