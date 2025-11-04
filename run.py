#!/usr/bin/env python
"""
CODE996 数据看板后端服务启动脚本
推荐使用此脚本启动服务
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.settings import Config

if __name__ == '__main__':
    print("=" * 60)
    print("CODE996 数据看板后端服务")
    print("=" * 60)
    print(f"服务地址: http://0.0.0.0:9970")
    print(f"Git工作目录: {Config.GIT_WORKSPACE}")
    print(f"缓存: Redis ({Config.REDIS_HOST}:{Config.REDIS_PORT})")
    print("")
    print("可用接口:")
    print("  • GET  /api/dashboard/summary?projects=xxx")
    print("  • GET  /api/dashboard/contributors?projects=xxx")
    print("  • GET  /api/dashboard/health")
    print("")
    print("=" * 60)
    print("")
    
    app.run(host='0.0.0.0', port=9970, debug=Config.DEBUG)

