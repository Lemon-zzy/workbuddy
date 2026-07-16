@echo off
chcp 65001 >nul
echo ================================
echo   workbuddy 专题 - 后端启动
echo ================================

cd /d %~dp0

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

REM 复制 .env
if not exist ".env" (
    copy .env.example .env
    echo 已生成 .env，请填入你的知乎 AccessKey
)

REM 启动
echo 启动后端服务...
python -m app.main
