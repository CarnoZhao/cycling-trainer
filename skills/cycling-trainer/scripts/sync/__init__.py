"""
sync_intervals 模块化同步组件

包含以下模块:
- config: 配置管理
- auth: 认证相关
- api: API 请求封装
- state: 同步状态管理
- storage: 数据持久化
- core: 核心同步逻辑
"""

from .config import load_config, get_credentials
from .auth import login_session
from .api import fetch_activities, fetch_activity_detail_api, fetch_activity_detail_browser
from .state import get_sync_state, save_sync_state
from .storage import ensure_data_dir, load_activities, save_activities
from .core import sync_activities, refresh_intervals_for_activities

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
    'sync_activities',
    'refresh_intervals_for_activities',
]
