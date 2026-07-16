@echo off
chcp 65001 >nul
echo ================================
echo   workbuddy 专题 - 一键启动
echo ================================
echo.
echo 将同时启动后端 (8000) 和前端 (5173)
echo.

REM 启动后端
start "workbuddy-backend" cmd /k "cd /d %~dp0backend && start.bat"

REM 等待 3 秒再启动前端
timeout /t 3 /nobreak >nul

REM 启动前端
start "workbuddy-frontend" cmd /k "cd /d %~dp0frontend && start.bat"

echo.
echo 启动完成！
echo 后端 API 文档: http://127.0.0.1:8000/docs
echo 前端页面:     http://127.0.0.1:5173
echo.
pause
