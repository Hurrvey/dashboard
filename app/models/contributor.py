"""
贡献者数据模型
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .commit import Commit


@dataclass
class Contributor:
    """贡献者数据模型"""
    
    name: str                    # 姓名
    email: str                   # 邮箱
    commits: int = 0             # commit 次数
    additions: int = 0           # 总新增行数
    deletions: int = 0           # 总删除行数
    rank: int = 0                # 排名
    
    @property
    def total_changes(self) -> int:
        """总代码变更量"""
        return self.additions + self.deletions

    @property
    def contribution_score(self) -> int:
        """贡献度分值（基于代码变更量）"""
        return self.total_changes

    @property
    def net_additions(self) -> int:
        """净新增行数（新增 - 删除）"""
        return self.additions - self.deletions

    @property
    def average_change(self) -> float:
        """单次提交平均变更行数"""
        if self.commits == 0:
            return 0.0
        return self.total_changes / self.commits
    
    def add_commit(self, commit: 'Commit'):
        """添加一个 commit 的统计"""
        self.commits += 1
        self.additions += commit.additions
        self.deletions += commit.deletions

