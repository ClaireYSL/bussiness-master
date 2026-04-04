# 商机线索引擎 / 探迹批量查询控制台

当前仓库已经不只是骨架，现阶段包含一版可运行的内部控制台基础能力：

- 单页查询工作台
- 探迹会话管理
- 浏览器插件同步探迹登录态
- 批量查询任务建单
- 最近查询记录回看
- 管理后台总览

探迹真实搜索/详情执行链路还在继续补，但两页版页面和后台基础设施已经可以启动和访问。

## 本地启动

### 1. 准备环境变量

复制 `.env.example` 为 `.env`，至少保证下面几项可用：

```env
APP_ENV=development
APP_NAME=business-leads-engine
APP_SECRET_KEY=replace-me
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/business_leads
REDIS_URL=redis://localhost:6379/0
TUNGEE_BASE_URL=https://user.tungee.com
TUNGEE_TIMEOUT_SECONDS=20
TUNGEE_SESSION_TTL_HOURS=24
```

### 2. 安装 Python 依赖

如果你本地直接用 `pip`：

```bash
python3 -m pip install .
```

### 3. 启动 API

```bash
./scripts/dev.sh
```

`scripts/dev.sh` 现在会在开发环境里自动完成这些动作：

- 如本机 Docker daemon 未启动，先尝试唤起 Docker Desktop
- 自动选择可用的 Docker context（优先 `desktop-raw`）
- 当 `.env` 指向本地 `localhost:5432 / 6379` 时，自动启动 `postgres / redis`
- 自动执行 `python3 -m alembic upgrade head`
- 最后启动 `uvicorn --reload`

如果你想跳过其中某一步，可以这样运行：

```bash
AUTO_START_DEPS=0 ./scripts/dev.sh
AUTO_MIGRATE=0 ./scripts/dev.sh
DOCKER_CONTEXT=desktop-linux ./scripts/dev.sh
```

如果你想改端口或 Python 解释器，也可以这样运行：

```bash
PORT=8010 ./scripts/dev.sh
PYTHON_BIN=/usr/bin/python3 ./scripts/dev.sh
```

默认地址：

- 首页：[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 健康检查：[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## 页面访问说明

启动后你可以直接访问这些页面：

- 首页：[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 查询页面：[http://127.0.0.1:8000/console](http://127.0.0.1:8000/console)
- 管理后台：[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- `/login`、`/history`、`/tungee/connect` 现在都会直接跳到 `/console`

当前默认是匿名内置用户模式，不需要系统登录。推荐你先按这个顺序走一遍：

1. 打开 [http://127.0.0.1:8000/console](http://127.0.0.1:8000/console)
2. 在页面顶部使用浏览器插件直接同步探迹登录态
3. 在同一页继续提交公司名单并查看最近查询记录
4. 用 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) 看全量记录

## 浏览器插件同步探迹会话

如果你已经在浏览器里登录了探迹，现在直接通过浏览器插件同步登录态即可，本地页面不再提供手动输入探迹账号密码入口。

仓库内已经提供一个 Chrome MV3 插件：

- 插件目录：[browser_extensions/tungee-session-sync/README.md](/Volumes/work/guandata/bussiness/browser_extensions/tungee-session-sync/README.md)

插件会从当前浏览器里同步这些上下文到本地服务：

- `sales.tungee.com` / `user.tungee.com` 对当前 URL 可用的 cookie
- 当前真实请求里的 `x-tonxis-pid / x-tonxis-sid / x-tonxis-signature`
- 当前浏览器 `User-Agent`

使用前提：

1. 本地 API 服务已经启动
2. 同一个浏览器里已经登录探迹
3. 当前页面打开的是 `sales.tungee.com` 的企业详情页

插件安装后，如果你打开本地 `/console` 页面，页面会自动检测插件并请求同步一次探迹上下文。常见情况下，本地页面无需再手输探迹账号密码。

## 当前已完成模块

- [main.py](/Volumes/work/guandata/bussiness/apps/api/main.py)：FastAPI 入口、静态资源和页面路由挂载
- [auth.py](/Volumes/work/guandata/bussiness/apps/api/routes/auth.py)：应用侧登录
- [tungee.py](/Volumes/work/guandata/bussiness/apps/api/routes/tungee.py)：探迹会话管理接口
- [query_jobs.py](/Volumes/work/guandata/bussiness/apps/api/routes/query_jobs.py)：查询任务接口
- [admin.py](/Volumes/work/guandata/bussiness/apps/api/routes/admin.py)：管理员接口
- [query_orchestrator.py](/Volumes/work/guandata/bussiness/shared/services/query_orchestrator.py)：查询任务模型编排
- [bootstrap_admin.py](/Volumes/work/guandata/bussiness/tools/bootstrap_admin.py)：初始化本地账号

## 当前未完成模块

- 探迹真实公司搜索、详情、招聘、联系方式执行器
- `query_item` 自动推进到 `completed / not_found / failed`
- 查询结果自动落 `raw_records / signals / contacts / research_reports`
- 查询结果导出和页面详情展示增强
