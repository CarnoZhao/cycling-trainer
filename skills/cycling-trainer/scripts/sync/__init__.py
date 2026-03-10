"""
sync_intervals 模块化同步组件

包含以下模块:
- config: 配置管理（已迁移到 scripts/config）
- auth: 认证相关
- api: API 请求封装
- state: 同步状态管理
- storage: 数据持久化（已迁移到 utils/storage）
- core: 核心同步逻辑
"""

import sys
from pathlib import Path

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_credentials
from sync.auth import login_session
from sync.api import fetch_activities, fetch_activity_detail_api, fetch_activity_detail_browser
from sync.state import get_sync_state, save_sync_state
from utils.storage import ensure_data_dir, load_activities, save_activities, merge_activities
from sync.core import sync_activities, refresh_intervals_for_activities

__all__ = [
    'load_config',
    'get_credentials',
    'login_session',
    'fetch_activities',
    'fetch_activity_detail_api',
    'fetch_activity_detail_browser',
    'get_sync_state',
    'save_sync_state',
    'ensure_data_dir',
    'load_activities',
    'save_activities',
    'merge_activities',
    'sync_activities',
    'refresh_intervals_for_activities',
]
