# Milestone 2-跨主线6家真实纠偏批次-复盘-v1

## 结论

这轮 milestone 已经把“真实纠偏批次”跑通，但结论也很明确：

1. 补官方源和补最小事实，能够让 `enrich` 的判定更可信。
2. 这还不足以直接把 observation 批量推成 `formal_candidate`。
3. 当前 `promote` 闸门是有效的，`3` 个 observation 仍然被稳定拦在 `block`，`3` 个对照样本则停在 `warn`，没有出现误放行。

## 本轮证实的规则

### 1. 官方源修复确实能进入执行层判定

本轮 `acc_popmart / acc_loctek / acc_jereh` 都完成了官方源入口补强，汇总中 `official_source_repaired = 3`。

这说明当前 `enrich` 已经不再只依赖旧 rectification 风险标记，而会消费实时事实层状态。

### 2. observation 不是补个官网就能自动转正

虽然 `3` 个 observation 都补了官方源，但仍全部保留在 `observation`：

- `acc_popmart`
- `acc_loctek`
- `acc_jereh`

原因不是脚本没生效，而是这些对象仍缺：

1. 稳定主画像
2. 更硬的公司级商业模式证据
3. 更清楚的 persona 边界

### 3. 对照样本也不该被轻易放进 allow

`acc_threesquirrels / acc_jihong / acc_bozon` 本轮都保留在 `warn`。

这说明当前 promote 闸门对“仍有缺口但具备推进价值”的样本，已经能稳定停在 `warn`，没有为了冲结果把它们放成 `allow`。

## 分样本复盘

### observation 样本

- `acc_popmart`
  - 从结果上看，官方源已补，但主画像仍待定，继续保留 `observation/block`
- `acc_loctek`
  - 产品服务和商业模式字段已补回，但主画像仍待定，继续保留 `observation/block`
- `acc_jereh`
  - 官方源与基础业务描述已补回，但制造画像边界仍未收敛，继续保留 `observation/block`

### 对照样本

- `acc_threesquirrels`
  - 当前维持 `formal_candidate/warn`，说明零售高 SKU 画像仍成立，但渠道与组织颗粒度还不够硬
- `acc_jihong`
  - 当前维持 `formal_candidate/warn`，说明跨境主线和主画像可保留，但平台结构与业务占比仍偏薄
- `acc_bozon`
  - 当前维持 `formal_candidate/warn`，说明先进制造画像成立，但 LTC 链路和组织复杂度证据不足

## 本轮没有完成的事

1. 没有把 observation 样本中的任何一家公司推成 `formal_candidate`
2. 没有把 `warn` 样本中的任何一家公司推进到 `allow`
3. 没有解决 `persona_resolved = 0` 这个问题

这不是执行失败，而是这轮真实验证后得到的更可信状态。

## 下一步建议

### 第一优先级

继续做 observation 深补，不扩样本：

1. `acc_popmart`
2. `acc_loctek`
3. `acc_jereh`

目标不是先升层，而是先把主画像从“待定”压到“可判”。

### 第二优先级

围绕 `warn` 样本继续补组织复杂度和经营颗粒度：

1. `acc_threesquirrels` 补渠道/库存/组织颗粒度
2. `acc_jihong` 补跨境业务占比、平台结构、供应链复杂度
3. `acc_bozon` 补 LTC 链路和组织复杂度

### 第三优先级

如果继续推进 execution-layer，本分支下一段最自然的工作不是再扩 provider，而是：

1. 给 observation 样本增加“主画像待定但已补官方源”的专门结果解释
2. 把 `warn` 样本的 remaining gaps 再程序化分组，便于后续定向补证
