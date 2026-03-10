#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractors 数据提取测试

测试范围:
- extract_status_data() 输出格式
- extract_week_data() 输出格式
- extract_latest_ride_data() 输出格式
- 使用 mock 数据测试边界情况（空数据、单条数据等）
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 添加 scripts 目录到路径
import sys
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import utils.storage as storage_module
import extract.extractors as extractors_module


class TestExtractorsStatusData(unittest.TestCase):
    """测试 extract_status_data 输出格式"""

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

    def test_extract_status_data_empty_list(self):
        """测试空活动列表"""
        self.test_activities_file.write_text(json.dumps([]))
        
        result = extractors_module.extract_status_data()
        
        # 应该返回有效结构，但数据为空
        self.assertIsInstance(result, dict)
        self.assertIn("athlete_id", result)
        self.assertIn("latest_activity", result)
        self.assertEqual(result["total_activities"], 0)
        self.assertEqual(result["week_activities"], [])

    def test_extract_status_data_single_activity(self):
        """测试单条活动数据"""
        today = datetime.now()
        activities = [{
            "id": "act_001",
            "name": "Single Ride",
            "type": "Ride",
            "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
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
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        self.assertEqual(result["total_activities"], 1)
        self.assertEqual(result["latest_activity"]["name"], "Single Ride")
        self.assertEqual(len(result["week_activities"]), 1)

    def test_extract_status_data_no_training_load(self):
        """测试没有训练负荷的活动被过滤"""
        today = datetime.now()
        activities = [
            {
                "id": "act_001",
                "name": "Valid Ride",
                "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
                "icu_training_load": 80,
                "icu_ctl": 60.0,
                "icu_atl": 65.0,
            },
            {
                "id": "act_002",
                "name": "Zero Load Ride",
                "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
                "icu_training_load": 0,
                "icu_ctl": 60.0,
                "icu_atl": 65.0,
            }
        ]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        # 只有有训练负荷的活动应该被包含
        self.assertEqual(len(result["week_activities"]), 1)
        self.assertEqual(result["week_activities"][0]["name"], "Valid Ride")

    def test_extract_status_data_tsb_calculation(self):
        """测试 TSB 计算"""
        today = datetime.now()
        activities = [{
            "id": "act_001",
            "name": "Test Ride",
            "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 80,
            "icu_ctl": 65.5,
            "icu_atl": 72.3,
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        # TSB = CTL - ATL = 65.5 - 72.3 = -6.8
        expected_tsb = round(65.5 - 72.3, 1)
        self.assertEqual(result["latest_activity"]["tsb"], expected_tsb)


class TestExtractorsWeekData(unittest.TestCase):
    """测试 extract_week_data 输出格式"""

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

    def test_extract_week_data_empty_list(self):
        """测试空活动列表"""
        self.test_activities_file.write_text(json.dumps([]))
        
        result = extractors_module.extract_week_data()
        
        # 应该返回有效结构，但数据为空
        self.assertIsInstance(result, dict)
        self.assertIn("week_start", result)
        self.assertIn("activities", result)
        self.assertEqual(result["activities"], [])
        self.assertEqual(result["summary"]["count"], 0)

    def test_extract_week_data_no_week_activities(self):
        """测试本周无活动"""
        today = datetime.now()
        # 上周的活动
        last_week = today - timedelta(days=7)
        activities = [{
            "id": "act_001",
            "name": "Last Week Ride",
            "start_date": last_week.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": last_week.strftime("%Y-%m-%dT%H:%M:%S"),
            "moving_time": 3600,
            "distance": 30000,
            "icu_training_load": 80,
            "icu_intensity": 0.80,
            "icu_ctl": 60.0,
            "icu_atl": 65.0,
            "icu_ftp": 280,
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_week_data()
        
        # 本周应该没有活动
        self.assertEqual(len(result["activities"]), 0)
        self.assertEqual(result["summary"]["count"], 0)

    def test_extract_week_data_multiple_days(self):
        """测试本周多天活动"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        
        activities = []
        for i in range(3):
            date = monday + timedelta(days=i)
            activities.append({
                "id": f"act_{i:03d}",
                "name": f"Day {i} Ride",
                "start_date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date_local": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "moving_time": 3600 + i * 600,
                "distance": 30000 + i * 5000,
                "icu_training_load": 80 + i * 10,
                "icu_intensity": 0.80,
                "icu_ctl": 60.0,
                "icu_atl": 65.0,
                "icu_ftp": 280,
                "average_heartrate": 150,
                "icu_weighted_avg_watts": 235,
            })
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_week_data()
        
        self.assertEqual(len(result["activities"]), 3)
        self.assertEqual(result["summary"]["count"], 3)
        # 验证统计计算
        self.assertEqual(result["summary"]["total_duration_min"], 210.0)  # 60 + 70 + 80
        self.assertEqual(result["summary"]["total_distance_km"], 105.0)  # 30 + 35 + 40
        self.assertEqual(result["summary"]["total_load"], 270.0)  # 80 + 90 + 100

    def test_extract_week_data_current_status_empty(self):
        """测试无活动时 current_status 为空"""
        self.test_activities_file.write_text(json.dumps([]))
        
        result = extractors_module.extract_week_data()
        
        self.assertEqual(result["current_status"], {})


class TestExtractorsLatestRideData(unittest.TestCase):
    """测试 extract_latest_ride_data 输出格式"""

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

    def test_extract_latest_ride_data_empty(self):
        """测试无数据时返回错误"""
        self.test_activities_file.write_text(json.dumps([]))
        
        result = extractors_module.extract_latest_ride_data()
        
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        # 空列表时返回 "No ride data found"
        self.assertEqual(result["error"], "No ride data found")

    def test_extract_latest_ride_data_no_valid_ride(self):
        """测试没有有效骑行数据"""
        activities = [{
            "id": "act_001",
            "name": "Zero Load",
            "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 0,  # 无训练负荷
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_latest_ride_data()
        
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No ride data found")

    def test_extract_latest_ride_data_structure(self):
        """测试返回数据结构"""
        today = datetime.now()
        activities = [{
            "id": "act_001",
            "name": "Latest Ride",
            "type": "Ride",
            "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
            "moving_time": 5400,
            "distance": 45000,
            "total_elevation_gain": 320,
            "average_speed": 8.33,
            "max_speed": 15.2,
            "average_heartrate": 155,
            "max_heartrate": 175,
            "icu_athlete_id": "ath_12345",
            "icu_average_watts": 220,
            "icu_weighted_avg_watts": 235,
            "icu_training_load": 85,
            "icu_intensity": 0.85,
            "icu_ftp": 280,
            "icu_resting_hr": 48,
            "lthr": 165,
            "icu_joules": 1188000,
            "icu_efficiency_factor": 1.52,
            "icu_variability_index": 1.07,
            "decoupling": 2.3,
            "device_name": "Garmin Edge 530",
            "trainer": False,
            "icu_zone_times": [
                {"id": "Z1", "secs": 600},
                {"id": "Z2", "secs": 1800},
                {"id": "Z3", "secs": 2400},
                {"id": "Z4", "secs": 600}
            ],
            "icu_hr_zone_times": [300, 1200, 2400, 1500, 0, 0, 0],
            "icu_intervals": [
                {
                    "type": "WORK",
                    "moving_time": 1200,
                    "average_watts": 260,
                    "max_watts": 285,
                    "average_heartrate": 165,
                    "zone": 4,
                    "training_load": 35
                },
                {
                    "type": "RECOVERY",
                    "moving_time": 300,
                    "average_watts": 150,
                    "max_watts": 165,
                    "average_heartrate": 135,
                    "zone": 2,
                    "training_load": 5
                }
            ]
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_latest_ride_data()
        
        # 验证顶级结构
        self.assertIn("activity", result)
        self.assertIn("metrics", result)
        self.assertIn("power", result)
        self.assertIn("heart_rate", result)
        self.assertIn("efficiency", result)
        self.assertIn("zones", result)
        self.assertIn("intervals", result)
        
        # 验证 activity 结构
        activity = result["activity"]
        self.assertIn("id", activity)
        self.assertIn("date", activity)
        self.assertIn("name", activity)
        self.assertIn("type", activity)
        self.assertIn("device", activity)
        self.assertIn("trainer", activity)
        
        # 验证 metrics 结构
        metrics = result["metrics"]
        self.assertIn("duration_min", metrics)
        self.assertIn("distance_km", metrics)
        self.assertIn("elevation_m", metrics)
        self.assertIn("avg_speed_kmh", metrics)
        self.assertIn("max_speed_kmh", metrics)
        
        # 验证 power 结构
        power = result["power"]
        self.assertIn("avg_watts", power)
        self.assertIn("np", power)
        self.assertIn("max_watts", power)
        self.assertIn("training_load", power)
        self.assertIn("intensity", power)
        self.assertIn("ftp", power)
        self.assertIn("joules", power)
        
        # 验证 heart_rate 结构
        hr = result["heart_rate"]
        self.assertIn("avg_hr", hr)
        self.assertIn("max_hr", hr)
        self.assertIn("resting_hr", hr)
        self.assertIn("lthr", hr)
        
        # 验证 efficiency 结构
        efficiency = result["efficiency"]
        self.assertIn("decoupling_pct", efficiency)
        self.assertIn("efficiency_factor", efficiency)
        self.assertIn("variability_index", efficiency)
        
        # 验证 zones 结构
        zones = result["zones"]
        self.assertIn("power_zone_times_min", zones)
        self.assertIn("hr_zone_times_min", zones)
        
        # 验证 intervals 结构
        intervals = result["intervals"]
        self.assertIn("work_count", intervals)
        self.assertIn("recovery_count", intervals)
        self.assertIn("work_details", intervals)
        self.assertIn("recovery_details", intervals)

    def test_extract_latest_ride_data_max_watts_from_intervals(self):
        """测试从 intervals 提取最大功率"""
        activities = [{
            "id": "act_001",
            "name": "Test Ride",
            "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 85,
            "icu_intervals": [
                {"type": "WORK", "max_watts": 300},
                {"type": "WORK", "max_watts": 350},
                {"type": "RECOVERY", "max_watts": 200},
            ]
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_latest_ride_data()
        
        # max_watts 应该从 intervals 中提取最大值
        self.assertEqual(result["power"]["max_watts"], 350)

    def test_extract_latest_ride_data_zone_times_conversion(self):
        """测试功率区间时间转换为分钟"""
        activities = [{
            "id": "act_001",
            "name": "Test Ride",
            "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 85,
            "icu_zone_times": [
                {"id": "Z1", "secs": 600},   # 10分钟
                {"id": "Z2", "secs": 1800},  # 30分钟
                {"id": "Z3", "secs": 2400},  # 40分钟
            ],
            "icu_hr_zone_times": [300, 1200, 2400, 0, 0, 0, 0],  # 5, 20, 40分钟
            "icu_intervals": []
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_latest_ride_data()
        
        # 验证功率区间时间（转换为分钟）
        power_zones = result["zones"]["power_zone_times_min"]
        self.assertEqual(power_zones["Z1"], 10.0)
        self.assertEqual(power_zones["Z2"], 30.0)
        self.assertEqual(power_zones["Z3"], 40.0)
        
        # 验证心率区间时间
        hr_zones = result["zones"]["hr_zone_times_min"]
        self.assertEqual(hr_zones["Z1"], 5.0)
        self.assertEqual(hr_zones["Z2"], 20.0)
        self.assertEqual(hr_zones["Z3"], 40.0)

    def test_extract_latest_ride_data_intervals_classification(self):
        """测试间歇分类（WORK vs RECOVERY）"""
        activities = [{
            "id": "act_001",
            "name": "Test Ride",
            "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 85,
            "icu_intervals": [
                {"type": "WORK", "moving_time": 1200, "average_watts": 260},
                {"type": "RECOVERY", "moving_time": 300, "average_watts": 150},
                {"type": "WORK", "moving_time": 1200, "average_watts": 265},
            ]
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_latest_ride_data()
        
        intervals = result["intervals"]
        self.assertEqual(intervals["work_count"], 2)
        self.assertEqual(intervals["recovery_count"], 1)
        self.assertEqual(len(intervals["work_details"]), 2)
        self.assertEqual(len(intervals["recovery_details"]), 1)


class TestExtractorsBoundaryCases(unittest.TestCase):
    """测试边界情况"""

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

    def test_extract_form_data_empty(self):
        """测试空数据的 extract_form_data"""
        self.test_activities_file.write_text(json.dumps([]))
        
        result = extractors_module.extract_form_data()
        
        self.assertIsInstance(result, dict)
        self.assertIn("total_intervals", result)
        self.assertEqual(result["total_intervals"], 0)
        self.assertEqual(result["all_intervals"], [])

    def test_extract_form_data_no_intervals(self):
        """测试没有间歇数据"""
        activities = [{
            "id": "act_001",
            "name": "No Intervals",
            "start_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 80,
            "icu_intervals": []
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_form_data()
        
        self.assertEqual(result["total_intervals"], 0)

    def test_extract_trend_data_empty(self):
        """测试空数据的 extract_trend_data"""
        self.test_activities_file.write_text(json.dumps([]))
        
        result = extractors_module.extract_trend_data()
        
        self.assertIsInstance(result, dict)
        self.assertIn("daily_data", result)
        self.assertIn("weekly_summary", result)
        self.assertEqual(result["daily_data"], [])
        self.assertEqual(result["weekly_summary"], [])

    def test_extract_trend_data_no_valid_activities(self):
        """测试没有有效活动（无训练负荷）"""
        today = datetime.now()
        activities = [
            {
                "id": "act_001",
                "name": "Zero Load",
                "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
                "icu_training_load": 0,
            }
        ]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_trend_data()
        
        # 应该过滤掉无训练负荷的活动
        self.assertEqual(result["daily_data"], [])

    def test_extract_status_data_missing_fields(self):
        """测试缺失字段的处理"""
        today = datetime.now()
        activities = [{
            "id": "act_001",
            "name": "Minimal Data",
            "start_date": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "start_date_local": today.strftime("%Y-%m-%dT%H:%M:%S"),
            "icu_training_load": 80,
            # 缺少许多可选字段
        }]
        
        self.test_activities_file.write_text(json.dumps(activities))
        
        result = extractors_module.extract_status_data()
        
        # 应该正常返回，缺失字段使用默认值
        self.assertIsInstance(result, dict)
        self.assertNotIn("error", result)
        self.assertEqual(result["latest_activity"]["name"], "Minimal Data")


if __name__ == '__main__':
    unittest.main()
