# 静态潜客池项目

当前仓库的默认主线已经收口为静态潜客池系统，而不是早期的探迹批量查询应用。

如果你要快速恢复上下文，优先看：

- [静态潜客池总入口](/Users/clairaipartner/Codex/bussiness-master/docs/README-静态潜客池.md)
- [主线恢复版总说明](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/静态潜客池-主线恢复版总说明-v1.md)
- [执行层落地分支说明](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/执行层落地分支说明-v1.md)
- [执行层落地分支复盘](/Users/clairaipartner/Codex/bussiness-master/docs/00-当前总览/执行层落地分支复盘-v1.md)

## 当前默认执行入口

- `expand`：[scripts/expand_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/expand_static_pool.py)
- `enrich`：[scripts/enrich_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/enrich_static_pool.py)
- `promote`：[scripts/promote_static_pool.py](/Users/clairaipartner/Codex/bussiness-master/scripts/promote_static_pool.py)

## 当前仓库结构

- `shared/static_pool/`
  - 当前静态池共享校验层、执行引擎和写回骨架
- `scripts/`
  - 当前现行执行入口和少量仍在使用的辅助脚本
- `scripts/legacy/`
  - 历史 wrapper、档案修复链路和阶段性专项脚本
- `docs/`
  - 当前制度、总览、结构模板、执行索引和归档
- `deliveries/`
  - 结果包与模板；其中大量历史批次结果仍待后续归档

## Legacy 说明

仓库里仍保留一批早期探迹应用相关代码，但已经整体降级到：

- [legacy_app](/Users/clairaipartner/Codex/bussiness-master/legacy_app)

其中包括旧应用的：

- `apps/`
- `browser_extensions/`
- `collectors/`
- `docker-compose*.yml`
- `Dockerfile`
- `alembic.ini`

相关部署文档也已迁入：

- [docs/archive/deployment](/Users/clairaipartner/Codex/bussiness-master/docs/archive/deployment)

这些内容当前不属于静态潜客池执行层主线，保留它们只是为了历史兼容和后续判断，不应再作为默认入口理解整个项目。
