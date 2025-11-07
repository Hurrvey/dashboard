"""
日期工具函数
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple


def get_last_week_range() -> Tuple[datetime, datetime]:
    """
    获取上周的起止日期（周一00:00:00 到 周日23:59:59）
    
    Returns:
        (start_date, end_date): 上周周一和周日的datetime对象（带时区信息）
    """
    # 使用UTC时区
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 获取今天是星期几 (0=周一, 6=周日)
    current_weekday = today.weekday()
    
    # 计算上周一的日期
    # 如果今天是周一(0)，上周一是7天前
    # 如果今天是周二(1)，上周一是8天前
    # 如果今天是周日(6)，上周一是6天前
    days_since_last_monday = current_weekday + 7
    last_monday = today - timedelta(days=days_since_last_monday)
    
    # 上周日是上周一+6天，23:59:59
    last_sunday = last_monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return last_monday, last_sunday


def get_last_week_range_str() -> Tuple[str, str]:
    """
    获取上周的起止日期字符串格式 (YYYY-MM-DD)
    
    Returns:
        (start_date_str, end_date_str): 格式化的日期字符串
    """
    start_date, end_date = get_last_week_range()
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def is_in_last_week(dt: datetime) -> bool:
    """
    判断给定日期是否在上周范围内
    
    Args:
        dt: 要判断的日期时间
        
    Returns:
        bool: 是否在上周范围内
    """
    start_date, end_date = get_last_week_range()
    return start_date <= dt <= end_date

