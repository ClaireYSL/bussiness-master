# promote批次配置模板-v1

## 1. 目的

本文件定义通用 `promote` 入口所使用的批次配置最小结构。

对应入口脚本：

- [promote_static_pool.py](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/scripts/promote_static_pool.py)

---

## 2. 推荐字段

```json
{
  "batch_id": "promote_batch_retail_l5_to_l3_v1",
  "from_level": "L5",
  "target_level": "L3",
  "track": "零售消费",
  "limit": 5,
  "account_ids": [],
  "output_file": "deliveries/promote_batch_retail_l5_to_l3_v1.json"
}
```

字段说明：

- `batch_id`
  - 本轮批次 ID
- `from_level`
  - 当前层级
- `target_level`
  - 目标层级
- `track`
  - 可选；为空表示不限制主线
- `limit`
  - 最多评估多少个对象
- `account_ids`
  - 若给定，则优先按显式名单评估
- `output_file`
  - 结果输出位置

---

## 3. 当前示例

当前仓库已提供两个示例配置：

- [retail_l5_to_l3_v1.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/configs/promote_batches/retail_l5_to_l3_v1.json)
- [l3_to_l2_mass_v1.json](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/configs/promote_batches/l3_to_l2_mass_v1.json)

---

## 4. 当前结论

一句话总结：

- 后续 `promote` 不应继续把批次定义写死在脚本文件名里，而应逐步转成“通用入口 + 批次配置”。
