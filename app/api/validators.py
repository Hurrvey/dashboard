"""
请求参数验证器
"""

from typing import List


def validate_projects_param(projects_param: str) -> List[str]:
    """
    验证 projects 参数
    
    Args:
        projects_param: 逗号分隔的项目名称字符串
    
    Returns:
        List[str]: 项目名称列表
    
    Raises:
        ValueError: 参数无效
    """
    if not projects_param:
        raise ValueError("projects 参数不能为空")
    
    # 分割并去除空白
    projects = [p.strip() for p in projects_param.split(',') if p.strip()]
    
    if not projects:
        raise ValueError("projects 参数格式不正确")
    
    if len(projects) > 50:  # 限制最大项目数
        raise ValueError("项目数量不能超过 50 个")
    
    return projects

