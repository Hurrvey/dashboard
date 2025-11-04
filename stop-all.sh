#!/bin/bash
###############################################################################
# CODE996 数据看板 - 停止脚本（Linux/Mac）
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo ""
echo "================================================================"
echo "  CODE996 数据看板 - 停止服务"
echo "================================================================"
echo ""

# 停止后端
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        log_info "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        log_success "后端服务已停止"
    else
        log_warning "后端服务未运行"
    fi
    rm .backend.pid
else
    log_warning "未找到后端PID文件"
    # 尝试通过端口查找并停止
    BACKEND_PID=$(lsof -ti:9970)
    if [ ! -z "$BACKEND_PID" ]; then
        log_info "找到运行在9970端口的进程 (PID: $BACKEND_PID)，正在停止..."
        kill $BACKEND_PID
        log_success "后端服务已停止"
    fi
fi

# 停止前端
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        log_info "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        log_success "前端服务已停止"
    else
        log_warning "前端服务未运行"
    fi
    rm .frontend.pid
else
    log_warning "未找到前端PID文件"
    # 尝试通过端口查找并停止
    FRONTEND_PID=$(lsof -ti:3801)
    if [ ! -z "$FRONTEND_PID" ]; then
        log_info "找到运行在3801端口的进程 (PID: $FRONTEND_PID)，正在停止..."
        kill $FRONTEND_PID
        log_success "前端服务已停止"
    fi
fi

echo ""
log_success "所有服务已停止"
echo ""

