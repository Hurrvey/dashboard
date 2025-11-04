"""
Flask 应用主入口
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app.api.routes import api_bp, init_services
from app.api.ai_routes import ai_bp, init_ai_services
from app.middleware.cors import setup_cors
from app.utils.logger import setup_logger
from app.services import GitService, StatsService, CacheService, build_analyzer_from_env
from app.settings import Config
import logging

# 设置日志
logger = setup_logger('code996', Config.LOG_DIR)


def create_app():
    """创建 Flask 应用"""
    
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 设置 CORS
    setup_cors(app)
    
    # 初始化服务
    git_service = GitService(workspace_dir=Config.GIT_WORKSPACE)
    stats_service = StatsService(git_service, project_timeout=Config.PROJECT_FETCH_TIMEOUT)
    cache_service = CacheService(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB
    )
    ai_analyzer = build_analyzer_from_env()
    
    # 注入服务到路由
    init_services(stats_service, cache_service)
    init_ai_services(stats_service, cache_service, ai_analyzer)
    
    # 注册 Blueprint
    app.register_blueprint(api_bp)
    app.register_blueprint(ai_bp)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {"code": 404, "message": "接口不存在", "data": None}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"服务器错误: {str(error)}")
        return {"code": 500, "message": "服务器内部错误", "data": None}, 500
    
    logger.info("Flask应用初始化完成")
    logger.info("已注册路由:")
    logger.info("  • /api/dashboard/summary")
    logger.info("  • /api/dashboard/contributors")
    logger.info("  • /api/dashboard/health")
    logger.info("  • /api/ai-ratio (新增)")
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    # 注意: 推荐使用 run.py 启动服务
    print("警告: 推荐使用 'python run.py' 启动服务")
    print("")
    app.run(host='0.0.0.0', port=9970, debug=Config.DEBUG)

