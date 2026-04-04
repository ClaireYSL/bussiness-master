# `account_review_queue_v1` 去重修正 v1.0

## 1. 文档目的

本文件用于记录 `Milestone 1` 去重治理中，对 queue 引用需要做的修正。

说明：

- 只有涉及 `old_account_id -> canonical_account_id` 合并的 queue 需要重映射
- 对于“同一 account_id 重复行”的情况，queue 无需改 id

## 2. 需要重映射的 queue 记录

| source_file | queue_item / line | old_account_id | canonical_account_id | reason |
| --- | --- | --- | --- | --- |
| `account_review_queue_v1-补充内容-v0.2.md` | line 15 | `acc_laiyifen` | `acc_laiyifen_legal` | 旧 id 并入 legal 口径主记录 |
| `account_review_queue_v1-补充内容-v0.2.md` | line 21 | `acc_laiyifen` | `acc_laiyifen_legal` | 旧 id 并入 legal 口径主记录 |
| `account_review_queue_v1-补充内容-v0.4.md` | line 17 | `acc_jemet` | `acc_jame` | 旧 id 并入当前主记录 |

## 3. 当前结论

除上述重映射外，其余 queue 引用可保持不变，因为：

1. 它们指向的是保留的 canonical account_id
2. 或者只是主表里出现了同 id 重复行，不影响 queue 唯一挂接

## 4. 后续要求

后续若再发生 duplicate account 合并，必须同步补 queue 修正文档，而不是只改主表。
