"""
工具函数模块

包含通用工具函数
"""


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
