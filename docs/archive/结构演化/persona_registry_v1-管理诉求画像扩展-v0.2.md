# persona_registry_v1-管理诉求画像扩展-v0.2

## 摘要

本轮在既有 `7` 个业务形态画像之上，新增并启用 `5` 个 `active` 管理诉求画像，用于增强静态潜客池的解释层与切入层，不直接改写现有账户主画像字段。

当前画像结构变为：

- `active` 业务形态画像：`7`
- `active` 管理诉求画像：`5`

本轮扩展的目标不是替换原有画像，而是补充回答：

- 这类公司更可能因什么管理问题被打动
- 为什么值得从这个诉求切入
- 哪些重点公司可以作为该诉求画像的代表样本

## 新增画像清单

### 1. `mgmt_hq_operating_visibility`

- 中文名：`总部经营穿透诉求型`
- 状态：`active`
- 主主线：`retail_consumer`
- 优先映射：
  - `retail_multi_store`
  - `retail_high_sku_brand`
  - `mfg_multi_factory_group`

适用重点：

- 连锁零售
- 品牌消费品
- 多区域经营
- 多事业部集团

典型 JTBD：

- 总部经营透视
- 区域差异复盘
- 统一经营口径
- 管理驾驶舱

### 2. `mgmt_profit_improvement`

- 中文名：`利润改善诉求型`
- 状态：`active`
- 主主线：`cross_border_ecommerce`
- 优先映射：
  - `cbec_multi_platform_brand`
  - `cbec_supply_chain_complex`
  - `retail_high_sku_brand`

适用重点：

- 跨境电商
- 品牌消费品
- 技术型制造
- 多环节利润核算复杂主体

典型 JTBD：

- T+1 利润分析
- 业财一体化
- 费用归因
- 履约与利润联动

### 3. `mgmt_inventory_supply_coordination`

- 中文名：`库存与供应链协同诉求型`
- 状态：`active`
- 主主线：`retail_consumer`
- 优先映射：
  - `retail_high_sku_brand`
  - `cbec_supply_chain_complex`
  - `mfg_multi_factory_group`

适用重点：

- 高 SKU 消费品
- 跨境供应链复杂主体
- 多工厂制造集团
- 供需平衡压力大的企业

典型 JTBD：

- 库存优化
- 供需平衡
- 补货/分货决策
- 计划协同

### 4. `mgmt_frontline_action_loop`

- 中文名：`一线动作闭环诉求型`
- 状态：`active`
- 主主线：`retail_consumer`
- 优先映射：
  - `retail_multi_store`
  - `retail_chain_fnb`

适用重点：

- 连锁零售
- 连锁餐饮
- 强总部运营型企业

典型 JTBD：

- 一线问数
- 督导动作闭环
- 店长复盘
- 门店经营诊断

### 5. `mgmt_group_coordination`

- 中文名：`集团协同与经营驾驶舱诉求型`
- 状态：`active`
- 主主线：`advanced_manufacturing`
- 优先映射：
  - `mfg_multi_factory_group`
  - `mfg_rnd_sales_complex`

适用重点：

- 多事业部
- 多工厂
- 多区域经营
- 研产销链路长的集团型企业

典型 JTBD：

- 集团经营驾驶舱
- LTC 协同
- 价值流分析
- 多事业部经营透明化

## 启用规则

当前 `5` 个管理诉求画像已升级为 `active` 辅助画像体系，但不直接写入 `external_target_account_pool_v2` 的主画像字段。

允许使用的范围：

- Obsidian 画像 note
- 重点公司 note
- 专题包
- 主线解释与分享材料

当前不允许：

- 直接替换现有 `7` 个 `active` 业务形态画像
- 作为账户主画像写回事实主表
- 作为动态机会判断字段使用

## 当前作用

本轮扩展后，画像体系已经从“业务形态画像单层结构”升级为“双层结构”：

- 第一层：业务形态画像
- 第二层：管理诉求画像

这样在解释重点公司时，不再只能说：

- 这家公司属于哪类行业/业务结构

还可以进一步说明：

- 它更可能因什么管理问题被打动
- 更适合从哪个经营诉求切入

## 当前落地范围

本轮已完成：

- `persona_registry_v1` 中新增并启用 `5` 条 `active` 记录
- Obsidian `/02-画像/` 下新增 `5` 个管理诉求画像 note
- 现有重点公司 note 已开始稳定回挂这些管理诉求画像作为补充解释标签

## 升级为 active 的判断依据

本轮把这 `5` 个管理诉求画像升级为 `active`，主要依据是：

1. 有清晰定义与非适配边界
2. 有稳定适配的重点公司样本
3. 有对应案例/方案知识资产支撑
4. 已在重点公司解释或专题包中被反复使用
5. 没有与现有 active 画像产生严重歧义或重复

## 当前边界

即使已升级为 `active`，管理诉求画像仍然只作为辅助画像体系使用：

1. 不替代现有业务形态主画像
2. 不直接写回账户主画像字段
3. 不作为动态机会判断字段
