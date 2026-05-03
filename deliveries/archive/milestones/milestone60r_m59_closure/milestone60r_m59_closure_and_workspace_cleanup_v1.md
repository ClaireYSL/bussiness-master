# Milestone 60R M59R 闭环固化与工作区清理 v1

## 目标

把 M59R 从临时可运行状态固化为正式 milestone，并对当前脏工作区做冻结盘点。本文档不代表删除、回滚或批量移动任何文件。

## 当前工作区判断

- tracked diff：28 个文件。
- untracked：686 个路径。
- M59R 最小安全候选：17 个核心代码/文档路径。
- 历史 milestone 未跟踪产物：238 个路径。
- raw materials/dependency bundle：6 个路径。

## 清理原则

- 不删除。
- 不 reset。
- 不把 raw materials 默认提交。
- 不把历史 M11-M58 大量产物混入 M59R 核心提交。
- 后续如果需要纳入历史 archive，单独做 archive import 批次。

## 最小安全提交包建议

详见 `workspace_cleanup_manifest_v1.json` 的 `m59r_core_code_docs_minimal_safe_candidates` 与 `m59r_generated_artifacts`。

## 下一步主线

M61R：trusted_pool_runner v2，补齐 baseline/signature/source trace/no-write proof/update_trusted_pool，并继续保持旧 Excel 默认不可写。
