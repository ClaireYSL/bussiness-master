# Docker 打包与服务器部署文档

## 1. 文档目标

本文档用于指导当前仓库通过 Docker 方式完成服务器部署，并明确区分：

- 首次部署：服务器第一次上线该项目
- 更新部署：已有运行实例基础上的版本升级

本文档基于仓库当前实现编写，适用于本项目当前结构：

- Web 服务：FastAPI，入口为 `apps.api.main:app`
- 数据库：PostgreSQL
- 缓存：Redis
- 数据迁移：Alembic
- 后台任务：当前仓库没有独立常驻 worker 进程要求，主流程由应用内逻辑驱动

## 2. 本次交付文件

本仓库已补充以下 Docker 化文件：

- `Dockerfile`：应用镜像定义
- `docker-compose.prod.yml`：服务器部署编排文件
- `.env.prod.example`：生产环境变量样板

## 3. 推荐部署方式

### 3.1 推荐拓扑

建议服务器上的运行结构如下：

- `app`：当前业务应用容器，对外提供 HTTP 服务
- `postgres`：业务数据库容器，使用 Docker Volume 持久化
- `redis`：缓存容器，使用 Docker Volume 持久化
- `nginx` 或云负载均衡：负责 HTTPS 终止与反向代理到 `app:8000`

### 3.2 镜像交付策略

当前仓库尚未提供 CI/CD 流水线，因此建议采用以下两种方式之一：

1. 简化方案：服务器拉取代码后本地执行 `docker compose build`
2. 标准方案：在 CI 或构建机完成 `docker build`，推送到镜像仓库后服务器只执行 `docker compose pull`

本文档默认先按“服务器本地构建”说明，文末补充“镜像仓库模式”。

## 4. 服务器前置条件

部署前请确保服务器满足以下条件：

- Linux 服务器一台，建议 Ubuntu 22.04 LTS 或同级发行版
- 已安装 Docker Engine 24+
- 已安装 Docker Compose Plugin
- 服务器可访问外部依赖：`user.tungee.com`、`sales.tungee.com`、`api.moonshot.cn`（如使用）
- 已开放业务入口端口，默认 `8000`，若前置 Nginx 则只需开放 `80/443`

推荐安装命令示例：

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker
```

## 5. 目录建议

建议将项目部署到如下目录：

```bash
/srv/business-leads-engine
```

示例：

```bash
sudo mkdir -p /srv/business-leads-engine
sudo chown -R $USER:$USER /srv/business-leads-engine
cd /srv/business-leads-engine
```

## 6. 首次部署

### 6.1 获取代码

```bash
git clone <your-repo-url> /srv/business-leads-engine
cd /srv/business-leads-engine
```

如果代码不是通过 Git 下发，也可以直接上传项目目录到该路径。

### 6.2 准备生产环境变量

复制样板文件：

```bash
cp .env.prod.example .env.prod
```

至少修改以下内容：

- `APP_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `MOONSHOT_API_KEY`（如果部署环境需要）

说明：

- `DATABASE_URL` 中的主机名必须保持为 `postgres`，因为这是 compose 内部服务名
- `REDIS_URL` 中的主机名必须保持为 `redis`

### 6.3 构建应用镜像

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml build app
```

### 6.4 启动基础依赖

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d postgres redis
```

确认依赖健康：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

### 6.5 执行数据库迁移

首次部署必须先完成迁移，再启动应用：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm app alembic upgrade head
```

### 6.6 启动应用

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d app
```

### 6.7 验证部署结果

检查容器状态：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

检查应用健康接口：

```bash
curl http://127.0.0.1:8000/health
```

预期返回：

```json
{"status":"ok"}
```

查看应用日志：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f app
```

### 6.8 可选：初始化管理账号

如果需要执行初始化脚本，可通过容器运行：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm app python tools/bootstrap_admin.py
```

## 7. 更新部署

更新部署与首次部署的最大区别在于：

- 不需要重新创建数据卷
- 不需要重建 PostgreSQL / Redis 数据
- 需要先备份数据，再替换应用版本，并按新版本代码执行迁移

推荐按以下顺序执行。

### 7.1 备份数据库

```bash
mkdir -p backups
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "backups/$(date +%F-%H%M%S)-business_leads.sql"
```

如果当前 shell 没有导入 `.env.prod`，请先执行：

```bash
set -a
source .env.prod
set +a
```

### 7.2 更新代码

```bash
git pull origin <your-branch>
```

### 7.3 构建新镜像

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml build app
```

### 7.4 执行升级迁移

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm app alembic upgrade head
```

### 7.5 重建应用容器

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d app
```

### 7.6 验证升级结果

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=200 app
curl http://127.0.0.1:8000/health
```

## 8. 回滚方案

如果更新后出现异常，按以下顺序回滚：

1. 切回上一个稳定版本代码或镜像标签
2. 重新构建或拉取旧镜像
3. 重新执行 `docker compose up -d app`
4. 如本次发布已经执行了破坏性迁移，再根据备份 SQL 做数据库恢复

