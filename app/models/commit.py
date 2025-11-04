"""
Commit 数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Commit:
    """Git Commit 数据模型"""
    
    hash: str                    # commit hash
    author_name: str             # 作者姓名
    author_email: str            # 作者邮箱
    timestamp: datetime          # 提交时间
    message: str                 # 提交信息
    additions: int = 0           # 新增行数
    deletions: int = 0           # 删除行数
    files_changed: int = 0       # 修改文件数
    
    @property
    def hour(self) -> int:
        """提交时间的小时 (0-23)"""
        return self.timestamp.hour
    
    @property
    def weekday(self) -> int:
        """提交时间的星期 (0=周一, 6=周日)"""
        return self.timestamp.weekday()
    
    @property
    def is_work_hour(self) -> bool:
        """是否工作时间 (9:00-18:00)"""
        return 9 <= self.hour < 18
    
    @property
    def is_overtime(self) -> bool:
        """是否加班时间 (18:00-9:00)"""
        return not self.is_work_hour
    
    @property
    def is_weekday(self) -> bool:
        """是否工作日 (周一-周五)"""
        return self.weekday < 5
    
    @property
    def is_weekend(self) -> bool:
        """是否周末 (周六-周日)"""
        return self.weekday >= 5

