#!/usr/bin/env python3
"""
intervals.icu 数据同步脚本 - 增量更新
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
import json
import os
import requests
import sys
import base64
from datetime import datetime as dt
from pathlib import Path

BASE_URL = "https://intervals.icu"
SCRIPT_DIR = Path(__file__).parent.parent  # skills/cycling-trainer/
DATA_DIR = SCRIPT_DIR.parent.parent / "data/cycling"
CACHE_FILE = DATA_DIR / "sync_state.json"
ACTIVITIES_FILE = DATA_DIR / "activities.json"
CONFIG_FILE = SCRIPT_DIR / "config.json"

def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def get_credentials(args):
    """获取认证信息，按优先级合并（命令行 > 环境变量 > 配置文件）"""
    config = load_config()
    
    athlete_id = args.athlete_id or os.getenv('INTERVALS_ATHLETE_ID') or config.get('athlete_id')
    api_key = args.api_key or os.getenv('INTERVALS_API_KEY') or config.get('api_key')
    email = args.email or os.getenv('INTERVALS_EMAIL') or config.get('email')
    password = args.password or os.getenv('INTERVALS_PASSWORD') or config.get('password')
    
    return athlete_id, api_key, email, password

def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
def get_sync_state():
    """获取同步状态"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {"last_sync": None, "last_activity_id": None, "activities_count": 0}

