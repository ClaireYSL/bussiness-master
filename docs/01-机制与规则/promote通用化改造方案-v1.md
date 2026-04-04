# promote通用化改造方案-v1

## 1. 目的

本文件用于回答一个明确问题：

- `promote` 是否应该按每种层级变化、每条主线、每个专项都写一个单独脚本？

结论是否定的。

当前仓库里像：

- [promote_l5_to_l3_consumer_20260331.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/scripts/promote_l5_to_l3_consumer_20260331.py)
- [promote_l3_to_l2_mass_20260331.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/scripts/promote_l3_to_l2_mass_20260331.py)

这类脚本，应该被理解为：

- 历史专项执行脚本

而不是：

- 长期系统架构的最终形态

---

## 2. 当前问题

如果继续沿用“每种 promote 一支脚本”的思路，后续会自然膨胀成：

1. `L5 -> L4` 一个脚本
2. `L5 -> L3` 一个脚本
3. `L4 -> L3` 一个脚本
4. `L3 -> L2` 一个脚本
5. 零售、跨境、制造各自再分版本
6. 每次规则变化再复制一个新版本

这会直接带来 4 个问题：

1. 规则重复  
   同一套上移闸门、persona 校验、知识引用逻辑，会散落在多个脚本里。

2. 行为漂移  
   不同脚本会各自长出不同的 `review_status`、字段回写、队列处理口径。

3. 维护成本过高  
   每次规则收紧都要改多支脚本。

4. 历史专项脚本越来越像“流程本身”  
   用户会误以为 “L5 -> L3” 本身就是一个固定系统动作，而不是某一轮执行选择。

---

## 3. 正确目标

`promote` 应逐步从“专项脚本集合”收束成：

1. 一个通用 promote 引擎
2. 若干批次配置 / 候选清单 / 执行任务包
3. 少量为历史兼容保留的专项 wrapper

一句话总结：

- 不再是“每种上移写一支脚本”
- 而是“一个通用上移框架 + 多种输入配置”

---

## 4. 建议架构

## 4.1 通用 promote 引擎

通用引擎负责固定动作，不关心这轮到底是 `L5 -> L3` 还是 `L3 -> L2`。

它只负责：

1. 读取本轮候选
2. 读取主表 / 档案 / evidence / queue
3. 运行共享上移闸门
4. 判断：
   - `allow`
   - `warn`
   - `block`
5. 生成结构化上移结果
6. 在需要时执行回写

这部分应该尽量沉到：

- `shared/static_pool/validators.py`
- `shared/static_pool/reporting.py`
- 一个新的通用入口脚本中

例如未来形态可以是：

- `scripts/promote_static_pool.py`

---

## 4.2 批次配置层

这一层只回答：

1. 本轮处理哪些账户
2. 当前目标层级是什么
3. 本轮属于哪个主线或专题
4. 是否允许实际回写
5. 是否只出结果包不执行

也就是说：

- “L5 -> L3”
- “只做零售”
- “只做这 2 家”

这些不应该体现在脚本文件名里，而应该体现在任务包或配置里。

建议未来通过这些方式承载：

1. JSON 任务包
2. 显式参数
3. 批次配置文件

例如：

```json
{
  "batch_id": "promote_phase1_retail_2026_04",
  "from_level": "L5",
  "target_level": "L3",
  "track": "零售消费",
  "account_ids": ["acc_xxx", "acc_yyy"],
  "write_back": false
}
```

---

## 4.3 历史专项 wrapper

现有的专项脚本不需要立刻删除。

更合理的做法是把它们降级成：

- wrapper
- 历史兼容入口

它们未来只做两件事：

1. 组装当前这轮专项配置
2. 调用通用 promote 引擎

这样：

- 旧入口还能继续跑
- 但核心规则只保留一份

---

## 5. 建议分层

## 5.1 通用层

长期保留：

- 通用 promote 引擎
- 共享闸门
- 统一报告输出

## 5.2 配置层

按批次变化：

- 本轮候选名单
- 目标层级
- 主线 / persona 限制
- 是否回写

## 5.3 历史层

逐步降级：

- `promote_l5_to_l3_consumer_20260331.py`
- `promote_l3_to_l2_mass_20260331.py`

它们保留作为：

- 历史专项记录
- 兼容 wrapper

