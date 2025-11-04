@echo off
chcp 65001 > nul

echo ========================================
echo CODE996 Dashboard Backend (标准版)
echo ========================================
echo.

REM 检查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)

echo ✓ Python 已安装

REM 创建虚拟环境
if not exist "venv" (
    echo.
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo ✓ 虚拟环境已激活

REM 安装依赖
echo.
echo 安装依赖...
pip install -q -r requirements.txt

echo ✓ 依赖已安装

REM 创建目录
if not exist "repos" mkdir repos
if not exist "logs" mkdir logs

echo ✓ 目录已创建

REM 复制环境变量文件
if not exist ".env" (
    copy .env.example .env
    echo ✓ 已创建 .env 文件
)

REM 启动服务
echo.
echo ========================================
echo 启动服务...
echo ========================================
echo.

python run.py

pause
