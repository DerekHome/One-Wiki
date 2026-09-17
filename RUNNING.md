# Knowledge Center 运行说明

## 后端

首次运行先在项目根目录复制 `.env.example` 为 `.env`，再按环境填写数据库和密钥配置。

在 `apps/server` 目录执行：

```powershell
python -m pip install -r requirements.txt
python -m alembic upgrade head
python init_admin.py --username admin --password "请替换为强密码"
python -m uvicorn app.main:app --reload --port 8000
```

正式环境必须设置 `ENVIRONMENT=production`、随机的 `SECRET_KEY`（至少 32 个字符）、`DATABASE_URL` 和 `UPLOAD_DIR`。生产启动时缺少密钥或附件目录会直接失败。数据库升级使用 `python -m alembic upgrade head`，执行前先完成备份。`python db_init.py` 仅保留给本地一次性初始化，在 `ENVIRONMENT=production` 时会拒绝执行。

存活检查为 `GET /health`，数据库就绪检查为 `GET /ready`。附件默认大小由 `MAX_UPLOAD_SIZE_MB` 控制，管理员在「存储配置」中保存的上限与扩展名白名单会写入数据库并立即作用于上传。

生产可用 Docker 一次拉起数据库、API 与 Nginx 反向代理：

```powershell
$env:SECRET_KEY = "至少32字符的随机密钥"
docker compose --profile full up -d --build
```

前端通过 80 端口访问，`/api/` 由 Nginx 转到 API。仅启动本地 MySQL 仍使用 `docker compose up -d db`。

## 前端

在 `apps/web` 目录执行：

```powershell
npm install
npm run build
npm run dev
```

开发环境默认通过 Vite 代理访问 `http://localhost:8000`。部署时使用 `VITE_API_BASE_URL` 配置 API 前缀；不要在业务代码中写死后端地址。

Windows 本地可用根目录 `start.bat`：先启动 Docker MySQL，再拉起前后端。`stop.bat` 关闭进程并停止数据库容器。

完整容器部署（MySQL + API + Nginx 反代）使用：

```powershell
$env:SECRET_KEY = "至少32字符的随机密钥"
docker compose --profile full up -d --build
```

## 测试

后端测试会自动使用隔离的 SQLite 内存数据库和临时附件目录，不会修改业务 MySQL 数据：

```powershell
cd apps/server
python -m pytest -q
```

前端类型检查和生产构建：

```powershell
cd apps/web
npm run build
```
