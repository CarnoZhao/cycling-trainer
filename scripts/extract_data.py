#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cycling Data Extractor
只负责从原始JSON中提取结构化数据，不做任何分析判断
所有分析和决策交给LLM处理
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path("/root/.openclaw/workspace/data/cycling/activities.json")

def load_data():
    """加载本地数据"""
    if not DATA_FILE.exists():
        return {"error": "No local data, please run sync first"}
    with open(DATA_FILE) as f:
        data = json.load(f)
    return sorted(data, key=lambda x: x.get('start_date', ''), reverse=True)

def extract_status_data():
    """提取状态相关原始数据"""
    data = load_data()
    if isinstance(data, dict) and 'error' in data:
        return data
    
    latest = data[0] if data else {}
    
    # 最近7天活动
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    week_activities = [
        {
            "date": a.get('start_date_local', '')[:10],
            "name": a.get('name', ''),
            "type": a.get('type', ''),
            "duration_min": round(a.get('moving_time', 0) / 60, 1),
            "distance_km": round(a.get('distance', 0) / 1000, 1),
            "training_load": a.get('icu_training_load', 0),
            "avg_watts": a.get('icu_weighted_avg_watts', 0),
            "avg_hr": a.get('average_heartrate', 0),
            "max_hr": a.get('max_heartrate', 0),
            "ftp": a.get('icu_ftp', 0),
            "ctl": a.get('icu_ctl', 0),
            "atl": a.get('icu_atl', 0),
        }
        for a in data
        if a.get('start_date', '') >= week_ago and a.get('icu_training_load', 0) > 0
    ]
    
    # 最近30天CTL/ATL历史
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    fitness_history = [
        {
            "date": a.get('start_date_local', '')[:10],
            "ctl": a.get('icu_ctl', 0),
            "atl": a.get('icu_atl', 0),
            "tsb": round((a.get('icu_ctl', 0) or 0) - (a.get('icu_atl', 0) or 0), 1),
            "training_load": a.get('icu_training_load', 0),
        }
        for a in data
        if a.get('start_date', '') >= month_ago and a.get('icu_ctl') is not None
    ][:30]
    
    return {
        "athlete_id": latest.get('icu_athlete_id', ''),
        "latest_activity": {
            "date": latest.get('start_date_local', '')[:10],
            "name": latest.get('name', ''),
            "ctl": latest.get('icu_ctl', 0),
            "atl": latest.get('icu_atl', 0),
            "tsb": round((latest.get('icu_ctl', 0) or 0) - (latest.get('icu_atl', 0) or 0), 1),
            "ftp": latest.get('icu_ftp', 0),
            "weight_kg": latest.get('icu_weight', 0),
            "resting_hr": latest.get('icu_resting_hr', 0),
            "lthr": latest.get('lthr', 0),
        },
        "week_activities": week_activities,
        "fitness_history": fitness_history,
        "total_activities": len(data),
    }

def extract_form_data():
    """提取状态走势相关原始数据（用于对比巅峰vs当前）"""
    data = load_data()
    if isinstance(data, dict) and 'error' in data:
        return data
    
    # 提取所有高强度间歇数据（>=9分钟的工作段）
    intervals_data = []
    for a in data:
        intervals = a.get('icu_intervals') or []
        for i in intervals:
            if i.get('type') == 'WORK' and i.get('moving_time', 0) >= 540:
                intervals_data.append({
                    "activity_date": a.get('start_date_local', '')[:10],
                    "activity_name": a.get('name', ''),
                    "duration_sec": i.get('moving_time', 0),
                    "duration_min": round(i.get('moving_time', 0) / 60, 1),
                    "avg_watts": i.get('average_watts', 0),
                    "max_watts": i.get('max_watts', 0),
                    "avg_hr": i.get('average_heartrate', 0),
                    "zone": i.get('zone', 0),
                    "training_load": i.get('training_load', 0),
                })
    
    # 按日期排序
    intervals_data.sort(key=lambda x: x['activity_date'])
    
    # 按心率分组的数据（便于相同努力程度对比）
    hr_groups = {}
    for i in intervals_data:
        hr = i['avg_hr']
        if hr:
            # 按5bpm分组
            hr_key = f"{hr//5*5}-{hr//5*5+4}"
            if hr_key not in hr_groups:
                hr_groups[hr_key] = []
            hr_groups[hr_key].append(i)
    
    # 取每个HR组最近的记录
    hr_group_latest = {
        k: v[-5:] for k, v in hr_groups.items() if len(v) >= 2
    }
    
    return {
        "total_intervals": len(intervals_data),
        "all_intervals": intervals_data[-50:],  # 最近50个间歇
        "hr_grouped": hr_group_latest,
        "date_range": {
            "earliest": intervals_data[0]['activity_date'] if intervals_data else None,
            "latest": intervals_data[-1]['activity_date'] if intervals_data else None,
        }
    }

