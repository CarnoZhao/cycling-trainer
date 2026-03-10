#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cycle Memory 模块单元测试

测试范围:
- load_memory() / save_memory()
- update_week_activity()
- advance_week()
- start_new_cycle()
- export_to_markdown()
- 数据验证（无效数据应被拒绝）
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# 添加 scripts 目录到路径
import sys
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from cycle_memory import (
    CycleMemoryManager,
    CycleMemory,
    CurrentCycle,
    WeekData,
    Activity,
    CycleHistoryEntry,
    load_memory,
    save_memory,
    update_week_activity,
    advance_week,
    start_new_cycle,
    export_to_markdown,
    DEFAULT_MEMORY_FILE,
)


class TestCycleMemoryManager(unittest.TestCase):
    """测试 CycleMemoryManager 类"""

    def setUp(self):
        """创建临时目录用于测试"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = Path(self.temp_dir) / "cycle_memory.json"
        self.manager = CycleMemoryManager(memory_file=self.memory_file)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)

    def _create_sample_memory(self):
        """创建示例周期记忆数据"""
        return CycleMemory(
            version=1,
            updated_at="2024-03-10T18:30:00+08:00",
            current_cycle=CurrentCycle(
                cycle_number=3,
                start_date="2024-02-19",
                current_week=3,
                week_type="peak",
                ftp=280
            ),
            this_week=WeekData(
                week_number=3,
                week_type="peak",
                intensity_target=3,
                intensity_completed=2,
                total_load=180,
                tsb=-8.5,
                status="in_progress",
                activities=[
                    Activity(
                        date="2024-03-10",
                        weekday="周日",
                        content="Sweet Spot 2x20min",
                        type="SS",
                        load=85,
                        status="completed"
                    ),
                    Activity(
                        date="2024-03-08",
                        weekday="周五",
                        content="Z2 Easy Ride",
                        type="Z2",
                        load=45,
                        status="completed"
                    )
                ]
            ),
            last_week=WeekData(
                week_number=2,
                week_type="build",
                intensity_target=2,
                intensity_completed=2,
                total_load=245,
                tsb=-5.2,
                status="completed",
                activities=[]
            ),
            week_before_last=None,
            cycle_history=[]
        )

    def test_load_memory_empty(self):
        """测试加载不存在的周期记忆"""
        result = self.manager.load_memory()
        self.assertIsNone(result)

    def test_save_and_load_memory(self):
        """测试保存和加载周期记忆"""
        memory = self._create_sample_memory()
        
        # 保存
        success = self.manager.save_memory(memory)
        self.assertTrue(success)
        self.assertTrue(self.memory_file.exists())
        
        # 加载
        loaded = self.manager.load_memory()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.version, 1)
        self.assertEqual(loaded.current_cycle.cycle_number, 3)
        self.assertEqual(loaded.current_cycle.ftp, 280)
        self.assertEqual(loaded.this_week.week_number, 3)
        self.assertEqual(len(loaded.this_week.activities), 2)

    def test_save_updates_timestamp(self):
        """测试保存时更新时间戳"""
        memory = self._create_sample_memory()
        old_timestamp = memory.updated_at
        
        import time
        time.sleep(0.01)  # 确保时间变化
        
        self.manager.save_memory(memory)
        loaded = self.manager.load_memory()
        
        self.assertNotEqual(loaded.updated_at, old_timestamp)

    def test_get_current_cycle(self):
        """测试获取当前周期信息"""
        memory = self._create_sample_memory()
        self.manager.save_memory(memory)
        
        cycle_info = self.manager.get_current_cycle()
        self.assertIsNotNone(cycle_info)
        self.assertEqual(cycle_info["cycle_number"], 3)
        self.assertEqual(cycle_info["week_type"], "peak")
        self.assertEqual(cycle_info["ftp"], 280)

    def test_get_current_cycle_empty(self):
        """测试空数据时获取当前周期"""
        cycle_info = self.manager.get_current_cycle()
        self.assertIsNone(cycle_info)

    def test_update_week_activity_existing(self):
        """测试更新已有活动"""
        memory = self._create_sample_memory()
        self.manager.save_memory(memory)
        
        # 更新已有活动
        success = self.manager.update_week_activity(
            "2024-03-10",
            {
                "date": "2024-03-10",
                "weekday": "周日",
                "content": "Updated Content",
                "type": "Threshold",
                "load": 100,
                "status": "completed"
            }
        )
        
        self.assertTrue(success)
        
        loaded = self.manager.load_memory()
        activity = loaded.this_week.activities[0]
        self.assertEqual(activity.content, "Updated Content")
        self.assertEqual(activity.type, "Threshold")
        self.assertEqual(activity.load, 100)

    def test_update_week_activity_new(self):
        """测试添加新活动"""
        memory = self._create_sample_memory()
        self.manager.save_memory(memory)
        
        # 添加新活动
        success = self.manager.update_week_activity(
            "2024-03-12",
            {
                "date": "2024-03-12",
                "weekday": "周二",
                "content": "New Activity",
                "type": "VO2max",
                "load": 90,
                "status": "planned"
            }
        )
        
        self.assertTrue(success)
        
        loaded = self.manager.load_memory()
        self.assertEqual(len(loaded.this_week.activities), 3)
        
        # 查找新添加的活动
        new_activity = next(
            (a for a in loaded.this_week.activities if a.date == "2024-03-12"),
            None
        )
        self.assertIsNotNone(new_activity)
        self.assertEqual(new_activity.content, "New Activity")

    def test_update_week_activity_recalculates_stats(self):
        """测试更新活动后重新计算统计"""
        memory = self._create_sample_memory()
        self.manager.save_memory(memory)
        
        # 计算原始已完成活动的总负荷
        original_completed_load = sum(
            a.load for a in memory.this_week.activities if a.status == "completed"
        )
        # 计算原始强度课数量（SS, Threshold, VO2max, Anaerobic 类型）
        original_intensity_count = sum(
            1 for a in memory.this_week.activities 
            if a.status == "completed" and a.type in ["SS", "Threshold", "VO2max", "Anaerobic"]
        )
        
        # 添加新的已完成活动
        self.manager.update_week_activity(
            "2024-03-12",
            {
                "date": "2024-03-12",
                "weekday": "周二",
                "content": "New Intensity",
                "type": "SS",  # 强度课
                "load": 50,
                "status": "completed"
            }
        )
        
        loaded = self.manager.load_memory()
        # 总负荷应该增加（只计算 completed 状态的活动）
        expected_load = original_completed_load + 50
        self.assertEqual(loaded.this_week.total_load, expected_load)
        # 强度课计数应该增加
        self.assertEqual(loaded.this_week.intensity_completed, original_intensity_count + 1)

    def test_update_week_activity_no_memory(self):
        """测试无数据时更新活动"""
        success = self.manager.update_week_activity(
            "2024-03-12",
            {"content": "Test", "type": "Z2", "load": 50, "status": "planned"}
        )
        self.assertFalse(success)

    def test_advance_week(self):
        """测试进入下一周"""
        memory = self._create_sample_memory()
        self.manager.save_memory(memory)
        
        success = self.manager.advance_week()
        self.assertTrue(success)
        
        loaded = self.manager.load_memory()
        # 当前周应该变为第4周
        self.assertEqual(loaded.current_cycle.current_week, 4)
        self.assertEqual(loaded.current_cycle.week_type, "recovery")
        # 本周应该移到上周
        self.assertIsNotNone(loaded.last_week)
        self.assertEqual(loaded.last_week.week_number, 3)

    def test_advance_week_new_cycle(self):
        """测试进入新周期"""
        memory = self._create_sample_memory()
        memory.current_cycle.current_week = 4  # 恢复周
        memory.current_cycle.week_type = "recovery"
        memory.this_week.week_number = 4
        memory.this_week.week_type = "recovery"
        self.manager.save_memory(memory)
        
        success = self.manager.advance_week()
        self.assertTrue(success)
        
        loaded = self.manager.load_memory()
        # 应该开始新周期的第1周
        self.assertEqual(loaded.current_cycle.current_week, 1)
        self.assertEqual(loaded.current_cycle.week_type, "base")
        # 周期号应该增加
        self.assertEqual(loaded.current_cycle.cycle_number, 4)

    def test_advance_week_no_memory(self):
        """测试无数据时进入下一周"""
        success = self.manager.advance_week()
        self.assertFalse(success)

    def test_start_new_cycle(self):
        """测试开始新周期"""
        memory = self._create_sample_memory()
        # 将本周状态改为 completed，避免触发 _complete_current_cycle
        memory.this_week.status = "completed"
        self.manager.save_memory(memory)
        
        success = self.manager.start_new_cycle(ftp=290, start_date="2024-03-11")
        self.assertTrue(success)
        
        loaded = self.manager.load_memory()
        # 周期号应该增加（从3增加到4）
        self.assertEqual(loaded.current_cycle.cycle_number, 4)
        # 应该重置为第1周
        self.assertEqual(loaded.current_cycle.current_week, 1)
        self.assertEqual(loaded.current_cycle.week_type, "base")
        # FTP应该更新
        self.assertEqual(loaded.current_cycle.ftp, 290)
        # 周数据应该重置
        self.assertIsNone(loaded.week_before_last)
        self.assertEqual(loaded.this_week.status, "in_progress")

    def test_start_new_cycle_empty(self):
        """测试无数据时开始新周期"""
        success = self.manager.start_new_cycle(ftp=280)
        self.assertTrue(success)
        
        loaded = self.manager.load_memory()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.current_cycle.cycle_number, 1)
        self.assertEqual(loaded.current_cycle.ftp, 280)

    def test_export_to_markdown(self):
        """测试导出为 Markdown"""
        memory = self._create_sample_memory()
        self.manager.save_memory(memory)
        
        markdown = self.manager.export_to_markdown()
        
        # 验证包含关键信息
        self.assertIn("Training Cycle Memory", markdown)
        self.assertIn("当前周期", markdown)
        self.assertIn("第 3 周期", markdown)
        self.assertIn("280w", markdown)
        self.assertIn("本周训练记录", markdown)
        self.assertIn("Sweet Spot 2x20min", markdown)

    def test_export_to_markdown_empty(self):
        """测试空数据时导出 Markdown"""
        markdown = self.manager.export_to_markdown()
        self.assertIn("暂无周期记忆数据", markdown)

    def test_create_default_memory(self):
        """测试创建默认周期记忆"""
        default = self.manager._create_default_memory()
        
        self.assertEqual(default.version, 1)
        self.assertEqual(default.current_cycle.cycle_number, 0)
        self.assertEqual(default.current_cycle.week_type, "base")
        self.assertEqual(default.this_week.week_number, 1)
        self.assertEqual(default.this_week.status, "planned")


class TestCycleMemoryDataClasses(unittest.TestCase):
    """测试数据类"""

    def test_activity_to_dict(self):
        """测试 Activity 转换为字典"""
        activity = Activity(
            date="2024-03-10",
            weekday="周日",
            content="Test",
            type="SS",
            load=85,
            status="completed"
        )
        
        d = activity.to_dict()
        self.assertEqual(d["date"], "2024-03-10")
        self.assertEqual(d["type"], "SS")

    def test_activity_from_dict(self):
        """测试从字典创建 Activity"""
        data = {
            "date": "2024-03-10",
            "weekday": "周日",
            "content": "Test",
            "type": "SS",
            "load": 85,
            "status": "completed"
        }
        
        activity = Activity.from_dict(data)
        self.assertEqual(activity.date, "2024-03-10")
        self.assertEqual(activity.load, 85)

    def test_week_data_to_dict(self):
        """测试 WeekData 转换为字典"""
        week = WeekData(
            week_number=1,
            week_type="base",
            intensity_target=2,
            intensity_completed=1,
            total_load=100,
            tsb=-5.0,
            status="in_progress",
            activities=[]
        )
        
        d = week.to_dict()
        self.assertEqual(d["week_number"], 1)
        self.assertEqual(d["week_type"], "base")

    def test_cycle_memory_to_dict(self):
        """测试 CycleMemory 转换为字典"""
        memory = CycleMemory(
            version=1,
            updated_at="2024-03-10T18:00:00+08:00",
            current_cycle=CurrentCycle(1, "2024-03-01", 1, "base", 280),
            this_week=WeekData(1, "base", 2, 0, 0, None, "planned", []),
            last_week=None,
            week_before_last=None,
            cycle_history=[]
        )
        
        d = memory.to_dict()
        self.assertEqual(d["version"], 1)
        self.assertEqual(d["current_cycle"]["ftp"], 280)

    def test_cycle_memory_from_dict(self):
        """测试从字典创建 CycleMemory"""
        data = {
            "version": 1,
            "updated_at": "2024-03-10T18:00:00+08:00",
            "current_cycle": {
                "cycle_number": 1,
                "start_date": "2024-03-01",
                "current_week": 1,
                "week_type": "base",
                "ftp": 280
            },
            "this_week": {
                "week_number": 1,
                "week_type": "base",
                "intensity_target": 2,
                "intensity_completed": 0,
                "total_load": 0,
                "tsb": None,
                "status": "planned",
                "activities": []
            },
            "last_week": None,
            "week_before_last": None,
            "cycle_history": []
        }
        
        memory = CycleMemory.from_dict(data)
        self.assertEqual(memory.version, 1)
        self.assertEqual(memory.current_cycle.ftp, 280)

    def test_invalid_data_rejected(self):
        """测试无效数据被拒绝"""
        # 缺少必需字段应该抛出异常
        with self.assertRaises((KeyError, TypeError)):
            Activity.from_dict({"date": "2024-03-10"})  # 缺少必需字段


class TestCycleMemoryFunctions(unittest.TestCase):
    """测试便捷函数接口"""

    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 保存原始默认路径
        import cycle_memory as cm_module
        self.original_default_file = cm_module.DEFAULT_MEMORY_FILE
        
        # 设置测试路径
        self.test_memory_file = Path(self.temp_dir) / "cycle_memory.json"
        cm_module.DEFAULT_MEMORY_FILE = self.test_memory_file

    def tearDown(self):
        """清理"""
        import cycle_memory as cm_module
        cm_module.DEFAULT_MEMORY_FILE = self.original_default_file
        shutil.rmtree(self.temp_dir)

    def test_load_memory_function(self):
        """测试 load_memory 便捷函数"""
        # 创建测试数据
        sample_data = {
            "version": 1,
            "updated_at": "2024-03-10T18:00:00+08:00",
            "current_cycle": {
                "cycle_number": 1,
                "start_date": "2024-03-01",
                "current_week": 1,
                "week_type": "base",
                "ftp": 280
            },
            "this_week": {
                "week_number": 1,
                "week_type": "base",
                "intensity_target": 2,
                "intensity_completed": 0,
                "total_load": 0,
                "tsb": None,
                "status": "planned",
                "activities": []
            },
            "last_week": None,
            "week_before_last": None,
            "cycle_history": []
        }
        
        self.test_memory_file.write_text(json.dumps(sample_data))
        
        result = load_memory()
        self.assertIsNotNone(result)
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["current_cycle"]["ftp"], 280)

    def test_export_to_markdown_function(self):
        """测试 export_to_markdown 便捷函数"""
        markdown = export_to_markdown()
        # 默认应该返回空数据提示
        self.assertIn("暂无周期记忆数据", markdown)


if __name__ == '__main__':
    unittest.main()
