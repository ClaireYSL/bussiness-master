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
