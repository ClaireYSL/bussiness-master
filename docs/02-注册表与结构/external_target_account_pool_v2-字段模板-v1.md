# `external_target_account_pool_v2` 字段模板 v1

## 1. 文档目的

本文件定义 `external_target_account_pool_v2` 的字段结构、判断字段、成熟度字段和治理字段。

这是未来静态潜客账户真相源，后续总池汇总视图应优先从这张表派生，而不是继续从批次文档口头汇总。

## 2. 表定义

- 表名：`external_target_account_pool_v2`
- 粒度：一行代表一个归一后的公司级目标账户

## 3. 字段分组

1. 识别与归一字段
2. 静态画像字段
3. 业务任务与判断字段
4. 成熟度与治理字段
5. 知识连接字段
6. 动态机会预留字段

## 4. 字段清单

| 字段名 | 中文名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `account_id` | 账户 ID | 文本 | 是 | 稳定主键 |
| `account_canonical_name` | 归一主体名 | 文本 | 是 | 唯一 canonical 名称 |
| `brand_name` | 品牌名 | 文本 | 否 | 市场常用名 |
| `group_name` | 集团名 | 文本 | 否 | 经营集团或控股集团 |
| `primary_track` | 主线 | 枚举文本 | 是 | 引用 `track_registry_v1.track_name` |
| `industry_l1` | 一级行业 | 文本 | 是 | 一级行业标签 |
| `industry_l2` | 二级行业 | 文本 | 是 | 二级行业标签 |
| `business_model` | 业务模式 | 文本 | 是 | 品牌零售、品牌出海、离散制造等 |
| `persona_tag` | 主画像 | 文本 | 是 | 只允许填写 1 个主画像，引用 `persona_registry_v1` |
| `secondary_persona_tags` | 次级画像 | 文本 | 否 | 可多值；只记录辅助解释或边界观察用画像 |
| `company_scale_band` | 公司规模分层 | 枚举文本 | 否 | `小型 / 中型 / 中大型 / 大型 / 未确认` |
| `complexity_tag` | 复杂度标签 | 文本 | 是 | 一句话复杂度概括 |
| `primary_jtbd` | 主 JTBD | 文本 | 是 | 必须写成任务 |
| `secondary_jtbd` | 次 JTBD | 文本 | 否 | 次级任务 |
| `transformation_stage_tag` | 转型阶段 | 文本 | 否 | BI 升级、AI+BI 探索等 |
| `current_business_problem` | 当前业务问题 | 长文本 | 是 | 为什么值得入池 |
| `admission_reason_summary` | 入池理由摘要 | 长文本 | 是 | 1-3 句，直接解释为什么进池 |
| `case_type_match` | 案例类型匹配 | 文本 | 是 | 对应案例类型 |
| `existing_customer_reference` | 样本客户引用 | 文本 | 是 | 1-3 个样本客户 |
| `solution_match` | 方案匹配 | 文本 | 是 | 对应方案或打法 |
| `knowledge_asset_refs` | 强相关知识资产引用 | 文本 | 否 | 对应资产 ID 列表；仅记录对该潜客判断和阅读最相关的资产 |
| `信息扎实度` | 信息扎实度 | 枚举 | 是 | `高 / 中高 / 中 / 中低`；表示当前已掌握信息的完整度、可靠性与边界清晰度 |
| `ICP匹配概率` | ICP匹配概率 | 枚举 | 是 | `高 / 中高 / 中 / 中低`；表示基于当前已知信息，对其符合目标客群画像的阶段性判断 |
| `静态潜客记录成熟度` | 静态潜客记录成熟度 | 枚举 | 是 | `L1 / L2 / L3 / L4 / L5`；表示该记录在静态池中的综合成熟度与使用层级 |
| `static_priority` | 静态优先级 | 枚举 | 是 | `A / B / C`；表示在不考虑动态机会强弱时，该账户在当前静态层内的轻量排序优先级 |
| `dedupe_status` | 去重状态 | 枚举 | 是 | `passed / pending / duplicate_flagged` |
| `legacy_customer_check_status` | 老客排除状态 | 枚举 | 是 | `passed / pending / suspected_existing_customer` |
| `review_status` | 当前复核状态 | 枚举 | 是 | `active / pending_review / hold / removed` |
| `source_note` | 来源说明 | 文本 | 是 | 主要来源 |
| `validation_gap` | 待验证项 | 长文本 | 否 | 仍缺什么证据 |
| `last_verified_at` | 最近核验时间 | 日期时间 | 否 | 最近核验时间 |
| `dynamic_signal_status` | 动态信号状态 | 枚举 | 否 | 预留字段 |
| `recent_trigger_event` | 近期触发事件 | 文本 | 否 | 预留字段 |
| `engagement_signal` | 互动信号 | 文本 | 否 | 预留字段 |
| `referral_signal` | 引荐信号 | 文本 | 否 | 预留字段 |
| `sales_feedback_status` | 销售反馈状态 | 文本 | 否 | 预留字段 |

