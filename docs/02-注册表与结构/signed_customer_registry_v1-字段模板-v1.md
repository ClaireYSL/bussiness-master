# `signed_customer_registry_v1` 字段模板 v1

## 1. 目的

`signed_customer_registry_v1` 是 BusinessMaster evidence-first 主线中的已签约客户 canonical registry，用于在候选发现、公开 evidence 采集、trusted pool 写入和 vault 发布前排除老客。

已签约客户可以作为客户案例或知识学习素材，但不得作为新潜客进入 `trusted_prospect_pool_v1`。

## 2. 表粒度

一条记录表示一个已确认签约/存量客户 canonical 主体。

## 3. 核心字段

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `customer_id` | string | 是 | 签约客户唯一 id |
| `canonical_name` | string | 是 | canonical 客户名称 |
| `signed_status` | enum | 是 | `confirmed_signed_customer / review_candidate / deprecated` |
| `contract_entity` | string | 是 | 签约或确认合作主体 |
| `market_name` | string | 否 | 市场简称 |
| `group_name` | string | 否 | 集团名 |
| `brand_names` | array | 否 | 品牌名列表 |
| `aliases` | array | 是 | 老客排除使用的名称集合 |
| `source_type` | string | 是 | 来源类型，例如 `legacy_customer_registry / user_signed_list / crm_export / customer_case_review` |
| `source_locator` | string | 是 | 来源定位 |
| `exclusion_scope` | enum | 是 | 当前固定为 `exclude_from_static_pool` |
| `effective_from` | string | 否 | 生效日期 |
| `last_verified_at` | string | 是 | 最近验证时间 |

## 4. alias registry

`signed_customer_alias_registry_v1` 一条记录表示一个 alias 到签约客户 canonical 主体的映射。

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `alias_id` | string | 是 | alias 唯一 id |
| `alias_name` | string | 是 | 品牌名、市场名、集团名、历史名或法体名 |
| `customer_id` | string | 是 | 对应 signed customer id |
| `canonical_name` | string | 是 | 对应 canonical 客户名称 |
| `alias_type` | enum | 是 | `brand_name / group_name / market_name / contract_entity / legacy_customer_name / historical_legal_name` |
| `status` | enum | 是 | `active / deprecated` |
| `source_locator` | string | 是 | 来源定位 |

## 5. 闸门状态

候选进入 source collection / trusted pool update / vault publish 前必须有：

- `existing_customer_check_status = passed`

其他状态处理：

- `excluded_existing_customer`：阻断，不进入新潜客池。
- `boundary_review`：进入边界复核，不得自动放行。
- `missing_check`：视为失败，不得写入 trusted pool。

## 6. 边界

- 不写旧 Excel。
- 不写 knowledge asset registry。
- 不写 persona registry。
- 不自动删除当前 trusted pool；若回溯命中老客，只生成 remediation package。