def extract_trend_data():
    """提取趋势分析原始数据"""
    data = load_data()
    if isinstance(data, dict) and 'error' in data:
        return data
    
    # 最近30天的每日数据
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    daily_data = [
        {
            "date": a.get('start_date_local', '')[:10],
            "name": a.get('name', ''),
            "type": a.get('type', ''),
            "duration_min": round(a.get('moving_time', 0) / 60, 1),
            "distance_km": round(a.get('distance', 0) / 1000, 1),
            "elevation_m": a.get('total_elevation_gain', 0),
            "training_load": a.get('icu_training_load', 0),
            "intensity": a.get('icu_intensity', 0),
            "avg_watts": a.get('icu_weighted_avg_watts', 0),
            "avg_hr": a.get('average_heartrate', 0),
            "decoupling": a.get('decoupling'),
            "efficiency_factor": a.get('icu_efficiency_factor', 0),
            "ftp": a.get('icu_ftp', 0),
            "ctl": a.get('icu_ctl', 0),
            "atl": a.get('icu_atl', 0),
        }
        for a in data
        if a.get('start_date', '') >= month_ago and a.get('icu_training_load', 0) > 0
    ][:30]
    
    # 按周汇总
    weeks = {}
    for a in daily_data:
        try:
            dt = datetime.strptime(a['date'], '%Y-%m-%d')
            week_key = dt.isocalendar()[:2]  # (year, week)
            if week_key not in weeks:
                weeks[week_key] = {
                    "week": f"{week_key[0]}-W{week_key[1]:02d}",
                    "count": 0,
                    "total_duration_min": 0,
                    "total_distance_km": 0,
                    "total_load": 0,
                    "avg_intensity": [],
                    "activities": [],
                }
            weeks[week_key]["count"] += 1
            weeks[week_key]["total_duration_min"] += a['duration_min']
            weeks[week_key]["total_distance_km"] += a['distance_km']
            weeks[week_key]["total_load"] += a['training_load']
            weeks[week_key]["avg_intensity"].append(a['intensity'])
            weeks[week_key]["activities"].append(a)
        except:
            pass
    
    # 计算平均强度
    for w in weeks.values():
        if w['avg_intensity']:
            w['avg_intensity'] = round(sum(w['avg_intensity']) / len(w['avg_intensity']), 2)
        else:
            w['avg_intensity'] = 0
    
    return {
        "daily_data": daily_data,
        "weekly_summary": list(weeks.values())[-4:],  # 最近4周
    }

def extract_latest_ride_data():
    """提取最近一次骑行的详细数据"""
    data = load_data()
    if isinstance(data, dict) and 'error' in data:
        return data
    
    # 找到最新的一条有数据的骑行
    latest = None
    for a in data:
        if a.get('icu_training_load', 0) > 0:
            latest = a
            break
    
    if not latest:
        return {"error": "No ride data found"}
    
    # 功率区间时间
    zone_times = {}
    for z in latest.get('icu_zone_times', []):
        zone_id = z.get('id', '')
        secs = z.get('secs', 0)
        zone_times[zone_id] = round(secs / 60, 1)
    
    # 心率区间时间
    hr_zones = latest.get('icu_hr_zone_times', [])
    hr_zone_times = {f"Z{i+1}": round(hr_zones[i]/60, 1) if i < len(hr_zones) else 0 for i in range(7)}
    
    # 间歇详情
    intervals = latest.get('icu_intervals', [])
    work_intervals = []
    recovery_intervals = []
    
    for i in intervals:
        interval_data = {
            "type": i.get('type'),
            "duration_min": round(i.get('moving_time', 0) / 60, 1),
            "avg_watts": i.get('average_watts', 0),
            "max_watts": i.get('max_watts', 0),
            "avg_hr": i.get('average_heartrate', 0),
            "zone": i.get('zone', 0),
            "training_load": i.get('training_load', 0),
        }
        if i.get('type') == 'WORK':
            work_intervals.append(interval_data)
        else:
            recovery_intervals.append(interval_data)
    
    return {
        "activity": {
            "id": latest.get('id'),
            "date": latest.get('start_date_local', '')[:10],
            "name": latest.get('name', ''),
            "type": latest.get('type', ''),
            "device": latest.get('device_name', ''),
            "trainer": latest.get('trainer', False),
        },
        "metrics": {
            "duration_min": round(latest.get('moving_time', 0) / 60, 1),
            "distance_km": round(latest.get('distance', 0) / 1000, 1),
            "elevation_m": latest.get('total_elevation_gain', 0),
            "avg_speed_kmh": round(latest.get('average_speed', 0) * 3.6, 1) if latest.get('average_speed') else 0,
            "max_speed_kmh": round(latest.get('max_speed', 0) * 3.6, 1) if latest.get('max_speed') else 0,
        },
        "power": {
            "avg_watts": latest.get('icu_weighted_avg_watts', 0),
            "max_watts": latest.get('max_watts', 0),
            "normalized_watts": latest.get('icu_normalized_watts', 0),
            "training_load": latest.get('icu_training_load', 0),
            "intensity": latest.get('icu_intensity', 0),
            "ftp": latest.get('icu_ftp', 0),
            "joules": latest.get('icu_joules', 0),
        },
        "heart_rate": {
            "avg_hr": latest.get('average_heartrate', 0),
            "max_hr": latest.get('max_heartrate', 0),
            "resting_hr": latest.get('icu_resting_hr', 0),
            "lthr": latest.get('lthr', 0),
        },
        "efficiency": {
            "decoupling_pct": latest.get('decoupling'),
            "efficiency_factor": latest.get('icu_efficiency_factor', 0),
            "variability_index": latest.get('icu_variability_index', 0),
        },
        "zones": {
            "power_zone_times_min": zone_times,
            "hr_zone_times_min": hr_zone_times,
        },
        "intervals": {
            "work_count": len(work_intervals),
            "recovery_count": len(recovery_intervals),
            "work_details": work_intervals,
            "recovery_details": recovery_intervals,
        },
    }

