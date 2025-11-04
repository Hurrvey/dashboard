@echo off
REM ###############################################################################
REM CODE996 数据看板 - 一键诊断脚本（Windows）
REM ###############################################################################

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "NC=[0m"

set issues=0
set warnings=0

echo.
echo ================================================================
echo   %PURPLE%CODE996 数据看板 - 系统诊断%NC%
echo ================================================================
echo.

REM 1. 检查依赖
echo %PURPLE%【1/8】检查系统依赖%NC%
echo ----------------------------------------

where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do set pyver=%%v
    echo %GREEN%[✓]%NC% Python: !pyver!
) else (
    echo %RED%[✗]%NC% Python 未安装
    set /a issues+=1
)

where node >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('node --version 2^>^&1') do set nodever=%%v
    echo %GREEN%[✓]%NC% Node.js: !nodever!
) else (
    echo %RED%[✗]%NC% Node.js 未安装
    set /a issues+=1
)

where git >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('git --version 2^>^&1') do set gitver=%%v
    echo %GREEN%[✓]%NC% Git: !gitver!
) else (
    echo %RED%[✗]%NC% Git 未安装
    set /a issues+=1
)

where curl >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[✓]%NC% curl: 已安装
) else (
    echo %YELLOW%[!]%NC% curl 未安装（部分功能可能受限）
    set /a warnings+=1
)

echo.

REM 2. 检查配置文件
echo %PURPLE%【2/8】检查配置文件%NC%
echo ----------------------------------------

if exist "projects.json" (
    echo %GREEN%[✓]%NC% projects.json 存在
) else (
    echo %YELLOW%[!]%NC% projects.json 不存在
    set /a warnings+=1
)

if exist "requirements.txt" (
    echo %GREEN%[✓]%NC% requirements.txt 存在
) else (
    echo %RED%[✗]%NC% requirements.txt 不存在
    set /a issues+=1
)

if exist "package.json" (
    echo %GREEN%[✓]%NC% package.json 存在
) else (
    echo %RED%[✗]%NC% package.json 不存在
    set /a issues+=1
)

echo.

REM 3. 检查Python环境
echo %PURPLE%【3/8】检查Python环境%NC%
echo ----------------------------------------

if exist "venv" (
    echo %GREEN%[✓]%NC% Python虚拟环境已创建
) else (
    echo %YELLOW%[!]%NC% Python虚拟环境未创建
    set /a warnings+=1
)

echo.

REM 4. 检查Node环境
echo %PURPLE%【4/8】检查Node环境%NC%
echo ----------------------------------------

if exist "node_modules" (
    echo %GREEN%[✓]%NC% Node依赖已安装
    
    if exist "node_modules\vue" (
        echo %GREEN%[✓]%NC% Vue 已安装
    ) else (
        echo %RED%[✗]%NC% Vue 未安装
        set /a issues+=1
    )
    
    if exist "node_modules\chart.xkcd" (
        echo %GREEN%[✓]%NC% chart.xkcd 已安装
    ) else (
        echo %RED%[✗]%NC% chart.xkcd 未安装
        set /a issues+=1
    )
) else (
    echo %YELLOW%[!]%NC% Node依赖未安装
    set /a warnings+=1
)

echo.

REM 5. 检查服务状态
echo %PURPLE%【5/8】检查服务状态%NC%
echo ----------------------------------------

curl -sf http://localhost:9970/api/dashboard/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[✓]%NC% 后端服务运行中 (端口 9970)
) else (
    echo %YELLOW%[!]%NC% 后端服务未运行或无法访问
    set /a warnings+=1
)

curl -sf http://localhost:3801 >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[✓]%NC% 前端服务运行中 (端口 3801)
) else (
    echo %YELLOW%[!]%NC% 前端服务未运行或无法访问
    set /a warnings+=1
)

echo.

REM 6. 检查目录结构
echo %PURPLE%【6/8】检查目录结构%NC%
echo ----------------------------------------

if exist "app" (
    echo %GREEN%[✓]%NC% app\ 目录存在
) else (
    echo %RED%[✗]%NC% app\ 目录不存在
    set /a issues+=1
)

if exist "src" (
    echo %GREEN%[✓]%NC% src\ 目录存在
) else (
    echo %RED%[✗]%NC% src\ 目录不存在
    set /a issues+=1
)

if exist "logs" (
    echo %GREEN%[✓]%NC% logs\ 目录存在
) else (
    echo %YELLOW%[!]%NC% logs\ 目录不存在
    set /a warnings+=1
)

if exist "repos" (
    echo %GREEN%[✓]%NC% repos\ 目录存在
    for /f %%i in ('dir /b /ad repos 2^>nul ^| find /c /v ""') do set repo_count=%%i
    echo %BLUE%[INFO]%NC% 已克隆的仓库数: !repo_count!
) else (
    echo %YELLOW%[!]%NC% repos\ 目录不存在
    set /a warnings+=1
)

echo.

REM 7. 测试 Git 连接
echo %PURPLE%【7/8】测试 Git 连接%NC%
echo ----------------------------------------

echo %BLUE%[INFO]%NC% 测试 GitHub 连接...
git ls-remote https://github.com/Hurrvey/asr-ws-ptt HEAD >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[✓]%NC% GitHub 连接正常
) else (
    echo %YELLOW%[!]%NC% GitHub 连接失败（网络问题或代理设置）
    set /a warnings+=1
)

echo.

REM 8. 测试 API 接口
echo %PURPLE%【8/8】测试 API 接口%NC%
echo ----------------------------------------

curl -sf http://localhost:9970/api/dashboard/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %BLUE%[INFO]%NC% 测试健康检查接口...
    curl -s http://localhost:9970/api/dashboard/health
    echo.
    echo %GREEN%[✓]%NC% 健康检查接口正常
) else (
    echo %YELLOW%[!]%NC% 健康检查接口异常（服务未启动）
    set /a warnings+=1
)

echo.

REM 生成报告
echo ================================================================
echo   %PURPLE%诊断报告%NC%
echo ================================================================
echo.

if %issues% equ 0 (
    if %warnings% equ 0 (
        echo %GREEN%✅ 系统状态良好，无问题发现！%NC%
    ) else (
        echo %YELLOW%⚠️  发现 %warnings% 个警告（非严重问题）%NC%
    )
) else (
    echo %RED%❌ 发现 %issues% 个错误，需要修复%NC%
    if %warnings% gtr 0 (
        echo %YELLOW%   同时发现 %warnings% 个警告%NC%
    )
)

echo.
echo 下一步建议:

if %issues% gtr 0 (
    echo   1. 根据上述错误提示修复问题
    echo   2. 安装缺失的依赖
    echo   3. 重新运行此诊断脚本
) else if %warnings% gtr 0 (
    echo   1. 警告可以忽略，不影响核心功能
    echo   2. 如需完整功能，可解决警告项
) else (
    echo   ✅ 系统已就绪，可以启动服务
    echo   1. 运行: start-all.bat
    echo   2. 访问: http://localhost:3801/?projects=test1,test2
)

echo.
echo 详细故障排查请参考: TROUBLESHOOTING.md
echo.
pause

