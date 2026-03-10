"""
日期处理工具模块

统一的日期计算和星期转换功能
"""

from datetime import datetime, timedelta


def get_weekday_cn(dt):
    """
    获取中文星期几

    Args:
        dt: datetime 对象

    Returns:
        str: 周一、周二...周日
    """
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[dt.weekday()]


def format_date_range(days=7, from_date=None):
    """
    格式化日期范围

    Args:
        days: 向前查看的天数
        from_date: 起始日期（默认为今天）

    Returns:
        tuple: (oldest_str, newest_str) 格式为 YYYY-MM-DD
    """
    if from_date is None:
        from_date = datetime.now()

    oldest = from_date.strftime('%Y-%m-%d')
    newest = (from_date + timedelta(days=days)).strftime('%Y-%m-%d')

    return oldest, newest


def get_week_start(date=None):
    """
    获取指定日期所在周的开始（周一）

    Args:
        date: datetime 对象（默认为今天）

    Returns:
        datetime: 本周一的日期（时间清零）
    """
    if date is None:
        date = datetime.now()

    monday = (date - timedelta(days=date.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return monday


def parse_activity_date(date_str):
    """
    解析活动日期字符串为 datetime 对象

    Args:
        date_str: 日期字符串（如 '2024-03-10T08:00:00'）

    Returns:
        datetime: 解析后的日期对象，解析失败返回 None
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str[:10], '%Y-%m-%d')
    except (ValueError, TypeError):
        return None


def is_date_in_range(date_str, days=30, end_date=None):
    """
    检查日期是否在指定范围内

    Args:
        date_str: 日期字符串
        days: 天数范围
        end_date: 结束日期（默认为今天）

    Returns:
        bool: 是否在范围内
    """
    if end_date is None:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=days)

    parsed = parse_activity_date(date_str)
    if not parsed:
        return False

    return start_date <= parsed <= end_date
