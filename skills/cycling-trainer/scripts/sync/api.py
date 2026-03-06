"""
API 请求模块

封装 intervals.icu 的所有 API 调用，包括：
- 标准 API（适用于 OAUTH_CLIENT 数据）
- 浏览器模拟方式（适用于 Strava 同步数据）
"""

import base64
import requests

BASE_URL = "https://intervals.icu"


def _build_auth_headers(api_key):
    """构建 Basic Auth headers"""
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Authorization': f'Basic {basic_token}'
    }


def fetch_activities(athlete_id, api_key, since_activity_id=None):
    """
    获取活动列表 - 使用纯 API 方式
    
    Args:
        athlete_id: 骑手 ID
        api_key: API Key
        since_activity_id: 如果指定，只获取该 ID 之后的新活动
    
    Returns:
        list: 活动列表（可能包含 Strava stub 数据）
    """
    headers = _build_auth_headers(api_key)
    params = {"oldest": "2025-01-01", "limit": 200}
    url = f"{BASE_URL}/api/v1/athlete/{athlete_id}/activities"
    
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code != 200:
        print(f"Error fetching activities: {resp.status_code}")
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
    """
    获取单个活动详情 - 使用标准 API（适用于非 Strava 数据）
    
    Args:
        activity_id: 活动 ID
        api_key: API Key
        with_intervals: 是否同时获取 intervals 数据
    
    Returns:
        dict: 活动详情，失败返回 None
    """
    headers = _build_auth_headers(api_key)
    url = f"{BASE_URL}/api/v1/activity/{activity_id}"
    if with_intervals:
        url += "?intervals=true"
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None


def fetch_activity_detail_browser(activity_id, session, api_key, with_intervals=True):
    """
    获取单个活动详情 - 模拟浏览器行为（仅用于 Strava stub 数据）
    
    浏览器方式返回两个独立请求的结果，需要合并以匹配 API 格式
    
    Args:
        activity_id: 活动 ID
        session: 已登录的 requests.Session
        api_key: API Key
        with_intervals: 是否同时获取 intervals 数据
    
    Returns:
        dict: 活动详情（已合并 intervals），失败返回 None
    """
    if not session:
        return None
    
    headers = _build_auth_headers(api_key)
    headers['Referer'] = f'https://intervals.icu/activities/{activity_id}/data'
    
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
