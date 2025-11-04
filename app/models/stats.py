"""
统计数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any
from .commit import Commit


@dataclass
class DashboardStats:
    """仪表板统计数据模型"""
    
    start_date: str                      # 统计开始日期
    end_date: str                        # 统计结束日期
    total_count: int                     # 总 commit 数
    repo_count: int                      # 项目数量
    hour_data: List[Dict[str, Any]]      # 按小时统计 (24个)
    week_data: List[Dict[str, Any]]      # 按星期统计 (7个)
    work_hour_pl: List[Dict[str, Any]]   # 工作/加班占比 (2个)
    work_week_pl: List[Dict[str, Any]]   # 工作日/周末占比 (2个)
    index_996: float                     # 996 指数
    overtime_ratio: float                # 加班比例
    is_standard: bool                    # 是否标准工作时间
    
    @staticmethod
    def from_commits(commits: List[Commit], repo_count: int) -> 'DashboardStats':
        """从 commit 列表生成统计数据"""
        from app.utils.stats_calculator import (
            calculate_hour_data,
            calculate_week_data,
            calculate_work_hour_ratio,
            calculate_work_week_ratio,
            calculate_996_index,
            calculate_overtime_ratio
        )
        
        # 如果没有 commit，返回空数据
        if not commits:
            return DashboardStats._empty_stats(repo_count)
        
        # 计算日期范围
        timestamps = [c.timestamp for c in commits]
        start_date = min(timestamps).strftime('%Y-%m-%d')
        end_date = max(timestamps).strftime('%Y-%m-%d')
        
        # 计算各项统计
        hour_data = calculate_hour_data(commits)
        week_data = calculate_week_data(commits)
        work_hour_pl = calculate_work_hour_ratio(commits)
        work_week_pl = calculate_work_week_ratio(commits)
        index_996 = calculate_996_index(commits)
        overtime_ratio = calculate_overtime_ratio(commits)
        
        # 判断是否标准工作时间
        is_standard = overtime_ratio < 0.2 and index_996 < 0.3
        
        return DashboardStats(
            start_date=start_date,
            end_date=end_date,
            total_count=len(commits),
            repo_count=repo_count,
            hour_data=hour_data,
            week_data=week_data,
            work_hour_pl=work_hour_pl,
            work_week_pl=work_week_pl,
            index_996=index_996,
            overtime_ratio=overtime_ratio,
            is_standard=is_standard
        )
    
    @staticmethod
    def _empty_stats(repo_count: int) -> 'DashboardStats':
        """生成空统计数据"""
        return DashboardStats(
            start_date=datetime.now().strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            total_count=0,
            repo_count=repo_count,
            hour_data=[{"time": f"{i:02d}", "count": 0} for i in range(24)],
            week_data=[{"time": d, "count": 0} for d in 
                      ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]],
            work_hour_pl=[{"time": "工作时间", "count": 0}, {"time": "加班时间", "count": 0}],
            work_week_pl=[{"time": "工作日", "count": 0}, {"time": "周末", "count": 0}],
            index_996=0.0,
            overtime_ratio=0.0,
            is_standard=True
        )

