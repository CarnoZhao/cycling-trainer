#!/usr/bin/env python3
"""
Workout Calculator 测试

测试内容:
- 日期计算（验证星期几匹配）
- 功率计算（验证 FTP 百分比转换）
- TSS 计算（验证标准公式）
- workout 语法生成（验证格式正确）
- 完整流程（从 JSON 到最终输出）
"""
import unittest
import json
from datetime import datetime

# 导入被测模块
import sys
sys.path.insert(0, '/root/.openclaw/workspace-cycling/skills/cycling-trainer/scripts')
from workout_calculator import WorkoutCalculator


class TestWorkoutCalculator(unittest.TestCase):
    """WorkoutCalculator 单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.calculator = WorkoutCalculator(ftp=260)
    
    # ==================== 日期计算测试 ====================
    
    def test_calculate_date_basic(self):
        """测试基本日期计算"""
        # 2026-03-11 是周三
        result = self.calculator._calculate_date('2026-03-11', 0)
        self.assertEqual(result['date'], '2026-03-11')
        self.assertEqual(result['weekday'], '周三')
    
    def test_calculate_date_offset(self):
        """测试日期偏移计算"""
        # 2026-03-11 (周三) + 1 = 2026-03-12 (周四)
        result = self.calculator._calculate_date('2026-03-11', 1)
        self.assertEqual(result['date'], '2026-03-12')
        self.assertEqual(result['weekday'], '周四')
    
    def test_calculate_date_week_boundary(self):
        """测试跨周边界"""
        # 2026-03-11 (周三) + 7 = 2026-03-18 (周三)
        result = self.calculator._calculate_date('2026-03-11', 7)
        self.assertEqual(result['date'], '2026-03-18')
        self.assertEqual(result['weekday'], '周三')
    
    def test_calculate_date_negative_offset(self):
        """测试负数偏移应该报错"""
        with self.assertRaises(ValueError) as context:
            self.calculator._calculate_date('2026-03-11', -1)
        self.assertIn('不能为负数', str(context.exception))
    
    def test_calculate_date_weekday_mapping(self):
        """测试星期几映射正确"""
        base_date = '2026-03-09'  # 周一
        expected_weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        for i, expected in enumerate(expected_weekdays):
            result = self.calculator._calculate_date(base_date, i)
            self.assertEqual(result['weekday'], expected, 
                           f"Offset {i} should be {expected}")
    
    # ==================== 功率计算测试 ====================
    
    def test_calculate_power_100_percent(self):
        """测试 100% FTP"""
        result = self.calculator._calculate_power(100)
        self.assertEqual(result, 260)
    
    def test_calculate_power_90_percent(self):
        """测试 90% FTP"""
        result = self.calculator._calculate_power(90)
        self.assertEqual(result, 234)  # 260 * 0.9 = 234
    
    def test_calculate_power_150_percent(self):
        """测试 150% FTP (应警告但仍计算)"""
        # 150% 应该计算但不阻止
        result = self.calculator._calculate_power(150)
        self.assertEqual(result, 390)  # 260 * 1.5 = 390
    
    def test_calculate_power_zero_percent(self):
        """测试 0% FTP"""
        result = self.calculator._calculate_power(0)
        self.assertEqual(result, 0)
    
    # ==================== TSS 计算测试 ====================
    
    def test_calculate_tss_basic(self):
        """测试基本 TSS 计算"""
        # TSS = IF^2 * hours * 100
        # IF=0.98, 1小时 => 0.98^2 * 1 * 100 = 96
        result = self.calculator._calculate_tss(255, 60, 0.98)
        self.assertEqual(result, 96)
    
    def test_calculate_tss_2_hours(self):
        """测试 2 小时 TSS"""
        # IF=0.98, 2小时 => 0.98^2 * 2 * 100 = 192
        result = self.calculator._calculate_tss(255, 120, 0.98)
        self.assertEqual(result, 192)
    
    def test_calculate_tss_zero_duration(self):
        """测试 0 时长 TSS"""
        result = self.calculator._calculate_tss(255, 0, 0.98)
        self.assertEqual(result, 0)
    
    # ==================== NP 计算测试 ====================
    
    def test_calculate_np_steady(self):
        """测试稳定训练的 NP"""
        # 稳定训练，NP ≈ Avg Power
        result = self.calculator._calculate_np(260, 'Threshold', 1)
        self.assertEqual(result, 260)
    
    def test_calculate_np_interval(self):
        """测试间歇训练的 NP"""
        # 间歇训练，NP 略低于目标功率（考虑恢复期）
        result = self.calculator._calculate_np(310, 'VO2max', 5)
        # 5组间歇，NP 约为目标功率的 94%
        self.assertLess(result, 310)
        self.assertGreater(result, 290)
    
    def test_calculate_np_z2(self):
        """测试 Z2 训练的 NP"""
        result = self.calculator._calculate_np(175, 'Z2', 1)
        self.assertEqual(result, 175)
    
    # ==================== 时长计算测试 ====================
    
    def test_calculate_duration_single_set(self):
        """测试单组时长"""
        result = self.calculator._calculate_duration(1, 20, 5)
        self.assertEqual(result['warmup_min'], 10)
        self.assertEqual(result['main_min'], 20)
        self.assertEqual(result['cooldown_min'], 10)
        self.assertEqual(result['total_min'], 40)
    
    def test_calculate_duration_multiple_sets(self):
        """测试多组时长"""
        # 2组 * 20分钟 + 1次休息 = 40 + 5 = 45分钟主课
        result = self.calculator._calculate_duration(2, 20, 5)
        self.assertEqual(result['warmup_min'], 10)
        self.assertEqual(result['main_min'], 45)  # 2*20 + 1*5
        self.assertEqual(result['cooldown_min'], 10)
        self.assertEqual(result['total_min'], 65)
    
    def test_calculate_duration_zero_sets(self):
        """测试 0 组（休息日）"""
        result = self.calculator._calculate_duration(0, 20, 5)
        self.assertEqual(result['total_min'], 20)  # 热身+冷身
    
    # ==================== Workout 语法生成测试 ====================
    
    def test_generate_description_threshold(self):
        """测试 Threshold 课程描述生成"""
        structure = {
            'warmup': {'duration': 10, 'power_start': 125, 'power_end': 185},
            'main': {
                'sets': 2,
                'work': {'duration': 20, 'power': 260},
                'rest': {'duration': 5, 'power': 150}
            },
            'cooldown': {'duration': 10, 'power_start': 185, 'power_end': 125}
        }
        result = self.calculator._generate_description(structure)
        
        # 检查包含关键元素
        self.assertIn('10m ramp 125w-185w', result)  # 热身
        self.assertIn('2x', result)  # 组数标记
        self.assertIn('20m @260w', result)  # 工作
        self.assertIn('5m @150w', result)  # 恢复
        self.assertIn('10m ramp 185w-125w', result)  # 冷身
    
    def test_generate_description_single_set(self):
        """测试单组课程描述（无组数标记）"""
        structure = {
            'warmup': {'duration': 10, 'power_start': 125, 'power_end': 185},
            'main': {
                'sets': 1,
                'work': {'duration': 30, 'power': 220},
                'rest': {'duration': 5, 'power': 150}
            },
            'cooldown': {'duration': 10, 'power_start': 185, 'power_end': 125}
        }
        result = self.calculator._generate_description(structure)
        
        # 单组不应该有 "1x" 标记
        self.assertNotIn('1x', result)
        self.assertIn('30m @220w', result)
    
    # ==================== 名称生成测试 ====================
    
    def test_generate_name_single_set(self):
        """测试单组名称"""
        result = self.calculator._generate_name('Threshold', 1, 30, 260)
        self.assertEqual(result, 'Threshold 30min@260w')
    
    def test_generate_name_multiple_sets(self):
        """测试多组名称"""
        result = self.calculator._generate_name('VO2max', 5, 4, 310)
        self.assertEqual(result, 'VO2max 5x4min@310w')
    
    # ==================== 完整流程测试 ====================
    
    def test_calculate_from_plan_full(self):
        """测试完整计划计算流程"""
        plan_json = {
            "rationale": "第3周峰值强度，安排 Threshold + VO2max",
            "workouts": [
                {
                    "date_offset": 0,
                    "type": "Threshold",
                    "sets": 2,
                    "duration_min": 20,
                    "intensity_pct": 100,
                    "rest_min": 5
                },
                {
                    "date_offset": 2,
                    "type": "VO2max",
                    "sets": 5,
                    "duration_min": 4,
                    "intensity_pct": 120,
                    "rest_min": 4
                },
                {
                    "date_offset": 4,
                    "type": "Z2",
                    "sets": 1,
                    "duration_min": 90,
                    "intensity_pct": 70,
                    "rest_min": 0
                }
            ]
        }
        
        workouts = self.calculator.calculate_from_plan(plan_json, '2026-03-11')
        
        # 验证数量
        self.assertEqual(len(workouts), 3)
        
        # 验证第一个 workout
        w1 = workouts[0]
        self.assertEqual(w1['date'], '2026-03-11')
        self.assertEqual(w1['weekday'], '周三')
        self.assertEqual(w1['type'], 'Threshold')
        self.assertEqual(w1['np'], 260)
        self.assertIn('2x20min@260w', w1['name'])
        
        # 验证第二个 workout
        w2 = workouts[1]
        self.assertEqual(w2['date'], '2026-03-13')
        self.assertEqual(w2['weekday'], '周五')
        self.assertEqual(w2['type'], 'VO2max')
        self.assertIn('5x4min', w2['name'])
        
        # 验证功率计算 (260 * 1.2 = 312)
        self.assertEqual(w2['structure']['main']['work']['power'], 312)
    
    def test_calculate_from_plan_with_rest(self):
        """测试包含休息日的计划"""
        plan_json = {
            "rationale": "恢复周安排",
            "workouts": [
                {
                    "date_offset": 0,
                    "type": "Z2",
                    "sets": 1,
                    "duration_min": 60,
                    "intensity_pct": 65,
                    "rest_min": 0
                },
                {
                    "date_offset": 1,
                    "type": "Rest",
                    "sets": 0,
                    "duration_min": 0,
                    "intensity_pct": 0,
                    "rest_min": 0
                }
            ]
        }
        
        workouts = self.calculator.calculate_from_plan(plan_json, '2026-03-11')
        
        # 验证第二个是休息日
        rest_day = workouts[1]
        self.assertTrue(rest_day.get('is_rest'))
        self.assertEqual(rest_day['name'], '🛌 完全休息')
        self.assertEqual(rest_day['tss'], 0)
    
    # ==================== 调整功能测试 ====================
    
    def test_adjust_workout_sets(self):
        """测试调整组数"""
        workout = {
            'date': '2026-03-11',
            'weekday': '周三',
            'name': 'Threshold 2x20min@260w',
            'type': 'Threshold',
            'duration_min': 65,
            'tss': 96,
            'np': 260,
            'structure': {
                'warmup': {'duration': 10, 'power_start': 125, 'power_end': 185},
                'main': {
                    'sets': 2,
                    'work': {'duration': 20, 'power': 260},
                    'rest': {'duration': 5, 'power': 150}
                },
                'cooldown': {'duration': 10, 'power_start': 185, 'power_end': 125}
            }
        }
        
        adjusted = self.calculator.adjust_workout(workout, {'sets': 3})
        
        # 验证组数更新
        self.assertEqual(adjusted['structure']['main']['sets'], 3)
        # 验证名称更新
        self.assertIn('3x20min', adjusted['name'])
        # 验证时长更新 (10 + 3*20 + 2*5 + 10 = 90)
        self.assertEqual(adjusted['duration_min'], 90)
    
    def test_adjust_workout_power(self):
        """测试调整功率"""
        workout = {
            'date': '2026-03-11',
            'weekday': '周三',
            'name': 'Threshold 2x20min@260w',
            'type': 'Threshold',
            'duration_min': 65,
            'tss': 96,
            'np': 260,
            'structure': {
                'warmup': {'duration': 10, 'power_start': 125, 'power_end': 185},
                'main': {
                    'sets': 2,
                    'work': {'duration': 20, 'power': 260},
                    'rest': {'duration': 5, 'power': 150}
                },
                'cooldown': {'duration': 10, 'power_start': 185, 'power_end': 125}
            }
        }
        
        adjusted = self.calculator.adjust_workout(workout, {'intensity_pct': 105})
        
        # 验证功率更新 (260 * 1.05 = 273)
        self.assertEqual(adjusted['structure']['main']['work']['power'], 273)
        # 验证名称更新
        self.assertIn('@273w', adjusted['name'])


class TestWorkoutCalculatorCLI(unittest.TestCase):
    """CLI 测试"""
    
    def test_cli_basic(self):
        """测试 CLI 基本功能"""
        import subprocess
        import sys
        
        plan_json = json.dumps({
            "rationale": "测试",
            "workouts": [
                {
                    "date_offset": 0,
                    "type": "Threshold",
                    "sets": 2,
                    "duration_min": 20,
                    "intensity_pct": 100,
                    "rest_min": 5
                }
            ]
        })
        
        result = subprocess.run(
            [sys.executable, '/root/.openclaw/workspace-cycling/skills/cycling-trainer/scripts/workout_calculator.py', 
             '260', '2026-03-11', plan_json],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        
        # 验证输出是有效 JSON
        output = json.loads(result.stdout)
        self.assertIn('workouts', output)
        self.assertEqual(len(output['workouts']), 1)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWorkoutCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkoutCalculatorCLI))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
