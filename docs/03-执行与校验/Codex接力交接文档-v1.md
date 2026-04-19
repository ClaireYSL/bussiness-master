# Codex接力交接文档-v1

## 1. 目标

让另一个环境的 Codex 在最少沟通成本下，直接接手当前项目执行层工作。

当前策略：优先使用 `Clean Start`（不迁历史坏档案，重建高质量档案）。

---

## 2. 当前代码基线

- 分支：`codex/execution-layer-foundation`
- 最新提交：`87b023d`

最近关键提交：

1. `87b023d` 路径配置化（支持环境变量）
2. `888a83a` 依赖迁移包与同步脚本
3. `63f9b98` 双轨迁移清单 + 高质量档案重建模板
4. `aadf52d` handoff snapshot 生成器
5. `674ae4e` milestone6/6r 执行层底座能力

---

## 3. 迁移包位置（已准备）

- 压缩包：`/Users/clairaipartner/Codex/migration-packages/static-pool-deps-20260419_151148.zip`
- 解压后包含：
1. `workbooks/`（5 个核心 xlsx）
2. `static-pool-raw-materials/`
3. `raw_materials_manifest_v1.json`
4. `hydrate_dependency_bundle.py`
5. `sync_raw_materials.py`

---

## 4. 新环境最短接力步骤

1. 拉代码并切分支

```bash
git clone git@github.com:ClaireYSL/bussiness-master.git
cd bussiness-master
git checkout codex/execution-layer-foundation
git pull
```

2. 解压迁移包到新环境 workspace

3. 落位工作簿（建议）

```bash
python3 scripts/hydrate_dependency_bundle.py \
  --bundle-dir /path/to/static-pool-deps-20260419_151148/workbooks \
  --target-dir "$HOME/Documents/Obsidian-Codex/潜客池"
```

4. 同步原素材

```bash
python3 scripts/sync_raw_materials.py \
  --source /path/to/static-pool-deps-20260419_151148/static-pool-raw-materials \
  --target "$HOME/Codex/static-pool-raw-materials"
```

5. 设环境变量（路径配置化）

```bash
export STATIC_POOL_ROOT="$HOME/Documents/Obsidian-Codex/潜客池"
```

若路径不一致，再设细粒度变量：

```bash
export STATIC_POOL_MAIN_FILE="/your/path/静态潜客主表.xlsx"
export STATIC_POOL_MAIN_SHARED_FILE="/your/path/内部运营-静态潜客池-共享版.xlsx"
export STATIC_POOL_PROFILE_FILE="/your/path/潜客档案库.xlsx"
export STATIC_POOL_GOVERNANCE_FILE="/your/path/治理与证据.xlsx"
export STATIC_POOL_TRACK_PERSONA_FILE="/your/path/主线与画像注册表.xlsx"
export STATIC_POOL_KNOWLEDGE_REGISTRY_FILE="/your/path/知识资产注册表.xlsx"
```

---

## 5. 首跑校验命令

1. 编译检查

```bash
python3 -m py_compile \
  scripts/run_execution_batch.py \
  scripts/enrich_static_pool.py \
  scripts/promote_static_pool.py \
  scripts/select_execution_candidates.py \
  scripts/repair_main_account_ids.py \
  scripts/check_workbook_integrity.py
```

2. 工作簿完整性检查

```bash
python3 scripts/check_workbook_integrity.py \
  --main-file "$STATIC_POOL_ROOT/静态潜客主表.xlsx" \
  --profile-file "$STATIC_POOL_ROOT/潜客档案库.xlsx" \
  --governance-file "$STATIC_POOL_ROOT/治理与证据.xlsx" \
  --output-file deliveries/archive/repairs/workbook_integrity_report_v1.json
```

3. 生成交接快照

```bash
python3 scripts/handoff_snapshot.py
```

---

## 6. 当前推荐执行模式

### 6.1 Clean Start（默认）

1. 不迁旧目录：`07-L3以上客户档案/`
2. 新建目录：`07-L3以上客户档案-v2/`
3. 仅重建高质量档案（高/中高 + 关键字段完整）

模板配置：

- `configs/execution_batches/archive_rebuild_high_quality_template_v1.json`

### 6.2 批次执行顺序（硬约束）

1. `report_only`
2. 人工复核
3. `write_back --require-report-baseline`

---

## 7. 已知边界与注意事项

1. 仓库外依赖必须落位到可访问路径（路径已支持配置，不再硬编码为特定用户目录）。
2. 写回阶段必须串行；并发场景会被文件锁拒绝（这是正常保护机制）。
3. 若 `static-pool-raw-materials` 来源继续变化，先更新 manifest 再同步，避免隐性漂移。
4. 旧潜客档案 Markdown 不作为事实源，事实修正以工作簿为准。

---

## 8. 交接完成判定

新环境 Codex 满足以下即视为接力成功：

1. 能成功执行 `check_workbook_integrity.py` 并输出 `ok=true`
2. 能成功执行一轮 `run_execution_batch --phase report_only`
3. 能生成新的 handoff snapshot 产物
4. 明确采用 `Clean Start` 或 `全量迁移` 之一并写入本地执行说明

