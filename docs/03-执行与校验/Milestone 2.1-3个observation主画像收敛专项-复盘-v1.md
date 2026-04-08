# Milestone 2.1-3个observation主画像收敛专项-复盘-v1

## 结论

`Milestone 2.1` 已经达成目标。

这轮最重要的结果不是升层，而是把 `Milestone 2` 中仍停在：

- `observation`
- `主画像待定`
- `block`

的 `3` 家对象，推进成：

- `formal_candidate`
- `主画像已收敛`
- `warn`

## 关键变化

### 1. 主画像已经收敛

本轮 `persona_resolved = 3`：

- `acc_popmart -> retail_fashion_group`
- `acc_loctek -> cbec_multi_platform_brand`
- `acc_jereh -> mfg_multi_factory_group`

### 2. observation 已全部退出

本轮 `observation_promoted_to_formal = 3`，说明这轮卡点已经不再是“能不能判 persona”，而是“判完 persona 后还差哪些上移条件”。

### 3. promote 仍保守停在 warn

虽然 `3` 家都已进入 `formal_candidate`，但 promote 结果仍是 `warn` 而不是 `allow`。

这说明当前闸门没有被绕过，系统仍要求：

1. 更细的组织/区域/平台颗粒度
2. 更硬的经营复杂度证据
3. 更充足的 promotion review 准备度

## 分样本结论

### acc_popmart

- 当前已能稳定理解为 `retail_fashion_group`
- 关键理由是 IP 商品零售、线下门店、机器人商店、会员经营结构已成立
- 后续缺口是区域经营、门店组织结构和更细零售网络颗粒度

### acc_loctek

- 当前已能稳定理解为 `cbec_multi_platform_brand`
- 关键理由是品牌出海、海外市场销售和多平台跨境经营属性已成立
- 后续缺口是平台结构、区域经营和品牌矩阵颗粒度

### acc_jereh

- 当前已能稳定理解为 `mfg_multi_factory_group`
- 关键理由是能源装备制造、工程服务和全球项目经营结构已成立
- 后续缺口是多基地布局、全球经营和更细业务条线颗粒度

## 当前阶段判断

本轮完成后，`Milestone 2` 系列的重点已经从：

- “补官方源”

切换成：

- “补复杂度颗粒度”

也就是下一步不该再围绕“有没有主画像”打转，而该开始补：

1. 组织结构
2. 区域经营
3. 平台结构
4. 多基地/多业务条线协同

## 下一步建议

### 方向

进入 `Milestone 2.2：3个warn样本复杂度补证专项`

对象仍可沿这 `3` 家继续做，不建议立刻扩面。

### 目标

把当前 `warn` 的阻塞点压细到：

- `acc_popmart`：门店网络 / 区域经营 / 组织结构
- `acc_loctek`：平台结构 / 品牌矩阵 / 区域经营
- `acc_jereh`：多基地布局 / 业务条线 / 全球经营

### 验收

不要求三家都进入 `allow`，但至少要把 `warn` 理由进一步压缩成可执行的最后一轮补证清单。
