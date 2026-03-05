#!/usr/bin/env python3
"""
intervals.icu 数据获取脚本 - 支持 Strava 同步活动
Usage: python3 fetch_intervals.py <athlete_id> --api-key <key> --days 90
"""

import argparse
import json
import requests
import sys
import base64
from datetime import datetime, timedelta

BASE_URL = "https://intervals.icu"

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

def get_athlete_data(athlete_id, api_key=None, days=90, email=None, password=None):
    """获取骑手基本信息和训练数据"""
    
    session = None
    if email and password:
        session = login_session(email, password)
    
    # Basic auth header
    basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://intervals.icu/activities/',
        'Authorization': f'Basic {basic_token}'
    }
    
    # 获取骑手信息
    athlete_url = f"{BASE_URL}/api/v1/athlete/{athlete_id}"
    athlete_resp = requests.get(athlete_url, headers=headers)
    
    if athlete_resp.status_code != 200:
        print(f"Error fetching athlete: {athlete_resp.status_code}", file=sys.stderr)
        sys.exit(1)
    
    athlete = athlete_resp.json()
    
    # 获取活动列表
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    activities_url = f"{BASE_URL}/api/v1/athlete/{athlete_id}/activities"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat(),
        "limit": 500
    }
    
    activities_resp = requests.get(activities_url, headers=headers, params=params)
    all_activities = activities_resp.json() if activities_resp.status_code == 200 else []
    
    # 过滤掉空活动占位符
    activities = [a for a in all_activities if a.get("type") and a.get("moving_time", 0) > 0]
    
    # 对于 Strava 同步的活动（type=None 但有 id），尝试通过网页 session 获取
    stub_activities = [a for a in all_activities if not a.get("type") or a.get("moving_time", 0) == 0]
    
    if session and stub_activities:
        print(f"发现 {len(stub_activities)} 个 Strava 同步活动，尝试获取详情...", file=sys.stderr)
        for stub in stub_activities:
            activity_id = stub.get("id")
            if not activity_id:
                continue
            
            try:
                # 获取活动详情
                url = f"{BASE_URL}/api/activity/{activity_id}"
                resp = session.get(url, headers=headers)
                if resp.status_code == 200:
                    detail = resp.json()
                    # 更新 stub 为完整数据
                    idx = all_activities.index(stub)
                    all_activities[idx] = detail
                    print(f"  ✓ 获取活动 {activity_id}: {detail.get('name', 'N/A')[:30]}", file=sys.stderr)
                else:
                    print(f"  ✗ 获取活动 {activity_id} 失败: {resp.status_code}", file=sys.stderr)
            except Exception as e:
                print(f"  ✗ 获取活动 {activity_id} 异常: {e}", file=sys.stderr)
        
        # 重新过滤
        activities = [a for a in all_activities if a.get("type") and a.get("moving_time", 0) > 0]
    
    # 计算关键指标
    result = {
        "athlete": {
            "id": athlete.get("id"),
            "name": athlete.get("name"),
            "ftp": athlete.get("ftp", {}).get("value"),
            "weight": athlete.get("weight")
        },
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        },
        "activities": activities,
        "stub_count": len(stub_activities),
        "summary": {
            "total_activities": len(activities),
            "total_duration_minutes": sum(a.get("moving_time", 0) for a in activities) / 60,
            "total_distance_km": sum(a.get("distance", 0) for a in activities) / 1000,
            "total_elevation_m": sum(a.get("total_elevation_gain", 0) for a in activities)
        }
    }
    
    return result

def calculate_metrics(activities, ftp):
    """计算训练负荷指标"""
    if not ftp or not activities:
        return {}
    
    # CTL (42天慢性训练负荷)
    recent_activities = sorted(activities, key=lambda x: x.get("start_date_local", ""), reverse=True)[:42]
    
    total_stress = 0
    for a in recent_activities:
        if "icu_training_load" in a:
            total_stress += a.get("icu_training_load", 0) or 0
    
    ctl = total_stress / 42 if recent_activities else 0
    
    # ATL (7天急性训练负荷)
    last_week = sorted(activities, key=lambda x: x.get("start_date_local", ""), reverse=True)[:7]
    atl = sum(a.get("icu_training_load", 0) or 0 for a in last_week) / 7 if last_week else 0
    
    # TSB (训练压力平衡)
    tsb = ctl - atl
    
    return {
        "ctl": round(ctl, 1),
        "atl": round(atl, 1),
        "tsb": round(tsb, 1),
        "form": "峰值状态" if tsb > 15 else ("最佳竞技" if tsb > 5 else ("维持" if tsb > -10 else "恢复"))
    }

def main():
    parser = argparse.ArgumentParser(description="获取 intervals.icu 训练数据")
    parser.add_argument("athlete_id", help="骑手 ID")
    parser.add_argument("--api-key", help="API Key")
    parser.add_argument("--email", help="Strava 同步活动需要网页登录邮箱")
    parser.add_argument("--password", help="Strava 同步活动需要网页登录密码")
    parser.add_argument("--days", type=int, default=90, help="获取天数（默认90天）")
    parser.add_argument("--output", choices=["json", "csv"], default="json", help="输出格式")
    
    args = parser.parse_args()
    
    data = get_athlete_data(args.athlete_id, args.api_key, args.days, args.email, args.password)
    
    # 计算指标
    if data["athlete"]["ftp"]:
        metrics = calculate_metrics(data["activities"], data["athlete"]["ftp"])
        data["metrics"] = metrics
    
    if args.output == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        # CSV 输出活动列表
        print("date,name,distance_km,duration_min,elevation_m,load,avg_watts")
        for a in data["activities"][:100]:
            print(f"{a.get('start_date_local', '')[:10]},{a.get('name', 'N/A')},{a.get('distance', 0)/1000:.1f},{a.get('moving_time', 0)/60:.0f},{a.get('total_elevation_gain', 0)},{a.get('icu_training_load', '')},{a.get('icu_weighted_avg_watts', '')}")

if __name__ == "__main__":
    main()