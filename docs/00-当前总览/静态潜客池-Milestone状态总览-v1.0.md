# 静态潜客池 Milestone 状态总览 v1.0

## 1. 文档目的

本文件用于单页汇总当前静态潜客池在 `Milestone 1`、`Milestone 2` 与 `Milestone 3` 上的状态，避免后续继续扩池时再回到旧口径。

当前默认主线补充说明：

- `知识库 -> 画像 -> L5 候选 -> 上移补强` 才是系统主闭环
- `客户档案修复` 属于 `Milestone 3` 的支持性动作，不应替代主闭环

## 1.1 当前字段口径修正

从这一版开始，原先容易被误读的“层级即判断”口径改为三字段并行：

1. `信息扎实度`
2. `ICP匹配概率`
3. `静态潜客记录成熟度`

说明：

- `信息扎实度` 表示我们当前掌握的信息有多完整、多可靠
- `ICP匹配概率` 表示基于当前已知信息，对其符合目标客群画像的阶段性判断
- `静态潜客记录成熟度` 表示这条记录在静态池中的综合成熟度与池内使用层级，对应 `L1-L5`
- `L1-L5` 不再直接代表“像不像”本身，更不代表动态机会强弱或成交概率
- 当前这两列在 Excel 中仍是根据既有 `L1-L5` 做的首轮回填口径，后续可再单独细化重评

## 2. 当前里程碑状态

### Milestone 1：事实源稳定化

当前状态：`已完成`

完成标志：

1. 已识别重复主体组 `13`
2. 已输出重复主体清单
3. 已固定去重治理规则
4. 已建立 alias / merge 机制
5. 已形成清洗后事实主表
6. 已将总池汇总切换到清洗后事实源

当前事实口径：

- 去重前结构化覆盖量：`373`
- 去重后唯一主体数：`358`
- 静态潜客记录成熟度分布：`L1=8 / L2=305 / L3=112 / L4=1 / L5=149`
- 高质量层：`425`

核心文档：

- [external_target_account_pool_v2-重复主体清单-v0.1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/external_target_account_pool_v2-重复主体清单-v0.1.md)
- [external_target_account_pool_v2-去重治理规则-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-去重治理规则-v1.0.md)
- [external_target_account_pool_v2-清洗后事实主表-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-清洗后事实主表-v1.0.md)
- [潜客池工作台首页](/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/潜客池-首页.md)

### Milestone 2：静态池持续扩展最小版

当前状态：`已启动`

当前固定机制：

1. 继续吃真实素材并增强知识库
2. 继续补强主线与画像定义
3. 继续扩池
4. 继续维护事实源质量

明确不做固定节奏的动作：

1. 上移
2. 复盘

这两项只在用户明确要求时触发。

当前最小机制约束：

1. 新增前先查 alias
2. 新增前先查清洗后事实主表
3. 做老客排除
4. 明确主线与主画像
5. 写入池理由
6. 补最小证据
7. 标记待验证项
8. 才允许进入 `L5`

核心文档：

- [静态潜客池-持续扩展最小机制-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/静态潜客池-持续扩展最小机制-v1.0.md)
- [external_target_account_pool_v2-L5入池模板-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-L5入池模板-v1.0.md)
- [account_alias_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/account_alias_registry_v1-首版真实内容-v0.1.md)

### Milestone 3：L1-L4 静态信息可靠度增强

当前状态：`进行中`

当前目标：

1. 把 `L1-L4` 的静态背景信息做厚
2. 让重点公司、共享版 Excel、专题包都能稳定消费这些背景信息
3. 让 `static-pool-expand` 按固定收集路径半自动补最小静态背景
4. 为上移判断提供更稳定的事实支撑

边界说明：

- 本阶段包括档案层增强
- 但档案层增强是支撑动作，不是系统总目标
- 不应把“逐客户修复全部档案”当作默认主线

当前结果：

- `L3+`：`425/425` 已建立客户档案页与团队共享索引（唯一主体口径）
- `L1-L2`：`313` 家已进入高质量可复用层
- `L3`：当前为 `112` 家（唯一主体口径）
- `L4`：当前仅剩 `1` 家
- 共享版 Excel 已升级为正式化结构，包含：
  - 管理诉求画像
  - 背景快照字段
  - 主要切入话术引用
