@echo off
REM ###############################################################################
REM CODE996 数据看板 - 一键启动脚本（Windows）
REM 自动启动后端和前端服务
REM ###############################################################################

setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
set "PYTHON_BIN="
if exist "%ROOT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_BIN=%ROOT_DIR%venv\Scripts\python.exe"
) else (
    for /f "delims=" %%p in ('where python 2^>nul') do (
        if not defined PYTHON_BIN set "PYTHON_BIN=%%~p"
    )
)
if not defined PYTHON_BIN (
    set "PYTHON_BIN=python"
)
call :log INFO "使用 Python: %PYTHON_BIN%"

if not exist "logs" mkdir logs
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TIMESTAMP=%%i"
set "LOG_FILE=logs\startup-%TIMESTAMP%.log"
set "BACKEND_LOG=logs\backend.log"
type nul > "%LOG_FILE%"
if not exist "%BACKEND_LOG%" type nul > "%BACKEND_LOG%"

call :log INFO "启动日志文件: %LOG_FILE%"
call :log INFO "工作目录: %cd%"

echo.
echo ================================================================
echo   CODE996 数据看板 - 一键启动
echo ================================================================
echo.

call :run_cmd "检查 Python" "where python"
if %errorlevel% neq 0 goto :fail_dep
for /f "delims=" %%i in ('python --version 2^>^&1') do set "PY_VERSION=%%i"
call :log INFO "Python 版本: !PY_VERSION!"

call :run_cmd "检查 Node" "where node"
if %errorlevel% neq 0 goto :fail_dep
for /f "delims=" %%i in ('node --version 2^>^&1') do set "NODE_VERSION=%%i"
call :log INFO "Node 版本: !NODE_VERSION!"

call :run_cmd "检查 npm" "where npm"
if %errorlevel% neq 0 goto :fail_dep
for /f "delims=" %%i in ('npm --version 2^>^&1') do set "NPM_VERSION=%%i"
call :log INFO "npm 版本: !NPM_VERSION!"

call :log SUCCESS "依赖检查通过"
echo.

call :log INFO "检查配置文件..."
if not exist "projects.json" (
    call :log WARNING "projects.json 不存在，正在从示例创建..."
    if exist "projects.json.example" (
        copy projects.json.example projects.json >nul
        call :log SUCCESS "已从 projects.json.example 创建 projects.json"
    ) else (
        call :log ERROR "projects.json.example 不存在，无法创建配置"
        goto :fail
    )
)
call :log SUCCESS "配置文件检查完成"
echo.

call :log INFO "创建必要目录..."
if not exist "repos" mkdir repos
call :log SUCCESS "目录检查完成"
echo.

call :log INFO "检查 Python 依赖..."
if not exist "venv" (
    call :run_cmd "创建 Python 虚拟环境" "python -m venv venv"
    if %errorlevel% neq 0 goto :fail
)
call :log INFO "安装 Python 依赖..."
call :log COMMAND ""%PYTHON_BIN%" -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/"
cmd /c ""%PYTHON_BIN%" -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/"
if errorlevel 1 (
    call :log ERROR "Python 依赖安装失败"
    goto :fail
)
call :log SUCCESS "Python 依赖已安装"
if %errorlevel% neq 0 goto :fail

echo.
call :log INFO "检查 Node 依赖..."
if not exist "node_modules" (
    call :run_cmd "安装 Node 依赖" "npm install"
    if %errorlevel% neq 0 goto :fail
) else (
    call :log SUCCESS "Node 依赖已存在"
)

set "RAW_PROJECTS="
set "TMP_OUTPUT=%TEMP%\code996_projects_%RANDOM%%RANDOM%.txt"
cmd /c ""%PYTHON_BIN%" "%ROOT_DIR%scripts\get_default_projects.py" > "%TMP_OUTPUT%" 2>nul"
if exist "%TMP_OUTPUT%" (
    set /p RAW_PROJECTS=<"%TMP_OUTPUT%"
    del "%TMP_OUTPUT%"
)
if defined RAW_PROJECTS (
    call :log INFO "已加载默认项目: %RAW_PROJECTS%"
) else (
    call :log WARNING "DEFAULT_PROJECTS 未配置或为空，将使用示例项目 test1,test2"
    set "RAW_PROJECTS=test1,test2"
)

set "PROJECT_ID_QUERY="

call :log INFO "启动后端服务..."
start "CODE996-Backend" /b powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_backend.ps1" -ProjectRoot "%cd%"
call :log INFO "后端日志输出将实时显示在当前窗口"
call :log INFO "等待后端服务启动..."
call :sleep 2

set "HEALTH_STATUS="
set "BACKEND_READY=0"
set "HEALTH_MAX_RETRIES=30"
for /L %%i in (1,1,!HEALTH_MAX_RETRIES!) do (
    set "HEALTH_STATUS=ERR"
    for /f "tokens=2 delims= " %%j in ('curl -s -I http://localhost:9970/api/dashboard/health 2^>nul ^| findstr /b "HTTP/"') do set "HEALTH_STATUS=%%j"
    if "!HEALTH_STATUS!"=="200" (
        set "BACKEND_READY=1"
        call :log SUCCESS "健康检查响应: 200"
        goto :backend_ready
    ) else (
        call :log INFO "健康检查响应: !HEALTH_STATUS!"
    )
    call :sleep 2
)

