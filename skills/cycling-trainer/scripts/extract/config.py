"""
配置管理模块

负责加载和合并配置（环境变量 > 配置文件）
"""

import json
import os
import sys
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent  # skills/cycling-trainer/scripts/
SKILL_DIR = SCRIPT_DIR.parent  # skills/cycling-trainer/
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
CONFIG_FILE = SKILL_DIR / "config.json"


def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception as e:
            print(f"[Config] Error loading config.json: {e}", file=sys.stderr)
    return {}


def get_credentials():
    """
    获取认证信息，按优先级合并（环境变量 > 配置文件）
    
    Returns:
        tuple: (athlete_id, api_key)
    """
    config = load_config()
    
    athlete_id = os.getenv('INTERVALS_ATHLETE_ID') or config.get('athlete_id')
    api_key = os.getenv('INTERVALS_API_KEY') or config.get('api_key')
    
    return athlete_id, api_key