- 三条主线专题包已达到首版可交付状态
- 4 个 skill 已完成结构级与样例级校验
- 已完成首轮 `L4 -> L3` 上移 `4` 家，并同步更新 evidence、review queue 与重点公司 note
- 已完成本轮 `L4 -> L3` 批量上移 `20` 家，并同步更新主表、evidence、review queue、共享版与浏览层
- 已完成先进制造主线 `L5 -> L4` 上移专项 `20` 家，并同步更新主表、evidence、review queue、共享版与浏览层
- 已完成档案层驱动 `L4 -> L3` 上移试运行 `2` 家（绝味、吉宏），并同步更新主表、档案、evidence、queue、共享版与浏览层
- 已补齐一批缺失的 `L1-L2` 高质量样本重点公司 note
- 已完成 `L3 -> L2` 批量上移 `55` 家，并同步更新主表、档案、evidence、queue、团队共享索引与 `L3+` 客户档案页
- 已完成第二轮 `L3 -> L2` 批量上移 `50` 家，并保留 `5` 家待单独补证
- 已完成 `L5 -> L3` 批量扩容 `55` 家，其中零售消费 `25`、跨境电商 `15`、先进制造 `15`
- 已完成公开主体名单批量补强并 `L5 -> L3` 上移 `110` 家
- 已完成 `贝泰妮 / 东山精密 / 迈为` `3` 组重复主体 cleanup，当前高质量层稳定为 `205`
- 已完成一轮大规模 `客户档案逐客户修复` 试运行，验证了档案层可按批次修复，但该机制应回归为上移和共享层的支持性工具，而不是默认总任务

### Milestone 4：治理收口与 Phase 1 全样本纠偏

当前状态：`已启动`

当前目标：

1. 把 `L4/L5` 正式候选与观察对象分开
2. 把旧 persona 漂移收回到标准画像体系
3. 把 `Phase 1` 的 `15` 家样本做成正式纠偏结果
4. 复核 `learning_queue` 中与本轮纠偏强相关的 queued 项
5. 把治理收口结果沉到结构层、共享校验层和核心脚本

当前结果：

- 已形成 `Phase 1` 三条主线 `15` 家校准样本外部初判
- 已将 `主画像 / 次级画像 / 强相关知识资产引用` 下沉到字段模板和校准打包脚本
- 已新增标准 persona 集合与 legacy persona alias 映射，作为共享校验层的一部分
- 已生成 `deliveries/phase1_rectification_package_v1.json`，收口 `15` 家样本的正式纠偏建议
- 已输出 `Phase1` 样本正式纠偏清单和 `learning_queue` 关联复核文档，作为本阶段的中间交付物

核心文档：

- [Milestone 4-治理收口与Phase1纠偏复盘-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/Milestone%204-%E6%B2%BB%E7%90%86%E6%94%B6%E5%8F%A3%E4%B8%8EPhase1%E7%BA%A0%E5%81%8F%E5%A4%8D%E7%9B%98-v1.md)
- [Phase1样本正式纠偏清单-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/Phase1%E6%A0%B7%E6%9C%AC%E6%AD%A3%E5%BC%8F%E7%BA%A0%E5%81%8F%E6%B8%85%E5%8D%95-v1.md)
- [learning_queue与Phase1样本关联复核-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/learning_queue%E4%B8%8EPhase1%E6%A0%B7%E6%9C%AC%E5%85%B3%E8%81%94%E5%A4%8D%E6%A0%B8-v1.md)
- [L4L5二次分流与画像收紧方案-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/L4L5%E4%BA%8C%E6%AC%A1%E5%88%86%E6%B5%81%E4%B8%8E%E7%94%BB%E5%83%8F%E6%94%B6%E7%B4%A7%E6%96%B9%E6%A1%88-v1.md)

核心文档：

- [Milestone 3 执行跟踪文档-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/Milestone%203%20执行跟踪文档-v1.md)
- [L1-L4 背景 enrich 覆盖清单-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/L1-L4%20背景%20enrich%20覆盖清单-v1.md)
- [静态潜客池-先进制造上移专项-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/静态潜客池-先进制造上移专项-v1.md)
- [静态潜客池-L2扩容专项-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/静态潜客池-L2扩容专项-v1.md)
- [静态潜客池-L2扩容专项-v2.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/静态潜客池-L2扩容专项-v2.md)
- [静态潜客池-L5到L3扩容专项-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/静态潜客池-L5到L3扩容专项-v1.md)
- [静态潜客池-档案层驱动上移试运行-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/静态潜客池-档案层驱动上移试运行-v1.md)
- [潜客档案质量校准-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/潜客档案质量校准-v1.md)
- [共享版 Excel 字段口径说明-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/共享版%20Excel%20字段口径说明-v1.md)
- [三条主线专题包校验记录-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-执行与校验/三条主线专题包校验记录-v1.md)
- [静态潜客信息收集路径与方法设计-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/静态潜客信息收集路径与方法设计-v1.md)
- [静态潜客信息与动态机会信息边界说明-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/01-机制与规则/静态潜客信息与动态机会信息边界说明-v1.md)

