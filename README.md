# 企业知识中心

企业知识中心（Knowledge Center）不是传统 Wiki。它是企业内部的**知识基础设施**：同一份经过权限与版本管理的知识，同时供给两类使用者——员工在线阅读、编辑、检索；智能体与其他 AI 工具通过标准接口取用。

本仓库为 Monorepo：`apps/web` 为 Vue 3 前端，`apps/server` 为 FastAPI 后端。

## 核心思想

> **知识是企业资产。人是第一读者，AI 是同等重要的消费者。系统先把知识管清楚，再把知识开放出去。**

| 不是 | 而是 |
| --- | --- |
| 个人笔记或文档站 | 企业级知识中心：空间、权限、版本、审计 |
| 只给人看的 Wiki | 人与 Agent 共用同一套知识源 |
| 以问答/RAG 为产品本身 | 以知识的创建、组织、检索、开放为产品本身；AI 能力可叠加，但不能成为系统成立的前提 |

落地原则：

1. **一份知识，两种入口**。Web 给人读；Agent API / MCP 给智能体用。两边读的是同一份已发布内容，遵守同一套权限。
2. **人优先，AI 兼容**。关闭 LLM、Embedding、RAG 后，创建、浏览、搜索、权限、版本仍必须可用。
3. **开放不等于裸奔**。Agent 取知识必须鉴权、按空间可见性过滤，并写入审计。
4. **AI 消费知识，不替代知识**。模型可以检索和引用知识中心，不能把未治理的生成结果当成权威来源。

建设方案全文见 [docs/企业知识中心系统建设方案.md](docs/企业知识中心系统建设方案.md)。

## 功能概览

- **知识空间**：创建空间并设置 public、internal 或 private 可见性。
- **权限管理**：系统角色与空间角色分离，支持 owner、admin、editor、viewer。
- **知识管理**：草稿、发布、归档；版本对比与历史恢复。草稿/归档不对智能体开放。
- **内容导入**：支持 Markdown / HTML 导入，自动提取标题与摘要。
- **附件管理**：上传、下载、删除；独立存储标识避免同名覆盖。
- **关键词检索**：按标题、正文、摘要、空间、专题与标签检索已发布知识。
- **模块系统**：搜索等模块的启用、停用与配置。
- **Agent / AI 入口**：独立 API Key、Agent REST、MCP；返回已发布版本快照与 `knowledge://{id}` 引用。
- **审计日志**：登录、知识、空间、成员、附件与 Agent 操作记录（人和 Agent 可区分）。

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Tailwind CSS、Element Plus、Pinia、Axios |
| 界面 | 浅色编辑风（Linear 风格）、IBM Plex Sans、CSS 设计令牌（`--kh-*`） |
| 内容编辑 | TipTap、Marked |
| 后端 | Python、FastAPI、SQLAlchemy、Alembic、Pydantic |
| 数据库 | MySQL 8（默认，utf8mb4） |
| 认证 | JWT、`scrypt` 密码哈希（兼容旧格式并自动升级） |
| 测试 | Pytest、FastAPI TestClient、隔离 SQLite 内存库 |

## 环境要求

- Python 3.11+
- Node.js 18+
- npm
- Docker Desktop（本地 MySQL，可选）

## 快速开始

### 0. 环境变量

在项目根目录复制配置模板：

```powershell
Copy-Item .env.example .env
```

开发环境可使用模板中的默认数据库连接。**生产环境**必须修改 `DATABASE_URL`、`SECRET_KEY`、`UPLOAD_DIR`、`CORS_ORIGINS` 等；`SECRET_KEY` 至少 32 字符，不能使用示例值。

若本机 **3306 端口已被占用**，可修改 `docker-compose.yml` 的端口映射（例如 `3307:3306`），并同步更新 `.env` 中的 `DATABASE_URL` 主机端口。

### 1. 启动数据库

```powershell
docker compose up -d db
```

### 2. 后端安装与迁移

```powershell
Set-Location apps/server
python -m pip install -r requirements.txt
python -m alembic upgrade head
python init_admin.py --username admin --password "请替换为强密码"
```

`init_admin.py` 用于**首次创建或重置**管理员；公开注册接口只能创建普通用户。

### 3. 启动后端

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

