# 智识库

面向 100 人以内团队的纯知识平台第一版。它不做部门、项目、会议或任务协作，而是专注于结构化知识、可信搜索与 AI 增强问答。

## 已实现

- 邮箱密码登录与 Reader / Contributor / Editor / Admin 角色
- 主题、标签、知识页面、草稿与发布版本
- 中文关键词搜索
- 本地磁盘附件上传与鉴权下载
- 本地文件元数据、UUID 存储键和 SHA-256
- AI 问答适配层；未配置模型时自动返回有出处的检索结果
- Next.js 前端和 FastAPI 后端

## 在 Windows 上启动

打开两个 PowerShell 窗口，分别运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start-server.ps1
```

```powershell
.\start-web.ps1
```

浏览器打开 `http://localhost:3000`。

初始管理员：

```text
admin@example.com
ChangeMe123!
```

请在正式使用前修改默认密码，并将 `server/storage` 与 `knowledge.db` 纳入同一备份策略。

## AI 配置

在启动后端的环境中设置以下变量即可接入 OpenAI-Compatible 服务：

```text
AI_ENABLED=true
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=...
LLM_MODEL=...
```

## 目录

```text
server/   FastAPI、SQLite/PostgreSQL 数据访问、本地文件存储
web/      Next.js 阅读、搜索、编辑和 AI 问答界面
infra/    后续部署配置预留
```

## 当前边界

这是可运行的第一版，优先实现完整的知识流：创建草稿 → 编辑 → 发布版本 → 搜索 / AI 引用。

下一轮可继续加入 pgvector 语义检索、Redis/Celery 异步索引、Tiptap 富文本编辑器、OIDC 登录、学习路径、阅读历史与内容复审提醒。
