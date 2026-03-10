#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract 模块单元测试

测试范围:
- extract_status_data() 返回结构
- extract_week_data() 返回结构
- extract_planned_data() 凭据缺失处理
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加 scripts 目录到路径
import sys
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# 需要 mock 的模块
import utils.storage as storage_module
import extract.extractors as extractors_module


class TestExtractStatusData(unittest.TestCase):
    """测试 extract_status_data 函数"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_activities_file = storage_module.ACTIVITIES_FILE
        self.test_activities_file = Path(self.temp_dir) / "activities.json"
        storage_module.ACTIVITIES_FILE = self.test_activities_file
        storage_module.DATA_DIR = Path(self.temp_dir)

    def tearDown(self):
        """清理测试环境"""
        storage_module.ACTIVITIES_FILE = self.original_activities_file
        shutil.rmtree(self.temp_dir)

    def _create_sample_activities(self):
        """创建示例活动数据"""
        today = datetime.now()
        activities = []
        
        # 最近的活动
        for i in range(5):
            date = today - timedelta(days=i*2)
            activities.append({
                "id": f"act_{i:03d}",
                "name": f"Test Ride {i}",
                "type": "Ride",
                "start_date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date_local": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "moving_time": 3600,
                "distance": 30000,
                "total_elevation_gain": 200,
                "average_speed": 8.33,
                "max_speed": 15.0,
                "average_heartrate": 150,
                "max_heartrate": 170,
                "icu_athlete_id": "ath_12345",
                "icu_average_watts": 220,
                "icu_weighted_avg_watts": 235,
                "icu_training_load": 80 + i * 5,
                "icu_intensity": 0.80,
                "icu_ctl": 60.0 + i,
                "icu_atl": 65.0 + i * 0.5,
                "icu_ftp": 280,
                "icu_weight": 70,
                "icu_resting_hr": 48,
                "lthr": 165,
                "icu_joules": 792000,
                "icu_efficiency_factor": 1.50,
                "icu_variability_index": 1.05,
                "decoupling": 2.5,
                "device_name": "Garmin Edge 530",
                "trainer": False,
                "icu_zone_times": [],
                "icu_hr_zone_times": [300, 1200, 1800, 300, 0, 0, 0],
                "icu_intervals": []
            })
        
        return activities

    def test_extract_status_data_structure(self):
        """测试 extract_status_data 返回结构"""
        activities = self._create_sample_activities()
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        # 验证返回类型
        self.assertIsInstance(result, dict)
        self.assertNotIn("error", result)
        
        # 验证必需字段
        self.assertIn("athlete_id", result)
        self.assertIn("today", result)
        self.assertIn("today_weekday", result)
        self.assertIn("latest_activity", result)
        self.assertIn("week_activities", result)
        self.assertIn("fitness_history", result)
        self.assertIn("total_activities", result)
        
        # 验证 latest_activity 结构
        latest = result["latest_activity"]
        self.assertIn("date", latest)
        self.assertIn("weekday", latest)
        self.assertIn("name", latest)
        self.assertIn("ctl", latest)
        self.assertIn("atl", latest)
        self.assertIn("tsb", latest)
        self.assertIn("ftp", latest)
        self.assertIn("weight_kg", latest)
        self.assertIn("resting_hr", latest)
        self.assertIn("lthr", latest)
        
        # 验证 week_activities 是列表
        self.assertIsInstance(result["week_activities"], list)
        
        # 验证 fitness_history 是列表
        self.assertIsInstance(result["fitness_history"], list)
        
        # 验证 total_activities 是数字
        self.assertIsInstance(result["total_activities"], int)

    def test_extract_status_data_empty_data(self):
        """测试无数据时的 extract_status_data"""
        result = extractors_module.extract_status_data()
        
        # 应该返回错误信息
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No local data, please run sync first")

    def test_extract_status_data_week_activities_structure(self):
        """测试 week_activities 中每个活动的结构"""
        activities = self._create_sample_activities()
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        if result["week_activities"]:
            activity = result["week_activities"][0]
            # 验证必需字段
            self.assertIn("date", activity)
            self.assertIn("weekday", activity)
            self.assertIn("name", activity)
            self.assertIn("type", activity)
            self.assertIn("duration_min", activity)
            self.assertIn("distance_km", activity)
            self.assertIn("training_load", activity)
            self.assertIn("avg_watts", activity)
            self.assertIn("avg_hr", activity)
            self.assertIn("max_hr", activity)
            self.assertIn("ftp", activity)
            self.assertIn("ctl", activity)
            self.assertIn("atl", activity)

    def test_extract_status_data_fitness_history_structure(self):
        """测试 fitness_history 中每个条目的结构"""
        activities = self._create_sample_activities()
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        if result["fitness_history"]:
            entry = result["fitness_history"][0]
            # 验证必需字段
            self.assertIn("date", entry)
            self.assertIn("weekday", entry)
            self.assertIn("ctl", entry)
            self.assertIn("atl", entry)
            self.assertIn("tsb", entry)
            self.assertIn("training_load", entry)


class TestExtractWeekData(unittest.TestCase):
    """测试 extract_week_data 函数"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_activities_file = storage_module.ACTIVITIES_FILE
        self.test_activities_file = Path(self.temp_dir) / "activities.json"
        storage_module.ACTIVITIES_FILE = self.test_activities_file
        storage_module.DATA_DIR = Path(self.temp_dir)

    def tearDown(self):
        """清理测试环境"""
        storage_module.ACTIVITIES_FILE = self.original_activities_file
        shutil.rmtree(self.temp_dir)

    def _create_sample_activities(self):
        """创建示例活动数据"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        activities = []
        
        # 本周的活动
        for i in range(3):
            date = monday + timedelta(days=i)
            activities.append({
                "id": f"act_{i:03d}",
                "name": f"Week Ride {i}",
                "type": "Ride",
                "start_date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date_local": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "moving_time": 3600,
                "distance": 30000,
                "total_elevation_gain": 200,
                "average_speed": 8.33,
                "max_speed": 15.0,
                "average_heartrate": 150,
                "max_heartrate": 170,
                "icu_athlete_id": "ath_12345",
                "icu_average_watts": 220,
                "icu_weighted_avg_watts": 235,
                "icu_training_load": 80,
                "icu_intensity": 0.80,
                "icu_ctl": 60.0,
                "icu_atl": 65.0,
                "icu_ftp": 280,
                "icu_weight": 70,
                "icu_resting_hr": 48,
                "lthr": 165,
                "icu_joules": 792000,
                "icu_efficiency_factor": 1.50,
                "icu_variability_index": 1.05,
                "decoupling": 2.5,
                "device_name": "Garmin Edge 530",
                "trainer": False,
                "icu_zone_times": [],
                "icu_hr_zone_times": [],
                "icu_intervals": []
            })
        
        return activities

    def test_extract_week_data_structure(self):
        """测试 extract_week_data 返回结构"""
        activities = self._create_sample_activities()
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_week_data()
        
        # 验证返回类型
        self.assertIsInstance(result, dict)
        self.assertNotIn("error", result)
        
        # 验证必需字段
        self.assertIn("week_start", result)
        self.assertIn("week_start_weekday", result)
        self.assertIn("today", result)
        self.assertIn("today_weekday", result)
        self.assertIn("activities", result)
        self.assertIn("summary", result)
        self.assertIn("current_status", result)
        
        # 验证 summary 结构
        summary = result["summary"]
        self.assertIn("count", summary)
        self.assertIn("total_duration_min", summary)
        self.assertIn("total_distance_km", summary)
        self.assertIn("total_load", summary)
        self.assertIn("avg_intensity", summary)
        
        # 验证 current_status 结构
        status = result["current_status"]
        self.assertIn("ctl", status)
        self.assertIn("atl", status)
        self.assertIn("tsb", status)
        self.assertIn("ftp", status)

    def test_extract_week_data_empty_data(self):
        """测试无数据时的 extract_week_data"""
        result = extractors_module.extract_week_data()
        
        # 应该返回错误信息
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No local data, please run sync first")

    def test_extract_week_data_activities_structure(self):
        """测试 activities 中每个活动的结构"""
        activities = self._create_sample_activities()
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_week_data()
        
        if result["activities"]:
            activity = result["activities"][0]
            # 验证必需字段
            self.assertIn("date", activity)
            self.assertIn("weekday", activity)
            self.assertIn("name", activity)
            self.assertIn("type", activity)
            self.assertIn("duration_min", activity)
            self.assertIn("distance_km", activity)
            self.assertIn("training_load", activity)
            self.assertIn("avg_watts", activity)
            self.assertIn("avg_hr", activity)
            self.assertIn("intensity", activity)
            self.assertIn("ftp", activity)
            self.assertIn("ctl", activity)
            self.assertIn("atl", activity)

    def test_extract_week_data_summary_calculation(self):
        """测试 summary 统计计算"""
        activities = self._create_sample_activities()
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_week_data()
        
        # 验证统计值
        self.assertEqual(result["summary"]["count"], 3)
        self.assertEqual(result["summary"]["total_duration_min"], 180.0)  # 3 * 60
        self.assertEqual(result["summary"]["total_distance_km"], 90.0)  # 3 * 30
        self.assertEqual(result["summary"]["total_load"], 240.0)  # 3 * 80


class TestExtractPlannedData(unittest.TestCase):
    """测试 extract_planned_data 函数"""

    @patch('extract.planned.fetch_planned_workouts')
    def test_extract_planned_data_structure(self, mock_fetch):
        """测试 extract_planned_data 返回结构"""
        # Mock 返回数据
        mock_fetch.return_value = {
            "count": 2,
            "date_range": {"from": "2024-03-10", "to": "2024-03-17"},
            "workouts": [
                {
                    "id": "workout_001",
                    "date": "2024-03-10",
                    "name": "Sweet Spot",
                    "description": "2x20min @ SS",
                    "duration_min": 90.0,
                    "training_load": 85,
                    "ftp": 280,
                    "intensity": 0.85,
                    "indoor": False,
                    "entered": False,
                    "paired_activity_id": None,
                    "avg_watts": 240,
                    "normalized_power": 245,
                    "steps": 5,
                    "zones": {"3": 40.0, "4": 20.0}
                },
                {
                    "id": "workout_002",
                    "date": "2024-03-12",
                    "name": "Recovery",
                    "description": "Easy spin",
                    "duration_min": 60.0,
                    "training_load": 45,
                    "ftp": 280,
                    "intensity": 0.65,
                    "indoor": False,
                    "entered": True,
                    "paired_activity_id": "act_123",
                    "avg_watts": 180,
                    "normalized_power": 185,
                    "steps": 3,
                    "zones": {"2": 60.0}
                }
            ]
        }
        
        from extract.planned import extract_planned_data
        result = extract_planned_data(days=7)
        
        # 验证返回类型
        self.assertIsInstance(result, dict)
        self.assertNotIn("error", result)
        
        # 验证必需字段
        self.assertIn("count", result)
        self.assertIn("date_range", result)
        self.assertIn("workouts", result)
        
        # 验证 count
        self.assertEqual(result["count"], 2)
        
        # 验证 date_range
        self.assertIn("from", result["date_range"])
        self.assertIn("to", result["date_range"])
        
        # 验证 workouts 是列表
        self.assertIsInstance(result["workouts"], list)
        self.assertEqual(len(result["workouts"]), 2)

    @patch('extract.planned.fetch_planned_workouts')
    def test_extract_planned_data_credentials_missing(self, mock_fetch):
        """测试凭据缺失时的 extract_planned_data"""
        # Mock 返回凭据缺失错误
        mock_fetch.return_value = {"error": "Missing credentials"}
        
        from extract.planned import extract_planned_data
        result = extract_planned_data()
        
        # 验证返回错误信息
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Missing credentials")

    @patch('extract.planned.fetch_planned_workouts')
    def test_extract_planned_data_empty_workouts(self, mock_fetch):
        """测试空训练计划"""
        mock_fetch.return_value = {
            "count": 0,
            "date_range": {"from": "2024-03-10", "to": "2024-03-17"},
            "workouts": []
        }
        
        from extract.planned import extract_planned_data
        result = extract_planned_data()
        
        self.assertEqual(result["count"], 0)
        self.assertEqual(len(result["workouts"]), 0)


if __name__ == '__main__':
    unittest.main()
