"""
CORS 中间件
"""

from flask_cors import CORS
import os


def setup_cors(app):
    """
    配置 CORS
    
    Args:
        app: Flask应用实例
    """
    # 生产环境使用严格的CORS策略，开发环境允许所有来源
    is_production = os.getenv('DEBUG', 'False').lower() == 'false'
    
    if is_production:
        # 生产环境：严格限制来源
        CORS(app, resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3801",
                    "http://localhost:3000",
                    "http://localhost:9970",
                    "https://your-domain.com"  # 修改为实际域名
                ],
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "X-API-Key"],
                "max_age": 3600
            }
        })
    else:
        # 开发环境：允许所有来源（便于调试）
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
                "max_age": 3600
            }
        })

