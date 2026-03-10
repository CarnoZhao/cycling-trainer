"""
数据存储模块

统一的数据加载和保存功能，供 extract/ 和 sync/ 模块使用
"""

import json
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
ACTIVITIES_FILE = DATA_DIR / "activities.json"
DATA_FILE = DATA_DIR / "activities.json"  # 别名，兼容旧代码


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """
    加载本地活动数据（兼容旧接口）

    Returns:
        list: 按时间倒序排列的活动列表
        dict: 如果出错，返回 {"error": "..."}
    """
    return load_activities()


def load_activities():
    """
    加载本地活动数据

    Returns:
        list: 活动列表，如果没有数据返回空列表
        dict: 如果出错，返回 {"error": "..."}
    """
    if not ACTIVITIES_FILE.exists():
        return {"error": "No local data, please run sync first"}

    try:
        with open(ACTIVITIES_FILE) as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x.get('start_date', ''), reverse=True)
    except Exception as e:
        return {"error": f"Error loading data: {e}"}


def save_activities(activities):
    """
    保存活动数据到本地

    Args:
        activities: 活动列表
    """
    ensure_data_dir()
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
