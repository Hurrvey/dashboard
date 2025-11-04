#!/bin/bash

echo "========================================"
echo "CODE996 Dashboard Backend (标准版)"
echo "========================================"

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建必要目录
mkdir -p repos logs

# 复制环境变量文件
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "已创建 .env 文件"
fi

# 启动服务
echo ""
echo "========================================"
echo "启动服务..."
echo "========================================"

python run.py
