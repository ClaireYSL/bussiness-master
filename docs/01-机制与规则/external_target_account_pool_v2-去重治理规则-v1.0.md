# `external_target_account_pool_v2` 去重治理规则 v1.0

## 1. 文档目的

本文件用于固定 `external_target_account_pool_v2` 的 canonical 去重治理规则，避免后续继续用临时判断处理重复主体。

## 2. 去重对象

本规则用于处理以下重复类型：

1. 同一 `canonical_name` 被重复写入主表
2. 不同 `account_id` 实际指向同一 canonical account
3. 同一 `account_id` 因重复迁移被写入多行

## 3. 主记录保留规则

### 3.1 层级优先级

默认优先保留层级更高的记录：

- `L1` > `L2` > `L3` > `L4` > `L5`

### 3.2 同层级冲突处理

若重复记录处于同一层级，则优先保留：

1. 命名更规范的 account_id
2. 知识资产挂接更完整的记录
3. 证据更完整的记录
4. 已被更多下游引用的记录

### 3.3 legal 优先

如果重复主体中存在：

- `*_legal`
- 或更明确指向法人主体的 account_id

则默认优先保留法人主体口径记录，除非它的层级显著更低且会破坏已有高质量层判断。

### 3.4 同 id 重复

若重复记录的 `account_id` 相同，则：

- 保留 1 行主记录
- 其余视为重复行
- 不产生新的 alias

## 4. 废弃记录处理规则

废弃记录不物理删除，但不再作为主表事实源。

统一处理方式：

- 标记为 `deprecated_duplicate`
- 记录 `merged_into_account_id`
- 不再参与总量和层级统计

## 5. 下游联动规则

去重治理必须同步影响：

1. `account_evidence_log_v1`
2. `account_review_queue_v1`
3. 总池汇总视图
4. 后续新增入池时的 alias 对照

## 6. evidence 联动规则

### 6.1 不同 id 合并

如果旧 `account_id` 被并入新 `account_id`，则对应 evidence 必须同步重映射。

### 6.2 同 id 重复行

如果只是同一 `account_id` 的重复主表行，则 evidence 无需改 id，只需在主表去掉重复行。

## 7. queue 联动规则

### 7.1 不同 id 合并

如果旧 `account_id` 被并入新 `account_id`，则 queue 必须同步改成新 id。

### 7.2 层级冲突

若同一 `account_id` 存在高低层级重复行，则 queue 统一挂到保留的高层级主记录。

## 8. alias 机制

后续重复治理统一通过：

- `account_alias_registry_v1`

来保留以下映射：

1. 重复 account_id 到 canonical account_id
2. 品牌名到 canonical account_id
3. 历史主体名到 canonical account_id
4. 集团名到 canonical account_id

## 9. 当前默认处理决策

本轮默认采用以下关键决策：

- 保留 `acc_laiyifen_legal`，合并 `acc_laiyifen`
- 保留 `acc_uxi`，合并 `acc_motern`
- 保留 `acc_jame`，合并 `acc_jemet`
- 保留 `acc_siasun` 的 `L2` 主记录，删除 `L5` 重复行
- 保留 `acc_juewei` 的 `L4` 主记录，删除 `L5` 重复行

## 10. 适用边界

本规则只用于 `静态潜客池事实源治理`。

不处理：

- 动态机会层
- 联系人层
- CRM 层

## 11. 关联文档

- [external_target_account_pool_v2-重复主体清单-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/03-执行与校验/external_target_account_pool_v2-重复主体清单-v0.1.md)
- [account_alias_registry_v1-字段模板-v1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/account_alias_registry_v1-字段模板-v1.md)
- [account_alias_registry_v1-首版真实内容-v0.1.md](/Users/clairaipartner/.openclaw/workspace-main/bussiness-master/docs/02-注册表与结构/account_alias_registry_v1-首版真实内容-v0.1.md)
