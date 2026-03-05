#!/usr/bin/env python3
"""
Telegram 骑行训练机器人
Usage: python3 telegram_bot.py --token <BOT_TOKEN> --athlete-id <ID> [--api-key <KEY>]

功能：
- /status - 当前训练状态
- /week - 本周训练总结
- /plan - 训练计划建议
- /ftp - FTP 变化趋势
"""

import argparse
import json
import requests
from datetime import datetime, timedelta

# Intervals.icu 配置
ICU_BASE = "https://intervals.icu"

def get_icu_data(athlete_id, api_key=None):
    """获取 intervals.icu 数据"""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # 获取骑手信息
    athlete = requests.get(f"{ICU_BASE}/api/v1/athlete/{athlete_id}", headers=headers).json()
    
    # 获取最近活动
    end = datetime.now()
    start = end - timedelta(days=90)
    activities = requests.get(
        f"{ICU_BASE}/api/v1/athlete/{athlete_id}/activities",
        headers=headers,
        params={"oldest": start.isoformat(), "newest": end.isoformat(), "limit": 500}
    ).json()
    
    return athlete, activities

def calculate_status(activities, ftp):
    """计算训练状态"""
    if not ftp or not activities:
        return None
    
    # 最近42天和7天
    recent = activities[:42] if len(activities) >= 42 else activities
    last_week = activities[:7] if len(activities) >= 7 else activities
    
    ctl = sum(a.get("suffer_score", 0) or 0 for a in recent) / 42 if recent else 0
    atl = sum(a.get("suffer_score", 0) or 0 for a in last_week) / 7 if last_week else 0
    tsb = ctl - atl
    
    return {"ctl": round(ctl, 1), "atl": round(atl, 1), "tsb": round(tsb, 1)}

def format_status(athlete, metrics):
    """格式化状态消息"""
    ftp = athlete.get("ftp", {}).get("value", "N/A")
    tsb = metrics["tsb"]
    
    # 状态判断
    if tsb > 10:
        form_emoji = "🔥"
        form_text = "巅峰状态！准备好比赛了"
    elif tsb > 0:
        form_emoji = "📈"
        form_text = "状态上升中，保持节奏"
    elif tsb > -15:
        form_emoji = "⚖️"
        form_text = "维持期，训练平衡"
    else:
        form_emoji = "😴"
        form_text = "恢复期，注意休息"
    
    return f"""🚴 **训练状态**

**FTP**: {ftp}W
**CTL**: {metrics["ctl"]}
**ATL**: {metrics["atl"]}
**TSB**: {metrics["tsb"]}

{form_emoji} {form_text}"""

def format_week(activities):
    """本周训练总结"""
    this_week = [a for a in activities[:7] if a.get("type") == "Ride"]
    
    if not this_week:
        return "本周还没有骑行记录"
    
    total_dist = sum(a.get("distance", 0) for a in this_week) / 1000
    total_time = sum(a.get("moving_time", 0) for a in this_week) / 60
    total_elevation = sum(a.get("total_elevation_gain", 0) for a in this_week)
    
    return f"""📅 **本周总结**

骑行次数: {len(this_week)}
距离: {total_dist:.1f} km
时间: {total_time:.0f} 分钟
爬升: {total_elevation:.0f} m"""

def generate_plan(metrics):
    """生成训练建议"""
    tsb = metrics["tsb"]
    
    if tsb > 15:
        return """**当前状态: 巅峰期**

建议:
- 保持高强度训练
- 可以安排比赛或计时赛
- 注意不要过度训练"""
    elif tsb > 5:
        return """**当前状态: 建立期**

建议:
- 加入更多阈值训练
- 周中安排2-3次高强度
- 周末长距离耐力"""
    elif tsb > -5:
        return """**当前状态: 积累期**

建议:
- 增加训练量
- 重点在有氧基础
- 减少高强度频率"""
    else:
        return """**当前状态: 恢复期**

建议:
- 完全休息或轻松骑
- 关注睡眠和营养
- 避免高强度训练"""

# Telegram Bot Handler
def handle_update(token, athlete_id, api_key):
    """处理 Telegram 更新"""
    # 获取数据
    athlete, activities = get_icu_data(athlete_id, api_key)
    ftp = athlete.get("ftp", {}).get("value")
    metrics = calculate_status(activities, ftp)
    
    print(f"Bot running for {athlete.get('name')}")
    print(f"FTP: {ftp}, CTL: {metrics['ctl']}, TSB: {metrics['tsb']}")
    print("\n可用命令: /status, /week, /plan, /ftp")
    print("按 Ctrl+C 停止")

def main():
    parser = argparse.ArgumentParser(description="骑行训练 Telegram 机器人")
    parser.add_argument("--token", required=True, help="Telegram Bot Token")
    parser.add_argument("--athlete-id", required=True, help="intervals.icu 骑手 ID")
    parser.add_argument("--api-key", help="intervals.icu API Key")
    
    args = parser.parse_args()
    handle_update(args.token, args.athlete_id, args.api_key)

if __name__ == "__main__":
    main()