:backend_ready
if "!BACKEND_READY!"=="1" (
    call :log SUCCESS "后端服务启动成功"
) else (
    call :log WARNING "后端健康检查失败，但服务可能正在启动中"
)

if defined RAW_PROJECTS (
    call :log INFO "预加载默认项目数据..."
    curl -s "http://localhost:9970/api/dashboard/summary?projects=%RAW_PROJECTS%" >nul 2>&1
    curl -s "http://localhost:9970/api/dashboard/contributors?projects=%RAW_PROJECTS%" >nul 2>&1
)

set "TMP_OUTPUT=%TEMP%\code996_project_ids_%RANDOM%%RANDOM%.txt"
cmd /c ""%PYTHON_BIN%" "%ROOT_DIR%scripts\get_project_ids.py" --projects "%RAW_PROJECTS%" > "%TMP_OUTPUT%" 2>nul"
if exist "%TMP_OUTPUT%" (
    set /p PROJECT_ID_QUERY=<"%TMP_OUTPUT%"
    del "%TMP_OUTPUT%"
)

if defined PROJECT_ID_QUERY (
    call :log INFO "默认项目已转换为 ID: %PROJECT_ID_QUERY%"
) else (
    set "PROJECT_ID_QUERY=%RAW_PROJECTS%"
    call :log WARNING "无法转换项目 ID，使用原始值: %PROJECT_ID_QUERY%"
)

call :log INFO "启动前端服务..."
start "CODE996-Frontend" /min cmd /c "npm run dev > logs\frontend.log 2>&1"
call :log INFO "等待前端服务启动..."
call :sleep 2

set "FRONTEND_READY=0"
for /L %%i in (1,1,15) do (
    powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://localhost:3801' -UseBasicParsing -Method Head | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        set "FRONTEND_READY=1"
        goto :frontend_ready
    )
    call :sleep 2
)

:frontend_ready
if "!FRONTEND_READY!"=="1" (
    call :log SUCCESS "前端服务可用"
) else (
    call :log WARNING "前端服务未确认启动，仍尝试继续"
)
call :log SUCCESS "前端服务启动命令已执行"

echo.
call :log SUCCESS "所有服务已启动，启动日志: %LOG_FILE%"
echo ================================================================
echo   CODE996 数据看板 - 服务信息
echo ================================================================
echo.
set "DASHBOARD_URL=http://localhost:3801/dashboard"
echo 📊 数据看板地址:
echo    %DASHBOARD_URL%
echo.
echo 🔧 后端 API 地址:
echo    http://localhost:9970
echo.
echo 📝 日志文件:
echo    后端: logs\backend.log
echo    前端: logs\frontend.log
echo    启动: %LOG_FILE%
echo.
echo 🛑 停止服务:
echo    运行 stop-all.bat 或关闭对应的命令窗口
echo.
echo ================================================================
echo.
echo 提示: 将尝试自动打开浏览器...
call :log INFO "正在打开仪表盘: %DASHBOARD_URL%"
powershell -NoProfile -Command "try { Start-Process '%DASHBOARD_URL%' } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    call :log SUCCESS "浏览器已打开"
) else (
    call :log WARNING "自动打开失败，请手动访问: %DASHBOARD_URL%"
)

call :log INFO "启动记录已写入 %LOG_FILE%"
echo.
echo 按任意键退出...
pause >nul
exit /b 0

:fail_dep
call :log ERROR "依赖检查失败"
pause
exit /b 1

:fail
call :log ERROR "启动失败，详情见 %LOG_FILE%"
pause
exit /b 1

:run_cmd
setlocal EnableExtensions EnableDelayedExpansion
set "DESC=%~1"
set "CMD=%~2"
set "LOG_CMD=!CMD:^=^^!"
set "LOG_CMD=!LOG_CMD:&=^&!"
set "LOG_CMD=!LOG_CMD:|=^|!"
set "LOG_CMD=!LOG_CMD:<=^<!"
set "LOG_CMD=!LOG_CMD:>=^>!"
call :log INFO "执行: %DESC%"
call :log COMMAND "%LOG_CMD%"
set "TMP_OUT=%TEMP%\cmd_output_%RANDOM%%RANDOM%.log"
cmd /c "%CMD%" > "%TMP_OUT%" 2>&1
set "ERR=%ERRORLEVEL%"
for /f "usebackq delims=" %%i in ("%TMP_OUT%") do (
    echo %%i
    >> "%LOG_FILE%" echo %%i
)
del "%TMP_OUT%" >nul 2>&1
if %ERR%==0 (
    call :log SUCCESS "%DESC% 完成"
) else (
    call :log ERROR "%DESC% 失败 (exit=%ERR%)"
)
endlocal & exit /b %ERR%

:log
setlocal EnableExtensions EnableDelayedExpansion
set "LEVEL=%~1"
set "MESSAGE=%~2"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set "NOW=%%i"
echo [%LEVEL%] %MESSAGE%
>> "%LOG_FILE%" echo %NOW% [%LEVEL%] %MESSAGE%
endlocal & exit /b 0

:sleep
powershell -NoProfile -Command "Start-Sleep -Seconds %1"
exit /b 0

