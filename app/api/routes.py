"""
API 路由定义
"""

from flask import Blueprint, request
from app.api.validators import validate_projects_param
from app.api.responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# 创建 Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/dashboard')

# 全局服务实例（在create_app中初始化）
stats_service = None
cache_service = None


def init_services(stats_svc, cache_svc):
    """初始化服务实例"""
    global stats_service, cache_service
    stats_service = stats_svc
    cache_service = cache_svc


def _parse_force_refresh() -> bool:
    value = request.args.get('force_refresh', '').lower()
    return value in ('1', 'true', 'yes', 'y')


@api_bp.route('/summary', methods=['GET'])
def get_summary():
    """
    获取汇总数据接口
    
    Query Parameters:
        projects: 逗号分隔的项目名称列表
    
    Returns:
        JSON: 汇总统计数据
    """
    try:
        # 1. 参数验证
        projects_param = request.args.get('projects', '')
        projects = validate_projects_param(projects_param)
        force_refresh = _parse_force_refresh()
        
        # 2. 生成缓存键
        cache_key = f"summary:{','.join(sorted(projects))}"
        
        # 3. 检查缓存
        if force_refresh:
            cache_service.delete(cache_key)
        else:
            cached_data = cache_service.get(cache_key)
            if cached_data:
                logger.info(f"缓存命中: {cache_key}")
                return success_response(cached_data)
        
        # 4. 获取数据
        logger.info(f"开始处理项目: {projects}")
        stats = stats_service.fetch_multi_project_stats(projects, force_refresh=force_refresh)
        
        # 5. 格式化响应
        data = {
            "start_date": stats.start_date,
            "end_date": stats.end_date,
            "total_count": stats.total_count,
            "repo_count": stats.repo_count,
            "hour_data": stats.hour_data,
            "week_data": stats.week_data,
            "work_hour_pl": stats.work_hour_pl,
            "work_week_pl": stats.work_week_pl,
            "index_996": stats.index_996,
            "overtime_ratio": stats.overtime_ratio,
            "is_standard": stats.is_standard
        }
        
        # 6. 写入缓存 (5 分钟)
        cache_service.set(cache_key, data, ttl=300)
        
        return success_response(data)
        
    except ValueError as e:
        logger.warning(f"参数错误: {str(e)}")
        return error_response(400, f"参数错误: {str(e)}")
    
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}", exc_info=True)
        return error_response(500, "服务器内部错误")


@api_bp.route('/contributors', methods=['GET'])
def get_contributors():
    """
    获取贡献者列表接口
    
    Query Parameters:
        projects: 逗号分隔的项目名称列表
    
    Returns:
        JSON: 贡献者列表（按 commits 降序）
    """
    try:
        # 1. 参数验证
        projects_param = request.args.get('projects', '')
        projects = validate_projects_param(projects_param)
        force_refresh = _parse_force_refresh()
        
        # 2. 生成缓存键
        cache_key = f"contributors:{','.join(sorted(projects))}"
        
        # 3. 检查缓存
        if force_refresh:
            cache_service.delete(cache_key)
        else:
            cached_data = cache_service.get(cache_key)
            if cached_data:
                logger.info(f"缓存命中: {cache_key}")
                return success_response(cached_data)
        
        # 4. 获取数据
        logger.info(f"开始获取贡献者: {projects}")
        contributors = stats_service.fetch_multi_project_contributors(projects, force_refresh=force_refresh)
        
        # 5. 写入缓存 (5 分钟)
        cache_service.set(cache_key, contributors, ttl=300)
        
        return success_response(contributors)
        
    except ValueError as e:
        logger.warning(f"参数错误: {str(e)}")
        return error_response(400, f"参数错误: {str(e)}")
    
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}", exc_info=True)
        return error_response(500, "服务器内部错误")


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return success_response({"status": "ok", "message": "服务运行正常"})

