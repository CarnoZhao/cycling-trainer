"""
extract_data 模块化数据提取组件

包含以下模块:
- config: 配置管理
- sync: 同步检查和触发
- storage: 数据加载（已迁移到 utils/storage）
- utils: 工具函数（中文星期等，已迁移到 utils/dates）
- extractors: 各类型数据提取器
- planned: 计划训练数据获取
"""

import sys
from pathlib import Path

# 确保 scripts 目录在路径中，用于绝对导入
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from config import load_config, get_credentials
from extract.sync import check_and_sync
from utils.storage import load_data
from utils.dates import get_weekday_cn
from extract.extractors import (
    extract_status_data,
    extract_form_data,
    extract_trend_data,
    extract_latest_ride_data,
    extract_week_data,
)
from extract.planned import extract_planned_data
from extract.cycle_memory import extract_cycle_memory, update_cycle_memory

__all__ = [
    'load_config',
    'get_credentials',
    'check_and_sync',
    'load_data',
    'get_weekday_cn',
    'extract_status_data',
    'extract_form_data',
    'extract_trend_data',
    'extract_latest_ride_data',
    'extract_week_data',
    'extract_planned_data',
    'extract_cycle_memory',
    'update_cycle_memory',
]
