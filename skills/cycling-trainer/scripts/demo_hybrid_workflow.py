#!/usr/bin/env python3
"""
演示混合架构工作流

展示 LLM + Python 分层流水线的工作方式
"""
import json
import sys

# 导入 workout_calculator
sys.path.insert(0, '/root/.openclaw/workspace-cycling/skills/cycling-trainer/scripts')
from workout_calculator import WorkoutCalculator


def demo_llm_output():
    """模拟 LLM 输出的 JSON 结构化意图"""
    return {
        "rationale": "第3周峰值强度，安排 Threshold + VO2max。CTL 趋势稳定，TSB 为正，可以承受高负荷。",
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
                "date_offset": 1,
                "type": "Z2",
                "sets": 1,
                "duration_min": 60,
                "intensity_pct": 70,
                "rest_min": 0
            },
            {
                "date_offset": 2,
                "type": "Rest",
                "sets": 0,
                "duration_min": 0,
                "intensity_pct": 0,
                "rest_min": 0
            },
            {
                "date_offset": 3,
                "type": "VO2max",
                "sets": 5,
                "duration_min": 4,
                "intensity_pct": 118,
                "rest_min": 4
            },
            {
                "date_offset": 4,
                "type": "Z2",
                "sets": 1,
                "duration_min": 90,
                "intensity_pct": 68,
                "rest_min": 0
            },
            {
                "date_offset": 5,
                "type": "Rest",
                "sets": 0,
                "duration_min": 0,
                "intensity_pct": 0,
                "rest_min": 0
            },
            {
                "date_offset": 6,
                "type": "Z2",
                "sets": 1,
                "duration_min": 120,
                "intensity_pct": 65,
                "rest_min": 0
            }
        ]
    }


def demo_python_calculation():
    """演示 Python 层精确计算"""
    print("=" * 60)
    print("混合架构演示: LLM + Python 分层流水线")
    print("=" * 60)
    print()
    
    # 配置
    ftp = 260
    base_date = "2026-03-11"  # 假设今天是 2026-03-11 (周三)
    
    print(f"配置: FTP={ftp}w, 基础日期={base_date}")
    print()
    
    # Layer 1: LLM 输出结构化意图
    print("-" * 60)
    print("Layer 1: LLM 输出结构化意图 (JSON)")
    print("-" * 60)
    
    llm_intent = demo_llm_output()
    print(json.dumps(llm_intent, indent=2, ensure_ascii=False))
    print()
    
    # Layer 2: Python 精确计算
    print("-" * 60)
    print("Layer 2: Python 精确计算")
    print("-" * 60)
    
    calculator = WorkoutCalculator(ftp=ftp)
    workouts = calculator.calculate_from_plan(llm_intent, base_date)
    
    print(f"✓ 计算了 {len(workouts)} 个 workouts")
    print(f"✓ 精确日期计算（自动匹配星期几）")
    print(f"✓ 功率计算（FTP × 百分比）")
    print(f"✓ TSS/NP 计算（标准公式）")
    print(f"✓ Workout 语法生成（intervals.icu 格式）")
    print()
    
    # Layer 3: 合并展示
    print("-" * 60)
    print("Layer 3: 合并展示")
    print("-" * 60)
    print()
    
    display = calculator.format_for_display(
        workouts, 
        ftp=ftp, 
        rationale=llm_intent['rationale']
    )
    print(display)
    print()
    
    # 展示单个 workout 的详细结构
    print("-" * 60)
    print("详细数据结构（第一个 workout）")
    print("-" * 60)
    print(json.dumps(workouts[0], indent=2, ensure_ascii=False))
    print()
    
    return workouts, calculator


def demo_adjustment(workouts, calculator):
    """演示用户调整功能"""
    print("=" * 60)
    print("用户调整演示")
    print("=" * 60)
    print()
    
    # 用户说："周四改成3组"
    print("用户指令: '周四改成3组'")
    print()
    
    # 找到周四的 workout
    thursday_workout = None
    for w in workouts:
        if w['weekday'] == '周四':
            thursday_workout = w
            break
    
    if thursday_workout:
        print(f"找到周四 workout: {thursday_workout['name']}")
        print(f"当前组数: {thursday_workout['structure']['main']['sets']}")
        print()
        
        # 调整
        adjusted = calculator.adjust_workout(thursday_workout, {'sets': 3})
        
        print("调整后:")
        print(f"  名称: {adjusted['name']}")
        print(f"  时长: {adjusted['duration_min']}min")
        print(f"  TSS: {adjusted['tss']}")
        print(f"  NP: {adjusted['np']}w")
        print()
        print("Workout 描述:")
        print("```")
        print(adjusted['description'])
        print("```")
    else:
        print("未找到周四的 workout")


def demo_cli():
    """演示 CLI 使用"""
    print("=" * 60)
    print("CLI 使用示例")
    print("=" * 60)
    print()
    
    plan_json = json.dumps(demo_llm_output())
    
    print("命令:")
    print(f"python3 workout_calculator.py 260 2026-03-11 '{plan_json[:50]}...'")
    print()
    
    # 模拟 CLI 输出
    calculator = WorkoutCalculator(ftp=260)
    workouts = calculator.calculate_from_plan(demo_llm_output(), "2026-03-11")
    
    output = {
        'rationale': demo_llm_output()['rationale'],
        'workouts': workouts
    }
    
    print("输出:")
    print(json.dumps(output, indent=2, ensure_ascii=False)[:800] + "...")
    print()


def main():
    """主函数"""
    # 演示完整流程
    workouts, calculator = demo_python_calculation()
    
    # 演示调整功能
    demo_adjustment(workouts, calculator)
    
    # 演示 CLI
    demo_cli()
    
    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print()
    print("关键改进:")
    print("1. ✓ 日期计算精确（Python datetime，不再出错）")
    print("2. ✓ 功率计算精确（FTP × 百分比）")
    print("3. ✓ TSS/NP 计算精确（标准公式）")
    print("4. ✓ Workout 语法格式正确（结构化生成）")
    print("5. ✓ 用户调整即时重新计算")


if __name__ == "__main__":
    main()
