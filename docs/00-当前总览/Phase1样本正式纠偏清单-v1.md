# Phase1样本正式纠偏清单-v1

## 1. 目的

本清单把 `Phase 1` 的 `15` 家校准样本，从 delegate 初判转成当前阶段可直接执行的正式纠偏口径。

结构化结果文件：

- [phase1_rectification_package_v1.json](/Users/clairaipartner/Codex/bussiness-master/deliveries/phase1_rectification_package_v1.json)

---

## 2. 横向结果

当前 `15` 家样本的正式纠偏结果为：

- `formal_candidate = 11`
- `observation = 4`
- `downgrade = 5`
- `maturity_regraded = 9`
- `persona_adjusted = 7`
- `official_source_repair_needed = 4`

一句话总结：

- 当前主线整体仍可保留
- 但 `L4/L5` 里已有 `4` 家必须退出正式候选链路
- 另有 `7` 家需要做 persona 重判或 persona 收紧

---

## 3. 高估整改样本

以下 `3` 家是第一批高估整改样本：

| account_id | 公司 | 当前主线 | 当前 persona | 纠偏结果 | 当前动作 |
| --- | --- | --- | --- | --- | --- |
| `acc_popmart` | 北京泡泡玛特文化创意有限公司 | 零售消费 | `retail_multi_store` | 转 `observation`，主画像留空，仅保留 `retail_fashion_group` 次级画像 | `boundary_review` |
| `acc_loctek` | 乐歌人体工学科技股份有限公司 | 跨境电商 | `cbec_brand_outbound` | 转 `observation`，退出 legacy persona，保留 `cbec_multi_platform_brand` 次级画像 | `boundary_review` |
| `acc_jereh` | 烟台杰瑞石油服务集团股份有限公司 | 先进制造 | `mfg_multi_factory_group` | 转 `observation`，主画像留空，仅保留 `mfg_multi_factory_group` 次级画像 | `boundary_review` |

统一动作：

1. 从正式候选链路中移出
2. 不再按当前层级继续推进
3. 优先补产品/服务、商业模式和官方来源

---

## 4. 画像重判样本

以下 `4` 家进入第一批 persona 收紧复核：

| account_id | 公司 | 当前 persona | 建议主画像 | 建议次级画像 | 当前动作 |
| --- | --- | --- | --- | --- | --- |
| `acc_jihong` | 厦门吉宏科技股份有限公司 | `cbec_supply_chain_complex` | `cbec_multi_platform_brand` | `cbec_platform_operator` | `verification` |
| `acc_zibuyu` | 子不语集团有限公司 | `cbec_supply_chain_complex` | `cbec_multi_platform_brand` | - | `verification` |
| `acc_amec` | 中微半导体设备（上海）股份有限公司 | `mfg_rnd_sales_complex` | 暂不硬贴 | `mfg_rnd_sales_complex` | `boundary_review` |
| `acc_bozon` | 博众精工科技股份有限公司 | `mfg_rnd_sales_complex` | `mfg_rnd_sales_complex` | `mfg_multi_factory_group` | `verification` |

统一动作：

1. 清理旧 persona 漂移
2. 回到标准 persona 集合重判
3. 无法稳定归类的，保留为观察对象或主画像留空

---

## 5. 正向锚点样本

以下 `3` 家继续作为当前体系的正向锚点：

| account_id | 公司 | 主线 | 主画像 | 当前结论 |
| --- | --- | --- | --- | --- |
| `acc_miniso` | 名创优品（广州）有限责任公司 | 零售消费 | `retail_multi_store` | 保留锚点 |
| `acc_anker` | 安克创新科技股份有限公司 | 跨境电商 | `cbec_multi_platform_brand` | 保留锚点 |
| `acc_inovance` | 深圳市汇川技术股份有限公司 | 先进制造 | `mfg_multi_factory_group` | 保留锚点 |

这三家用于：

1. 反向支撑 persona 边界
2. 作为后续校准与扩池的稳定锚点

---

## 6. 正向推进样本

当前最明确的正向推进样本是：

- `acc_eastroc`

当前口径：

- 主画像保留为 `retail_high_sku_brand`
- 建议成熟度为 `L3`
- 继续走 `promotion_review`

---

## 7. 纠偏后的层内分流

本轮 `15` 家样本纠偏后，应按以下口径理解：

### 正式候选

- `11` 家
- 可以继续进入 `verification / promotion_review`

### 观察对象

- `4` 家
- 不得再继续按正式候选推进
- 必须先补关键事实或重判主画像

---

## 8. 当前结论

一句话总结：

- `Phase 1` 的 `15` 家样本已经不再只是“外部校准结果”，而是形成了第一批正式纠偏口径；下一步可以直接按这份清单推进主表、档案和队列的定向回写，而不需要重新判断方向。
