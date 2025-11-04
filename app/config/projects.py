"""
项目配置管理
"""
import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ProjectsConfig:
    """项目配置管理器"""
    
    def __init__(self, config_file: str = 'projects.json'):
        """
        初始化项目配置
        
        Args:
            config_file: 项目配置文件路径
        """
        self.config_file = config_file
        self.projects = self._load_config()
    
    def _load_config(self) -> Dict[str, str]:
        """
        从配置文件加载项目映射
        
        Returns:
            项目名称 -> 仓库路径的映射字典
        """
        # 1. 尝试从配置文件加载
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 过滤掉注释字段
                    config = {k: v for k, v in config.items() if not k.startswith('_')}
                    logger.info(f"从配置文件加载项目: {len(config)} 个")
                    return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        
        # 2. 尝试从环境变量加载
        projects_env = os.getenv('PROJECTS_CONFIG')
        if projects_env:
            try:
                config = json.loads(projects_env)
                logger.info(f"从环境变量加载项目: {len(config)} 个")
                return config
            except Exception as e:
                logger.error(f"解析环境变量失败: {e}")
        
        # 3. 返回空配置
        logger.warning("未找到项目配置，将使用默认行为（从工作目录查找）")
        return {}
    
    def get_repo_path(self, project_name: str) -> Optional[str]:
        """
        获取项目对应的仓库路径
        
        Args:
            project_name: 项目名称
        
        Returns:
            仓库路径，如果不存在返回 None
        """
        return self.projects.get(project_name)
    
    def reload(self):
        """重新加载配置"""
        self.projects = self._load_config()
        logger.info("配置已重新加载")
    
    def list_projects(self) -> Dict[str, str]:
        """
        获取所有项目配置
        
        Returns:
            所有项目的映射字典
        """
        return self.projects.copy()


# 全局配置实例
projects_config = ProjectsConfig()