## 3. 当前仍保留的边界主体

当前继续保留在边界层、暂不直接并入事实主表的主体：

- 深圳市万得福电子商务有限公司
- 厦门建发股份有限公司

## 4. 从现在开始的事实源原则

从这一版开始：

1. 历史 `v0.x / v1.0 / v1.1` 汇总文档只作为过程记录
2. 当前静态池事实口径以：
   - [external_target_account_pool_v2-清洗后事实主表-v1.0.md](/Users/clairaipartner/Codex/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-清洗后事实主表-v1.0.md)
   - [潜客池工作台首页](/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/潜客池-首页.md)
   为准
3. 后续继续扩池时，必须优先复用：
   - alias 注册表
   - L5 入池模板
   - 最小证据约束

## 5. 下一步默认动作

如果用户没有额外改变方向，后续默认动作优先级调整为：

1. 优先继续吃真实素材，维护 `learning_queue` 与知识资产
2. 校准和补强主线、业务形态画像、经营诉求画像
3. 按画像继续新增 `L5`
4. 在明确范围下选择一小轮上移对象并定向补证
5. 对会阻碍上移或共享消费的对象，按需修复档案与阅读层
6. 新增 `L5` 时同步执行：
   - alias 对照
   - canonical 去重
   - 老客排除
   - 最小证据补齐
   - 最小静态背景 enrich

上移与复盘继续按用户要求触发，不做固定重机制。

默认不再优先进入：

- 大面积逐客户修复档案
- 先把页面做厚再决定谁上移
- 把档案完整度误当成系统主产出

## 6. 新阶段：Milestone 7-10 执行闭环稳定化

当前新增阶段目标：

1. 把执行层从“能跑”推进到“可重复、可解释、可迁移、可防漂移”
2. 固定 `select -> report_only -> gate_check -> write_back -> post_integrity` 批次闭环
3. 把历史 `review_status` 口径漂移收进规则层，而不是依赖逐批人工改表

当前核心文档：

- [Milestone 7-10-执行闭环稳定化路线-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/Milestone%207-10-%E6%89%A7%E8%A1%8C%E9%97%AD%E7%8E%AF%E7%A8%B3%E5%AE%9A%E5%8C%96%E8%B7%AF%E7%BA%BF-v1.md)

优先级：

1. Milestone 7：状态口径与准入规则收口
2. Milestone 8：批次执行闭环标准化
3. Milestone 9：候选重选与上移结果复核
4. Milestone 10：执行层迁移与交接固化

## 7. Milestone 11：Warn 级质量解阻与补证闭环

当前状态：`已完成首轮`

目标：

1. 在 Milestone 7 已解除 `review_status` 系统性 block 后，处理 6R 样本剩余 warn
2. 优先降低 `evidence_thin / generic_product / generic_admission`
3. 不强求本轮全部 allow，把剩余风险收敛为可解释的画像边界问题

当前结果：

1. `allow=0 / warn=12 / block=0`
2. `evidence_thin: 10 -> 0`
3. `generic_product: 6 -> 0`
4. `generic_admission: 1 -> 0`
5. `persona_boundary_unstable: 12 -> 12`
6. 写回后 workbook integrity 为 `ok=true`

核心文档：

- [Milestone 11-warn质量解阻执行说明-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-%E6%89%A7%E8%A1%8C%E4%B8%8E%E6%A0%A1%E9%AA%8C/Milestone%2011-warn%E8%B4%A8%E9%87%8F%E8%A7%A3%E9%98%BB%E6%89%A7%E8%A1%8C%E8%AF%B4%E6%98%8E-v1.md)
- [Milestone 11-warn质量解阻复盘-v1.md](/Users/clairaipartner/Codex/bussiness-master/docs/03-%E6%89%A7%E8%A1%8C%E4%B8%8E%E6%A0%A1%E9%AA%8C/Milestone%2011-warn%E8%B4%A8%E9%87%8F%E8%A7%A3%E9%98%BB%E5%A4%8D%E7%9B%98-v1.md)

