# 探迹会话同步器

这是一个 Chrome Manifest V3 插件，用于把当前浏览器里已经登录好的探迹会话同步到本地 `bussiness` 服务。

插件会做三件事：

- 读取 `sales.tungee.com` 和 `user.tungee.com` 对当前 URL 可见的 cookie
- 在当前探迹企业详情页主动触发一次真实详情请求，抓取 `x-tonxis-pid / x-tonxis-sid / x-tonxis-signature`
- 把这些上下文同步到本地 `http://127.0.0.1:8000/api/tungee/session/import`
- 当本地 `/console` 创建查询批次时，优先由插件在浏览器里执行企业搜索，再把命中的 `enterprise_id` 回传本地

## 使用方式

1. 先启动本地服务，例如 `./scripts/dev.sh`
2. 打开 Chrome 扩展管理页：`chrome://extensions/`
3. 打开「开发者模式」
4. 选择「加载已解压的扩展程序」
5. 选择当前目录：`browser_extensions/tungee-session-sync`
6. 在同一个浏览器里先登录探迹
7. 打开任意一个 `sales.tungee.com/enterprise-details/...` 企业详情页
8. 点击插件，执行「抓取并同步」

## 自动同步

插件安装后，如果你打开的是本地 `bussiness` 项目的 `/console` 页面，并且浏览器里已经有一个打开中的探迹企业详情页，页面会自动检测插件并请求同步一次探迹上下文。

也就是说常见流程可以变成：

1. 浏览器里登录探迹
2. 保持一个 `sales.tungee.com/enterprise-details/...` 页面打开
3. 打开本地 `/console`
4. 页面自动请求插件同步
5. 不再需要在本地页面手输探迹账号密码

## 说明

- 本地服务默认无需系统登录，会落到匿名内置用户上
- 如果你本地服务不是 `8000` 端口，可以在插件里改「本地 API 地址」
- 同步成功后，打开本地 `/console` 即可直接使用，无需再手输探迹账号密码
