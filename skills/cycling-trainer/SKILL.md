---
name: cycling-trainer
description: 公路车骑行训练数据分析与规划工具。使用 intervals.icu API 进行训练数据获取、同步、持久化保存。Python只负责数据提取，所有分析判断由LLM通过不同prompt完成。
---

# Cycling Trainer - 公路车训练助手

## 架构设计

### 混合流水线架构 (LLM + Python)

为了解决纯 LLM 生成的问题（日期计算错误、TSS/NP 估算不准、workout 语法格式错误），我们采用分层流水线架构：

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: LLM 输出结构化意图（JSON）                           │
│  - 训练类型决策                                               │
│  - 组数/时长规划                                              │
│  - 强度百分比选择                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Python 精确计算                                     │
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

**核心原则**: 
- LLM 负责策略决策（做什么训练）
- Python 负责精确计算（具体数值）
- 两者通过 JSON 结构化数据交互

---

## Agent 执行流程

### 标准命令流程

收到 `/ride-xxx` 命令时（除 `/ride-sync`）：
1. 调用 `extract_data.py` 提取数据（自动检查同步）
2. 读取对应 prompt 文件
3. 结合数据进行分析并回复

### `/ride-plan` 流程（新混合架构）

```
1. 调用 extract_data.py --plan 提取数据
2. 调用 extract_data.py --cycle-memory 获取周期记忆
3. 读取 plan_generation.md prompt
4. 调用 LLM → 获取 JSON 意图（rationale + workouts 数组）
5. 调用 workout_calculator.calculate_from_plan() → 精确计算
   - 计算日期和星期几
   - 计算绝对功率
   - 计算 TSS/NP
   - 生成 workout 描述语法
6. 格式化输出给用户
7. 询问是否需要调整或上传
```

### `/ride-plan` 后的交互流程

```
用户说"周四改成3组"时：
1. 解析用户意图，定位到对应 workout
2. 调用 calculator.adjust_workout() 修改 JSON
3. 重新计算日期、功率、TSS、NP、描述
4. 展示新结果
5. 询问是否上传
```

---

## Workout Calculator 使用文档

### 核心类: `WorkoutCalculator`

```python
from workout_calculator import WorkoutCalculator

# 初始化
calculator = WorkoutCalculator(ftp=260, athlete_weight=70)

# 从 LLM 意图计算完整 workout
plan_json = {
    "rationale": "第3周峰值强度",
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
workouts = calculator.calculate_from_plan(plan_json, base_date='2026-03-11')

# 调整 workout
adjusted = calculator.adjust_workout(workout, {'sets': 3})

# 格式化展示
display = calculator.format_for_display(workouts, ftp=260, rationale="...")
```

### CLI 使用

```bash
# 计算 workouts
python3 scripts/workout_calculator.py 260 2026-03-11 '{"rationale":"...","workouts":[...]}'

# 输出 JSON 格式
{
  "rationale": "...",
  "workouts": [
    {
      "date": "2026-03-11",
      "weekday": "周三",
      "name": "Threshold 2x20min@260w",
      "type": "Threshold",
      "description": "...",
      "duration_min": 70,
      "tss": 96,
      "np": 260,
      "structure": {...}
    }
  ]
}
```

### 计算方法

| 方法 | 功能 |
|------|------|
| `_calculate_date()` | 计算精确日期和星期几 |
| `_calculate_power()` | FTP × 百分比 = 绝对功率 |
| `_calculate_tss()` | TSS = (IF² × hours × 100) |
| `_calculate_np()` | 估算 Normalized Power |
| `_calculate_duration()` | 总时长 = 热身 + 主课 + 冷身 |
| `_generate_description()` | 生成 intervals.icu 语法 |
| `_generate_name()` | 生成课程名称 |

---

## 配置方式

优先级：配置文件 > 环境变量 > 命令行参数

```bash
# 方式1: 配置文件 (推荐)
cp config.example.json config.json
# 编辑填入 athlete_id 和 api_key

# 方式2: 环境变量
export INTERVALS_ATHLETE_ID="xxx"
export INTERVALS_API_KEY="xxx"

# 方式3: 命令行参数
python3 scripts/sync_intervals.py <athlete_id> --api-key <key>
```

---

## 快速开始

```bash
# 首次全量同步
python3 skills/cycling-trainer/scripts/sync_intervals.py --full

# 增量同步（自动跳过4小时内数据）
python3 skills/cycling-trainer/scripts/sync_intervals.py

# 数据提取供LLM使用
python3 skills/cycling-trainer/scripts/extract_data.py --week

# 测试 workout 计算器
python3 skills/cycling-trainer/tests/test_workout_calculator.py
```

---

## 命令列表

| 命令 | 功能 | 数据提取 | Prompt |
|------|------|---------|--------|
| `/ride-sync [天数]` | 手动同步 | `sync_intervals.py` | - |
| `/ride-stats` | 训练状态 | `--status` | `status_analysis.md` |
| `/ride-form` | 状态走势 | `--form` | `form_analysis.md` |
| `/ride-trend` | 30天趋势 | `--trend` | `trend_analysis.md` |
| `/ride-week` | 本周总结 | `--week` | `week_summary.md` |
| `/ride-latest` | 单次分析 | `--latest` | `latest_ride_analysis.md` |
| `/ride-plan [FTP]` | 训练计划 | `--plan` | `plan_generation.md` → `workout_calculator.py` |
| `/ride-full` | 完整报告 | `--full` | 组合prompt |