下一步：

1. 对 12 家进入主画像稳定性复核
2. 只在证据和画像均稳定时再追求 allow / promoted
3. 继续沿用 `report_only -> gate_check -> write_back -> post_integrity` 闭环

## 8. 新主线：Milestone 12-16 从画像收敛到合格静态池

当前状态：`已规划并启动 Milestone 12 准备`

阶段目标：

1. 不再只围绕单批次写回局部优化
2. 把系统主线推进为 `画像稳定性收敛 -> 知识库资产化 -> 合格潜客池扩容 -> 共享消费落地 -> 迁移交接固化`
3. 将 LLM 纳入增强层，但不允许绕过本地 evidence、规则和 gate check

当前核心文档：

- [BusinessMaster主线推进路线图-M12-M16-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/00-当前总览/BusinessMaster主线推进路线图-M12-M16-v1.md)
- [Milestone 12-主画像稳定性复核执行说明-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/03-执行与校验/Milestone 12-主画像稳定性复核执行说明-v1.md)

优先级：

1. Milestone 12：主画像稳定性复核与画像体系收敛
2. Milestone 13：知识库资产化与规则沉淀
3. Milestone 14：合格静态潜客池扩容
4. Milestone 15：共享消费与业务使用闭环
5. Milestone 16：迁移、交接与长期运行机制

当前默认下一步：

1. 使用 `scripts/build_persona_stability_review_package.py` 生成 12 家抽象画像复核输入包
2. 使用 `scripts/llm_delegate.py` 调用本机 `.env` 中的 Ark 配置生成复核草稿
3. 人工或规则复核后，再决定哪些对象可从 `pending_review` 转为 `active`
4. 转入下一轮 `report_only -> gate_check -> write_back -> post_integrity`

## 9. Milestone 12 首轮闭环结果

当前状态：`已完成首轮工程闭环，未执行写回`

结果：

1. 已补 12 条强 evidence
2. 已继承 M11 质量补丁并叠加 M12 evidence patch
3. `report_only` 结果为 `allow=0 / warn=12 / block=0`
4. `gate_check=PASS`
5. `status_patch_allowed_count=0`，因此本轮不执行 write_back

判断：

M12 证明了画像稳定性闭环可跑通，但当前 12 家仍需人工画像转正判断或进入 M13 规则沉淀。下一阶段不应直接扩大候选池，优先把“什么证据足以解除 persona_boundary_unstable”沉淀成规则。

## 10. Milestone 13 首轮规则沉淀结果

当前状态：`已完成首轮规则评估，未执行写回`

结果：

1. 已新增画像边界转正规则配置与评估脚本
2. 已对 M12 的 12 家样本完成规则评估
3. 规则结果为 `keep_pending_review=12 / active_candidate=0 / hold_review=0`
4. promote 结果为 `allow=0 / warn=12 / block=0`
5. gate_check 为 `PASS`

核心结论：

强 evidence 是转正必要条件，但不是充分条件。`pending_review -> active` 还需要人工或明确复核确认，LLM 单独建议不能触发状态转正。

下一步建议进入 M13.2：制作人工画像确认清单，对 12 家逐一确认是否可转 active。

## 11. Milestone 14-20：从小批扩容到首批可消费池

当前状态：`已完成 M14-M20 非写回/写回组合闭环`

阶段主线：

1. M14 验证小批扩容链路，暴露 `missing_field / evidence_thin / official_source_missing` 等入池质量问题。
2. M14.2 通过结构化 patch 把扩容样本从 block 解到 warn。
3. M14.3 建立候选预检和分层选择机制。
4. M15/M15.2 形成共享消费包，把规则结果翻译成业务可读摘要。
5. M16/M16.2 固化 readiness、自检和自治状态面板。
6. M17 在用户确认后完成真实写回试点。
7. M18 形成首批 L3 可消费池运营包。
8. M19 识别下一轮扩容候选池和业务反馈闭环。
9. M20 完成 30 家批量补证自动化 report-only/gate。

关键结果：

1. M17 真实写回：`promoted=15 / skipped=0 / allow=15 / warn=0 / block=0`。
2. M17 写回后工作簿完整性：`ok=true`。
3. M18 首批可消费 L3：`l3_share_ready=15 / needs_fix_count=0`。
4. M19 下一批候选池：`next_candidate_count=134 / needs_intake_patch=106 / not_ready=28`。
5. M20 批量补证：`allow=0 / warn=30 / block=0`。
6. M20 gate check：`PASS`。
7. M20 主要剩余问题：`persona_boundary_unstable=30`。

