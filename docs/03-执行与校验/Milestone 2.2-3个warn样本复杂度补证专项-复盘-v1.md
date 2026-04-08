# Milestone 2.2-3个warn样本复杂度补证专项-复盘-v1

## 结论

`Milestone 2.2` 已达成。

这轮把 `Milestone 2.1` 中仍停在 `warn` 的 `3` 家样本全部压到了 `allow`：

- `acc_popmart`
- `acc_loctek`
- `acc_jereh`

## 关键认识

### 1. 当前 warn 的真实瓶颈不是事实字段，而是治理动作没挂上

这轮开始前，三家的 promote warning 都只有一条：

- `promotion_review_missing`

这说明上一轮主画像收敛后，事实层其实已经够了；剩下问题是没有把治理队列同步推进到 `promotion_review`。

### 2. 复杂度补证和队列动作要成对出现

如果只补 evidence、不补 `promotion_review` 队列，promote 仍然会停在 `warn`。

所以这一轮证实了一个更稳定的执行规则：

1. 主画像收敛后
2. 复杂度颗粒度补到最小可读
3. 必须同步开 `promotion_review`

否则 promote 不会进 `allow`

### 3. 三家现在都已经是“可推进对象”

当前状态已经不是 observation，不是 warn，而是 allow。

因此下一步不应再围绕这三家做同层级纠偏，而该进入：

- 真正的升层动作
- 或更大范围复制这套执行模式

## 分样本结论

### acc_popmart

- 当前已能作为 `retail_fashion_group` 的可推进对象
- 现阶段更适合先维持 `L4 allow`，再评估是否值得进入 `L3`

### acc_loctek

- 当前已能作为 `cbec_multi_platform_brand` 的可推进对象
- 现阶段可理解为 `L3 allow`

### acc_jereh

- 当前已能作为 `mfg_multi_factory_group` 的可推进对象
- 现阶段可理解为 `L3 allow`

## 当前阶段已经完成什么

如果把 `Milestone 2 / 2.1 / 2.2` 连起来看，这一段其实已经完成了三步：

1. `Milestone 2`
   - 补官方源，让 observation 判定进入真实执行链
2. `Milestone 2.1`
   - 把 observation 的主画像收敛到标准 persona
3. `Milestone 2.2`
   - 把 warn 样本补到 allow

这意味着当前执行层已经不只是“能跑 enrich/promote”，而是已经验证了：

- `事实补强 -> 主画像收敛 -> promotion_review -> allow`

这条真实主链。

## 下一步建议

最自然的下一步不是继续围绕这 `3` 家补同类细节，而是二选一：

1. `Milestone 2.3：这3家的升层执行`
   - `acc_loctek / acc_jereh` 优先看 `L3 -> 更高层`
   - `acc_popmart` 先评估是否从 `L4 -> L3`

2. `Milestone 3：复制到下一批同类对象`
   - 把 `Milestone 2 -> 2.1 -> 2.2` 这套模式复制到下一组 `observation/warn` 样本
