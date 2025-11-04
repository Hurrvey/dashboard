#!/bin/bash
###############################################################################
# CODE996 数据看板 - 一键诊断脚本
# 自动检测并诊断常见问题
###############################################################################

set +e  # 允许命令失败，继续执行

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "================================================================"
echo -e "  ${PURPLE}CODE996 数据看板 - 系统诊断${NC}"
echo "================================================================"
echo ""

# 诊断计数
issues=0
warnings=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    warnings=$((warnings + 1))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    issues=$((issues + 1))
}

# 1. 检查依赖
echo -e "${PURPLE}【1/8】检查系统依赖${NC}"
echo "----------------------------------------"

if command -v python3 &> /dev/null; then
    version=$(python3 --version)
    log_success "Python3: $version"
else
    log_error "Python3 未安装"
fi

if command -v node &> /dev/null; then
    version=$(node --version)
    log_success "Node.js: $version"
else
    log_error "Node.js 未安装"
fi

if command -v git &> /dev/null; then
    version=$(git --version)
    log_success "Git: $version"
else
    log_error "Git 未安装"
fi

if command -v curl &> /dev/null; then
    log_success "curl: 已安装"
else
    log_warning "curl 未安装（部分功能可能受限）"
fi

echo ""

# 2. 检查配置文件
echo -e "${PURPLE}【2/8】检查配置文件${NC}"
echo "----------------------------------------"

if [ -f "projects.json" ]; then
    log_success "projects.json 存在"
    project_count=$(python3 -c "import json; data=json.load(open('projects.json')); print(len([k for k in data if not k.startswith('_')]))" 2>/dev/null || echo "0")
    log_info "配置的项目数: $project_count"
else
    log_warning "projects.json 不存在"
fi

if [ -f "requirements.txt" ]; then
    log_success "requirements.txt 存在"
else
    log_error "requirements.txt 不存在"
fi

if [ -f "package.json" ]; then
    log_success "package.json 存在"
else
    log_error "package.json 不存在"
fi

echo ""

# 3. 检查Python环境
echo -e "${PURPLE}【3/8】检查Python环境${NC}"
echo "----------------------------------------"

if [ -d "venv" ]; then
    log_success "Python虚拟环境已创建"
    source venv/bin/activate
    
    # 检查关键依赖
    if python -c "import flask" 2>/dev/null; then
        log_success "Flask 已安装"
    else
        log_error "Flask 未安装"
    fi
    
    if python -c "import git" 2>/dev/null; then
        log_success "GitPython 已安装"
    else
        log_error "GitPython 未安装"
    fi
else
    log_warning "Python虚拟环境未创建"
fi

echo ""

# 4. 检查Node环境
echo -e "${PURPLE}【4/8】检查Node环境${NC}"
echo "----------------------------------------"

if [ -d "node_modules" ]; then
    log_success "Node依赖已安装"
    
    if [ -d "node_modules/vue" ]; then
        log_success "Vue 已安装"
    else
        log_error "Vue 未安装"
    fi
    
    if [ -d "node_modules/chart.xkcd" ]; then
        log_success "chart.xkcd 已安装"
    else
        log_error "chart.xkcd 未安装"
    fi
else
    log_warning "Node依赖未安装"
fi

echo ""

# 5. 检查服务状态
echo -e "${PURPLE}【5/8】检查服务状态${NC}"
echo "----------------------------------------"

if curl -sf http://localhost:9970/api/dashboard/health > /dev/null 2>&1; then
    log_success "后端服务运行中 (端口 9970)"
else
    log_warning "后端服务未运行或无法访问"
fi

if curl -sf http://localhost:3801 > /dev/null 2>&1; then
    log_success "前端服务运行中 (端口 3801)"
else
    log_warning "前端服务未运行或无法访问"
fi

if command -v redis-cli &> /dev/null && redis-cli ping > /dev/null 2>&1; then
    log_success "Redis 运行中（可选服务）"
else
    log_info "Redis 未运行（使用内存缓存）"
fi

echo ""

# 6. 检查目录结构
echo -e "${PURPLE}【6/8】检查目录结构${NC}"
echo "----------------------------------------"

if [ -d "app" ]; then
    log_success "app/ 目录存在"
else
    log_error "app/ 目录不存在"
fi

if [ -d "src" ]; then
    log_success "src/ 目录存在"
else
    log_error "src/ 目录不存在"
fi

if [ -d "logs" ]; then
    log_success "logs/ 目录存在"
    log_count=$(ls -1 logs/ 2>/dev/null | wc -l)
    log_info "日志文件数: $log_count"
else
    log_warning "logs/ 目录不存在"
fi

if [ -d "repos" ]; then
    log_success "repos/ 目录存在"
    repo_count=$(ls -1 repos/ 2>/dev/null | wc -l)
    log_info "已克隆的仓库数: $repo_count"
    
    if [ $repo_count -gt 0 ]; then
        echo -e "   ${BLUE}已克隆的仓库:${NC}"
        ls -1 repos/ | head -5 | while read repo; do
            echo "   - $repo"
        done
    fi
else
    log_warning "repos/ 目录不存在"
fi

echo ""

# 7. 测试 Git 连接
echo -e "${PURPLE}【7/8】测试 Git 连接${NC}"
echo "----------------------------------------"

log_info "测试 GitHub 连接..."
if git ls-remote https://github.com/Hurrvey/asr-ws-ptt HEAD > /dev/null 2>&1; then
    log_success "GitHub 连接正常"
else
    log_warning "GitHub 连接失败（网络问题或代理设置）"
fi

echo ""

# 8. 测试 API 接口
echo -e "${PURPLE}【8/8】测试 API 接口${NC}"
echo "----------------------------------------"

if curl -sf http://localhost:9970/api/dashboard/health > /dev/null 2>&1; then
    log_info "测试健康检查接口..."
    response=$(curl -s http://localhost:9970/api/dashboard/health)
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    log_success "健康检查接口正常"
else
    log_error "健康检查接口异常"
fi

echo ""

# 生成报告
echo "================================================================"
echo -e "  ${PURPLE}诊断报告${NC}"
echo "================================================================"
echo ""

if [ $issues -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✅ 系统状态良好，无问题发现！${NC}"
elif [ $issues -eq 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $warnings 个警告（非严重问题）${NC}"
else
    echo -e "${RED}❌ 发现 $issues 个错误，需要修复${NC}"
    if [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}   同时发现 $warnings 个警告${NC}"
    fi
fi

echo ""
echo "下一步建议:"

if [ $issues -gt 0 ]; then
    echo "  1. 根据上述错误提示修复问题"
    echo "  2. 安装缺失的依赖"
    echo "  3. 重新运行此诊断脚本"
elif [ $warnings -gt 0 ]; then
    echo "  1. 警告可以忽略，不影响核心功能"
    echo "  2. 如需完整功能，可解决警告项"
else
    echo "  ✅ 系统已就绪，可以启动服务"
    echo "  1. 运行: ./start-all.sh"
    echo "  2. 访问: http://localhost:3801/?projects=test1,test2"
fi

echo ""
echo "详细故障排查请参考: TROUBLESHOOTING.md"
echo ""

