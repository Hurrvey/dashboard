"""
Git 仓库管理服务
"""

import os
import shutil
from git import Repo, GitCommandError
from typing import List, Optional
import logging
from app.models.commit import Commit

logger = logging.getLogger(__name__)


class GitService:
    """Git 仓库管理服务"""
    
    def __init__(self, workspace_dir: str = './repos'):
        """
        初始化
        
        Args:
            workspace_dir: Git仓库工作目录
        """
        self.workspace_dir = workspace_dir
        self.mirror_dir = os.path.join(workspace_dir, '_mirror')
        os.makedirs(workspace_dir, exist_ok=True)
        os.makedirs(self.mirror_dir, exist_ok=True)
        logger.info(f"Git工作目录: {workspace_dir}")
        logger.info(f"Git镜像目录: {self.mirror_dir}")
    
    def get_or_clone_repo(self, repo_url: str, project_name: str, force_refresh: bool = False) -> Repo:
        """
        获取或克隆仓库（浅克隆，只拉取必要的 commit 历史）
        
        Args:
            repo_url: 仓库 URL
            project_name: 项目ID（用作本地目录名）
        
        Returns:
            Repo: GitPython 仓库对象
        
        Note:
            所有在线项目都存储在 repos/_mirror/<project_id>/ 目录下
        """
        repo_path = os.path.join(self.mirror_dir, project_name)
        
        # 强制刷新：删除已有仓库，重新克隆
        if force_refresh and os.path.exists(repo_path):
            logger.info(f"强制刷新仓库: {project_name} -> 删除 {repo_path}")
            self._remove_repo_dir(repo_path)

        # 如果仓库已存在，尝试更新
        if os.path.exists(repo_path):
            try:
                repo = Repo(repo_path)
                logger.info(f"本地仓库已存在: {project_name}，正在更新...")
                
                # 获取远程更新
                origin = repo.remote('origin')
                origin.fetch()
                
                # 更新当前分支
                try:
                    origin.pull()
                    logger.info(f"仓库更新成功: {project_name}")
                except GitCommandError as pull_error:
                    logger.warning(f"Pull 失败，尝试 fetch: {pull_error}")
                    # 即使 pull 失败，fetch 的数据也已经拉取
                
                return repo
            except Exception as e:
                logger.warning(f"更新仓库失败: {e}，将重新克隆")
                self._remove_repo_dir(repo_path)
        
        # 克隆仓库（使用浅克隆优化性能）
        try:
            logger.info(f"开始克隆仓库: {repo_url}")
            logger.info(f"目标位置: {repo_path}")
            logger.info("使用浅克隆模式（depth=1000），只拉取最近 1000 个 commit")
            
            # 浅克隆参数
            clone_options = {
                'depth': 1000,  # 只克隆最近 1000 个 commit
                'single_branch': True,  # 只克隆默认分支
                'no_checkout': False,  # 需要检出文件以便分析
            }
            
            repo = Repo.clone_from(
                repo_url, 
                repo_path,
                **clone_options
            )
            
            logger.info(f"✅ 仓库克隆成功: {project_name}")
            logger.info(f"   - 仓库大小: {self._get_repo_size(repo_path)} MB")
            logger.info(f"   - Commit 数量: {sum(1 for _ in repo.iter_commits())}")
            
            return repo
            
        except GitCommandError as e:
            logger.error(f"克隆仓库失败: {repo_url}")
            logger.error(f"错误信息: {str(e)}")
            raise ValueError(f"克隆仓库失败: {str(e)}")
        except Exception as e:
            logger.error(f"克隆过程出现异常: {str(e)}")
            raise
    
    def _get_repo_size(self, repo_path: str) -> float:
        """
        获取仓库大小（MB）
        
        Args:
            repo_path: 仓库路径
            
        Returns:
            仓库大小（MB）
        """
        try:
            import os
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(repo_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0
    
    def get_repo_from_path(self, repo_path: str, force_refresh: bool = False) -> Repo:
        """
        从现有路径获取仓库
        
        Args:
            repo_path: 仓库路径
        
        Returns:
            Repo对象
        """
        try:
            repo = Repo(repo_path)
            if force_refresh:
                self._refresh_existing_repo(repo, repo_path)
            return repo
        except Exception as e:
            raise ValueError(f"打开仓库失败: {str(e)}")
    
    def get_commits(
        self, 
        repo: Repo, 
        branch: str = 'HEAD',
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_count: int = 10000
    ) -> List[Commit]:
        """
        获取仓库的 commit 列表
        
        Args:
            repo: 仓库对象
            branch: 分支名称
            since: 开始日期 (YYYY-MM-DD)
            until: 结束日期 (YYYY-MM-DD)
            max_count: 最大commit数量
        
        Returns:
            List[Commit]: Commit 对象列表
        """
        commits = []
        
        # 构建 git log 参数
        kwargs = {}
        if since:
            kwargs['since'] = since
        if until:
            kwargs['until'] = until
        
        # 遍历 commit
        try:
            for i, git_commit in enumerate(repo.iter_commits(branch, **kwargs)):
                if i >= max_count:
                    break
                
                try:
                    commit = Commit(
                        hash=git_commit.hexsha[:8],  # 短hash
                        author_name=git_commit.author.name,
                        author_email=git_commit.author.email,
                        timestamp=git_commit.committed_datetime,
                        message=git_commit.message.strip(),
                        additions=git_commit.stats.total['insertions'],
                        deletions=git_commit.stats.total['deletions'],
                        files_changed=git_commit.stats.total['files']
                    )
                    commits.append(commit)
                except Exception as e:
                    logger.warning(f"解析commit失败: {e}")
                    continue
            
            logger.info(f"获取commits成功: {len(commits)}条")
            return commits
            
        except Exception as e:
            logger.error(f"获取commits失败: {e}")
            raise

    def _remove_repo_dir(self, path: str):
        if not os.path.exists(path):
            return
        try:
            shutil.rmtree(path)
            logger.info(f"已删除仓库目录: {path}")
        except Exception as e:
            logger.error(f"删除仓库目录失败 ({path}): {e}")
            raise

    def _refresh_existing_repo(self, repo: Repo, repo_path: str):
        try:
            remotes = list(repo.remotes)
            if not remotes:
                logger.debug(f"仓库 {repo_path} 没有远程配置，跳过刷新")
                return
            origin = remotes[0]
            logger.info(f"刷新仓库 {repo_path}: fetch & pull")
            origin.fetch()
            try:
                origin.pull()
            except GitCommandError as pull_error:
                logger.warning(f"pull 失败，将忽略: {pull_error}")
        except Exception as e:
            logger.warning(f"刷新仓库失败 ({repo_path}): {e}")

