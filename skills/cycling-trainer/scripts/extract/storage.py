"""
数据存储模块

负责加载本地 activities.json 数据
"""

import json
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
DATA_FILE = DATA_DIR / "activities.json"


def load_data():
    """
    加载本地活动数据
    
    Returns:
        list: 按时间倒序排列的活动列表
        dict: 如果出错，返回 {"error": "..."}
    """
    if not DATA_FILE.exists():
        return {"error": "No local data, please run sync first"}
    
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    return sorted(data, key=lambda x: x.get('start_date', ''), reverse=True)