def save_sync_state(state):
    """保存同步状态"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def login_session(email, password):
    """模拟网页登录获取 session"""
    session = requests.Session()
    login_data = {
        'email': email,
        'password': password,
        'deviceClass': "desktop"
    }
    resp = session.post(f'{BASE_URL}/api/login', data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    return session

def fetch_activities(athlete_id, api_key, since_activity_id=None):
    """获取活动列表 - 使用纯 API 方式"""
    
    # Basic auth header（和你的参考代码一致）
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Authorization': f'Basic {basic_token}'
    }
    
    # 直接获取（从2025年开始）
    params = {"oldest": "2025-01-01", "limit": 200}
    url = f"{BASE_URL}/api/v1/athlete/{athlete_id}/activities"
    
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code}", file=sys.stderr)
        return []
    
    all_activities = resp.json()
    
    # 如果指定了since_activity_id，找到该ID之后的所有活动
    if since_activity_id:
        for i, a in enumerate(all_activities):
            if a.get('id') == since_activity_id:
                all_activities = all_activities[:i]
                break
    
    return all_activities

def fetch_activity_detail_api(activity_id, api_key, with_intervals=True):
    """获取单个活动详情 - 使用标准 API（适用于非 Strava 数据）"""
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Authorization': f'Basic {basic_token}'
    }
    
    # 使用 intervals=true 参数一次性获取活动和 intervals 数据
    url = f"{BASE_URL}/api/v1/activity/{activity_id}"
    if with_intervals:
        url += "?intervals=true"
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None


def fetch_activity_detail_browser(activity_id, session, api_key, with_intervals=True):
    """获取单个活动详情 - 模拟浏览器行为（仅用于 Strava stub 数据）
    
    浏览器方式返回两个独立请求的结果，需要合并以匹配 API 格式
    """
    if not session:
        return None
    
    # 构建认证 header（和你的代码一致）
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://intervals.icu/activities/{activity_id}/data',
        'Authorization': f'Basic {basic_token}'
    }
    
    # 第一步：获取活动基础数据（去掉 /v1/）
    url = f"{BASE_URL}/api/activity/{activity_id}"
    resp = session.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"  ✗ {activity_id}: 获取活动详情失败 ({resp.status_code})")
        return None
    
    activity = resp.json()
    
    # 第二步：获取 intervals 数据（如果需要）
    if with_intervals:
        interval_url = f"{BASE_URL}/api/activity/{activity_id}/intervals"
        interval_resp = session.get(interval_url, headers=headers)
        if interval_resp.status_code == 200:
            interval_data = interval_resp.json()
            # 合并 intervals 数据到 activity，匹配 API 格式
            activity['icu_intervals'] = interval_data.get('icu_intervals', [])
            activity['icu_groups'] = interval_data.get('icu_groups', [])
        else:
            activity['icu_intervals'] = []
            activity['icu_groups'] = []
    
    return activity

def sync(athlete_id, api_key, email=None, password=None, full=False, refresh_intervals=False, force_from=None):
    """同步数据
    refresh_intervals: 强制刷新所有活动的intervals详情
    force_from: 强制同步从指定日期的数据 (格式: YYYY-MM-DD)
    """
    from datetime import datetime as dt
    ensure_data_dir()
    
    # 加载已有数据
    existing_activities = []
    if ACTIVITIES_FILE.exists():
        with open(ACTIVITIES_FILE) as f:
            existing_activities = json.load(f)
    
    existing_ids = {a.get('id') for a in existing_activities}
    
    # 获取同步状态
    state = get_sync_state()
    
    # 判断是否增量
    if full:
        since_id = None
        print("全量同步模式...")
    elif force_from:
        # 强制从指定日期同步
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
        from datetime import datetime as dt
        try:
            force_date =  dt.strptime(force_from, '%Y-%m-%d').date()
            all_activities = [
                a for a in all_activities 
                if a.get('start_date_local') and 
                 dt.strptime(a['start_date_local'][:10], '%Y-%m-%d').date() >= force_date
            ]
            print(f"按日期过滤后: {len(all_activities)} 个活动 (从 {force_from} 起)")
        except ValueError:
            print(f"警告: 无效的日期格式 {force_from}，忽略过滤")
    
    # 找出需要获取详情的活动（ Strava stub 或新增）
    session = None
    if email and password:
        session = login_session(email, password)
    
    # 为 session 添加 auth header（用于获取详情）
    if session and api_key:
        basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
        session.headers.update({
            'Authorization': f'Basic {basic_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    # 分离：已有活动ID、新增活动
    new_activities = [a for a in all_activities if a.get('id') not in existing_ids]
    
    if new_activities and session:
        print(f"获取 {len(new_activities)} 个新增活动的详情...")
        
        for a in new_activities:
            activity_id = a.get('id')
            source = a.get('source')
            has_type = a.get('type') is not None
            has_time = a.get('moving_time', 0) > 0
            
            # 需要获取详情的情况：
            # 1. Strava stub 活动 (source=STRAVA 且包含 _note 字段)
            # 2. 空stub活动 (type=None or moving_time=0)
            is_strava_stub = (source == 'STRAVA' and '_note' in a)
            need_detail = is_strava_stub or (not has_type) or (not has_time)
            
            if need_detail:
                # Strava stub 用浏览器模拟方式，其他用标准 API
                if is_strava_stub:
                    detail = fetch_activity_detail_browser(activity_id, session, api_key, with_intervals=True)
                else:
                    detail = fetch_activity_detail_api(activity_id, api_key, with_intervals=True)
                if detail:
                    idx = new_activities.index(a)
                    new_activities[idx] = detail
                    name = detail.get('name', 'N/A')[:35]
                    src = detail.get('source', 'UNKNOWN')
                    # 检查是否有详细的间歇数据
                    has_intervals = 'icu_intervals' in detail and detail['icu_intervals']
                    interval_count = len(detail.get('icu_intervals', [])) if has_intervals else 0
                    print(f"  ✓ {activity_id} ({src}): {name} [intervals: {interval_count}]")
                else:
                    print(f"  ✗ {activity_id}: 获取失败，保留原始数据")
    
    # 过滤掉真正无效的活动（不是stub，是真正的空数据）
    valid_activities = []
    for a in new_activities:
        has_type = a.get('type') is not None
        has_time = a.get('moving_time', 0) > 0
        source = a.get('source')
        
        # 如果有类型和时间，或者来源是STRAVA/OAUTH_CLIENT（已知来源），就保留
        if has_type or has_time or source in ['STRAVA', 'OAUTH_CLIENT']:
            valid_activities.append(a)
        else:
            print(f"  - 跳过无效活动: {a.get('id')}")
    
    # 合并数据
    really_new = valid_activities
    all_activities = valid_activities + existing_activities
    
    # 按时间排序（新的在前）
    all_activities = sorted(all_activities, key=lambda x: x.get('start_date', ''), reverse=True)
    
    # 去重
    seen = set()
    unique_activities = []
    for a in all_activities:
        aid = a.get('id')
        if aid not in seen:
            seen.add(aid)
            unique_activities.append(a)
    
    # 保存
    with open(ACTIVITIES_FILE, 'w') as f:
        json.dump(unique_activities, f, indent=2)
    
    # 统计
    strava_count = len([a for a in unique_activities if a.get('source') == 'STRAVA'])
    indoor_count = len([a for a in unique_activities if a.get('source') == 'OAUTH_CLIENT'])
    
    # 更新同步状态
    if unique_activities:
        new_state = {
            "last_sync": dt.now().isoformat(),
            "last_activity_id": unique_activities[0].get('id'),
            "activities_count": len(unique_activities)
        }
        save_sync_state(new_state)
    
    print(f"\n同步完成!")
    print(f"  新增: {len(really_new)} 个活动")
    print(f"  总计: {len(unique_activities)} 个活动 (室内:{indoor_count}, 户外:{strava_count})")
    
    return unique_activities

def show_status():
    """显示同步状态"""
    state = get_sync_state()
    if ACTIVITIES_FILE.exists():
        with open(ACTIVITIES_FILE) as f:
            activities = json.load(f)
        
        strava = len([a for a in activities if a.get('source') == 'STRAVA'])
        indoor = len([a for a in activities if a.get('source') == 'OAUTH_CLIENT'])
        
        # 统计有intervals的活动
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

def refresh_intervals(athlete_id, api_key, email, password, limit=50):
    """刷新活动的intervals详情"""
    if not ACTIVITIES_FILE.exists():
        print("没有本地数据，先运行同步")
        return
    
    with open(ACTIVITIES_FILE) as f:
        activities = json.load(f)
    
    # 登录获取session
    session = login_session(email, password)
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    session.headers.update({
        'Authorization': f'Basic {basic_token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 获取最近N个活动的intervals详情
    print(f"刷新最近 {limit} 个活动的intervals详情...")
    
    for i, a in enumerate(activities[:limit]):
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
            activities[i] = detail
            interval_count = len(detail.get('icu_intervals', []))
            print(f"  {i+1}. ✓ {activity_id}: {name} [intervals: {interval_count}]")
        else:
            print(f"  {i+1}. ✗ {activity_id}: {name} - 获取失败")
    
    # 保存
    with open(ACTIVITIES_FILE, 'w') as f:
        json.dump(activities, f, indent=2)
    
    print(f"\n刷新完成!")

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
        refresh_intervals(athlete_id, api_key, email, password, args.refresh_limit)
    else:
        # 处理强制同步参数
        force_from = None
        if args.days:
            from datetime import timedelta
            force_from = (dt.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        elif args.from_date:
            force_from = args.from_date
        
        sync(athlete_id, api_key, email, password, args.full, force_from)

if __name__ == "__main__":
    main()