| 地址 | 说明 |
| --- | --- |
| [Swagger UI](http://localhost:8000/docs) | 交互式 API |
| [ReDoc](http://localhost:8000/redoc) | API 文档 |
| `GET /health` | 存活检查 |
| `GET /ready` | 数据库就绪检查 |

### 4. 启动前端

新终端：

```powershell
Set-Location apps/web
npm install
npm run dev
```

- 前端：<http://localhost:3000>
- 开发环境通过 Vite 代理访问后端；切换 API 地址使用 `VITE_API_BASE_URL` 或 `VITE_API_PROXY_TARGET`，无需改业务代码。

### Windows 一键启动（可选）

根目录 `start.bat` 会先 `docker compose up -d db` 拉起 MySQL，再打开后端（8000）与前端（3000）窗口并打开浏览器。`stop.bat` 关闭前后端进程并 `docker compose stop db`（数据卷保留）。首次使用前请已完成数据库迁移与 `init_admin.py`。

## 测试与构建

后端测试使用隔离 SQLite 与临时附件目录，**不会**写入业务 MySQL：

```powershell
Set-Location apps/server
python -m pytest -q
```

前端生产构建：

```powershell
Set-Location apps/web
npm run build
```

迁移检查：

```powershell
Set-Location apps/server
python -m alembic heads
python -m alembic upgrade head
```

正式库执行迁移前请先备份。`db_init.py` 仅用于本地一次性初始化，长期升级请用 Alembic。

## 目录结构

```text
One-Wiki/                    # 本仓库（Knowledge Center Monorepo）
├─ apps/
│  ├─ server/                # FastAPI：API、Service、Model、迁移、测试
│  │  ├─ app/
│  │  ├─ migrations/
│  │  ├─ tests/
│  │  └─ init_admin.py
│  └─ web/                   # Vue 3 前端
│     ├─ src/api/
│     ├─ src/components/
│     ├─ src/layouts/
│     ├─ src/views/
│     └─ src/router/
├─ docs/                     # 产品与技术文档
├─ modules/                  # 扩展模块
├─ packages/                 # 共享包预留
├─ docker-compose.yml        # db 默认启动；api/web 使用 --profile full
├─ .github/workflows/ci.yml  # push/PR 自动跑 pytest 与前端 build
├─ .env.example
├─ start.bat                 # Windows：启动 MySQL + 前后端
├─ stop.bat                  # Windows：停止前后端与 MySQL 容器
├─ RUNNING.md                # 运行补充说明
└─ CLAUDE.md                 # 仓库开发约束
```

## 配置说明

| 变量 | 说明 | 示例 |
| --- | --- | --- |
| `DATABASE_URL` | MySQL 连接串 | `mysql+pymysql://admin:password@localhost:3306/knowledge_center?charset=utf8mb4` |
| `ENVIRONMENT` | 运行环境 | `development` / `production` |
| `SECRET_KEY` | JWT 签名密钥 | 生产环境随机长密钥 |
| `UPLOAD_DIR` | 附件目录 | 见 `apps/server` 配置 |
| `MAX_UPLOAD_SIZE_MB` | 单文件上限 | `50` |
| `CORS_ORIGINS` | 允许的前端来源（逗号分隔） | `http://localhost:3000` |
| `VITE_API_BASE_URL` | 前端 API 前缀 | `/api/v1` |
| `VITE_API_PROXY_TARGET` | Vite 开发代理目标 | `http://localhost:8000` |
| `MCP_AUTH_USER` | MCP 进程使用的系统用户名（禁止回落管理员） | `admin` |
| `MCP_API_KEY` | MCP 优先使用的 Agent API Key（`kck_` 开头） | 系统配置中签发 |

## Agent 接入

智能体不要借用员工登录密码。任意登录用户可在 **设置 → Agent 凭证** 配置 Agent 信息与权限并签发 Key（管理员仍可看到全部配置页）：

```http
Authorization: Bearer kck_...
GET /api/v1/agent/search?q=出差报销
GET /api/v1/agent/knowledge/{id}/latest
```

- Key 只能访问 `/api/v1/agent/*`，不能写知识、不能管用户。
- 可填写用途说明；可多选空间；不选空间则沿用签发人可见范围。
- 可勾选只读能力（列空间、检索、读正文、关联、版本、附件）。未授权的能力会 403。
- 签发后仍可改信息和权限，不必换 Key；明文只在签发时显示一次。
- 只返回 **已发布** 最新版本，载荷含 `citation_uri`（如 `knowledge://12`）、专题、标签。
- MCP 设置 `MCP_API_KEY`，或退而使用 `MCP_AUTH_USER`；两者都缺则拒绝启动式回落到管理员。

在 `apps/server` 安装依赖后启动 MCP（stdio）：

```powershell
$env:MCP_API_KEY = "kck_..."
python -m app.mcp_server
```

## 常见问题

**登录后立即回到登录页**

- 确认后端与数据库已启动（前端代理 `ECONNREFUSED` 时会表现为登录失败）。
- 集合类 API 路径需带尾部斜杠（如 `/spaces/`），否则 FastAPI 307 重定向可能丢失 `Authorization` 头；前端 `apiClient` 已自动补全，后端亦关闭 `redirect_slashes` 以减少重定向。

**无法连接数据库**

- 检查 `docker compose ps` 与 `.env` 中 `DATABASE_URL` 端口是否一致。

## 安全注意事项

- 不要提交 `.env`、JWT 密钥、数据库密码或上传文件。
- 生产环境必须设置安全的 `SECRET_KEY` 和 `UPLOAD_DIR`；缺失或使用示例值时应用会拒绝启动。
- 正文导入与 Markdown 渲染使用白名单过滤；新增富文本入口需同等处理。
- 登录失败会按 IP + 用户名限流；修改密码后旧 JWT 立即失效。
- 生产环境将 `CORS_ORIGINS` 限制为实际前端域名，并通过 HTTPS 暴露服务。

## 文档

- [RUNNING.md](RUNNING.md) — 运行与测试补充说明  
- [DECISIONS.md](DECISIONS.md) — 产品定位与架构决策  
- [PROGRESS.md](PROGRESS.md) — 开发进度  
- [docs/企业知识中心系统建设方案.md](docs/企业知识中心系统建设方案.md) — 建设方案  

## 验证状态

后端回归测试、前端 `npm run build` 与 Alembic 在隔离环境下的升级流程已在开发中验证。真实 MySQL 迁移与完整浏览器回归请在目标环境中执行。
