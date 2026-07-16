@echo off
chcp 65001 >nul
echo ================================
echo   workbuddy 专题 - 前端启动
echo ================================

cd /d %~dp0

if not exist "node_modules" (
    echo 安装依赖...
    call npm install --registry=https://registry.npmmirror.com
)

echo 启动 Vite 开发服务器...
call npm run dev
