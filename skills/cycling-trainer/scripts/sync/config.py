"""
配置管理模块

负责加载和合并配置（命令行参数 > 环境变量 > 配置文件）
"""

import json
import os
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent  # skills/cycling-trainer/scripts/
SKILL_DIR = SCRIPT_DIR.parent  # skills/cycling-trainer/
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
CONFIG_FILE = SKILL_DIR / "config.json"


def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def get_credentials(args):
    """
    获取认证信息，按优先级合并（命令行 > 环境变量 > 配置文件）
    
    Args:
        args: argparse.Namespace 或具有属性的对象
    
    Returns:
        tuple: (athlete_id, api_key, email, password)
    """
    config = load_config()
    
    # 支持 args 是 dict 或 Namespace
    def get_attr(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default) if hasattr(obj, key) else default
    
    athlete_id = get_attr(args, 'athlete_id') or os.getenv('INTERVALS_ATHLETE_ID') or config.get('athlete_id')
    api_key = get_attr(args, 'api_key') or os.getenv('INTERVALS_API_KEY') or config.get('api_key')
    email = get_attr(args, 'email') or os.getenv('INTERVALS_EMAIL') or config.get('email')
    password = get_attr(args, 'password') or os.getenv('INTERVALS_PASSWORD') or config.get('password')
    
    return athlete_id, api_key, email, password
