@echo off
REM ###############################################################################
REM CODE996 数据看板 - 停止脚本（Windows）
REM ###############################################################################

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ================================================================
echo   CODE996 数据看板 - 停止服务
echo ================================================================
echo.

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM 停止后端服务
echo [INFO] 停止后端服务...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":9970" ^| find "LISTENING"') do (
    set BACKEND_PID=%%a
)

if defined BACKEND_PID (
    taskkill /F /PID !BACKEND_PID! >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[SUCCESS]%NC% 后端服务已停止 (PID: !BACKEND_PID!)
    ) else (
        echo %YELLOW%[WARNING]%NC% 无法停止后端服务
    )
) else (
    echo %YELLOW%[WARNING]%NC% 后端服务未运行
)

REM 停止前端服务
echo [INFO] 停止前端服务...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3801" ^| find "LISTENING"') do (
    set FRONTEND_PID=%%a
)

if defined FRONTEND_PID (
    taskkill /F /PID !FRONTEND_PID! >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[SUCCESS]%NC% 前端服务已停止 (PID: !FRONTEND_PID!)
    ) else (
        echo %YELLOW%[WARNING]%NC% 无法停止前端服务
    )
) else (
    echo %YELLOW%[WARNING]%NC% 前端服务未运行
)

REM 关闭可能的命令窗口
taskkill /FI "WindowTitle eq CODE996-Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq CODE996-Frontend*" /F >nul 2>&1

echo.
echo %GREEN%[SUCCESS]%NC% 所有服务已停止
echo.
pause