数据库恢复示例：

```bash
cat backups/<backup-file>.sql | docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

说明：

- 若迁移只做了向前兼容变更，通常只需回滚应用镜像
- 若迁移涉及删字段、删表、重写数据，必须先设计数据库回滚方案再发布

## 9. 运维常用命令

启动全部服务：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

停止全部服务：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml down
```

查看服务状态：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

查看应用日志：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f app
```

进入应用容器：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec app /bin/sh
```

## 10. 一键脚本使用

本仓库已补充一套脚本化入口：

- `scripts/install.sh`：首次部署
- `scripts/update.sh`：更新部署
- `scripts/rollback.sh`：按 git 版本回滚

这 3 个脚本当前都**不依赖 Docker Compose**，而是直接使用 `docker build`、`docker run`、`docker exec` 管理容器。

当前默认镜像源已调整为 `docker.1ms.run`：

- Python 基础镜像：`docker.1ms.run/python:3.11-slim`
- PostgreSQL：`docker.1ms.run/postgres:16-alpine`
- Redis：`docker.1ms.run/redis:7-alpine`

如果后续需要切回其他镜像源，只需修改 `.env.prod` 中的 `PYTHON_BASE_IMAGE`、`POSTGRES_IMAGE`、`REDIS_IMAGE`。

Python 依赖下载当前默认走国内 PyPI 镜像：

- `PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`
- `PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn`

如果服务器访问清华镜像不稳定，也可以改成其他可用源，例如阿里云 PyPI 镜像。

脚本默认会创建并使用以下 Docker 资源：

- 应用容器：`<app-name>-app`
- PostgreSQL 容器：`<app-name>-postgres`
- Redis 容器：`<app-name>-redis`
- 网络：`<app-name>-net`
- 数据卷：`<app-name>-postgres-data`、`<app-name>-redis-data`

其中 `<app-name>` 由 `APP_NAME` 自动转换而来，当前默认值是 `business-leads-engine`。

首次使用前请先赋予执行权限：

```bash
chmod +x scripts/*.sh
```

### 10.1 首次部署脚本

```bash
./scripts/install.sh
```

行为说明：

- 如果 `.env.prod` 不存在，脚本会自动从 `.env.prod.example` 复制一份
- 复制完成后脚本会直接退出，并提示你先修改 `.env.prod`
- 脚本默认会在安装开始前尝试执行 `git pull --ff-only origin master`
- 如果仓库有本地改动，脚本会安全跳过自动拉取并继续部署当前代码
- 修改完成后，再次执行 `./scripts/install.sh`，脚本才会继续构建镜像、创建网络与数据卷、启动依赖、执行迁移并拉起应用

如果你不希望 `install.sh` 自动拉取代码，可以临时关闭：

```bash
INSTALL_AUTO_PULL=0 ./scripts/install.sh
```

### 10.2 更新部署脚本

```bash
./scripts/update.sh
```

行为说明：

- 脚本默认执行 `git checkout master` 和 `git pull --ff-only origin master`
- 自动执行数据库备份
- 自动重建应用镜像、执行迁移、重启应用并校验健康状态
- 如果仓库存在未提交变更，脚本会直接退出，避免误覆盖

### 10.3 回滚脚本

```bash
./scripts/rollback.sh <tag|commit|branch>
```

示例：

```bash
./scripts/rollback.sh v2026.03.21
./scripts/rollback.sh 5ee81c2
```

行为说明：

- 回滚前会先自动备份数据库
- 脚本会切换到你指定的 git 版本，再重建并启动应用
- 数据库不会自动恢复到旧版本，只会提示你按备份手工恢复，避免误操作

## 11. 反向代理建议

生产环境不建议直接把 `8000` 暴露到公网，建议由 Nginx 做 HTTPS 终止和转发。

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

如果已经使用云厂商负载均衡，也可以由负载均衡直接转发到宿主机 `8000`。

## 12. 镜像仓库模式补充

如果后续接入 CI/CD，建议改为以下流程：

1. CI 构建镜像：`docker build -t registry.example.com/business-leads-engine:<tag> .`
2. 推送镜像到仓库
3. 服务器更新 `.env.prod` 中的 `APP_IMAGE`
4. 服务器执行：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull app
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm app alembic upgrade head
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d app
```

该模式的优点是：

- 服务器不需要编译环境
- 发布时间更可控
- 更容易做镜像版本管理和回滚

## 13. 当前项目部署结论

就当前仓库状态而言，推荐采用以下落地方案：

- 用 `Dockerfile` 打包 FastAPI 应用
- 用 `docker-compose.prod.yml` 在服务器统一编排 `app + postgres + redis`
- 首次部署时先起依赖、后做迁移、再起应用
- 更新部署时先备份、再更新镜像、执行迁移、最后重建应用容器

这套方案已经覆盖当前项目上线所需的核心路径，后续如果再引入独立 worker、对象存储或 CI/CD，可在此基础上继续扩展。
