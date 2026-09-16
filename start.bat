@echo off
chcp 65001 >nul
title 企业知识中心一键启动器
color 0A

echo ========================================================
echo           企业知识中心 (Knowledge Hub) 一键启动
echo ========================================================
echo.

set "ROOT_DIR=%~dp0"
set "SERVER_DIR=%ROOT_DIR%apps\server"
set "WEB_DIR=%ROOT_DIR%apps\web"

:: 优先检测可用 Python 解释器
set "PY_CMD=python"
if exist "C:\Users\admin\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set "PY_CMD=C:\Users\admin\AppData\Local\Python\pythoncore-3.14-64\python.exe"
)

echo [1/4] 正在启动 MySQL (Docker, 端口 3306)...
cd /d "%ROOT_DIR%"
docker compose up -d db
if errorlevel 1 (
    echo [提示] docker compose 不可用，尝试 docker-compose...
    docker-compose up -d db
)
if errorlevel 1 (
    echo [警告] 未能启动 MySQL 容器。请确认 Docker Desktop 已运行。后端仍会继续启动。
) else (
    echo [成功] MySQL 容器已启动: localhost:3306
    echo [等待] 给 MySQL 几秒完成就绪...
    timeout /t 5 /nobreak >nul
)

echo [2/4] 正在启动后端服务 (FastAPI 端口: 8000)...
start "【后端】企业知识中心 - FastAPI (8000)" cmd /k "cd /d "%SERVER_DIR%" && "%PY_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [3/4] 正在启动前端服务 (Vue3 + Vite 端口: 3000)...
start "【前端】企业知识中心 - Web (3000)" cmd /k "cd /d "%WEB_DIR%" && npm run dev"

echo [4/4] 正在准备打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================================
echo [成功] 数据库与前后端服务已在后台启动！
echo.
echo  - 前端地址: http://localhost:3000
echo  - 后端接口: http://localhost:8000/docs
echo  - 数据库:   MySQL 8 @ localhost:3306
echo.
echo 如需关闭服务，请直接运行 stop.bat
echo ========================================================
timeout /t 5 >nul
exit
