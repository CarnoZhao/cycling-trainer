#!/usr/bin/env python3
"""
Workout Calculator - 精确计算 workout 数据

Layer 2: Python 精确计算（日期、功率、TSS、NP、workout 语法）
"""
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class WorkoutCalculator:
    """Workout 计算器 - 从结构化意图计算完整 workout 数据"""
    
    # 功率区间定义（基于FTP百分比）
    POWER_ZONES = {
        'Z1': (0, 0.55),      # 恢复区
        'Z2': (0.56, 0.75),   # 有氧区
        'Z3': (0.76, 0.90),   # 节奏区
        'Z4': (0.91, 1.05),   # 阈值区
        'Z5': (1.06, 1.20),   # VO2max
        'Z6': (1.21, 1.50),   # 无氧区
        'Z7': (1.51, 2.00),   # 神经区
    }
    
    # 训练类型对应的典型强度因子
    WORKOUT_INTENSITY_FACTORS = {
        'Z1': 0.50,
        'Z2': 0.65,
        'SS': 0.90,
        'SweetSpot': 0.90,
        'Threshold': 0.98,
        'VO2max': 1.08,
        'Anaerobic': 1.25,
        'Sprint': 1.50,
    }
    
    # 星期几映射
    WEEKDAY_MAP = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    def __init__(self, ftp: int, athlete_weight: float = None):
        """
        初始化计算器
        
        Args:
            ftp: 功能性阈值功率 (watts)
            athlete_weight: 运动员体重 (kg)，可选
        """
        self.ftp = ftp
        self.athlete_weight = athlete_weight
    
    def calculate_from_plan(self, plan_json: dict, base_date: str) -> list:
        """
        从 LLM 输出的 JSON 计划计算完整 workout 数据
        
        Args:
            plan_json: LLM 输出的结构化意图，格式:
                {
                    "rationale": "...",
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
                }
            base_date: 计划开始日期 (YYYY-MM-DD)
        
        Returns:
            list: 包含完整计算数据的 workout 列表
        """
        workouts = []
        
        for workout_intent in plan_json.get('workouts', []):
            # 计算日期
            date_offset = workout_intent.get('date_offset', 0)
            date_info = self._calculate_date(base_date, date_offset)
            
            # 休息日处理
            sets = workout_intent.get('sets', 0)
            if sets == 0:
                workouts.append({
                    'date': date_info['date'],
                    'weekday': date_info['weekday'],
                    'name': '🛌 完全休息',
                    'type': 'Rest',
                    'description': '今天安排完全休息，让身体恢复。',
                    'duration_min': 0,
                    'tss': 0,
                    'np': 0,
                    'structure': None,
                    'is_rest': True
                })
                continue
            
            # 计算功率
            intensity_pct = workout_intent.get('intensity_pct', 100)
            target_power = self._calculate_power(intensity_pct)
            
            # 计算时长
            duration_min = workout_intent.get('duration_min', 20)
            rest_min = workout_intent.get('rest_min', 5)
            duration_info = self._calculate_duration(sets, duration_min, rest_min)
            
            # 计算 NP
            workout_type = workout_intent.get('type', 'Z2')
            np = self._calculate_np(target_power, workout_type, sets)
            
            # 计算 TSS
            intensity_factor = self.WORKOUT_INTENSITY_FACTORS.get(workout_type, 0.85)
            tss = self._calculate_tss(np, duration_info['total_min'], intensity_factor)
            
            # 生成名称
            name = self._generate_name(workout_type, sets, duration_min, target_power)
            
            # 构建 workout 结构
            structure = self._build_structure(
                workout_type, sets, duration_min, rest_min, 
                target_power, duration_info
            )
            
            # 生成描述
            description = self._generate_description(structure)
            
            workouts.append({
                'date': date_info['date'],
                'weekday': date_info['weekday'],
                'name': name,
                'type': workout_type,
                'description': description,
                'duration_min': duration_info['total_min'],
                'tss': tss,
                'np': np,
                'structure': structure,
                'is_rest': False
            })
        
        return workouts
    
    def _calculate_date(self, base_date: str, offset: int) -> dict:
        """
        计算精确日期和星期几
        
        Args:
            base_date: 基础日期 (YYYY-MM-DD)
            offset: 偏移天数
        
        Returns:
            dict: {'date': 'YYYY-MM-DD', 'weekday': '周一'}
        """
        # 边界检查
        if offset < 0:
            raise ValueError(f"date_offset 不能为负数: {offset}")
        
        base = datetime.strptime(base_date, '%Y-%m-%d')
        target_date = base + timedelta(days=offset)
        
        # weekday(): Monday=0, Sunday=6
        weekday_cn = self.WEEKDAY_MAP[target_date.weekday()]
        
        return {
            'date': target_date.strftime('%Y-%m-%d'),
            'weekday': weekday_cn
        }
    
    def _calculate_power(self, intensity_pct: float) -> int:
        """
        根据 FTP 和百分比计算绝对功率
        
        Args:
            intensity_pct: 强度百分比 (如 100 表示 100% FTP)
        
        Returns:
            int: 绝对功率 (watts)
        """
        # 边界检查
        if intensity_pct > 150:
            # 警告但不阻止
            print(f"Warning: intensity_pct {intensity_pct}% 超过 150%")
        
        power = int(self.ftp * (intensity_pct / 100))
        return power
    
    def _calculate_tss(self, normalized_power: int, duration_min: int, intensity_factor: float) -> int:
        """
        计算 TSS (Training Stress Score)
        
        公式: TSS = (NP/FTP)^2 * (duration_seconds/3600) * 100
        或: TSS = (IF^2 * duration_hours) * 100
        
        Args:
            normalized_power: 标准化功率 (watts)
            duration_min: 时长 (分钟)
            intensity_factor: 强度因子 (IF)
        
        Returns:
            int: TSS 值
        """
        duration_hours = duration_min / 60
        
        # 使用 IF 计算
        tss = (intensity_factor ** 2) * duration_hours * 100
        
        return round(tss)
    
    def _calculate_np(self, target_power: int, workout_type: str, sets: int = 1) -> int:
        """
        估算 Normalized Power
        
        - 对于稳定输出，NP ≈ Avg Power
        - 对于间歇，NP 略高于 Avg Power
        
        Args:
            target_power: 目标功率 (watts)
            workout_type: 训练类型
            sets: 组数
        
        Returns:
            int: 估算的 NP
        """
        # 稳定训练类型
        steady_types = ['Z1', 'Z2', 'Z3', 'Threshold']
        
        if workout_type in steady_types or sets == 1:
            # 稳定输出，NP ≈ Avg Power
            return target_power
        else:
            # 间歇训练，NP 略高（考虑恢复期的低功率拉低平均）
            # 估算：间歇训练的 NP 约为目标功率的 95-98%
            # 但由于有恢复期，实际 NP 会更接近目标功率
            np_factor = 0.96 if sets <= 3 else 0.94
            return round(target_power * np_factor)
    
    def _calculate_duration(self, sets: int, work_min: int, rest_min: int = 5) -> dict:
        """
        计算总时长
        
        结构: 热身10min + 主课 + 冷身10min
        
        Args:
            sets: 组数
            work_min: 每组工作时长 (分钟)
            rest_min: 组间休息时长 (分钟)，默认5分钟
        
        Returns:
            dict: 时长详情
        """
        warmup_min = 10
        cooldown_min = 10
        
        # 主课时长 = 组数 * (工作 + 休息) - 最后一次休息
        main_min = sets * work_min + (sets - 1) * rest_min if sets > 0 else 0
        
        total_min = warmup_min + main_min + cooldown_min
        
        return {
            'warmup_min': warmup_min,
            'main_min': main_min,
            'cooldown_min': cooldown_min,
            'total_min': total_min,
            'sets': sets,
            'work_min': work_min,
            'rest_min': rest_min
        }
    
    def _build_structure(self, workout_type: str, sets: int, work_min: int, 
                         rest_min: int, target_power: int, duration_info: dict) -> dict:
        """
        构建 workout 结构数据
        
        Args:
            workout_type: 训练类型
            sets: 组数
            work_min: 工作时长
            rest_min: 休息时长
            target_power: 目标功率
            duration_info: 时长信息
        
        Returns:
            dict: workout 结构
        """
        # 热身功率: 48%-71% FTP
        warmup_start = int(self.ftp * 0.48)
        warmup_end = int(self.ftp * 0.71)
        
        # 冷身功率: 71%-48% FTP
        cooldown_start = int(self.ftp * 0.71)
        cooldown_end = int(self.ftp * 0.48)
        
        # 组间恢复功率: ~58% FTP
        rest_power = int(self.ftp * 0.58)
        
        structure = {
            'warmup': {
                'duration': duration_info['warmup_min'],
                'power_start': warmup_start,
                'power_end': warmup_end
            },
            'main': {
                'sets': sets,
                'work': {
                    'duration': work_min,
                    'power': target_power
                },
                'rest': {
                    'duration': rest_min,
                    'power': rest_power
                }
            },
            'cooldown': {
                'duration': duration_info['cooldown_min'],
                'power_start': cooldown_start,
                'power_end': cooldown_end
            }
        }
        
        return structure
    
    def _generate_description(self, structure: dict) -> str:
        """
        生成 intervals.icu workout 描述语法
        
        格式:
        - {时长}m @{功率}w
        - {时长}m ramp {开始}w-{结束}w
        {组数}x
        - {时长}m @{功率}w
        
        Args:
            structure: workout 结构数据
        
        Returns:
            str: workout 描述
        """
        lines = []
        
        # 热身
        warmup = structure['warmup']
        lines.append(f"-{warmup['duration']}m ramp {warmup['power_start']}w-{warmup['power_end']}w")
        lines.append("")  # 空行
        
        # 主课
        main = structure['main']
        if main['sets'] > 1:
            lines.append(f"{main['sets']}x")
        
        work = main['work']
        rest = main['rest']
        lines.append(f"-{work['duration']}m @{work['power']}w")
        
        if main['sets'] > 1:
            lines.append(f"-{rest['duration']}m @{rest['power']}w")
        
        lines.append("")  # 空行
        
        # 冷身
        cooldown = structure['cooldown']
        lines.append(f"-{cooldown['duration']}m ramp {cooldown['power_start']}w-{cooldown['power_end']}w")
        
        return '\n'.join(lines)
    
    def _generate_name(self, workout_type: str, sets: int, duration_min: int, power: int) -> str:
        """
        生成课程名称
        
        格式: {类型} {组数}x{时间}@{功率}w
        示例: Threshold 2x20min@260w
        
        Args:
            workout_type: 训练类型
            sets: 组数
            duration_min: 时长 (分钟)
            power: 功率 (watts)
        
        Returns:
            str: 课程名称
        """
        if sets == 1:
            return f"{workout_type} {duration_min}min@{power}w"
        else:
            return f"{workout_type} {sets}x{duration_min}min@{power}w"
    
    def adjust_workout(self, workout: dict, adjustments: dict) -> dict:
        """
        根据用户调整修改 workout
        
        Args:
            workout: 原始 workout 数据
            adjustments: 调整参数，如 {'sets': 3, 'duration_min': 15}
        
        Returns:
            dict: 调整后的 workout
        """
        # 创建副本
        adjusted = workout.copy()
        structure = workout.get('structure', {}).copy() if workout.get('structure') else None
        
        if structure:
            # 更新组数
            if 'sets' in adjustments:
                structure['main']['sets'] = adjustments['sets']
            
            # 更新时长
            if 'duration_min' in adjustments:
                structure['main']['work']['duration'] = adjustments['duration_min']
            
            # 更新功率
            if 'intensity_pct' in adjustments:
                new_power = self._calculate_power(adjustments['intensity_pct'])
                structure['main']['work']['power'] = new_power
            
            # 重新计算
            duration_info = self._calculate_duration(
                structure['main']['sets'],
                structure['main']['work']['duration'],
                structure['main']['rest']['duration']
            )
            
            target_power = structure['main']['work']['power']
            workout_type = adjusted.get('type', 'Z2')
            sets = structure['main']['sets']
            
            np = self._calculate_np(target_power, workout_type, sets)
            intensity_factor = self.WORKOUT_INTENSITY_FACTORS.get(workout_type, 0.85)
            tss = self._calculate_tss(np, duration_info['total_min'], intensity_factor)
            
            # 更新结构
            adjusted['structure'] = self._build_structure(
                workout_type, sets, structure['main']['work']['duration'],
                structure['main']['rest']['duration'], target_power, duration_info
            )
            
            # 更新其他字段
            adjusted['name'] = self._generate_name(workout_type, sets, structure['main']['work']['duration'], target_power)
            adjusted['description'] = self._generate_description(adjusted['structure'])
            adjusted['duration_min'] = duration_info['total_min']
            adjusted['tss'] = tss
            adjusted['np'] = np
        
        return adjusted
    
    def format_for_display(self, workouts: list, ftp: int, rationale: str = "") -> str:
        """
        格式化 workouts 用于展示
        
        Args:
            workouts: workout 列表
            ftp: FTP 值
            rationale: LLM 的决策理由
        
        Returns:
            str: 格式化后的展示文本
        """
        lines = []
        lines.append("🚴 **Workout 生成**")
        lines.append("")
        lines.append(f"👤 Carno  ⚡ FTP {ftp}w")
        
        if rationale:
            lines.append(f"💡 {rationale}")
        
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        for workout in workouts:
            lines.append(f"📅 **{workout['date']} ({workout['weekday']})** — **{workout['name']}**")
            lines.append("")
            
            if workout.get('is_rest'):
                lines.append(workout['description'])
            else:
                lines.append("```")
                lines.append(workout['description'])
                lines.append("```")
                lines.append(f"⏱️ {workout['duration_min']}min · ⚡ NP ~{workout['np']}w · 📊 TSS {workout['tss']}")
            
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
        
        lines.append(f"**总结**: 共生成 **{len(workouts)}** 个 workouts")
        lines.append("")
        lines.append("💡 调整还是上传？")
        lines.append("• 调整：告诉我修改内容（如「周四改成3组」、「周六缩短到80分钟」）")
        lines.append("• 上传：回复「上传」直接上传到 intervals.icu")
        
        return '\n'.join(lines)


def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: workout_calculator.py <ftp> <base_date> '<plan_json>'")
        print("Example: workout_calculator.py 260 2026-03-11 '{\"rationale\":\"...\",\"workouts\":[...]}'")
        sys.exit(1)
    
    ftp = int(sys.argv[1])
    base_date = sys.argv[2]
    plan_json_str = sys.argv[3]
    
    try:
        plan_json = json.loads(plan_json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    calculator = WorkoutCalculator(ftp=ftp)
    workouts = calculator.calculate_from_plan(plan_json, base_date)
    
    # 输出 JSON
    output = {
        'rationale': plan_json.get('rationale', ''),
        'workouts': workouts
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
