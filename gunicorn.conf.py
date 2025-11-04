"""
Gunicorn 配置文件 - 生产环境
"""

import multiprocessing
import os

# 绑定地址和端口
bind = "0.0.0.0:9970"

# Worker 进程数（推荐：CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
worker_class = "sync"

# 超时时间（秒）
timeout = 60

# Keep-alive 连接时间
keepalive = 5

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 守护进程（生产环境可设为 True）
daemon = False

# 进程名称
proc_name = "code996-dashboard"

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 预加载应用（提升性能）
preload_app = True

# 工作目录
chdir = os.path.dirname(os.path.abspath(__file__))

# 捕获输出
capture_output = True

# Hooks
def on_starting(server):
    """服务器启动时"""
    print("=" * 60)
    print("CODE996 数据看板后端服务")
    print("=" * 60)
    print(f"Workers: {workers}")
    print(f"Bind: {bind}")
    print(f"Timeout: {timeout}s")
    print("=" * 60)

def when_ready(server):
    """服务器就绪时"""
    print("✅ 服务器已就绪，等待请求...")

def on_exit(server):
    """服务器退出时"""
    print("👋 服务器已关闭")

