#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cycling Data Extractor - 重构版本

只负责从原始JSON中提取结构化数据，不做任何分析判断
所有分析和决策交给LLM处理

本文件仅作为入口点，实际功能由 extract/ 模块提供
"""

import argparse
import json
import sys
from pathlib import Path

# 添加 extract 模块到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from extract import (
    get_credentials,
    check_and_sync,
    extract_status_data,
    extract_form_data,
    extract_trend_data,
    extract_latest_ride_data,
    extract_week_data,
    extract_planned_data,
)


def main():
    parser = argparse.ArgumentParser(description='Extract cycling data for LLM analysis')
    parser.add_argument('--status', action='store_true', help='Extract status data')
    parser.add_argument('--form', action='store_true', help='Extract form trend data')
    parser.add_argument('--trend', action='store_true', help='Extract trend data')
    parser.add_argument('--latest', action='store_true', help='Extract latest ride data')
    parser.add_argument('--week', action='store_true', help='Extract week data')
    parser.add_argument('--planned', action='store_true', help='Extract planned workouts')
    parser.add_argument('--planned-days', type=int, default=7, help='Days to look ahead for planned workouts')
    parser.add_argument('--full', action='store_true', help='Extract all data')
    parser.add_argument('--no-sync', action='store_true', help='Skip auto-sync check')
    
    args = parser.parse_args()
    
    # 获取认证信息
    athlete_id, api_key = get_credentials()
    
    # 自动同步检查（除非指定 --no-sync）
    if not args.no_sync and athlete_id and api_key:
        check_and_sync(athlete_id, api_key)
    
    # 根据参数执行对应提取
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
    elif args.planned:
        result = extract_planned_data(days=args.planned_days)
    elif args.full:
        result = {
            "status": extract_status_data(),
            "form": extract_form_data(),
            "trend": extract_trend_data(),
            "latest": extract_latest_ride_data(),
            "week": extract_week_data(),
            "planned": extract_planned_data(days=7),
        }
    else:
        result = extract_status_data()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
