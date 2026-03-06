"""
同步状态管理模块

负责读写 sync_state.json，记录上次同步时间和最后活动 ID
"""

import json
from datetime import datetime as dt
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
CACHE_FILE = DATA_DIR / "sync_state.json"


def get_sync_state():
    """
    获取同步状态
    
    Returns:
        dict: 包含 last_sync, last_activity_id, activities_count
    """
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {"last_sync": None, "last_activity_id": None, "activities_count": 0}


def save_sync_state(state):
    """
    保存同步状态
    
    Args:
        state: dict 包含同步状态信息
    """
    with open(CACHE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def update_sync_state(activities):
    """
    根据活动列表更新同步状态
    
    Args:
        activities: 活动列表（按时间倒序排列）
    """
    if activities:
        new_state = {
            "last_sync": dt.now().isoformat(),
            "last_activity_id": activities[0].get('id'),
            "activities_count": len(activities)
        }
        save_sync_state(new_state)
