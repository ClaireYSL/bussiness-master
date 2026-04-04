# 01-机制与规则

本目录承载当前有效规则，但不是所有文档优先级都一样。

后续默认应分成三类理解：

1. 核心机制
2. 执行性规则
3. 支撑专题

如果你不确定先看什么，先看“核心机制”，不要从支撑专题反推全局主流程。

---

## 1. 核心机制

以下文档应被视为当前规则层的主干：

- [静态潜客池-冻结口径与可信最小字段集规范-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客池-冻结口径与可信最小字段集规范-v1.md)
- [知识库持续学习与素材接入机制-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/知识库持续学习与素材接入机制-v1.md)
- [L5 候选来源与入池路径说明-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/L5%20候选来源与入池路径说明-v1.md)
- [static-pool-promote-上移选项与单轮定义-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/static-pool-promote-上移选项与单轮定义-v1.md)
- [已知存量客户与签约主体排除规则-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/已知存量客户与签约主体排除规则-v1.md)
- [静态潜客信息与动态机会信息边界说明-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客信息与动态机会信息边界说明-v1.md)
- [静态潜客信息收集路径与方法设计-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客信息收集路径与方法设计-v1.md)
- [静态潜客池-持续扩展最小机制-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客池-持续扩展最小机制-v1.0.md)

这组文档共同回答：

- 知识怎么进
- 候选怎么入
- 上移怎么判
- 冻结边界怎么守
- 静态/动态边界怎么分

---

## 2. 执行性规则

以下文档更偏“具体动作怎么做”：

- [用户提供名单时的L5校验与分流规则-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/用户提供名单时的L5校验与分流规则-v1.md)
- [external_target_account_pool_v2-L5入池模板-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-L5%E5%85%A5%E6%B1%A0%E6%A8%A1%E6%9D%BF-v1.0.md)
- [external_target_account_pool_v2-去重治理规则-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-%E5%8E%BB%E9%87%8D%E6%B2%BB%E7%90%86%E8%A7%84%E5%88%99-v1.0.md)
- [共享版 Excel 字段口径说明-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/%E5%85%B1%E4%BA%AB%E7%89%88%20Excel%20%E5%AD%97%E6%AE%B5%E5%8F%A3%E5%BE%84%E8%AF%B4%E6%98%8E-v1.md)

这组文档适合在明确主线之后使用。

不要把这类执行性模板误读为比核心机制更高一层的规则。

---

## 3. 支撑专题

以下文档有价值，但更适合作为支撑性专题机制使用：

- [客户档案体系重构与逐客户修复机制-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/客户档案体系重构与逐客户修复机制-v1.md)
- [团队共享层最小化设计-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/团队共享层最小化设计-v1.md)
- [外部LLM委派边界与最小接入说明-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/外部LLM委派边界与最小接入说明-v1.md)
- [静态潜客池-使用层增强方案-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客池-使用层增强方案-v1.md)
- [静态潜客池-治理层增强方案-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客池-治理层增强方案-v1.md)

这组文档回答的是：

- 档案层怎么支撑主线
- 共享层怎么最小化设计
- 外部 LLM 如何受控接入
- 使用层和治理层如何增强

它们不应替代核心机制文档本身。

---

## 4. 当前推荐阅读顺序

### 路径 A：恢复项目执行

1. [静态潜客池-冻结口径与可信最小字段集规范-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客池-冻结口径与可信最小字段集规范-v1.md)
2. [L5 候选来源与入池路径说明-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/L5%20候选来源与入池路径说明-v1.md)
3. [static-pool-promote-上移选项与单轮定义-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/static-pool-promote-上移选项与单轮定义-v1.md)

### 路径 B：恢复知识学习链路

1. [知识库持续学习与素材接入机制-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/知识库持续学习与素材接入机制-v1.md)
2. [静态潜客信息收集路径与方法设计-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客信息收集路径与方法设计-v1.md)
3. [静态潜客信息与动态机会信息边界说明-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/静态潜客信息与动态机会信息边界说明-v1.md)

### 路径 C：执行具体扩池动作

1. [用户提供名单时的L5校验与分流规则-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/用户提供名单时的L5校验与分流规则-v1.md)
2. [external_target_account_pool_v2-L5入池模板-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-L5%E5%85%A5%E6%B1%A0%E6%A8%A1%E6%9D%BF-v1.0.md)
3. [external_target_account_pool_v2-去重治理规则-v1.0.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/external_target_account_pool_v2-%E5%8E%BB%E9%87%8D%E6%B2%BB%E7%90%86%E8%A7%84%E5%88%99-v1.0.md)

---

## 5. 当前使用原则

后续默认按下面顺序判断优先级：

1. 先看总入口 [README-静态潜客池.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/README-%E9%9D%99%E6%80%81%E6%BD%9C%E5%AE%A2%E6%B1%A0.md)
2. 再回到本目录的“核心机制”
3. 只有遇到具体动作时，再看“执行性规则”
4. 只有涉及档案、共享、外部委派等专题时，再看“支撑专题”
