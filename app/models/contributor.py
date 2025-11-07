"""
贡献者数据模型
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .commit import Commit


@dataclass
class Contributor:
    """贡献者数据模型"""
    
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.commits = 0
        self.additions = 0
        self.deletions = 0
        self.rank = 0
        self.project_ids: set[str] = set()
        self.project_names: set[str] = set()
        self._daily_counts: List[int] = [0] * 7
        self._last_week_counts: List[int] = [0] * 7  # 上周的按天统计

    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions

    @property
    def contribution_score(self) -> int:
        return self.total_changes

    @property
    def net_additions(self) -> int:
        return self.additions - self.deletions

    @property
    def average_change(self) -> float:
        if self.commits == 0:
            return 0.0
        return self.total_changes / self.commits

    def add_commit(self, commit: 'Commit', is_last_week: bool = False):
        """
        添加commit到统计
        
        Args:
            commit: Commit对象
            is_last_week: 是否为上周的commit
        """
        self.commits += 1
        self.additions += commit.additions
        self.deletions += commit.deletions
        weekday_index = commit.weekday
        if 0 <= weekday_index < len(self._daily_counts):
            self._daily_counts[weekday_index] += 1
            
        # 如果是上周的commit，同时记录到上周统计中
        if is_last_week and 0 <= weekday_index < len(self._last_week_counts):
            self._last_week_counts[weekday_index] += 1

        if commit.project_id:
            self.project_ids.add(commit.project_id)

        if commit.project_name:
            self.project_names.add(commit.project_name)

    @property
    def weekday_distribution(self) -> List[Dict[str, int]]:
        """所有时间的按星期分布"""
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return [
            {"time": weekday_names[index], "count": self._daily_counts[index]}
            for index in range(len(weekday_names))
        ]
    
    @property
    def last_week_distribution(self) -> List[Dict[str, int]]:
        """上周的按天分布"""
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return [
            {"time": weekday_names[index], "count": self._last_week_counts[index]}
            for index in range(len(weekday_names))
        ]

