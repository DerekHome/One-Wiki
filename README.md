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
- Windows 启动脚本、Docker Compose 配置、后端测试与前端生产构建

## 在 Windows 上启动

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

首次启动后请立即修改默认密码。备份时必须同时保存根目录的 `knowledge.db` 与 `server/storage`。

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