而不是未来继续扩张的模式。

---

## 6. 对当前仓库的具体判断

当前最明显的两个历史 promote 脚本分别代表：

### `promote_l5_to_l3_consumer_20260331.py`

它混合了：

1. 候选筛选
2. 主线 / persona 专项假设
3. 上移闸门
4. 档案渲染
5. 主表 / 档案 / 队列回写

所以它不是“一个 promote 动作”，而是：

- 一轮消费品专项批处理

### `promote_l3_to_l2_mass_20260331.py`

它代表的是另一种专项：

- 高层记录批量增强与升层

这两支脚本的存在本身没错，但不应继续被复制为未来模板。

---

## 7. 推荐的未来入口

未来对用户和系统都更清晰的入口应是：

### 入口 A：通用 promote

例如：

- `scripts/promote_static_pool.py`

它接受：

1. `from_level`
2. `target_level`
3. `track`
4. `account_ids`
5. `write_back`
6. `batch_id`

### 入口 B：专项 wrapper

例如：

- `scripts/promote_l5_to_l3_consumer_20260331.py`

它只做：

1. 固定一组参数
2. 调通用引擎

---

## 8. 迁移建议

### 第一阶段

先不要重写所有 promote。

只做：

1. 抽通用候选评估函数
2. 抽通用回写函数
3. 抽通用批次输出函数

当前已落地：

- 新增 [promote_engine.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/shared/static_pool/promote_engine.py)，抽出主表 / 档案 / evidence / queue 的通用读取、候选选择与批次闸门评估能力
- 新增 [promote_static_pool.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/scripts/promote_static_pool.py)，作为通用 promote 的只读评估入口，可直接输出结构化批次结果包
- 新增 [promote批次配置模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/01-机制与规则/promote批次配置模板-v1.md) 以及 `configs/promote_batches/*.json` 示例配置，让批次定义开始脱离历史脚本文件名

当前示例结果：

- [promote_batch_retail_l5_to_l3_v1.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/deliveries/promote_batch_retail_l5_to_l3_v1.json)

### 第二阶段

新增：

- `scripts/promote_static_pool.py`

并让现有历史脚本逐步调用它。

当前已落地：

- [promote_l5_to_l3_consumer_20260331.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/scripts/promote_l5_to_l3_consumer_20260331.py) 已支持 `--report-only`，会先调用通用 preflight 入口并输出 [promote_batch_retail_l5_to_l3_v1_wrapper.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/deliveries/promote_batch_retail_l5_to_l3_v1_wrapper.json)
- [promote_l3_to_l2_mass_20260331.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/scripts/promote_l3_to_l2_mass_20260331.py) 已支持 `--report-only`，会先调用通用 preflight 入口并输出 [promote_batch_l3_to_l2_mass_v1_wrapper.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/deliveries/promote_batch_l3_to_l2_mass_v1_wrapper.json)

说明：

- 当前这两支脚本还保留历史专项写回逻辑
- 但在“只读评估”入口上已经不再各自维护独立实现
- 默认主流程也已优先消费通用 preflight 选出来的账户集合，不再自己再做一轮完整候选发现
- 已新增 [promotion_writeback.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/shared/static_pool/promotion_writeback.py)，将 `source_note` 追加、`validation_gap` 前缀、promotion evidence 去重补写、`promotion_review` 队列关闭等共享写回骨架抽到统一位置
- 该共享层现已进一步覆盖：主表核心升层写回、档案核心状态写回、coverage 核心状态写回；历史脚本里剩余的差异主要集中在消费品专项文案、观察记录、档案渲染等真正的专题逻辑
- 这意味着当前 `promote` 线已经在“评估入口 + 公共写回骨架”两层完成统一，剩余差异主要集中在各专项脚本自己的业务字段更新
- 这意味着它们已经从“完全独立脚本”进入“半 wrapper 化”状态

### 第三阶段

当新入口稳定后，再把历史专项脚本明确降级为：

- wrapper
- archive

---

## 9. 当前结论

一句话总结：

- `promote` 不应该每种可能都写一个单独脚本
- 现有这些脚本是历史专项执行产物
- 正确方向是：**一个通用 promote 引擎 + 多个批次配置 / 历史 wrapper**

这才是后续能长期维护的结构。
