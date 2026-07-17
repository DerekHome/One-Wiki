# 智识库（One Wiki）

面向 100 人以内团队的纯知识平台。它不承担部门、项目、会议或任务协作，而是帮助团队把长期可复用的知识沉淀为可验证、可搜索、可被 AI 引用的内容。

当前第一版已实现完整的知识流：**创建草稿 → 编辑 → 发布版本 → 搜索或 AI 引用**。

## 文档

- [功能说明与产品边界](docs/FEATURES.md)
- [架构设计与关键决策](docs/ARCHITECTURE.md)

## 已实现

- 邮箱密码登录与 `Reader`、`Contributor`、`Editor`、`Admin` 四级角色
- 主题、标签、知识页面、草稿和发布版本
- 中文关键词搜索
- 本地磁盘附件上传、鉴权下载、UUID 存储键与 SHA-256 校验
- 基于已发布内容的 AI 问答接口；未配置模型时返回带出处的检索结果
- Next.js 前端与 FastAPI 后端
- MySQL 8.4 默认数据库，SQLite 仅用于自动化测试或显式轻量配置
- Windows 启动脚本、Docker Compose 配置、后端测试与前端生产构建

## Docker 启动（推荐）

Docker Compose 默认启动 MySQL、FastAPI 和 Next.js，并为数据库和附件分别创建持久化卷：

```powershell
Copy-Item .env.example .env
# 部署前修改 .env 中的 MySQL 密码
docker compose up -d --build
```

浏览器打开 `http://localhost:3000`。MySQL 仅绑定到宿主机 `127.0.0.1:3306`，容器之间通过内部网络通信。

## 在 Windows 上启动

直接在 Windows 上运行前，请先准备 MySQL 8，并通过环境变量或设置中心配置 `DATABASE_URL`。默认连接地址为：

```text
mysql+pymysql://onewiki:onewiki_dev_password@127.0.0.1:3306/onewiki?charset=utf8mb4
```

打开两个 PowerShell 窗口，分别运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd 'F:\Projects\one wiki'
.\start-server.ps1
```

```powershell
cd 'F:\Projects\one wiki'
.\start-web.ps1
```

浏览器打开 `http://localhost:3000`。

默认管理员：

```text
admin@example.com
ChangeMe123!
```

首次启动后请立即修改默认密码。备份时必须同时保存 MySQL 数据库与 `server/storage`；Docker 部署需要备份 `mysql-data` 和 `knowledge-files` 两个卷。

## AI 配置

后端支持任意 OpenAI-Compatible 服务。设置以下环境变量后重启后端：

```text
AI_ENABLED=true
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=...
LLM_MODEL=...
```

AI 回答只使用已发布知识；当资料不足时应明确说明，而不是补全或猜测。

## 工程结构

```text
server/   FastAPI、SQLAlchemy、知识 API、本地文件存储与 AI 适配层
web/      Next.js 阅读、搜索、编辑和 AI 问答界面
docs/     产品功能和架构设计文档
infra/    后续部署配置预留
```

## 验证

```powershell
cd 'F:\Projects\one wiki'
.\server\.venv\Scripts\python.exe -m pytest -q
cd web
npm run build
```

## 初始化说明

数据库首次启动时会自动建表，并创建默认管理员、默认群组、默认目录和欢迎页。详细字段与默认数据见 [初始化字段与默认数据](docs/INITIALIZATION.md)。
