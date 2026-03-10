"""
计划训练数据获取模块

负责从 intervals.icu API 获取已安排的训练计划
"""

import sys
from pathlib import Path
import json
import urllib.request
import base64
from datetime import datetime, timedelta

# 确保 scripts 目录在路径中
SCRIPT_DIR = Path(__file__).parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def fetch_planned_workouts(athlete_id=None, api_key=None, days=7):
    """
    从 intervals.icu API 获取已安排的训练计划

    Args:
        athlete_id: 骑手 ID（为 None 时从配置获取）
        api_key: API Key（为 None 时从配置获取）
        days: 向前查看的天数

    Returns:
        dict: 包含 count, date_range, workouts
    """
    # 获取凭据
    if not athlete_id or not api_key:
        from config import get_credentials
        creds = get_credentials()
        cred_athlete_id, cred_api_key = creds[0], creds[1]

        athlete_id = athlete_id or cred_athlete_id
        api_key = api_key or cred_api_key

    # 检查凭据是否完整
    if not athlete_id or not api_key:
        return {"error": "Missing credentials"}

    # 计算日期范围
    today = datetime.now()
    oldest = today.strftime('%Y-%m-%d')
    newest = (today + timedelta(days=days)).strftime('%Y-%m-%d')

    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/eventscsv?oldest={oldest}&newest={newest}&category=WORKOUT"

    # 构建Basic Auth
    auth_str = base64.b64encode(f"API_KEY:{api_key}".encode()).decode()

    headers = {
        'accept': '*/*',
        'authorization': f'Basic {auth_str}'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))

        # 简化数据结构
        workouts = []
        for item in data:
            workout = {
                "id": item.get("id"),
                "date": item.get("start_date_local", "")[:10],
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "duration_min": round(item.get("moving_time", 0) / 60, 1) if item.get("moving_time") else None,
                "training_load": item.get("icu_training_load"),
                "ftp": item.get("icu_ftp"),
                "intensity": item.get("icu_intensity"),
                "indoor": item.get("indoor", False),
                "entered": item.get("entered", False),  # 是否已完成
                "paired_activity_id": item.get("paired_activity_id"),  # 关联的实际活动ID
            }

            # 提取workout结构信息
            workout_doc = item.get("workout_doc", {})
            if workout_doc:
                workout["avg_watts"] = workout_doc.get("average_watts")
                workout["normalized_power"] = workout_doc.get("normalized_power")
                workout["steps"] = len(workout_doc.get("steps", []))

                # 提取功率区间分布
                zone_times = workout_doc.get("zoneTimes", [])
                workout["zones"] = {
                    z.get("id", "unknown").replace("Z", ""): round(z.get("secs", 0) / 60, 1)
                    for z in zone_times if z.get("secs", 0) > 0
                }

            workouts.append(workout)

        return {
            "count": len(workouts),
            "date_range": {"from": oldest, "to": newest},
            "workouts": workouts
        }

    except Exception as e:
        return {"error": str(e), "url": url}


def extract_planned_data(days=7):
    """
    提取已安排的训练计划数据

    Args:
        days: 向前查看的天数

    Returns:
        dict: 计划训练数据
    """
    return fetch_planned_workouts(days=days)
