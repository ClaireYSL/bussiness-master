# 4个Skill同步更新方案-v1

## 摘要

当前 `4` 个 skill 仍主要基于旧版 Markdown 主表和首版知识资产定义，已落后于当前体系。

本方案用于明确这轮需要同步更新的内容：

- `static-pool-expand`
- `static-pool-cleanup`
- `static-pool-promote`
- `static-pool-share`

## 一、统一更新原则

所有 skill 从本轮开始必须统一到以下口径：

1. Excel 是唯一事实源
2. Obsidian 是解释层
3. 三大判断字段为：
   - `信息扎实度`
   - `ICP匹配概率`
   - `静态潜客记录成熟度`
4. 可补静态背景字段，但不把它们纳入动态层
5. 可使用：
   - 业务形态画像
   - 管理诉求画像
   - 案例/方案资产
   - 切入话术资产

## 二、各 skill 更新点

### `static-pool-expand`

新增要求：

- 入池后优先补最小背景字段
- 可引用管理诉求画像建议
- 必查最新知识资产扩展文档

### `static-pool-cleanup`

新增要求：

- cleanup 不只处理重复主体，也要处理背景字段回挂和 enrichment 冲突
- 保证新增背景字段 canonical 化

### `static-pool-promote`

新增要求：

- 上移不仅补证据，也补管理诉求画像和解释资产
- 上移时可同步校准 `信息扎实度` 与 `ICP匹配概率`

### `static-pool-share`

新增要求：

- 输出共享版 Excel 结构建议
- 输出专题包结构
- 输出重点公司导出结构

## 三、需同步更新的文件

### 每个 skill

1. `SKILL.md`
2. `agents/openai.yaml`

## 四、验收标准

1. 4 个 skill 都不再依赖旧版首版知识资产文档
2. 4 个 skill 都能识别新的三大判断字段
3. `share` skill 能覆盖共享版与专题包
4. `expand / cleanup / promote` 都能识别背景字段 enrichment
