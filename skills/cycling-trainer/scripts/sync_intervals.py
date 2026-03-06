#!/usr/bin/env python3
"""
intervals.icu 数据同步脚本 - 增量更新

重构版本：功能拆分为多个模块，本文件仅作为入口点

功能：
- 只下载新增的活动
- 本地持久化保存
- 支持 CLI 调用

配置方式（优先级从高到低）：
1. 命令行参数 --athlete-id 和 --api-key
2. 环境变量 INTERVALS_ATHLETE_ID 和 INTERVALS_API_KEY
3. 配置文件 config.json（与 SKILL.md 同级目录）
"""

import argparse
import sys
from pathlib import Path

# 添加 sync 模块到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from sync import (
    load_config,
    get_credentials,
    get_sync_state,
    ensure_data_dir,
    load_activities,
    sync_activities,
    refresh_intervals_for_activities,
)


def show_status():
    """显示同步状态"""
    from sync.config import DATA_DIR
    from sync.state import CACHE_FILE
    from sync.storage import ACTIVITIES_FILE
    
    state = get_sync_state()
    
    if ACTIVITIES_FILE.exists():
        activities = load_activities()
        
        strava = len([a for a in activities if a.get('source') == 'STRAVA'])
        indoor = len([a for a in activities if a.get('source') == 'OAUTH_CLIENT'])
        with_intervals = len([a for a in activities if a.get('icu_intervals')])
        
        print(f"本地保存: {len(activities)} 个活动")
        print(f"  - 室内训练: {indoor}")
        print(f"  - 户外骑行: {strava}")
        print(f"  - 有intervals: {with_intervals}")
    else:
        print("本地无数据")
    
    if state.get("last_sync"):
        print(f"上次同步: {state['last_sync']}")
    else:
        print("从未同步")


def main():
    parser = argparse.ArgumentParser(description="intervals.icu 数据同步")
    parser.add_argument("athlete_id", nargs="?", help="骑手 ID (可选，优先从配置读取)")
    parser.add_argument("--api-key", help="API Key (可选，优先从配置读取)")
    parser.add_argument("--email", help="Strava 同步需要邮箱")
    parser.add_argument("--password", help="Strava 同步需要密码")
    parser.add_argument("--full", action="store_true", help="全量同步")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--refresh-intervals", action="store_true", help="刷新所有活动的intervals详情")
    parser.add_argument("--refresh-limit", type=int, default=50, help="刷新最近N个活动的intervals")
    parser.add_argument("--days", type=int, help="强制同步最近N天的数据")
    parser.add_argument("--from", dest="from_date", help="强制同步从指定日期至今的数据 (格式: YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # 获取认证信息（按优先级合并：命令行 > 环境变量 > 配置文件）
    athlete_id, api_key, email, password = get_credentials(args)
    
    if args.status:
        show_status()
    elif args.refresh_intervals:
        # 刷新intervals详情
        if not email or not password:
            print("错误: --refresh-intervals 需要 email 和 password (通过参数、环境变量或 config.json 提供)")
            sys.exit(1)
        
        activities = load_activities()
        if not activities:
            print("没有本地数据，先运行同步")
            return
        
        refresh_intervals_for_activities(activities, api_key, email, password, args.refresh_limit)
        print(f"\n刷新完成!")
    else:
        # 处理强制同步参数
        force_from = None
        if args.days:
            from datetime import timedelta, datetime as dt
            force_from = (dt.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        elif args.from_date:
            force_from = args.from_date
        
        # 执行同步
        ensure_data_dir()
        all_activities, new_count = sync_activities(
            athlete_id, api_key, email, password, 
            full=args.full, force_from=force_from
        )
        
        # 统计
        strava_count = len([a for a in all_activities if a.get('source') == 'STRAVA'])
        indoor_count = len([a for a in all_activities if a.get('source') == 'OAUTH_CLIENT'])
        
        print(f"\n同步完成!")
        print(f"  新增: {new_count} 个活动")
        print(f"  总计: {len(all_activities)} 个活动 (室内:{indoor_count}, 户外:{strava_count})")


if __name__ == "__main__":
    main()
