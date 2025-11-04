#!/bin/bash
###############################################################################
# CODE996 数据看板 - 健康检查脚本
###############################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKEND_URL="${BACKEND_URL:-http://localhost:9970}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3801}"

check_service() {
    local name=$1
    local url=$2
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name 运行正常"
        return 0
    else
        echo -e "${RED}✗${NC} $name 无法访问"
        return 1
    fi
}

echo ""
echo "=========================================="
echo "  CODE996 数据看板 - 健康检查"
echo "=========================================="
echo ""

failed=0

# 检查后端
if ! check_service "后端服务" "$BACKEND_URL/api/dashboard/health"; then
    failed=1
fi

# 检查前端
if ! check_service "前端服务" "$FRONTEND_URL"; then
    failed=1
fi

# 检查Redis（可选）
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis 运行正常"
    else
        echo -e "${YELLOW}⚠${NC} Redis 未运行（可选服务）"
    fi
fi

echo ""
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}所有服务运行正常${NC}"
    exit 0
else
    echo -e "${RED}部分服务异常${NC}"
    exit 1
fi