## 5. 状态字段口径

### `信息扎实度`

- `高`：主体边界清晰，官方源与高可信源稳定，且页面可读到至少 3 个公司级事实字段、2 个来源型摘录，并至少有 1 项公司级市场参考，或已明确沉淀重点公司 note / 公司级资产映射
- `中高`：主体边界清晰，官方源稳定，且页面可读到至少 2 个公司级事实字段和 1 个来源型摘录
- `中`：方向成立，但页面仍以归类判断为主，公司级事实偏薄
- `中低`：仅满足最低入池标准，仍主要依赖后续补证据

补充说明：

- `信息扎实度` 不能只根据来源层判断
- 它必须与客户档案页前半部分实际可读到的公司级事实厚度一致
- persona / track 默认模板句不允许再作为“已掌握信息”计入扎实度
- 默认知识资产/话术引用不再自动作为“公司级资产映射”计入扎实度
- md 客户档案页只是阅读投影，不是事实源；若页面信息要修正，必须先回写结构化事实层

### `ICP匹配概率`

- `高`：基于当前信息，较大概率符合目标客群画像
- `中高`：大体符合画像，但仍有若干关键点待确认
- `中`：方向较可能成立，但还不够稳
- `中低`：当前信息下仅能判断“可能相邻”，不宜高估

### `静态潜客记录成熟度`

- `L1`：高成熟、低缺口、可长期稳定保留的成熟潜客层
- `L2`：高成熟、高可信但仍有一定缺口的成熟潜客层
- `L3`：中高成熟、可读可治理的潜客层
- `L4`：中成熟候选
- `L5`：初步入池候选

说明：

- `静态潜客记录成熟度` 不是成交概率
- 也不是动态机会强弱
- 它表示这条静态潜客记录在池内的综合成熟度、参考价值和治理优先顺序
- `L1 / L2 / L3` 解决的是“这条潜客记录有多成熟、多稳”
- 它们不等于“重点公司”或“高质量客户样本”标签
- “是否值得反复拿来解释、分享和复用”由重点公司层与独立高质量样本层承担，不由 `L1/L2` 直接代表

## 5.1 客户档案修复工作流

自 `2026-04-03` 起，客户档案修复默认不再按字段全量批量补，而改成：

1. 先统一架构、规范、渲染逻辑
2. 再按客户逐个修复
3. 每修完一家，就达到“用户可用”
4. 通过自检后再 mark

这意味着：

- 主表仍存结论
- 档案库仍存事实
- evidence 仍存依据
- md 页只是阅读层
- 后续页面修复不能直接改 md 文案，而要先回写 Excel 结构化层

### `static_priority`

- `A`：在当前层内优先级最高，值得优先补证、优先解释、优先评估上移
- `B`：当前层内合理保留，但优先级次一档
- `C`：当前先保留在池中，但不是最优先投入静态治理资源的对象

说明：

