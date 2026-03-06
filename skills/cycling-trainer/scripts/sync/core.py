"""
核心同步逻辑模块

负责增量同步、详情获取、数据过滤等核心功能
"""

from datetime import datetime as dt, timedelta
from .api import fetch_activities, fetch_activity_detail_api, fetch_activity_detail_browser
from .storage import load_activities, save_activities, merge_activities
from .state import update_sync_state


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
    
    # 如果有类型和时间，或者来源是STRAVA/OAUTH_CLIENT（已知来源），就保留
    return has_type or has_time or source in ['STRAVA', 'OAUTH_CLIENT']


def _print_activity_fetched(activity, is_new=True):
    """打印活动获取成功的信息"""
    activity_id = activity.get('id')
    name = activity.get('name', 'N/A')[:35]
    src = activity.get('source', 'UNKNOWN')
    interval_count = len(activity.get('icu_intervals', [])) if activity.get('icu_intervals') else 0
    prefix = "  ✓" if is_new else "  →"
    print(f"{prefix} {activity_id} ({src}): {name} [intervals: {interval_count}]")


def sync_activities(athlete_id, api_key, email=None, password=None, 
                    full=False, force_from=None, existing_activities=None):
    """
    同步活动数据
    
    Args:
        athlete_id: 骑手 ID
        api_key: API Key
        email: 邮箱（用于 Strava 数据）
        password: 密码（用于 Strava 数据）
        full: 是否全量同步
        force_from: 强制从指定日期同步 (格式: YYYY-MM-DD)
        existing_activities: 已有活动列表（如果为 None 则从文件加载）
    
    Returns:
        tuple: (all_activities, new_activities_count)
    """
    from .auth import login_session
    from .state import get_sync_state
    
    # 加载已有数据
    if existing_activities is None:
        existing_activities = load_activities()
    
    existing_ids = {a.get('id') for a in existing_activities}
    
    # 获取同步状态
    state = get_sync_state()
    
    # 判断是否增量
    if full:
        since_id = None
        print("全量同步模式...")
    elif force_from:
        since_id = None
        print(f"强制同步模式: 从 {force_from} 至今...")
    else:
        since_id = state.get("last_activity_id")
        if since_id:
            print(f"增量同步，从 {since_id} 开始...")
        else:
            print("首次同步，全量获取...")
    
    # 获取活动列表（API 方式，Strava 数据会是 stub）
    all_activities = fetch_activities(athlete_id, api_key, since_id)
    print(f"获取到 {len(all_activities)} 个原始活动")
    
    # 统计有多少 Strava stub 需要后续处理
    strava_stubs = [a for a in all_activities if a.get('source') == 'STRAVA' and '_note' in a]
    if strava_stubs:
        print(f"  其中 {len(strava_stubs)} 个 Strava 活动需要模拟浏览器获取详情")
    
    # 如果指定了 force_from，按日期过滤
    if force_from:
        try:
            force_date = dt.strptime(force_from, '%Y-%m-%d').date()
            all_activities = [
                a for a in all_activities 
                if a.get('start_date_local') and 
                dt.strptime(a['start_date_local'][:10], '%Y-%m-%d').date() >= force_date
            ]
            print(f"按日期过滤后: {len(all_activities)} 个活动 (从 {force_from} 起)")
        except ValueError:
            print(f"警告: 无效的日期格式 {force_from}，忽略过滤")
    
    # 登录获取 session（如果需要获取 Strava 详情）
    session = None
    if email and password:
        session = login_session(email, password)
        # 为 session 添加 auth header
        import base64
        basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
        session.headers.update({
            'Authorization': f'Basic {basic_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    # 分离：已有活动ID、新增活动
    new_activities = [a for a in all_activities if a.get('id') not in existing_ids]
    
    # 获取新增活动的详情
    if new_activities and session:
        print(f"获取 {len(new_activities)} 个新增活动的详情...")
        
        for i, a in enumerate(new_activities):
            activity_id = a.get('id')
            is_strava_stub = (a.get('source') == 'STRAVA' and '_note' in a)
            
            if _needs_detail_fetch(a):
                # Strava stub 用浏览器模拟方式，其他用标准 API
                if is_strava_stub:
                    detail = fetch_activity_detail_browser(activity_id, session, api_key, with_intervals=True)
                else:
                    detail = fetch_activity_detail_api(activity_id, api_key, with_intervals=True)
                
                if detail:
                    new_activities[i] = detail
                    _print_activity_fetched(detail)
                else:
                    print(f"  ✗ {activity_id}: 获取失败，保留原始数据")
    
    # 过滤掉真正无效的活动
    valid_activities = [a for a in new_activities if _is_valid_activity(a)]
    skipped_count = len(new_activities) - len(valid_activities)
    if skipped_count > 0:
        for a in new_activities:
            if not _is_valid_activity(a):
                print(f"  - 跳过无效活动: {a.get('id')}")
    
    # 合并数据
    all_activities = merge_activities(existing_activities, valid_activities)
    
    # 保存
    save_activities(all_activities)
    
    # 更新同步状态
    update_sync_state(all_activities)
    
    return all_activities, len(valid_activities)


def refresh_intervals_for_activities(activities, api_key, email, password, limit=50):
    """
    刷新活动的 intervals 详情
    
    Args:
        activities: 活动列表
        api_key: API Key
        email: 邮箱
        password: 密码
        limit: 最多刷新前 N 个活动
    
    Returns:
        list: 更新后的活动列表
    """
    from .auth import login_session
    
    # 登录获取session
    session = login_session(email, password)
    import base64
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    session.headers.update({
        'Authorization': f'Basic {basic_token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 获取最近N个活动的intervals详情
    print(f"刷新最近 {limit} 个活动的intervals详情...")
    
    updated_activities = list(activities)  # 复制列表
    
    for i, a in enumerate(updated_activities[:limit]):
        activity_id = a.get('id')
        name = a.get('name', 'N/A')[:30]
        
        # 检查是否已经有intervals
        if a.get('icu_intervals') and len(a.get('icu_intervals', [])) > 1:
            print(f"  {i+1}. {activity_id}: {name} - 已有 {len(a.get('icu_intervals', []))} intervals，跳过")
            continue
        
        # 根据数据来源选择获取方式
        source = a.get('source')
        is_strava_stub = (source == 'STRAVA' and '_note' in a)
        
        if is_strava_stub:
            detail = fetch_activity_detail_browser(activity_id, session, api_key, with_intervals=True)
        else:
            detail = fetch_activity_detail_api(activity_id, api_key, with_intervals=True)
        
        if detail and detail.get('icu_intervals'):
            updated_activities[i] = detail
            interval_count = len(detail.get('icu_intervals', []))
            print(f"  {i+1}. ✓ {activity_id}: {name} [intervals: {interval_count}]")
        else:
            print(f"  {i+1}. ✗ {activity_id}: {name} - 获取失败")
    
    # 保存
    save_activities(updated_activities)
    
    return updated_activities
