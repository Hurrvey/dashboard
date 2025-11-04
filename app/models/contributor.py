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
    
    def add_commit(self, commit: 'Commit'):
        """添加一个 commit 的统计"""
        self.commits += 1
        self.additions += commit.additions
        self.deletions += commit.deletions

