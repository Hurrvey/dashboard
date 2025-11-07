"""
统计服务
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import logging
import os
from app.services.git_service import GitService
from app.services.project_registry import project_registry, ProjectEntry
from app.models.commit import Commit
from app.models.stats import DashboardStats
from app.utils.stats_calculator import calculate_contributors
from app.config.projects import projects_config

logger = logging.getLogger(__name__)


class StatsService:
    """统计服务"""
    
    def __init__(self, git_service: GitService, project_timeout: int = 120):
        """
        初始化
        
        Args:
            git_service: Git服务实例
        """
        self.git_service = git_service
        self.project_timeout = project_timeout
    
    def fetch_multi_project_stats(
        self, 
        project_names: List[str],
        max_workers: int = 5,
        force_refresh: bool = False
    ) -> DashboardStats:
        """
        并发获取多个项目的统计数据
        
        Args:
            project_names: 项目名称列表
            max_workers: 最大并发数
        
        Returns:
            DashboardStats: 汇总的统计数据
        """
        all_commits = []
        successful_projects = []
        failed_projects = {}
        
        # 并发处理各个项目
        revealed_commits: List[Commit] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single_project_with_meta, name, force_refresh): name
                for name in project_names
            }
            
            for future in as_completed(futures):
                project_name = futures[future]
                try:
                    commits, project_id = future.result(timeout=self.project_timeout)
                    annotated = self._attach_project_info(commits, project_id, project_name)
                    all_commits.extend(annotated)
                    revealed_commits.extend(annotated)
                    successful_projects.append(project_name)
                    logger.info(f"项目 {project_name} 数据获取成功: {len(commits)} commits")
                except Exception as e:
                    failed_projects[project_name] = str(e)
                    logger.error(f"项目 {project_name} 数据获取失败: {str(e)}")
        
        # 生成统计数据
        repo_count = len(successful_projects) if successful_projects else len(project_names)
        repo_count = max(repo_count, len(set(project_names)))

        if failed_projects:
            logger.warning(
                "以下项目获取失败，将不会计入统计: %s",
                ", ".join(f"{name} ({reason})" for name, reason in failed_projects.items())
            )

        return DashboardStats.from_commits(all_commits, repo_count)
    
    def fetch_multi_project_contributors(
        self,
        project_names: List[str],
        max_workers: int = 5,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        并发获取多个项目的贡献者数据
        
        Args:
            project_names: 项目名称列表
            max_workers: 最大并发数
        
        Returns:
            贡献者列表（按commits降序）
        """
        all_commits: List[Commit] = []
        successful_projects = []
        failed_projects = {}
        
        # 并发处理各个项目
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single_project_with_meta, name, force_refresh): name
                for name in project_names
            }
            
            for future in as_completed(futures):
                project_name = futures[future]
                try:
                    commits, project_id = future.result(timeout=self.project_timeout)
                    annotated = self._attach_project_info(commits, project_id, project_name)
                    all_commits.extend(annotated)
                    successful_projects.append(project_name)
                except Exception as e:
                    failed_projects[project_name] = str(e)
                    logger.error(f"项目 {project_name} 数据获取失败: {str(e)}")
        
        if failed_projects:
            logger.warning(
                "以下项目贡献者数据获取失败: %s",
                ", ".join(f"{name} ({reason})" for name, reason in failed_projects.items())
            )

        # 计算贡献者统计
        contributors = calculate_contributors(all_commits)

        for contributor in contributors:
            contributor.setdefault('projects', [])
            contributor.setdefault('project_names', [])

        return contributors

    def _extract_project_display_name(self, project_name: str) -> str:
        """
        提取项目显示名称（URL的最后一个路由部分）
        
        Args:
            project_name: 完整的项目标识符或URL
            
        Returns:
            项目的显示名称
            
        Examples:
            https://gitea.zhifukj.com.cn/zhifukeji/dev-docs -> dev-docs
            /path/to/my-project -> my-project
            my-project -> my-project
        """
        # 移除URL末尾的斜杠
        name = project_name.rstrip('/')
        
        # 如果是URL，移除.git后缀
        if name.endswith('.git'):
            name = name[:-4]
        
        # 提取最后一个路由部分
        if '/' in name:
            name = name.split('/')[-1]
        
        return name
    
    def _attach_project_info(self, commits: List[Commit], project_id: str, project_name: str) -> List[Commit]:
        # 提取项目显示名称（只保留URL的最后一部分）
        display_name = self._extract_project_display_name(project_name)
        
        for commit in commits:
            commit.project_id = project_id
            commit.project_name = display_name
        return commits

    def _fetch_single_project_with_meta(self, project_name: str, force_refresh: bool = False) -> tuple[List[Commit], str]:
        entry = self._resolve_project_entry(project_name, force_refresh=force_refresh)
        repo = self.git_service.get_repo_from_path(entry.path, force_refresh=force_refresh)
        commits = self.git_service.get_commits(repo)
        project_registry.register_identifier(project_name, entry.path, entry.project_id)
        return commits, entry.project_id

    def _fetch_single_project(self, project_name: str, force_refresh: bool = False) -> List[Commit]:
        """获取单个项目的 commit 数据并同步项目到本地缓存"""

        entry = self._resolve_project_entry(project_name, force_refresh=force_refresh)

        repo = self.git_service.get_repo_from_path(entry.path, force_refresh=force_refresh)
        commits = self.git_service.get_commits(repo)

        project_registry.register_identifier(project_name, entry.path, entry.project_id)
        return commits

    def _resolve_project_entry(self, identifier: str, force_refresh: bool = False) -> ProjectEntry:
        """根据项目标识解析并返回本地仓库信息"""

        existing = project_registry.get_entry(identifier)
        if existing and os.path.exists(existing.path):
            return existing

        if self._is_git_url(identifier):
            remote_entry = self._resolve_remote_repo(identifier, force_refresh=force_refresh)
            project_registry.register_identifier(identifier, remote_entry.path, remote_entry.project_id)
            return ProjectEntry(identifier, remote_entry.project_id, remote_entry.path)

        repo_mapping = projects_config.get_repo_path(identifier)
        if repo_mapping:
            if self._is_git_url(repo_mapping):
                remote_entry = self._resolve_remote_repo(repo_mapping, force_refresh=force_refresh)
                project_registry.register_identifier(identifier, remote_entry.path, remote_entry.project_id)
                project_registry.register_identifier(repo_mapping, remote_entry.path, remote_entry.project_id)
                return ProjectEntry(identifier, remote_entry.project_id, remote_entry.path)

            local_entry = self._resolve_local_project(identifier, repo_mapping, force_refresh=force_refresh)
            project_registry.register_identifier(repo_mapping, local_entry.path, local_entry.project_id)
            return local_entry

        return self._resolve_local_project(identifier, identifier, force_refresh=force_refresh)

    def _resolve_remote_repo(self, repo_url: str, force_refresh: bool = False) -> ProjectEntry:
        workspace_entry = project_registry.prepare_repo_workspace(repo_url)
        repo = self.git_service.get_or_clone_repo(repo_url, workspace_entry.project_id, force_refresh=force_refresh)
        path = os.path.abspath(repo.working_tree_dir)
        project_registry.register_identifier(repo_url, path, workspace_entry.project_id)
        return ProjectEntry(repo_url, workspace_entry.project_id, path)

    def _resolve_local_project(self, identifier: str, path_value: str, force_refresh: bool = False) -> ProjectEntry:
        candidate_paths = []

        if os.path.isabs(path_value):
            candidate_paths.append(path_value)
        else:
            candidate_paths.append(os.path.abspath(path_value))
            candidate_paths.append(os.path.join(self.git_service.workspace_dir, path_value))

        for candidate in candidate_paths:
            if candidate and os.path.exists(candidate):
                abs_candidate = os.path.abspath(candidate)
                project_id = project_registry.generate_project_id(abs_candidate)
                canonical_entry = project_registry.ensure_local_copy(
                    identifier=abs_candidate,
                    source_path=abs_candidate,
                    force_refresh=force_refresh,
                    project_id=project_id,
                )

                project_registry.register_identifier(identifier, canonical_entry.path, canonical_entry.project_id)
                if path_value != identifier:
                    project_registry.register_identifier(path_value, canonical_entry.path, canonical_entry.project_id)

                return ProjectEntry(identifier, canonical_entry.project_id, canonical_entry.path)

        raise FileNotFoundError(
            f"找不到项目 '{identifier}' 对应的路径 {path_value}。"
            f"请确认配置或输入是否正确。"
        )

    def get_commits_for_project(self, project_name: str, force_refresh: bool = False) -> List[Commit]:
        """获取单个项目的 commit 列表（对外暴露的公共方法）"""
        return self._fetch_single_project(project_name, force_refresh=force_refresh)
    
    def _is_git_url(self, path: str) -> bool:
        """检查字符串是否为 Git URL"""
        git_protocols = ('http://', 'https://', 'git://', 'ssh://', 'git@')
        return any(path.startswith(protocol) for protocol in git_protocols)

