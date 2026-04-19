# 依赖迁移包 v1

## 已打包进 GitHub

目录：

- `workbooks/`

包含：

1. `静态潜客主表.xlsx`
2. `潜客档案库.xlsx`
3. `治理与证据.xlsx`
4. `内部运营-静态潜客池-共享版.xlsx`
5. `知识资产注册表.xlsx`

## 未打包进 GitHub

`static-pool-raw-materials/` 未直接入仓，原因：

1. 总体积较大（约 1.4GB）
2. 含超过 100MB 的单文件，普通 GitHub 仓库不可直接接收

已提供：

1. `raw_materials_manifest_v1.json`（全量文件清单、size、sha256）
2. `scripts/sync_raw_materials.py`（自动同步原素材目录）

## 一键恢复工作簿（新环境）

```bash
python3 scripts/hydrate_dependency_bundle.py \
  --bundle-dir deliveries/archive/dependency_bundle/v1/workbooks \
  --target-dir "$HOME/Documents/Obsidian-Codex/潜客池"
```

## 同步原素材（新环境）

```bash
python3 scripts/sync_raw_materials.py \
  --source "/path/to/static-pool-raw-materials" \
  --target "$HOME/Codex/static-pool-raw-materials"
```