def extract_week_data():
    """提取本周数据"""
    data = load_data()
    if isinstance(data, dict) and 'error' in data:
        return data
    
    # 获取本周一
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    
    week_activities = []
    for a in data:
        try:
            activity_date = datetime.strptime(a.get('start_date_local', '')[:10], '%Y-%m-%d')
            if activity_date >= monday:
                week_activities.append({
                    "date": a.get('start_date_local', '')[:10],
                    "weekday": activity_date.strftime('%A'),
                    "name": a.get('name', ''),
                    "type": a.get('type', ''),
                    "duration_min": round(a.get('moving_time', 0) / 60, 1),
                    "distance_km": round(a.get('distance', 0) / 1000, 1),
                    "training_load": a.get('icu_training_load', 0),
                    "avg_watts": a.get('icu_weighted_avg_watts', 0),
                    "avg_hr": a.get('average_heartrate', 0),
                    "intensity": a.get('icu_intensity', 0),
                    "ftp": a.get('icu_ftp', 0),
                    "ctl": a.get('icu_ctl', 0),
                    "atl": a.get('icu_atl', 0),
                })
        except:
            pass
    
    # 汇总统计
    total_duration = sum(a['duration_min'] for a in week_activities)
    total_distance = sum(a['distance_km'] for a in week_activities)
    total_load = sum(a['training_load'] for a in week_activities)
    avg_intensity = sum(a['intensity'] for a in week_activities) / len(week_activities) if week_activities else 0
    
    return {
        "week_start": monday.strftime('%Y-%m-%d'),
        "today": today.strftime('%Y-%m-%d'),
        "activities": week_activities,
        "summary": {
            "count": len(week_activities),
            "total_duration_min": round(total_duration, 1),
            "total_distance_km": round(total_distance, 1),
            "total_load": round(total_load, 1),
            "avg_intensity": round(avg_intensity, 2),
        },
        "current_status": {
            "ctl": week_activities[0]['ctl'] if week_activities else 0,
            "atl": week_activities[0]['atl'] if week_activities else 0,
            "tsb": round((week_activities[0]['ctl'] or 0) - (week_activities[0]['atl'] or 0), 1) if week_activities else 0,
            "ftp": week_activities[0]['ftp'] if week_activities else 0,
        } if week_activities else {},
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract cycling data for LLM analysis')
    parser.add_argument('--status', action='store_true', help='Extract status data')
    parser.add_argument('--form', action='store_true', help='Extract form trend data')
    parser.add_argument('--trend', action='store_true', help='Extract trend data')
    parser.add_argument('--latest', action='store_true', help='Extract latest ride data')
    parser.add_argument('--week', action='store_true', help='Extract week data')
    parser.add_argument('--full', action='store_true', help='Extract all data')
    
    args = parser.parse_args()
    
    if args.status:
        result = extract_status_data()
    elif args.form:
        result = extract_form_data()
    elif args.trend:
        result = extract_trend_data()
    elif args.latest:
        result = extract_latest_ride_data()
    elif args.week:
        result = extract_week_data()
    elif args.full:
        result = {
            "status": extract_status_data(),
            "form": extract_form_data(),
            "trend": extract_trend_data(),
            "latest": extract_latest_ride_data(),
            "week": extract_week_data(),
        }
    else:
        result = extract_status_data()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
