"""
核心同步逻辑模块

负责增量同步、详情获取、数据过滤等核心功能
"""

import sys
from pathlib import Path
from datetime import datetime as dt, timedelta

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sync.api import fetch_activities, fetch_activity_detail_api, fetch_activity_detail_browser
from sync.auth import login_session
from utils.storage import load_activities, save_activities, merge_activities
from sync.state import update_sync_state


def _needs_detail_fetch(activity):
    """
    判断活动是否需要获取详情

    需要获取详情的情况：
    1. Strava stub 活动 (source=STRAVA 且包含 _note 字段)
    2. 空stub活动 (type=None or moving_time=0)
    3. 没有 icu_intervals 的活动（API列表返回的数据不完整）

    Args:
        activity: 活动数据 dict

    Returns:
        bool: 是否需要获取详情
    """
    source = activity.get('source')
    has_type = activity.get('type') is not None
    has_time = activity.get('moving_time', 0) > 0
    has_intervals = 'icu_intervals' in activity
    is_strava_stub = (source == 'STRAVA' and '_note' in activity)

    return is_strava_stub or (not has_type) or (not has_time) or (not has_intervals)


def _is_valid_activity(activity):
    """
    判断活动是否有效（非空数据）

    Args:
        activity: 活动数据 dict

    Returns:
        bool: 是否有效
    """
    has_type = activity.get('type') is not None
    has_time = activity.get('moving_time', 0) > 0
    source = activity.get('source')

    # 室内训练（OAUTH_CLIENT）只要有类型和时间就有效
    if source == 'OAUTH_CLIENT':
        return has_type and has_time

    # Strava 活动需要更多检查
    return has_type and has_time


def sync_activities(athlete_id, api_key, email=None, password=None, full=False, force_from=None):
    """
    同步活动数据（增量或全量）

    Args:
        athlete_id: 骑手ID
        api_key: API Key
        email: Strava邮箱（可选）
        password: Strava密码（可选）
        full: 是否全量同步
        force_from: 强制从指定日期同步（格式：YYYY-MM-DD）

    Returns:
        tuple: (all_activities, new_count)
    """
    # 加载现有数据
    existing = load_activities()
    if isinstance(existing, dict) and 'error' in existing:
        existing = []

    # 确定同步范围
    if full:
        oldest = "2020-01-01"
        print(f"[Sync] Full sync from {oldest}")
    elif force_from:
        oldest = force_from
        print(f"[Sync] Force sync from {oldest}")
    else:
        # 增量同步：从最新活动日期开始
        if existing:
            latest_date = existing[0].get('start_date_local', '')[:10] if existing else None
            if latest_date:
                # 往前多取7天，确保不遗漏
                oldest_dt = dt.strptime(latest_date, '%Y-%m-%d') - timedelta(days=7)
                oldest = oldest_dt.strftime('%Y-%m-%d')
            else:
                oldest = "2024-01-01"
        else:
            oldest = "2024-01-01"
        print(f"[Sync] Incremental sync from {oldest}")

    # 获取活动列表
    activities = fetch_activities(athlete_id, api_key, oldest)

    if not activities:
        print("[Sync] No activities found")
        return existing, 0

    print(f"[Sync] Fetched {len(activities)} activities from API")

    # 获取需要详情的活动
    needs_detail = [a for a in activities if _needs_detail_fetch(a)]
    print(f"[Sync] {len(needs_detail)} activities need detail fetch")

    # 获取详情
    if needs_detail and email and password:
        print(f"[Sync] Fetching details for {len(needs_detail)} activities...")

        # 先登录获取 session
        session = login_session(email, password)

        if session:
            for i, activity in enumerate(needs_detail, 1):
                aid = activity.get('id')
                print(f"  [{i}/{len(needs_detail)}] Fetching details for activity {aid}...", end='', flush=True)

                # 尝试 API 方式获取详情
                detail = fetch_activity_detail_api(aid, api_key)

                # 如果 API 失败，尝试浏览器方式
                if not detail and session:
                    detail = fetch_activity_detail_browser(aid, session)

                if detail:
                    # 合并详情到活动数据
                    activity.update(detail)
                    print(" ✓")
                else:
                    print(" ✗")
        else:
            print("[Sync] Login failed, skipping detail fetch")

    # 过滤有效活动
    valid_activities = [a for a in activities if _is_valid_activity(a)]
    print(f"[Sync] {len(valid_activities)} valid activities after filtering")

    # 合并数据
    all_activities = merge_activities(existing, valid_activities)

    # 保存
    save_activities(all_activities)

    # 更新同步状态
    update_sync_state(len(valid_activities))

    new_count = len(valid_activities)
    return all_activities, new_count


def refresh_intervals_for_activities(activities, api_key, email, password, limit=50):
    """
    刷新活动的 intervals 详情

    Args:
        activities: 活动列表
        api_key: API Key
        email: Strava邮箱
        password: Strava密码
        limit: 只刷新最近N个活动
    """
    # 先登录获取 session
    session = login_session(email, password)

    if not session:
        print("Login failed, cannot refresh intervals")
        return

    # 只处理最近的活动
    to_refresh = activities[:limit]

    # 筛选没有 intervals 的活动
    needs_refresh = [a for a in to_refresh if not a.get('icu_intervals')]

    print(f"Refreshing intervals for {len(needs_refresh)} activities...")

    for i, activity in enumerate(needs_refresh, 1):
        aid = activity.get('id')
        print(f"  [{i}/{len(needs_refresh)}] Activity {aid}...", end='', flush=True)

        # 尝试 API 方式
        detail = fetch_activity_detail_api(aid, api_key)

        # 如果 API 失败，尝试浏览器方式
        if not detail:
            detail = fetch_activity_detail_browser(aid, session)

        if detail:
            activity.update(detail)
            print(" ✓")
        else:
            print(" ✗")

    # 保存更新后的数据
    save_activities(activities)
    print(f"\nSaved {len(activities)} activities")
