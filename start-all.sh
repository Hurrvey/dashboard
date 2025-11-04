#!/bin/bash
###############################################################################
# CODE996 数据看板 - 一键启动脚本（Linux/Mac）
# 自动启动后端和前端服务
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 日志目录与文件
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/startup-$(date '+%Y%m%d-%H%M%S').log"
touch "$LOG_FILE"

log_to_file() {
    local level="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $message" >> "$LOG_FILE"
}

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log_to_file "INFO" "$1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log_to_file "SUCCESS" "$1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log_to_file "WARNING" "$1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log_to_file "ERROR" "$1"
}

log_section() {
    log_info "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [STEP] $1" >> "$LOG_FILE"
}

run_and_log() {
    local description="$1"
    shift
    log_info "执行: $description"
    log_to_file "COMMAND" "$(printf '%q ' "$@")"
    if "$@" \
        2> >(while IFS= read -r line; do log_to_file "STDERR" "$line"; echo -e "${RED}[STDERR]${NC} $line"; done) | \
        while IFS= read -r line; do log_to_file "STDOUT" "$line"; echo "$line"; done
    then
        log_success "$description 完成"
    else
        log_error "$description 失败"
        exit 1
    fi
}

tail_backend_logs() {
    if [ -f "logs/backend.log" ]; then
        log_section "实时输出后端日志 (Ctrl+C 停止)"
        tail -f logs/backend.log &
        TAIL_PID=$!
    else
        TAIL_PID=""
    fi
}

stop_tail_logs() {
    if [ -n "$TAIL_PID" ]; then
        kill "$TAIL_PID" >/dev/null 2>&1 || true
    fi
}

# 打印标题
print_banner() {
    echo ""
    echo "================================================================"
    echo "  CODE996 数据看板 - 一键启动"
    echo "================================================================"
    echo ""
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        return 1
    fi
    return 0
}

# 检查依赖
check_dependencies() {
    log_section "检查依赖"
    
    local missing_deps=0
    
    if check_command python3; then
        log_info "Python版本: $(python3 --version 2>&1)"
    else
        log_error "Python3 未安装"
        missing_deps=1
    fi
    
    if check_command node; then
        log_info "Node 版本: $(node --version 2>&1)"
    else
        log_error "Node.js 未安装"
        missing_deps=1
    fi

    if check_command npm; then
        log_info "npm 版本: $(npm --version 2>&1)"
    else
        log_error "npm 未安装"
        missing_deps=1
    fi
    
    if [ $missing_deps -eq 1 ]; then
        log_error "缺少必要的依赖，请先安装"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 检查配置文件
check_config() {
    log_section "检查配置文件"
    
    if [ ! -f "projects.json" ]; then
        log_warning "projects.json 不存在，正在创建..."
        if [ -f "projects.json.example" ]; then
            cp projects.json.example projects.json
            log_success "已从 projects.json.example 创建 projects.json"
        else
            log_error "projects.json.example 不存在，无法创建配置"
            exit 1
        fi
    fi
    
    log_success "配置文件检查完成"
}

# 安装Python依赖
install_python_deps() {
    log_section "安装 Python 依赖"
    
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv >> "$LOG_FILE" 2>&1
        log_success "虚拟环境创建成功"
    fi
    
    source venv/bin/activate
    run_and_log "安装 Python 依赖" pip install -r requirements.txt
}

# 安装Node依赖
install_node_deps() {
    log_section "安装 Node 依赖"
    
    if [ ! -d "node_modules" ]; then
        run_and_log "安装 Node 依赖" npm install
    else
        log_success "Node依赖已存在"
    fi
}

# 创建必要的目录
create_dirs() {
    log_section "准备目录"
    
    mkdir -p logs
    mkdir -p repos
    
    log_success "目录创建完成"
}

# 启动后端服务
start_backend() {
    log_section "启动后端服务"
    source venv/bin/activate
    python run.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    log_info "后端日志: logs/backend.log"
    tail_backend_logs
    log_info "等待后端服务启动..."
    sleep 3
    if ps -p $BACKEND_PID > /dev/null; then
        log_success "后端服务启动成功 (PID: $BACKEND_PID)"
        echo $BACKEND_PID > .backend.pid
        max_retries=10
        retry=0
        while [ $retry -lt $max_retries ]; do
            if curl -s -w "HTTP %{http_code}\n" http://localhost:9970/api/dashboard/health >> "$LOG_FILE" 2>&1; then
                log_success "后端健康检查通过"
                break
            fi
            retry=$((retry+1))
            log_info "后端健康检查重试 ($retry/$max_retries)"
            sleep 1
        done
        if [ $retry -eq $max_retries ]; then
            log_warning "后端健康检查超时，但服务可能正在启动中"
        fi
    else
        stop_tail_logs
        log_error "后端服务启动失败"
        exit 1
    fi
}

# 启动前端服务
start_frontend() {
    log_section "启动前端服务"
    npm run dev > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    log_info "前端日志: logs/frontend.log"
    log_info "等待前端服务启动..."
    sleep 3
    if ps -p $FRONTEND_PID > /dev/null; then
        log_success "前端服务启动成功 (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > .frontend.pid
    else
        log_error "前端服务启动失败"
        stop_tail_logs
        exit 1
    fi
}

# 显示访问信息
show_info() {
    echo ""
    echo "================================================================"
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo "================================================================"
    echo ""
    echo "📊 数据看板地址:"
    echo "   http://localhost:3801/?projects=test1,test2"
    echo ""
    echo "🔧 后端API地址:"
    echo "   http://localhost:9970"
    echo ""
    echo "📝 日志文件:"
    echo "   后端: logs/backend.log"
    echo "   前端: logs/frontend.log"
    echo "   启动: $LOG_FILE"
    echo ""
    echo "🛑 停止服务:"
    echo "   ./stop-all.sh"
    echo ""
    echo "================================================================"
    echo ""
}

# 主函数
main() {
    print_banner
    log_info "启动脚本初始化完成"
    log_info "日志文件: $LOG_FILE"
    log_info "工作目录: $PROJECT_ROOT"
    check_dependencies
    check_config
    create_dirs
    install_python_deps
    install_node_deps
    start_backend
    start_frontend
    show_info
    log_success "所有服务已启动！详情请查看 $LOG_FILE"
    stop_tail_logs
}

main

