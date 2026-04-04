# `account_alias_registry_v1` 字段模板 v1

## 1. 文档目的

本文件定义 `account_alias_registry_v1` 的结构化字段模板，用于：

- 品牌名映射
- 集团名映射
- 历史主体名映射
- 重复 account_id 合并映射

## 2. 表粒度

一行表示一条 alias 到 canonical account 的映射关系。

## 3. 字段定义

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `alias_id` | string | 是 | alias 记录唯一 id |
| `alias_name` | string | 是 | alias 名称，可为品牌名、旧主体名或重复 account_id |
| `canonical_account_id` | string | 是 | 对应的 canonical 主记录 id |
| `canonical_name` | string | 是 | 对应的 canonical 主体全称 |
| `alias_type` | enum | 是 | alias 类型 |
| `status` | enum | 是 | 当前状态 |
| `source_note` | string | 是 | 来源说明 |
| `note` | string | 否 | 补充说明 |

## 4. 枚举定义

### 4.1 `alias_type`

- `brand_name`
- `group_name`
- `historical_legal_name`
- `duplicate_account_id`
- `project_alias`

### 4.2 `status`

- `active`
- `deprecated`

## 5. 最小填写规则

每条 alias 至少要保证：

1. 能唯一映射到 `canonical_account_id`
2. alias 类型明确
3. 来源说明明确

## 6. 空表表头

```md
| alias_id | alias_name | canonical_account_id | canonical_name | alias_type | status | source_note | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
```
