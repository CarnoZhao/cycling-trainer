"""
数据持久化模块

负责数据目录管理和 activities.json 的读写
"""

import json
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
ACTIVITIES_FILE = DATA_DIR / "activities.json"


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_activities():
    """
    加载本地活动数据
    
    Returns:
        list: 活动列表，如果没有数据返回空列表
    """
    if ACTIVITIES_FILE.exists():
        with open(ACTIVITIES_FILE) as f:
            return json.load(f)
    return []


def save_activities(activities):
    """
    保存活动数据到本地
    
    Args:
        activities: 活动列表
    """
    with open(ACTIVITIES_FILE, 'w') as f:
        json.dump(activities, f, indent=2)


def merge_activities(existing, new):
    """
    合并新旧活动数据，去重并按时间倒序排列
    
    Args:
        existing: 已有活动列表
        new: 新增活动列表
    
    Returns:
        list: 合并后的活动列表
    """
    # 合并数据
    all_activities = new + existing
    
    # 按时间排序（新的在前）
    all_activities = sorted(all_activities, key=lambda x: x.get('start_date', ''), reverse=True)
    
    # 去重
    seen = set()
    unique_activities = []
    for a in all_activities:
        aid = a.get('id')
        if aid not in seen:
            seen.add(aid)
            unique_activities.append(a)
    
    return unique_activities
