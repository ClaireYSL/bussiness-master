# learning_queue与Phase1样本关联复核-v1

## 1. 目的

本文件用于完成 `Milestone 4` 中“知识侧复核”的最小闭环：

- 不启动新的素材学习
- 只复核 `learning_queue` 里哪些 queued 项与 `Phase 1` 的 `15` 家样本强相关

---

## 2. 当前 queued 概况

当前 `learning_queue` 中仍处于 `queued` 的条目共 `11` 条：

- `1` 条为团队新素材入口占位：`klq_003`
- `10` 条为真实待学习素材

其中与本轮 `15` 家样本直接强相关的，是按三条主线分布的 `10` 条真实素材：

- 零售消费：`klq_057 ~ klq_060`
- 跨境电商：`klq_051 ~ klq_054`
- 先进制造：`klq_055 ~ klq_056`

---

## 3. 按主线复核

## 3.1 零售消费

直接相关样本：

- `acc_miniso`
- `acc_threesquirrels`
- `acc_ays`
- `acc_popmart`
- `acc_eastroc`

强相关 queued 项：

| queue_id | 素材 | 当前优先级 | 关联 persona |
| --- | --- | --- | --- |
| `klq_057` | LLLM 采销供应链数据化解决方案 | `P2` | `retail_high_sku_brand` |
| `klq_058` | CJ Foods 需求计划数字化平台方案 | `P1` | `retail_high_sku_brand` |
| `klq_059` | 鲜丰水果数据智能化应用方案 | `P2` | `retail_multi_store` |
| `klq_060` | 7-Eleven 终端经营透视案例 | `P2` | `retail_multi_store` |

复核结论：

1. `klq_058` 应视为零售消费本轮最值得后续优先复核的 queued 项
2. `klq_059 / klq_060` 可直接支撑 `retail_multi_store` 边界继续收紧
3. `klq_057` 仍 relevant，但优先级次于 `klq_058`

---

## 3.2 跨境电商

直接相关样本：

- `acc_anker`
- `acc_songmics`
- `acc_jihong`
- `acc_zibuyu`
- `acc_loctek`

强相关 queued 项：

| queue_id | 素材 | 当前优先级 | 关联 persona |
| --- | --- | --- | --- |
| `klq_051` | 乐其 SmallRig 跨境电商数据分析体系案例 | `P1` | `cbec_multi_platform_brand` |
| `klq_052` | 碧橙 TP/DP BI 数据应用平台方案 | `P1` | `cbec_multi_platform_brand` |
| `klq_053` | 倍思 BI 案例分享 | `P1` | `cbec_multi_platform_brand` |
| `klq_054` | 有棵树 BI 案例分享 | `P2` | `cbec_multi_platform_brand` |

复核结论：

1. 跨境线当前 queued 项与本轮纠偏高度一致
2. `klq_051 / 052 / 053` 都应保留在后续优先复核组
3. `klq_054` 保留但不提级

---

## 3.3 先进制造

直接相关样本：

- `acc_inovance`
- `acc_sany`
- `acc_amec`
- `acc_bozon`
- `acc_jereh`

强相关 queued 项：

| queue_id | 素材 | 当前优先级 | 关联 persona |
| --- | --- | --- | --- |
| `klq_055` | SAP PCE 对接技术白皮书 | `P1` | `mfg_multi_factory_group` |
| `klq_056` | 兆驰集团多工厂多产线经营效能案例 | `P1` | `mfg_multi_factory_group` |

复核结论：

1. 制造线 queued 项数量少，但相关度很高
2. `klq_056` 更直接支撑多工厂画像边界
3. `klq_055` 更偏系统打通和数据底座能力说明

---

## 4. 本轮复核后的处理口径

本轮不新增学习，但后续优先级应这样理解：

### 后续优先复核组

- `klq_051`
- `klq_052`
- `klq_053`
- `klq_055`
- `klq_056`
- `klq_058`

### 保留待后续处理组

- `klq_054`
- `klq_057`
- `klq_059`
- `klq_060`

### 不纳入本轮纠偏判断组

- `klq_003`

说明：

- `klq_003` 只是手工入口占位，不是具体素材，不应参与本轮 persona / 样本纠偏判断

---

## 5. 当前结论

一句话总结：

- 当前 `learning_queue` 不需要扩张，也不需要现在立刻开学新素材；但已经可以明确哪些 queued 项和 `Phase 1` 的样本纠偏强相关，并把它们作为下一轮知识侧优先复核入口。