核心判断：

项目已从“执行链路是否能跑”进入“画像确认、业务反馈、知识资产沉淀、可控扩容”阶段。继续扩大候选池之前，应优先处理 M20 的 30 家画像确认问题，并让 M18 的 15 家 L3 进入业务反馈。

核心文档：

- [Milestone 17-写回候选准入试点最终复盘-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/03-执行与校验/Milestone%2017-写回候选准入试点最终复盘-v1.md)
- [Milestone 18-L3可消费池运营化复盘-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/03-执行与校验/Milestone%2018-L3可消费池运营化复盘-v1.md)
- [Milestone 19-扩容节奏与业务反馈闭环复盘-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/03-执行与校验/Milestone%2019-扩容节奏与业务反馈闭环复盘-v1.md)
- [Milestone 20-批量补证自动化最终复盘-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/03-执行与校验/Milestone%2020-批量补证自动化最终复盘-v1.md)

## 12. 新阶段：Milestone 21R-28R 可信画像匹配潜客池

当前状态：`M25R 扩容补证和真实 enrich 写回已完成；M26R/M27R/M28R 已完成消费层、画像确认包、二次 promote 准入和真实 promote 写回；M30R-M32R 已完成写回后消费与反馈闭环准备；M33R-M38R 完成历史三表治理并收口为非阻塞；M40R 已完成可信潜客池重启与 legacy 隔离；整体状态 PASS_M40R_TRUSTED_POOL_RESTART_READY`

阶段目标：

1. 基于知识库和理想客户画像，持续找到匹配潜客。
2. 为每个潜客提供核心、可靠、可解释的信息。
3. M21R 已把 M20 的 `persona_boundary_unstable=30` 转成 `trusted_match_ready=30`。
4. M23R 已生成 30 张可信潜客摘要卡，M24R 已完成知识资产来源治理与 no-write proof。
5. M25R 已完成下一批 50 家补证、report-only/gate 和可信复核：`warn=50 / block=0`，`trusted_match_ready=50`。
6. 用户已确认并执行 M25R 真实 `write_back`：enrich 写入 `profile_updates=50 / main_updates=50 / main_shared_updates=50 / evidence_items_created=50 / queue_items_created=48`。
7. M25R promote 写回未上移，`promoted=0 / skipped=50`，原因是本地 promote 仍保留 `persona_boundary_unstable=50` 的 warn 边界。
8. M26R 已生成 50 家可信潜客摘要卡/share view/review index，强来源覆盖 `50/50`。
9. M27R 已生成画像稳定性确认包，系统建议 `confirm_active_candidate=50`，但仍要求人工确认后才能真实写回。
10. M28R 已完成二次 promote 准入试运行：`allow=50 / warn=0 / block=0`，gate check PASS。
11. 用户已确认并执行 M28R 真实 promote 写回：`promoted=50 / skipped=0`，写回后 workbook integrity PASS。
12. M30R 已完成写回后 50 家可消费池复核与 15 家业务抽样评估模板：`l3_share_ready=50 / needs_fix=0`，抽样覆盖 4 个画像。
13. M31R 已完成业务反馈闭环准备：15 家抽样对象均待业务反馈，生成候选观察 15 条、source gap 4 条、规则校准建议 4 条，no-write proof PASS。
14. M32R 已完成反馈采集与质量验证闭环：当前空反馈模板保持 `pending=15`，不自动生成 accepted/rejected 结论；已填写样例和缺淘汰原因负例校验通过。
15. M33R 已完成三表口径治理审计：主表 575 行、档案库 490 行、共享版 355 行；发现主表重复 account_id 7 组、主表有档案库无 78 个、主表有共享版无 222 个、共享字段差异 225 个。
16. M33R 仅生成审计和同步候选包，未真实修表、未覆盖共享版、未删除任何行。
17. M34R 已完成三表治理安全修复准入包：建议移除 7 行重复主表记录、补 78 条档案 stub、生成 568 行共享版重建预览。
18. 用户已确认并执行 M34R 真实三表治理修复：主表删除重复行 7 行、档案库补写 78 条 profile stub、共享版重建为 568 行。
19. 修复后 M33R 复审结果：主表/档案库/共享版均为 568 行，主表重复为 0，主表缺档案为 0，主表缺共享版为 0，workbook integrity PASS。
20. 当前仍有字段级差异：profile mismatch 69 个、shared mismatch 68 个，下一步进入 M35R 字段口径收敛。
21. M35R 已完成字段级差异治理准入包：64 家 profile 可安全补齐 320 个空字段，15 个 profile 字段差异需人工复核；共享版 131 个 diff 均解释为生成视图占位或补充。
22. 用户已确认并执行 M35R 安全 profile 字段真实修复：64 家 profile 补齐 320 个空字段，未处理人工复核项，未让共享版反向覆盖主表。
23. M35R 修复后 profile mismatch 从 69 家降至 5 家，剩余 15 个字段均保留人工复核；共享版 131 个 diff 继续作为生成视图占位/补充解释。
24. M36R 已完成人工字段复核与共享占位口径包：5 家/15 字段进入人工复核，3 家/10 字段形成“人工确认后可写”候选 patch；共享版 68 家/131 个 diff 固化为生成视图占位说明。
25. M37R 已生成最终字段确认表：5 家/15 字段待人工填写，其中建议同步 8 个、建议记录别名 2 个、建议暂挂补证 5 个；未填写 human_decision 前不生成最终写回 patch。
26. M38R 已将剩余历史差异登记为非阻塞差异，停止要求逐字段人工确认，主线可继续。
27. M40R 已完成可信潜客池重启与 legacy 隔离：旧主表/档案/共享版不再作为可信事实源，新可信池入口切换为 evidence-first。
28. 潜客观察不能直接沉淀为正式知识资产，只能进入候选观察、source gap 和规则校准建议。

