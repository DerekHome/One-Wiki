# 企业知识中心

企业知识中心（Knowledge Center）是一套面向企业内部知识沉淀、检索和协作的 Web 系统。项目采用前后端分离架构，支持知识空间、成员权限、知识版本、标签、附件、全文检索、审计日志和 Agent 查询接口。

## 功能概览

- 知识空间：创建空间并设置 public、internal 或 private 可见性。
- 权限管理：系统角色和空间角色分离，支持 owner、admin、editor、viewer。
- 知识管理：创建、编辑、发布、软删除、版本比较和历史版本恢复。
- 内容导入：支持 Markdown 和 HTML 文件导入，并自动提取标题和摘要。
- 附件管理：上传、下载和删除附件，使用独立存储标识避免同名文件覆盖。
- 全文检索：按标题、正文、摘要、空间和标签检索已发布知识。
- 模块系统：支持搜索等模块的启用、停用和配置管理。
- Agent API：提供空间、知识、版本、关联内容和搜索查询接口。
- 审计日志：记录登录、知识、空间、成员、附件和 Agent 操作。

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Tailwind CSS、Element Plus、Pinia、Axios |
| 内容编辑 | TipTap、Marked |
| 后端 | Python、FastAPI、SQLAlchemy、Alembic、Pydantic |
| 数据库 | PostgreSQL 15 |
| 认证 | JWT、Python `scrypt` 密码哈希，兼容旧版密码格式并自动升级 |
| 测试 | Pytest、FastAPI TestClient、隔离 SQLite 内存数据库 |

## 环境要求

- Python 3.11 或更高版本
- Node.js 18 或更高版本
- npm
- Docker Desktop（用于启动 PostgreSQL）

## 快速开始

在项目根目录复制环境配置：

```powershell
Copy-Item .env.example .env
```

开发环境可以使用 `.env.example` 中的默认 PostgreSQL 连接配置。生产环境必须修改 `DATABASE_URL`、`SECRET_KEY`、`CORS_ORIGINS` 等配置；`SECRET_KEY` 至少需要 32 个字符，不能使用示例值。

### 1. 启动数据库

```powershell
docker compose up -d db
```

### 2. 安装后端并初始化数据库

```powershell
Set-Location apps/server
python -m pip install -r requirements.txt
python -m alembic upgrade head
python init_admin.py --username admin --password "请替换为强密码"
```

`init_admin.py` 用于首次创建或重置管理员账户。公开注册接口只允许创建普通用户，不能通过请求参数创建管理员。

### 3. 启动后端

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

后端 API 文档：

- Swagger UI：<http://localhost:8000/docs>
- ReDoc：<http://localhost:8000/redoc>
- 存活检查：<http://localhost:8000/health>
- 数据库就绪检查：<http://localhost:8000/ready>

### 4. 安装并启动前端

在新的终端窗口执行：

```powershell
Set-Location apps/web
npm install
npm run dev
```

前端默认运行在 <http://localhost:3000>。开发环境通过 Vite 代理访问后端；如需切换 API 地址，使用 `VITE_API_BASE_URL` 或 `VITE_API_PROXY_TARGET`，无需修改业务源码。

## 测试与构建

后端测试会使用隔离的 SQLite 内存数据库和临时附件目录，不会修改业务 PostgreSQL 数据：

```powershell
Set-Location apps/server
python -m pytest -q
```

前端类型检查和生产构建：

```powershell
Set-Location apps/web
npm run build
```

数据库迁移检查：

```powershell
Set-Location apps/server
python -m alembic heads
python -m alembic upgrade head
```

正式数据库执行迁移前请先完成备份。`db_init.py` 仅保留用于本地一次性初始化，长期升级应使用 Alembic。

## 目录结构

```text
knowledge-center/
├─ apps/
│  ├─ server/              # FastAPI 后端、模型、服务、路由、迁移和测试
│  │  ├─ app/
│  │  ├─ migrations/
│  │  ├─ tests/
│  │  └─ init_admin.py
│  └─ web/                 # Vue 3 前端
│     ├─ src/api/
│     ├─ src/stores/
│     ├─ src/views/
│     └─ src/router/
├─ docs/                   # 产品和技术文档
├─ modules/                # 扩展模块相关目录
├─ packages/               # 共享包预留目录
├─ docker-compose.yml      # PostgreSQL 开发环境
├─ .env.example            # 环境变量模板
└─ RUNNING.md              # 启动和运行补充说明
```

## 配置说明

| 变量 | 说明 | 示例 |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://admin:password@localhost:5432/knowledge_center` |
| `ENVIRONMENT` | 运行环境 | `development` / `production` |
| `SECRET_KEY` | JWT 签名密钥 | 生产环境使用随机长密钥 |
| `UPLOAD_DIR` | 附件存储目录 | `D:/Claude/knowledge-center/apps/server/uploads` |
| `MAX_UPLOAD_SIZE_MB` | 单个附件大小上限 | `50` |
| `CORS_ORIGINS` | 允许的前端来源，逗号分隔 | `http://localhost:3000` |
| `VITE_API_BASE_URL` | 前端 API 前缀 | `/api/v1` |
| `VITE_API_PROXY_TARGET` | Vite 开发代理目标 | `http://localhost:8000` |

## 安全注意事项

- 不要提交 `.env`、JWT 密钥、数据库密码或上传文件。
- 生产环境必须设置安全的 `SECRET_KEY`，缺失或使用示例值时应用会拒绝启动。
- 正文导入和 Markdown 渲染使用白名单过滤；新增富文本入口时也必须经过同等处理。
- 生产环境请将 `CORS_ORIGINS` 限制为实际前端域名，并通过 HTTPS 暴露服务。

## 当前验证状态

当前代码已验证后端回归测试、Vue 类型检查、前端生产构建及 Alembic 临时 SQLite 升级/回滚流程。真实 PostgreSQL 迁移和浏览器端到端流程需要在相应运行环境中执行。

更多运行细节见 [RUNNING.md](RUNNING.md)，开发进度见 [PROGRESS.md](PROGRESS.md)。
