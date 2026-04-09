# promote批次配置模板-v1

## 1. 目的

本文件定义通用 `promote` 入口所使用的批次配置最小结构。

对应入口脚本：

- [promote_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/promote_static_pool.py)

---

## 2. 推荐字段

```json
{
  "batch_id": "promote_batch_retail_l5_to_l3_v1",
  "goal": "本轮 promote 的业务目标",
  "from_level": "L5",
  "target_level": "L3",
  "track": "零售消费",
  "limit": 5,
  "account_ids": [],
  "write_back": false,
  "output_file": "deliveries/promote_batch_retail_l5_to_l3_v1.json",
  "summary_file": "deliveries/promote_batch_retail_l5_to_l3_v1_summary.json",
  "review_file": "docs/03-执行与校验/promote_batch_retail_l5_to_l3_v1-复盘.md"
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
- `write_back`
  - 是否在 `allow` 后执行真实升层写回
- `output_file`
  - promote 结果包输出位置
- `summary_file`
  - promote summary JSON 输出位置
- `review_file`
  - promote 复盘 Markdown 输出位置

---

## 3. 当前示例

当前仓库已提供两个示例配置：

- [retail_l5_to_l3_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/promote_batches/retail_l5_to_l3_v1.json)
- [l3_to_l2_mass_v1.json](/Users/clairaipartner/Codex/bussiness-master/configs/promote_batches/l3_to_l2_mass_v1.json)

---

## 4. 当前结论

一句话总结：

- 后续 `promote` 不应继续把批次定义写死在脚本文件名里，而应逐步转成“通用入口 + 批次配置 + 统一 summary/review 产物”。
