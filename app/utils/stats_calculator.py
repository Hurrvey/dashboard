"""
统计计算工具
"""

from typing import List, Dict, Any
from app.models.commit import Commit


def calculate_hour_data(commits: List[Commit]) -> List[Dict[str, Any]]:
    """
    计算按小时分布的数据
    
    Returns:
        24 个元素的列表，每个元素格式: {"time": "00", "count": 10}
    """
    # 初始化 24 小时数据
    hour_counts = {f"{i:02d}": 0 for i in range(24)}
    
    # 统计每个小时的 commit 数
    for commit in commits:
        hour_key = f"{commit.hour:02d}"
        hour_counts[hour_key] += 1
    
    # 转换为列表格式（保持顺序）
    return [{"time": f"{i:02d}", "count": hour_counts[f"{i:02d}"]} for i in range(24)]


def calculate_week_data(commits: List[Commit]) -> List[Dict[str, Any]]:
    """
    计算按星期分布的数据
    
    Returns:
        7 个元素的列表，格式: {"time": "周一", "count": 100}
    """
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    week_counts = {name: 0 for name in weekday_names}
    
    # 统计每个星期的 commit 数
    for commit in commits:
        day_name = weekday_names[commit.weekday]
        week_counts[day_name] += 1
    
    # 按周一到周日顺序返回
    return [{"time": day, "count": week_counts[day]} for day in weekday_names]


def calculate_work_hour_ratio(commits: List[Commit]) -> List[Dict[str, Any]]:
    """
    计算工作时间和加班时间的占比
    
    工作时间: 9:00 - 18:00
    加班时间: 18:00 - 9:00 (次日)
    
    Returns:
        2 个元素: [{"time": "工作时间", "count": 500}, {"time": "加班时间", "count": 300}]
    """
    work_count = sum(1 for c in commits if c.is_work_hour)
    overtime_count = sum(1 for c in commits if c.is_overtime)
    
    return [
        {"time": "工作时间", "count": work_count},
        {"time": "加班时间", "count": overtime_count}
    ]


def calculate_work_week_ratio(commits: List[Commit]) -> List[Dict[str, Any]]:
    """
    计算工作日和周末的占比
    
    工作日: 周一 - 周五
    周末: 周六 - 周日
    
    Returns:
        2 个元素: [{"time": "工作日", "count": 800}, {"time": "周末", "count": 200}]
    """
    weekday_count = sum(1 for c in commits if c.is_weekday)
    weekend_count = sum(1 for c in commits if c.is_weekend)
    
    return [
        {"time": "工作日", "count": weekday_count},
        {"time": "周末", "count": weekend_count}
    ]


def calculate_996_index(commits: List[Commit]) -> float:
    """
    计算 996 指数
    
    996 = 每天工作 9:00-21:00 (12小时), 每周工作 6 天
    
    计算公式:
    - 晚上提交占比 (18:00-21:00) * 0.6
    - 周末提交占比 * 0.4
    
    Returns:
        float: 0-1 之间的数值，越接近 1 表示越 996
    """
    if not commits:
        return 0.0
    
    # 晚上提交占比 (18:00 - 21:00)
    evening_commits = sum(1 for c in commits if 18 <= c.hour < 21)
    evening_ratio = evening_commits / len(commits)
    
    # 周末提交占比
    weekend_commits = sum(1 for c in commits if c.is_weekend)
    weekend_ratio = weekend_commits / len(commits)
    
    # 综合指数
    index = evening_ratio * 0.6 + weekend_ratio * 0.4
    
    return round(min(index, 1.0), 2)


def calculate_overtime_ratio(commits: List[Commit]) -> float:
    """
    计算加班比例
    
    Returns:
        float: 加班 commit 数 / 总 commit 数
    """
    if not commits:
        return 0.0
    
    overtime_count = sum(1 for c in commits if c.is_overtime)
    return round(overtime_count / len(commits), 2)


def calculate_contributors(commits: List[Commit]) -> List[Dict[str, Any]]:
    """
    统计贡献者列表
    
    Returns:
        按 commits 数量降序排列的贡献者列表
    """
    from app.models.contributor import Contributor
    
    # 按邮箱分组统计
    contributors_map = {}
    
    for commit in commits:
        email = commit.author_email
        if email not in contributors_map:
            contributors_map[email] = Contributor(
                name=commit.author_name,
                email=email
            )
        contributors_map[email].add_commit(commit)
    
    # 转换为列表并排序
    contributors = list(contributors_map.values())
    contributors.sort(key=lambda c: c.commits, reverse=True)
    
    # 添加排名
    for rank, contributor in enumerate(contributors, start=1):
        contributor.rank = rank
    
    # 转换为字典格式
    return [
        {
            "rank": c.rank,
            "name": c.name,
            "email": c.email,
            "commits": c.commits,
            "additions": c.additions,
            "deletions": c.deletions
        }
        for c in contributors
    ]

