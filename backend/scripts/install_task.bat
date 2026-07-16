@echo off
REM ============================================
REM  安装 WorkBuddy 每日同步任务
REM  请右键此文件 → "以管理员身份运行"
REM ============================================

echo.
echo === 正在注册 WorkBuddy 每日同步任务 (02:00) ===
echo.

schtasks /Create ^
    /TN "WorkBuddyDailySync" ^
    /TR "D:\workbuddy专题\backend\scripts\daily_sync.bat" ^
    /SC DAILY ^
    /ST 02:00 ^
    /RL HIGHEST ^
    /F

if %errorlevel% equ 0 (
    echo.
    echo === 安装成功！ ===
    echo 任务名: WorkBuddyDailySync
    echo 执行时间: 每天 02:00
    echo 脚本: D:\workbuddy专题\backend\scripts\daily_sync.bat
    echo 日志: D:\workbuddy专题\backend\logs\sync_YYYYMMDD.log
    echo.
    echo 验证: schtasks /Query /TN "WorkBuddyDailySync"
    echo 手动跑: schtasks /Run /TN "WorkBuddyDailySync"
    echo 删除: schtasks /Delete /TN "WorkBuddyDailySync" /F
    echo.
) else (
    echo.
    echo === 安装失败！请以管理员身份重新运行。 ===
    echo.
)

pause
