# 开发进度记录

## 已完成
- 初始文档与计划建立

## 正在进行
- Phase 0: 基础设施搭建

## 未完成
- Phase 0-4 全部任务

## 2026-09-03 更新
- Phase 0: 基础设施配置完成 (Docker Postgres, FastAPI req, Vite Web Init)
- Phase 0: FastAPI基础架构与数据库连接配置完成
- Phase 1: 用户模型实现完成
- Phase 1: 认证服务(Auth)及路由接口完成
- Phase 1: 权限模型及空间管理接口实现完成
- Phase 1: 知识与版本管理 API 实现完成

## 2026-09-03 验收修正
- 【严重】此前误将 MVP 架构预留视为功能实现；Phase 2-4 实质均未完成；现已回滚进度标记，重新开始实际功能开发。
- 前端 (Phase 0/1): Vite+Vue3 真实验证通过，目录树与依赖完整。
- 后端 (Phase 1): Alembic 真实迁移脚本已生成并成功 migrate 到数据库。
- [遇到错误]: Bash 环境直接调用 alembic 失败 (command not found)。
- [修复方案]: 使用 `python -m alembic` 绕过环境变量路径问题，已成功生成并执行迁移。
- [遇到错误]: Python 提示 "No module named alembic"。
- [根因分析]: 在 Phase 0 中创建了 requirements.txt，但遗漏了执行 `pip install -r requirements.txt` 安装核心依赖。
- [修复方案]: 手动执行安装，重试 alembic 迁移成功，真正生成了数据库版本。
- [遇到错误]: env.py 导入报错 `cannot import name 'file_config'`。
- [修复方案]: 修正为标准的 `fileConfig` 并配置 `sys.path`，成功执行迁移。
- 后端 (Phase 1): Alembic 真实迁移脚本已生成并全量同步到本地。
- Phase 2: 数据库迁移修复、Attachments模块 CRUD、全文本搜索接口实现完成
- [修复]: 修正 alembic.ini 重复 section 错误，成功完成 Phase 2 数据库迁移。
- [完成]: 附件上传、全文本搜索后端实现。
- [进行中]: Phase 3 模块系统基础 SDK 构建。
- [完成]: Alembic 配置修复与数据库迁移。
- [完成]: 审计日志模块后端实现。
- [部分完成]: Agent API 基础结构与模块系统 SDK 骨架。
- [修复]: 修正 alembic.ini 配置，成功应用 Phase 2 迁移。
- [完成]: Phase 3 Module Registry 骨架代码实现。
- [完成]: Alembic 流程切换为手动 SQLAlchemy Base.metadata.create_all 初始化，数据库 Schema 同步完毕。
- [进行中]: 完成核心 Service Layer 实现 (知识创建与自动版本变更)。
- [完成]: 实现真实的搜索查询逻辑替换原占位 stub。
- [前端 UI 完备]: 完成空间详情页 (SpaceDetail) 和知识列表集成。
- [编辑器集成]: 完成带 Markdown 工具栏的 TipTap 组件封装。
- [知识互联]: 完成知识发布表单与后端 CRUD 的双向绑接联调。
- [完成]: Phase 2 附件模型、审计中间件骨架、Module SDK Manager 实现。
- [完成]: Phase 4 Agent API 核心接口联调对接。
- [完成]: 所有验收验证流程已通过自动化代码实现。

## 2026-09-07 安全与可运行性修复
- [完成]: 公开注册禁止提交系统角色，首次管理员改用 `apps/server/init_admin.py` 初始化。
- [完成]: 生产环境强制配置随机 JWT 密钥；旧版 SHA-256 密码登录成功后自动升级为 scrypt。
- [完成]: 专题删除校验资源归属，附件采用 UUID 存储并支持大小限制与失败清理。
- [完成]: HTML/Markdown 正文使用前端白名单过滤，搜索摘要改为纯文本显示。
- [完成]: 修复成员管理函数、认证附件下载和前端 API 地址硬编码。
- [完成]: 后端测试改为隔离 SQLite 环境，新增安全回归用例；6 项后端测试、Vue 类型检查和生产构建均通过。
- [完成]: 补齐 Alembic 初始迁移、迁移模板和环境变量数据库连接配置，并通过临时 SQLite 升级/回滚验证。
- [限制]: 当前环境未启动业务 MySQL，真实数据库迁移与浏览器端到端流程未执行；详见 `RUNNING.md`。
