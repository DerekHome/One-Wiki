@echo off
chcp 65001 >nul
title 企业知识中心停止器
color 0C

echo ========================================================
echo           企业知识中心 (Knowledge Hub) 停止服务
echo ========================================================
echo.

set "ROOT_DIR=%~dp0"

echo [1/3] 正在关闭前后端窗口...
taskkill /FI "WINDOWTITLE eq 【后端】企业知识中心 - FastAPI (8000)*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq 【前端】企业知识中心 - Web (3000)*" /T /F >nul 2>&1

echo [2/3] 正在释放 8000 / 3000 端口...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING"') do taskkill /F /PID %%P >nul 2>&1
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":3000 .*LISTENING"') do taskkill /F /PID %%P >nul 2>&1

echo [3/3] 正在停止 MySQL 容器（数据卷保留）...
cd /d "%ROOT_DIR%"
docker compose stop db >nul 2>&1
if errorlevel 1 docker-compose stop db >nul 2>&1

echo.
echo ========================================================
echo [完成] 服务已停止。再次启动请运行 start.bat
echo ========================================================
pause
