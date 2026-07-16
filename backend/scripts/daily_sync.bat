@echo off
REM ============================================
REM  workbuddy 专题 - 每日同步任务
REM  每天 02:00 自动跑一次
REM ============================================

setlocal
set WORKBUDDY_HOME=D:\workbuddy专题\backend
set PYTHON_EXE=python
set URL_FILE=%WORKBUDDY_HOME%\data\seed_urls.txt
set LOG_DIR=%WORKBUDDY_HOME%\logs
set LOG_FILE=%LOG_DIR%\sync_%date:~0,4%%date:~5,2%%date:~8,2%.log

REM 确认日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 切到 backend 目录跑模块
cd /d "%WORKBUDDY_HOME%"

echo === workbuddy daily sync === > "%LOG_FILE%"
echo 时间: %date% %time% >> "%LOG_FILE%"

%PYTHON_EXE% -m app.scheduler.daily_sync --file "%URL_FILE%" --sleep 3.0 --keyword "daily" >> "%LOG_FILE%" 2>&1

echo === 完成 %date% %time% === >> "%LOG_FILE%"

endlocal
