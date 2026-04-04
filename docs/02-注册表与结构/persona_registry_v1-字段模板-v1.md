# `persona_registry_v1` 字段模板 v1

## 1. 文档目的

本文件定义 `persona_registry_v1` 的字段结构、版本化规则和启用条件。

这张表是未来所有静态潜客画像的唯一注册入口，不允许只在账户表里临时写一个画像名而不注册。

## 2. 表定义

- 表名：`persona_registry_v1`
- 粒度：一行代表一个画像版本

## 3. 字段清单

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `persona_id` | 画像 ID | 文本 | 是 | 稳定主键，建议英文 snake_case |
| `persona_version` | 画像版本 | 文本 | 是 | 如 `v1`、`v1.1` |
| `persona_name` | 画像名称 | 文本 | 是 | 中文显示名 |
| `track_id` | 所属主线 ID | 文本 | 是 | 引用 `track_registry_v1.track_id` |
| `status` | 状态 | 枚举 | 是 | `active / draft / deprecated` |
| `definition` | 画像定义 | 长文本 | 是 | 一句话到一段话定义 |
| `fit_criteria` | 适配标准 | 长文本 | 是 | 满足哪些条件才算这个画像 |
| `non_fit_boundary` | 非适配边界 | 长文本 | 是 | 哪些相似公司不应归入 |
| `typical_jtbd` | 典型 JTBD | 长文本 | 是 | 高频任务集合 |
| `complexity_signals` | 复杂度信号 | 长文本 | 否 | 多门店、多工厂等 |
| `reference_customers` | 样本客户 | 文本 | 否 | 1-10 个已验证客户 |
| `reference_cases` | 参考案例 | 文本 | 否 | 对应案例或材料 |
| `reference_solutions` | 参考方案 | 文本 | 否 | 对应方案或场景包 |
| `admission_hint` | 入池判断提示 | 长文本 | 否 | 用于 LLM 或人工做初判 |
| `promotion_hint` | 上移判断提示 | 长文本 | 否 | 用于强核验和上移判断 |
| `replaced_by_persona_id` | 替代画像 ID | 文本 | 否 | 当前画像废弃后指向新画像 |
| `created_at` | 创建时间 | 日期时间 | 否 | 创建时间 |
| `last_reviewed_at` | 最近复核时间 | 日期时间 | 否 | 最近复核时间 |

## 4. 状态规则

### `draft`

- 已提出画像概念
- 但还不允许正式大规模扩池

### `active`

- 已可正式用于账户入池、核验和知识挂接

### `deprecated`

- 已停止新增引用
- 历史记录保留
- 必须通过 `replaced_by_persona_id` 指向新画像或留空说明

## 5. 从 `draft -> active` 的条件

必须同时满足：

1. `definition` 完整
2. `fit_criteria` 完整
3. `non_fit_boundary` 完整
4. `typical_jtbd` 完整
5. 至少有一组 `reference_customers`
6. 至少有一组 `reference_cases` 或 `reference_solutions`

## 6. 版本化规则

- 同一个画像升级时，不覆盖旧行
- 保留旧版行，并新增新版行
- 如果新版正式替代旧版：
  - 旧版设为 `deprecated`
  - 旧版 `replaced_by_persona_id` 指向新版 `persona_id`

## 7. 推荐空表表头

```text
persona_id,persona_version,persona_name,track_id,status,definition,fit_criteria,non_fit_boundary,typical_jtbd,complexity_signals,reference_customers,reference_cases,reference_solutions,admission_hint,promotion_hint,replaced_by_persona_id,created_at,last_reviewed_at
```

## 8. 样例记录

| persona_id | persona_version | persona_name | track_id | status | definition |
| --- | --- | --- | --- | --- | --- |
| retail_multi_store | v1 | 多门店连锁零售 | retail_consumer | active | 总部强管理、多门店、多区域、多层级经营复盘需求明显的连锁零售经营主体 |
| retail_high_sku_brand | v1 | 高 SKU 品牌消费品 | retail_consumer | active | SKU 多、上新快、渠道复杂、库存与商品经营联动明显的品牌消费品企业 |
| cbec_multi_platform_brand | v1 | 多平台品牌出海型 | cross_border_ecommerce | active | 多平台、多店铺、多国家经营，利润分析与供需协同复杂的品牌出海企业 |
| mfg_multi_factory_group | v1 | 多工厂离散制造集团 | advanced_manufacturing | active | 多工厂、多事业部、经营协同和 LTC 可视化需求明显的制造集团 |

## 9. 与其他表的关系

- `external_target_account_pool_v2.persona_tag` 应引用本表中的 `persona_id` 或 `persona_name`
- `external_target_account_pool_v2.secondary_persona_tags` 应引用本表中的 `persona_id` 或 `persona_name`
- `knowledge_asset_registry_v1.persona_ids` 应引用本表
- 新行业接入前，至少要先在本表建立初始画像集
