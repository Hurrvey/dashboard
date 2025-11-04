"""
应用配置
"""

import json
import os
from typing import Optional
from dotenv import load_dotenv


def _optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None

def _parse_project_list(raw_value: Optional[str]) -> list[str]:
    if not raw_value:
        return []

    projects: list[str]

    try:
        decoded = json.loads(raw_value)
    except json.JSONDecodeError:
        decoded = None

    if isinstance(decoded, dict):
        projects = [str(v).strip() for v in decoded.values() if str(v).strip()]
    elif isinstance(decoded, (list, tuple)):
        projects = [str(item).strip() for item in decoded if str(item).strip()]
    elif isinstance(decoded, str) and decoded.strip():
        projects = [decoded.strip()]
    else:
        projects = [item.strip() for item in raw_value.split(',') if item.strip()]

    unique: list[str] = []
    seen = set()
    for project in projects:
        if project and project not in seen:
            seen.add(project)
            unique.append(project)
    return unique


load_dotenv()


# AI 分析默认配置（可通过环境变量覆盖）
DEFAULT_AI_ANALYZER_ENDPOINT = 'https://llm-router-new-api.zhifukj.com.cn/v1/chat/completions'
DEFAULT_AI_ANALYZER_API_KEY = 'sk-esDgULBKSr7a6vy33u70ouoxIcLGdh2Ef4AZnyn9xDRvk9Cr'
DEFAULT_AI_ANALYZER_MODEL = 'deepseek-chat'


class Config:
    """应用配置"""
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    DEFAULT_PROJECTS = _parse_project_list(os.getenv('DEFAULT_PROJECTS'))
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Git 配置
    GIT_WORKSPACE = os.getenv('GIT_WORKSPACE', './repos')
    GIT_MAX_DEPTH = int(os.getenv('GIT_MAX_DEPTH', 1000))
    
    # 缓存配置
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5 分钟
    
    # 性能配置
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))
    MAX_PROJECTS = int(os.getenv('MAX_PROJECTS', 50))
    PROJECT_FETCH_TIMEOUT = int(os.getenv('PROJECT_FETCH_TIMEOUT', 180))
    AI_RATIO_CACHE_TTL = int(os.getenv('AI_RATIO_CACHE_TTL', 300))

    # AI 分析服务配置
    AI_ANALYZER_ENDPOINT = os.getenv('AI_ANALYZER_ENDPOINT', DEFAULT_AI_ANALYZER_ENDPOINT)
    AI_ANALYZER_API_KEY = os.getenv('AI_ANALYZER_API_KEY', DEFAULT_AI_ANALYZER_API_KEY)
    AI_ANALYZER_MODEL = os.getenv('AI_ANALYZER_MODEL', DEFAULT_AI_ANALYZER_MODEL)
    AI_ANALYZER_MAX_TOKENS = int(os.getenv('AI_ANALYZER_MAX_TOKENS', 4096))
    AI_ANALYZER_TIMEOUT = int(os.getenv('AI_ANALYZER_TIMEOUT', 60))
    AI_ANALYZER_MAX_FILES = _optional_int(os.getenv('AI_ANALYZER_MAX_FILES'))
    AI_ANALYZER_MAX_FILE_SIZE = _optional_int(os.getenv('AI_ANALYZER_MAX_FILE_SIZE'))
    AI_ANALYZER_MAX_CHARACTERS = _optional_int(os.getenv('AI_ANALYZER_MAX_CHARACTERS'))
    AI_ANALYZER_CONCURRENCY = int(os.getenv('AI_ANALYZER_CONCURRENCY', 5))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', './logs')