核心文档：

- [BusinessMaster阶段盘点与下一阶段总体规划-M21-M26-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/00-当前总览/BusinessMaster阶段盘点与下一阶段总体规划-M21-M26-v1.md)
- [BusinessMaster主线校正与下一阶段计划-可信画像匹配潜客池-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/00-当前总览/BusinessMaster主线校正与下一阶段计划-可信画像匹配潜客池-v1.md)
- [BusinessMaster产品专家评审与路线修订-M21-M26-v1.md](/Users/clairelu2026/CodexProjects/BusinessMaster/docs/00-当前总览/BusinessMaster产品专家评审与路线修订-M21-M26-v1.md)（历史评审参考，不作为当前主口径）

优先级：

1. M21R：可信画像匹配复核，P0。
2. M22R：可信潜客写回准入试点，P0/P1。
3. M23R：可信潜客摘要层，P1。
4. M24R：知识资产来源治理与潜客观察隔离，P1。
5. M25R：可信扩容预检与补证准备，P2。
6. M26R：M25R 可信潜客消费层，P1。
7. M27R：M25R 画像稳定性确认包，P0/P1。
8. M28R：M25R 二次 promote 准入试运行，P0/P1。

北极星指标：`可信画像匹配潜客数`。

定义：同时满足 ICP/画像匹配明确、核心公司信息完整、关键 evidence 可追溯、入池/上移理由清楚、风险和待补点明确、当前治理状态可解释的公司数量。

当前默认下一步：

1. 后续真实 write_back 仍需用户单独确认。
2. M25R 已在用户确认后执行真实 write_back，并使用对应 baseline 与 `--require-report-baseline`。
3. M25R 当前已写入 enrich 补证/核心信息，但未完成 promote 上移；`trusted_match_ready=50` 是可信准入/摘要口径，不等于正式画像 active。
4. 不允许把 M23R/M25R 潜客摘要直接写入正式知识资产。
5. M28R 真实 promote 写回已完成，当前不是“准入材料”而是“已写回事实”。
6. M30R 已完成写回后 50 家可消费池复核与业务抽样评估模板。
7. M31R/M32R 已形成反馈采集模板、导入汇总逻辑和质量验证闭环，但尚无真实业务反馈。
8. M34R 真实三表治理修复已完成，三表行数和主体覆盖已对齐。
9. M35R 安全字段真实修复已完成。
10. M36R 已形成人工复核队列与共享版占位口径说明。
11. M38R 已终止低价值历史字段纠缠，剩余差异不再阻塞项目。
12. M40R 已将 legacy 与新可信池隔离。
13. 默认下一步进入 M41R：选择 20-30 家候选，按 evidence-first schema 重新采集强证据和可信摘要，不继承旧档案字段。
