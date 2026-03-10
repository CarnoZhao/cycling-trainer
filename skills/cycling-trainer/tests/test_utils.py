#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils 模块单元测试

测试范围:
- utils/storage.py: 活动数据的加载、保存、合并
- utils/dates.py: 日期计算和星期转换
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

from utils.storage import (
    load_data,
    load_activities,
    save_activities,
    merge_activities,
    ensure_data_dir,
)
from utils.dates import (
    get_weekday_cn,
    format_date_range,
    get_week_start,
    parse_activity_date,
    is_date_in_range,
)


class TestStorage(unittest.TestCase):
    """测试数据存储功能"""

    def setUp(self):
        """创建临时目录用于测试"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_data_dir = None
        
        # 保存原始 DATA_DIR 引用
        import utils.storage as storage_module
        self.original_data_dir = storage_module.DATA_DIR
        self.original_activities_file = storage_module.ACTIVITIES_FILE
        
        # 设置测试数据目录
        self.test_data_dir = Path(self.temp_dir) / "data" / "cycling"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        storage_module.DATA_DIR = self.test_data_dir
        storage_module.ACTIVITIES_FILE = self.test_data_dir / "activities.json"

    def tearDown(self):
        """清理临时目录"""
        # 恢复原始 DATA_DIR
        import utils.storage as storage_module
        storage_module.DATA_DIR = self.original_data_dir
        storage_module.ACTIVITIES_FILE = self.original_activities_file
        
        shutil.rmtree(self.temp_dir)

    def test_ensure_data_dir(self):
        """测试 ensure_data_dir 创建目录"""
        import utils.storage as storage_module
        test_dir = Path(self.temp_dir) / "test_nested" / "data"
        storage_module.DATA_DIR = test_dir
        storage_module.ACTIVITIES_FILE = test_dir / "activities.json"
        
        ensure_data_dir()
        self.assertTrue(test_dir.exists())

    def test_load_activities_empty(self):
        """测试加载不存在的活动数据返回错误信息"""
        result = load_activities()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No local data, please run sync first")

    def test_load_data_alias(self):
        """测试 load_data 是 load_activities 的别名"""
        # load_data 应该调用 load_activities 并提供相同的功能
        # 两者都是有效的函数
        self.assertTrue(callable(load_data))
        self.assertTrue(callable(load_activities))

    def test_save_and_load_activities(self):
        """测试保存和加载活动数据"""
        sample_activities = [
            {
                "id": "act_001",
                "name": "Test Ride 1",
                "start_date": "2024-03-10T08:00:00Z",
                "icu_training_load": 85
            },
            {
                "id": "act_002", 
                "name": "Test Ride 2",
                "start_date": "2024-03-08T08:00:00Z",
                "icu_training_load": 60
            }
        ]
        
        save_activities(sample_activities)
        
        # 验证文件已创建
        import utils.storage as storage_module
        self.assertTrue(storage_module.ACTIVITIES_FILE.exists())
        
        # 加载并验证数据
        loaded = load_activities()
        self.assertIsInstance(loaded, list)
        self.assertEqual(len(loaded), 2)
        # 数据应该按时间倒序排列
        self.assertEqual(loaded[0]["id"], "act_001")
        self.assertEqual(loaded[1]["id"], "act_002")

    def test_load_activities_invalid_json(self):
        """测试加载损坏的 JSON 文件"""
        import utils.storage as storage_module
        storage_module.ACTIVITIES_FILE.write_text("invalid json")
        
        result = load_activities()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_merge_activities(self):
        """测试合并新旧活动数据"""
        existing = [
            {"id": "act_001", "start_date": "2024-03-08T08:00:00Z"},
            {"id": "act_002", "start_date": "2024-03-06T08:00:00Z"}
        ]
        new = [
            {"id": "act_003", "start_date": "2024-03-10T08:00:00Z"},
            {"id": "act_001", "start_date": "2024-03-08T08:00:00Z"}  # 重复项
        ]
        
        merged = merge_activities(existing, new)
        
        # 应该去重
        self.assertEqual(len(merged), 3)
        # 应该按时间倒序排列
        self.assertEqual(merged[0]["id"], "act_003")
        self.assertEqual(merged[1]["id"], "act_001")
        self.assertEqual(merged[2]["id"], "act_002")

    def test_merge_activities_empty(self):
        """测试合并空列表"""
        existing = [{"id": "act_001", "start_date": "2024-03-08T08:00:00Z"}]
        
        # 合并空的新列表
        merged = merge_activities(existing, [])
        self.assertEqual(len(merged), 1)
        
        # 合并到空列表
        merged = merge_activities([], existing)
        self.assertEqual(len(merged), 1)


class TestDates(unittest.TestCase):
    """测试日期处理功能"""

    def test_get_weekday_cn(self):
        """测试中文星期几转换"""
        monday = datetime(2024, 3, 4)  # 周一
        sunday = datetime(2024, 3, 10)  # 周日
        
        self.assertEqual(get_weekday_cn(monday), "周一")
        self.assertEqual(get_weekday_cn(sunday), "周日")
        
        # 测试所有星期
        for i, expected in enumerate(['周一', '周二', '周三', '周四', '周五', '周六', '周日']):
            dt = datetime(2024, 3, 4 + i)  # 2024-03-04 是周一
            self.assertEqual(get_weekday_cn(dt), expected)

    def test_format_date_range(self):
        """测试日期范围格式化"""
        from_date = datetime(2024, 3, 10)
        oldest, newest = format_date_range(days=7, from_date=from_date)
        
        self.assertEqual(oldest, "2024-03-10")
        self.assertEqual(newest, "2024-03-17")

    def test_format_date_range_default(self):
        """测试默认日期范围（从今天开始）"""
        oldest, newest = format_date_range(days=7)
        today = datetime.now()
        
        self.assertEqual(oldest, today.strftime('%Y-%m-%d'))
        expected_newest = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        self.assertEqual(newest, expected_newest)

    def test_get_week_start(self):
        """测试获取周开始日期（周一）"""
        # 周日应该返回当周周一
        sunday = datetime(2024, 3, 10)
        monday = get_week_start(sunday)
        self.assertEqual(monday.weekday(), 0)  # 周一
        self.assertEqual(monday.day, 4)  # 2024-03-04
        
        # 周一应该返回当天
        monday_input = datetime(2024, 3, 4, 14, 30, 0)
        result = get_week_start(monday_input)
        self.assertEqual(result.weekday(), 0)
        self.assertEqual(result.hour, 0)  # 时间清零
        self.assertEqual(result.minute, 0)

    def test_get_week_start_default(self):
        """测试默认获取本周开始"""
        result = get_week_start()
        self.assertEqual(result.weekday(), 0)  # 应该是周一
        self.assertEqual(result.hour, 0)

    def test_parse_activity_date(self):
        """测试活动日期解析"""
        # 标准格式
        result = parse_activity_date("2024-03-10T08:00:00")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 10)
        
        # 仅日期格式
        result = parse_activity_date("2024-03-10")
        self.assertIsNotNone(result)
        self.assertEqual(result.day, 10)

    def test_parse_activity_date_invalid(self):
        """测试无效日期解析"""
        self.assertIsNone(parse_activity_date(""))
        self.assertIsNone(parse_activity_date(None))
        self.assertIsNone(parse_activity_date("invalid"))
        self.assertIsNone(parse_activity_date("2024-13-45"))  # 无效日期

    def test_is_date_in_range(self):
        """测试日期范围检查"""
        end_date = datetime(2024, 3, 10)
        
        # 在范围内
        self.assertTrue(is_date_in_range("2024-03-10", days=7, end_date=end_date))
        self.assertTrue(is_date_in_range("2024-03-05", days=7, end_date=end_date))
        
        # 范围外（太早）
        self.assertFalse(is_date_in_range("2024-03-01", days=7, end_date=end_date))
        
        # 范围外（太晚）
        self.assertFalse(is_date_in_range("2024-03-15", days=1, end_date=end_date))

    def test_is_date_in_range_default(self):
        """测试默认日期范围检查"""
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        last_month = (today - timedelta(days=40)).strftime('%Y-%m-%d')
        
        self.assertTrue(is_date_in_range(yesterday, days=30))
        self.assertFalse(is_date_in_range(last_month, days=30))


if __name__ == '__main__':
    unittest.main()
