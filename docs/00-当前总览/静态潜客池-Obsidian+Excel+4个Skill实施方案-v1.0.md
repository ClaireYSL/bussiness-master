# 静态潜客池 Obsidian + Excel + 4 个 Skill 实施方案 v1.0

## 1. 文档目的

本文件用于把当前静态潜客池的承载方案正式定稿为：

1. `Excel` 承载静态潜客池唯一事实源
2. `Obsidian` 承载解释层、知识层和重点公司层
3. `4 个 Skill` 承担未来主要触发入口

## 2. 当前已锁定设计

### 事实源

- Excel 是唯一事实源
- 当前事实口径以 [external_target_account_pool_v2-清洗后事实主表-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/external_target_account_pool_v2-清洗后事实主表-v1.0.md) 为准
- 当前判断字段统一为：
  - `信息扎实度`
  - `ICP匹配概率`
  - `静态潜客记录成熟度`

说明：

- `信息扎实度` 看当前信息和证据是否扎实
- `ICP匹配概率` 看基于当前信息，对其符合目标客群的阶段性判断
- `静态潜客记录成熟度` 对应 `L1-L5`，表示记录在静态池内的综合成熟度，而不是动态机会强弱

### 知识层

- Obsidian vault 根目录：`/Users/clairaipartner/Documents/Obsidian-Codex`
- 潜客池根目录：`/Users/clairaipartner/Documents/Obsidian-Codex/潜客池`
- 不混入 `/Users/clairaipartner/Documents/Obsidian-Codex/产品矩阵`

### 公司 note 策略

Obsidian 不给全量公司建 note，只给重点公司建 note。

重点公司来自：

1. `L1 + L2`
2. 边界主体
3. 用户点名关注公司
4. 画像代表账户

## 3. Excel 结构

当前建议使用 4 本工作簿：

1. `静态潜客主表.xlsx`
2. `治理与证据.xlsx`
3. `知识资产注册表.xlsx`
4. `主线与画像注册表.xlsx`

其中：

- `静态潜客主表.xlsx` 承载全量账户与汇总
- `治理与证据.xlsx` 承载 alias、evidence、queue
- `知识资产注册表.xlsx` 承载结构化知识资产
- `主线与画像注册表.xlsx` 承载主线与画像注册

### 当前新增的静态背景补充字段方向

在不改变三大判断字段的前提下，允许在主表中补充以下背景快照字段：

- `公司产品与服务概述`
- `商业模式概述`
- `核心客户客群`
- `收入规模区间`
- `利润状态概述`
- `营收增长概述`
- `已上线系统概况`
- `数字化项目动态`
- `相似客户线索`
- `主要竞品概述`
- `招聘代表岗位`
- `近一年重大事件`

这些字段属于 `静态背景补充字段层`，不直接参与当前静态判断公式。

## 4. Obsidian 结构

当前目录结构固定为：

- `01-主线`
- `02-画像`
- `03-重点公司`
- `04-知识资产`
- `05-汇总与状态`
- `06-规则与机制`

## 5. 4 个 Skill

当前正式采用以下 4 个 skill：

1. `static-pool-expand`
2. `static-pool-cleanup`
3. `static-pool-promote`
4. `static-pool-share`

### skill 边界

- `expand`：扩充静态池
- `cleanup`：清洗与去重治理
- `promote`：强核验与上移
- `share`：按对象和场景打包分享

### 当前 skill 更新方向

- `expand`：新增最小背景字段 enrichment，并采用“主体归一 -> 官方源优先 -> 高可信源补充 -> 解释层后置”的收集路径
- `cleanup`：新增背景字段 canonical 化与幂等检查
- `promote`：新增管理诉求画像与话术资产补强
- `share`：新增共享版 Excel 与专题包增强结构

### 当前共享层结构

共享版 Excel 当前已正式化，包含：

1. `全量主表`
2. `主线汇总`
3. `高质量层`
4. `L4_L5扩展层`
5. `边界主体`
6. `画像汇总`

当前专题包已覆盖：

- 零售消费
- 跨境电商
- 先进制造

## 6. 当前不纳入的内容

当前明确不纳入：

- 动态机会层
- 联系人层
- CRM 集成
- 固定节奏的上移机制
- 固定节奏的复盘机制

这些都后置。

## 7. 当前实现状态

当前已落地：

1. 去重治理文档与清洗后事实主表
2. Obsidian 根目录结构与主线/画像/知识资产/规则/状态 note
3. 第一批重点公司 note
4. 4 本 Excel 模板工作簿
5. 4 个 Skill 骨架
6. `L1-L4` 背景 enrich 首轮落地
7. 共享版 Excel 首版正式化
8. 三条主线专题包首版正式化

## 8. 后续默认动作

如果用户没有改变方向，后续默认动作只有两类：

1. 继续新增高质量 `L5`
2. 继续维护事实源质量

上移与复盘继续按用户要求触发。

## 9. 当前入口分工

- Excel：事实源
- Obsidian：工作台与阅读入口  
  [潜客池-首页.md](/Users/clairaipartner/Documents/Obsidian-Codex/潜客池/潜客池-首页.md)
- repo docs：制度、结构、执行与归档入口  
  [README-静态潜客池.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/README-静态潜客池.md)