- `static_priority` 是 `静态潜客记录成熟度` 之内的层内排序
- 它回答的是“在当前层里，谁更值得优先处理”
- 它不代表成交概率
- 不代表动态机会强弱
- 不代表销售优先级
- 它主要综合以下因素：
  - 静态匹配价值
  - 样本代表性
  - 解释复用价值
  - 当前治理优先顺序

### `review_status`

- `active`：当前有效
- `pending_review`：待核验或待边界裁决
- `hold`：暂缓，不上移也不删除
- `removed`：移出正式总池

补充约束：

- `queued` 已废弃；历史旧值读取时统一按 `pending_review` 兼容
- 在 `L5` 阶段，`review_status=active` 表示正式候选
- 在 `L5` 阶段，`review_status=pending_review` 表示观察 / 边界对象，不得直接按正式候选推进

### `persona_tag` 与 `secondary_persona_tags`

- `persona_tag` 只允许填写 1 个主画像
- `secondary_persona_tags` 用于记录次级画像、边界画像或辅助解释画像，可多值
- 一个潜客可以命中多个画像，但主表判断、默认入池理由和默认上移判断都必须以 `persona_tag` 为主
- 任何新增画像都必须先注册到 [persona_registry_v1-字段模板-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/persona_registry_v1-字段模板-v1.md)，不允许在账户表里临时发明画像

### `knowledge_asset_refs`

- 本字段只记录与当前潜客强相关的知识资产引用
- 允许用于说明“为什么它像这个画像、为什么值得补证或上移”
- 不允许把知识资产引用直接当成公司事实字段
- 默认展示时应优先展示强相关资产，而不是把所有相邻资产都堆进去

## 6. 最低入池约束

一条账户记录要正式进入本表，至少必须满足：

1. `primary_track` 非空
2. `persona_tag` 非空
3. `admission_reason_summary` 非空
4. `source_note` 非空
5. `dedupe_status` 不为 `duplicate_flagged`

## 7. 推荐空表表头

```text
account_id,account_canonical_name,brand_name,group_name,primary_track,industry_l1,industry_l2,business_model,persona_tag,secondary_persona_tags,company_scale_band,complexity_tag,primary_jtbd,secondary_jtbd,transformation_stage_tag,current_business_problem,admission_reason_summary,case_type_match,existing_customer_reference,solution_match,knowledge_asset_refs,信息扎实度,ICP匹配概率,静态潜客记录成熟度,static_priority,dedupe_status,legacy_customer_check_status,review_status,source_note,validation_gap,last_verified_at,dynamic_signal_status,recent_trigger_event,engagement_signal,referral_signal,sales_feedback_status
```

## 8. 样例记录

| account_id | account_canonical_name | primary_track | persona_tag | 信息扎实度 | ICP匹配概率 | 静态潜客记录成熟度 | static_priority | admission_reason_summary |
| --- | --- | --- | --- | --- | --- | --- |
| acc_miniso | 名创优品集团 | 零售消费 | retail_multi_store | 高 | 高 | L1 | A | 多门店、多区域、零售经营复杂度高，与现有连锁零售样本和案例高度相邻，可作为稳定扩池标尺。 |
| acc_anker | 安克创新 | 跨境电商 | cbec_multi_platform_brand | 高 | 高 | L1 | A | 多平台品牌出海、跨境经营复杂度高，利润分析与经营协同场景明确，案例和解决方案匹配强。 |
| acc_inovance | 汇川技术 | 先进制造 | mfg_multi_factory_group | 高 | 高 | L1 | A | 多事业部、多场景经营协同明显，制造业经营驾驶舱切入成立，具备稳定样本价值。 |

## 9. 与 v1.0 旧主表模板的关系

- 本表是 [外部目标客户池-v1.0-静态潜客池主表模板.md](/Users/clairaipartner/Codex/bussiness-master/docs/archive/外部目标客户池-v1.0/外部目标客户池-v1.0-静态潜客池主表模板.md) 的升级版
- 升级点主要是：
  - 增加了 `account_id`
  - 增加了治理字段
  - 增加了知识资产连接字段
  - 明确主表将成为长期真相源
