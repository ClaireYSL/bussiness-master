# `trusted_prospect_pool_v1` 字段模板 v1

## 1. 文档目的

本文件定义 evidence-first 可信潜客池的默认承载 schema。它是 M59R 之后新静态潜客池的 canonical schema，用于承载候选发现、补证、静态升层、摘要卡和正式档案输出。

旧 `external_target_account_pool_v2`、旧主表、旧档案库、旧共享版只作 legacy reference，不作为新可信池事实源。

## 2. 核心字段

| 字段名 | 中文名 | 必填 | 说明 |
| --- | --- | --- | --- |
| `prospect_id` | 潜客 ID | 是 | 稳定主键 |
| `company_name` | 公司名称 | 是 | 公司 canonical 名称 |
| `level` | 静态层级 | 是 | `L1 / L2 / L3 / L4 / L5` |
| `trusted_status` | 可信状态 | 是 | 与静态层级对应的状态 |
| `matched_persona` | 匹配画像 | 否 | 引用已校准画像 |
| `match_reason` | ICP 匹配理由 | 否 | 回答为什么像我们的 ICP |
| `core_product_service_summary` | 核心产品/服务 | 否 | 公司级事实摘要 |
| `business_model_summary` | 业务模式 | 否 | 静态经营结构说明 |
| `risk_or_gap` | 风险/待补点 | 否 | 缺什么才能升层 |
| `source_locator` | 主来源定位 | 否 | 官网、公告、年报、IR、监管披露、平台经营事实等 |
| `evidence_strength` | evidence 强度 | 否 | `official_site / annual_report / ir / regulatory / platform_store / authoritative_research` 等 |
| `source_category` | 来源类别 | 否 | `official_owned / regulatory_or_capital_market / platform_operating_fact / authoritative_third_party / internal_or_legacy_reference` |
| `static_promotion_summary` | 静态升层摘要 | 否 | 由 `trusted_pool_runner` 生成 |
| `static_gap_count` | 静态缺口数量 | 否 | 缺口队列数量 |
| `legacy_reference_only` | legacy 边界 | 否 | 如果引用旧资料，必须标记仅作去重/审计 |

## 3. Source category v2

- `official_owned`：官网、品牌官网、官方新闻、官方门店/渠道页、官方招聘、官方公众号/小程序公开页。
- `regulatory_or_capital_market`：年报、公告、CNINFO、交易所、SEC、港交所、招股书、公开转让说明书。
- `platform_operating_fact`：官方旗舰店、平台品牌店、门店网络、App/小程序/SaaS 公开页、可验证经营页面。
- `authoritative_third_party`：权威媒体深度报道、融资公告、投资机构 portfolio、行业协会/政府/研究机构材料。
- `internal_or_legacy_reference`：结构化 patch、旧档案、旧主表、人工整理记录，只能辅助，不计入 L1 强来源。

`source_type` 表示具体来源形式，`source_category` 表示来源在静态可信判断中的角色。上市披露是高可信来源，但不再是 L1 的事实默认路径。

## 4. Evidence-first L1-L5 v2

- `L5`：候选线索，有公司名或来源线索，但事实不足。
- `L4`：ICP 可能，已有初步事实，但证据或画像解释不足。
- `L3`：至少 1 条强来源，可生成可信摘要卡。
- `L2`：至少 2 条强来源，画像匹配清楚，解释完整，可生成正式潜客档案。
- `L1`：L2 基础上，至少 3 条可定位强来源、至少 2 类来源类别、至少 1 条来源直接支撑 ICP 匹配。

## 5. 边界

- 本 schema 只表达静态 ICP 匹配、证据成熟度和信息完整度。
- 不表达是否现在经营、由谁跟进、何时触达或销售优先级。
- 知识资产引用只能作为 `icp_reference_asset_refs`，表示 ICP 判断参考，不是潜客 evidence 或客户案例归因。
- 潜客产出不能反向写入正式知识资产或 persona registry。
