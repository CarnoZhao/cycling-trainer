# 混合架构实现总结

## 概述

成功实现了 LLM + Python 混合架构，解决原有纯 LLM 方案的问题。

## 解决的问题

| 问题 | 原方案 | 新方案 |
|------|--------|--------|
| 日期计算错误 | LLM 计算日期和星期几 | Python datetime 精确计算 |
| TSS/NP 估算不准 | LLM 估算 | Python 标准公式精确计算 |
| Workout 语法错误 | LLM 生成文本 | Python 结构化生成 |

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: LLM 输出结构化意图（JSON）                           │
│  - 训练类型决策                                               │
│  - 组数/时长规划                                              │
│  - 强度百分比选择                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Python 精确计算 (workout_calculator.py)             │
│  - 日期计算（精确到星期几）                                    │
│  - 功率计算（FTP × 百分比）                                    │
│  - TSS/NP 计算（标准公式）                                    │
│  - Workout 语法生成（intervals.icu 格式）                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 合并展示                                            │
│  - 格式化输出                                                 │
│  - 用户确认/调整                                              │
│  - 上传到 intervals.icu                                       │
└─────────────────────────────────────────────────────────────┘
```

## 新增文件

### 1. `scripts/workout_calculator.py`
核心计算模块，提供 `WorkoutCalculator` 类：

```python
class WorkoutCalculator:
    def __init__(self, ftp: int, athlete_weight: float = None)
    def calculate_from_plan(self, plan_json: dict, base_date: str) -> list
    def adjust_workout(self, workout: dict, adjustments: dict) -> dict
    def format_for_display(self, workouts: list, ftp: int, rationale: str = "") -> str
```

### 2. `tests/test_workout_calculator.py`
完整测试套件，27 个测试用例覆盖：
- 日期计算（验证星期几匹配）
- 功率计算（验证 FTP 百分比转换）
- TSS 计算（验证标准公式）
- workout 语法生成（验证格式正确）
- 完整流程（从 JSON 到最终输出）

### 3. `scripts/demo_hybrid_workflow.py`
演示脚本，展示完整工作流程

## 修改的文件

### 1. `prompts/commands/plan_generation.md`
- 移除详细输出格式模板
- 改为要求 LLM 输出 JSON 结构化意图
- 保留 rationale 字段

### 2. `prompts/commands/workout_generation.md`
- 同样改为 JSON 输出格式
- 移除 workout 语法生成说明（移到 Python 层）

### 3. `SKILL.md`
- 添加混合架构说明
- 更新 `/ride-plan` 流程
- 添加 workout_calculator 使用文档

## JSON 数据格式

### LLM 输出格式

```json
{
  "rationale": "第3周峰值强度，安排 Threshold + VO2max",
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
```

### Python 输出格式

```json
{
  "date": "2026-03-11",
  "weekday": "周三",
  "name": "Threshold 2x20min@260w",
  "type": "Threshold",
  "description": "-10m ramp 125w-185w\n\n2x\n-20m @260w\n-5m @150w\n\n-10m ramp 185w-125w",
  "duration_min": 70,
  "tss": 96,
  "np": 260,
  "structure": {
    "warmup": {"duration": 10, "power_start": 125, "power_end": 185},
    "main": {"sets": 2, "work": {"duration": 20, "power": 260}, "rest": {"duration": 5, "power": 150}},
    "cooldown": {"duration": 10, "power_start": 185, "power_end": 125}
  }
}
```

## 新的 `/ride-plan` 流程

```
1. 调用 extract_data.py --plan 提取数据
2. 读取 plan_generation.md prompt
3. 调用 LLM → 获取 JSON 意图
4. 调用 workout_calculator.calculate_from_plan() → 精确计算
5. 格式化输出给用户
6. 询问是否需要调整或上传
```

## 用户调整流程

```
用户说"周四改成3组"时：
1. 解析用户意图，定位到对应 workout
2. 调用 calculator.adjust_workout({'sets': 3})
3. 重新计算日期、功率、TSS、NP、描述
4. 展示新结果
```

## 边界情况处理

| 情况 | 处理方式 |
|------|----------|
| date_offset 为负数 | 抛出 ValueError |
| intensity_pct > 150% | 警告但仍计算 |
| sets = 0 | 视为休息日 |
| 缺少 rest_min | 使用默认值 5min |

## 测试

```bash
# 运行所有测试
cd /root/.openclaw/workspace-cycling/skills/cycling-trainer
python3 tests/test_workout_calculator.py

# 运行演示
cd /root/.openclaw/workspace-cycling/skills/cycling-trainer
python3 scripts/demo_hybrid_workflow.py
```

## 向后兼容

- 保持现有命令不变
- 不影响 `/ride-stats`, `/ride-week` 等非计划命令
- 仅 `/ride-plan` 和相关 workout 生成功能使用新架构