> 所有提取命令默认启用自动同步检查

---

## Workout 生成与上传流程

Workout 生成不是独立命令，而是 `/ride-plan` 后的持续对话交互。

### 流程

```
1. /ride-plan → LLM 输出 JSON → Python 计算 → 展示结果
                    ↓ 用户说「需要生成 workout」
2. 生成 **未来7天所有训练** 的 workouts
   - 包括：强度课 + Z2有氧 + 恢复周课程
   - **必须包含休息日**（sets: 0）
   - Python 精确计算日期、功率、TSS、NP
   - 展示所有 workouts 供用户确认
                    ↓ 用户要求调整
3. 根据反馈调整（功率、时长、日期等）
   - 调用 calculator.adjust_workout()
   - 重新计算并展示
                    ↓ 用户确认「上传」
4. 调用 API 上传到 intervals.icu → 完成
```

### 用户指令

| 阶段 | 用户回复 | 动作 |
|------|---------|------|
| 询问生成 | 「需要」、「生成」 | 进入生成阶段，生成**所有**未来训练 |
| 查看确认 | 「上传」或「调整」 | 确认后上传，或根据反馈调整 |
| 调整指令 | 「周四改成3组」、「缩短到80分钟」、「功率提到250w」等 | 修改对应 workout |
| 日期调整 | 「把周四的课改到周三」 | 调整 date_offset，Python 重新计算 |

### 上传技术细节

**Python 脚本**: `upload_workouts.py`
- 计算准确的 `moving_time`（秒）和 `icu_training_load`（TSS）
- 使用标准 NP 算法（30秒滑动窗口平均的四次方平均再开四次方）
- **API 认证**: Basic Auth with base64 encoded `API_KEY:{api_key}`
- **API URL**: `POST /api/v1/athlete/{athlete_id}/events/bulk?upsertOnUid=false&updatePlanApplied=false`

**Workout 描述语法**:
```
- {时长}m @{功率}w           # 固定功率
- {时长}m ramp {开始}w-{结束}w  # 渐进式ramp
{组数}x                      # 重复组标记
- {时长}m @{功率}w           # 组内步骤
```

**热身冷身功率限制** (基于 FTP):
- 热身: ramp 48%-71% FTP
- 冷身: ramp 71%-48% FTP  
- 组间恢复: ~58% FTP

**强度课命名规则**:
- 格式: `{类型} {组数}x{时间}@{功率}w`
- 示例: `Threshold 2x20min@260w`, `VO2max 5x4min@310w`
- 使用**绝对功率值**，不用百分比

**Z2 Easy 恢复骑模板** (参考):
```
-10m ramp 125w-175w
4x
-5m 165w
-5m 175w
-10m ramp 175w-125w
```

---

## 周期化训练系统

**4周超量恢复周期**: 3周强度周 + 1周恢复周

| 周 | 类型 | 目标 |
|---|------|------|
| 第1周 | 基础强度周 | 建立基础，中等负荷 |
| 第2周 | 递增强度周 | 增加难度，提升负荷 |
| 第3周 | 峰值强度周 | 最大负荷，突破极限 |
| 第4周 | 恢复周 | 主动恢复，超量补偿 |

**周期记忆**: 保存在 `MEMORY.md` (workspace 根目录)，包含周期位置、训练记录、下周目标。

---

## 本地数据位置

| 数据 | 路径 | 说明 |
|------|------|------|
| 活动数据 | `data/cycling/activities.json` | 从 intervals.icu 同步的原始活动数据 |
| 同步状态 | `data/cycling/sync_state.json` | 同步时间戳等状态 |
| 周期记忆 | `data/cycling/cycle_memory.json` | **JSON 数据库**，包含周期状态、训练记录 |
| 周期记忆视图 | `MEMORY.md` | 由 `cycle_memory.json` **自动生成**，只读 |

## 周期记忆系统

周期记忆现在使用 JSON 数据库存储，提供更强的数据完整性和可维护性。

### 架构变更

**旧架构**: MEMORY.md 纯文本 → 正则匹配更新 ❌
**新架构**: cycle_memory.json → cycle_memory.py API → MEMORY.md 自动生成 ✅

### API 接口 (`scripts/cycle_memory.py`)

```python
from cycle_memory import (
    load_memory,           # 加载周期记忆
    save_memory,           # 保存周期记忆
    get_current_cycle,     # 获取当前周期信息
    update_week_activity,  # 更新本周活动
    advance_week,          # 进入下一周
    start_new_cycle,       # 开始新周期
    export_to_markdown,    # 导出为 Markdown
)

# 或使用管理器类
from cycle_memory import CycleMemoryManager
manager = CycleMemoryManager()
memory = manager.load_memory()
manager.export_to_markdown()
```

### 数据提取

```bash
# 提取周期记忆数据
python3 scripts/extract_data.py --cycle-memory

# 生成 MEMORY.md（从 JSON 自动更新）
python3 scripts/generate_memory_md.py
```

### 更新 MEMORY.md

当修改了 `cycle_memory.json` 后，运行以下命令重新生成 MEMORY.md：

```bash
python3 skills/cycling-trainer/scripts/generate_memory_md.py
```

---

## 参考资料

- intervals.icu API: [references/api.md](references/api.md)
- 功率训练知识: [references/power_training.md](references/power_training.md)
- Workout Calculator: [scripts/workout_calculator.py](scripts/workout_calculator.py)
