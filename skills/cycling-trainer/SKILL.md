---
name: cycling-trainer
description: 公路车骑行训练数据分析与规划工具。使用 intervals.icu API 进行训练数据获取、同步、持久化保存。Python只负责数据提取，所有分析判断由LLM通过不同prompt完成。
---

# Cycling Trainer - 公路车训练助手 (重构版)

## 架构设计

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Discord/TG    │────▶│  Python Extractor │────▶│      LLM        │
│   /ride-xxx     │     │  (extract_data.py)│     │  (Prompt-based) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                           │
                              ▼                           ▼
                        ┌──────────────┐           ┌──────────────┐
                        │ activities.json│          │  Analysis &  │
                        │ sync_state.json│          │  Recommendations│
                        └──────────────┘           └──────────────┘
```

**核心原则**: Python只做数据提取和结构化，不做任何if-else判断。所有分析、建议、计划生成由LLM通过专用prompt完成。

---

## Agent 执行流程

当收到 `/ride-xxx` 命令时（除 `/ride-sync`）：

```
1. 根据命令类型调用 extract_data.py 提取对应数据
2. 读取对应 prompt 文件
3. 结合数据和 prompt 进行分析并回复
```

---

## 配置方式

支持三种方式配置 athlete_id 和 api_key（优先级从高到低）：

### 方式1：配置文件（推荐）

```bash
# 1. 复制示例配置文件
cp config.example.json config.json

# 2. 编辑 config.json，填入真实信息
{
  "athlete_id": "your_athlete_id_here",
  "api_key": "your_api_key_here"
}
```

### 方式2：环境变量

```bash
export INTERVALS_ATHLETE_ID="your_athlete_id_here"
export INTERVALS_API_KEY="your_api_key_here"
```

### 方式3：命令行参数

```bash
python3 scripts/sync_intervals.py <athlete_id> --api-key <key>
python3 scripts/extract_data.py --status --athlete-id <athlete_id> --api-key <key>
```

---

## 快速开始

### 1. 数据同步

```bash
# 首次全量同步（需先配置好 config.json 或环境变量）
python3 skills/cycling-trainer/scripts/sync_intervals.py --full

# 或使用命令行参数
python3 skills/cycling-trainer/scripts/sync_intervals.py <athlete_id> --api-key <key> --full

# 增量同步
python3 skills/cycling-trainer/scripts/sync_intervals.py

# 强制同步最近N天
python3 skills/cycling-trainer/scripts/sync_intervals.py --days 7
```

### 2. 数据提取（供LLM使用）

```bash
# 所有提取命令都支持自动同步检查（默认启用）
# 提取状态数据（如需同步会自动执行）
python3 skills/cycling-trainer/scripts/extract_data.py --status

# 跳过自动同步
python3 skills/cycling-trainer/scripts/extract_data.py --status --no-sync

# 其他提取命令
python3 skills/cycling-trainer/scripts/extract_data.py --form
python3 skills/cycling-trainer/scripts/extract_data.py --trend
python3 skills/cycling-trainer/scripts/extract_data.py --latest
python3 skills/cycling-trainer/scripts/extract_data.py --week
python3 skills/cycling-trainer/scripts/extract_data.py --full
```

---

## Prompt 目录

| Prompt文件 | 用途 | 对应命令 |
|-----------|------|---------|
| `prompts/status_analysis.md` | CTL/ATL/TSB状态分析 | `/ride-stats` |
| `prompts/form_analysis.md` | 巅峰vs当前功率对比 | `/ride-form` |
| `prompts/trend_analysis.md` | 30天趋势解读 | `/ride-trend` |
| `prompts/week_summary.md` | 本周训练总结 | `/ride-week` |
| `prompts/latest_ride_analysis.md` | 单次骑行分析 | `/ride-latest` |
| `prompts/plan_generation.md` | 周期化训练计划 (3+1超量恢复) | `/ride-plan` |

## 周期化训练系统

### 4周超量恢复周期
训练计划采用经典的 **3周强度周 + 1周恢复周** 周期化模式：

```
第1周 (基础强度周): 建立基础，中等负荷
第2周 (递增强度周): 增加难度，提升负荷  
第3周 (峰值强度周): 最大负荷，突破极限
第4周 (恢复周): 主动恢复，超量补偿
```

### 周期记忆
周期状态保存在 `memory/cycling.md` 中，包含：
- 当前周期编号和周期周位置
- 每周完成的训练记录
- 下周训练目标

Agent 调用 `/ride-plan` 时会读取周期记忆，判断当前处于周期的第几周，然后按周期化原则安排训练。

---


## 命令列表

在 Discord/Telegram 骑行频道中直接发送以下命令：

| 命令 | 功能 | 数据提取 | Prompt | 自动同步 |
|------|------|---------|--------|---------|
| `/ride-sync [天数]` | 手动同步数据 | `sync_intervals.py` | - | ❌ 不适用 |
| `/ride-stats` | 当前训练状态 | `--status` | `status_analysis.md` | ✅ |
| `/ride-form` | 状态走势分析 | `--form` | `form_analysis.md` | ✅ |
| `/ride-trend` | 30天趋势分析 | `--trend` | `trend_analysis.md` | ✅ |
| `/ride-week` | 本周训练总结 | `--week` | `week_summary.md` | ✅ |
| `/ride-latest` | 最近一次骑行分析 | `--latest` | `latest_ride_analysis.md` | ✅ |
| `/ride-plan [FTP]` | 个性化训练计划 | `--status` + `--week` | `plan_generation.md` | ✅ |
| `/ride-full` | 完整报告 | `--full` | 组合多个prompt | ✅ |

> ✅ = 执行前自动检查并同步数据（如需要）

---

## 数据结构说明

### Status Data (`--status`)
```json
{
  "latest_activity": {
    "date": "2026-03-04",
    "ctl": 39.96,
    "atl": 39.28,
    "tsb": 0.68,
    "ftp": 260,
    "weight_kg": 65.0
  },
  "week_activities": [...],
  "fitness_history": [...]
}
```

### Form Data (`--form`)
```json
{
  "all_intervals": [
    {
      "activity_date": "2026-01-05",
      "avg_watts": 287,
      "avg_hr": 157,
      "duration_min": 9.9,
      "zone": 4
    }
  ],
  "hr_grouped": {
    "155-159": [...],
    "160-164": [...]
  }
}
```

### Trend Data (`--trend`)
```json
{
  "daily_data": [...],
  "weekly_summary": [
    {
      "week": "2026-W09",
      "count": 3,
      "total_load": 132,
      "avg_intensity": 0.85
    }
  ]
}
```

---

## 本地数据位置

- 活动数据: `~/.openclaw/workspace-cycling/data/cycling/activities.json`
- 同步状态: `~/.openclaw/workspace-cycling/data/cycling/sync_state.json`
- 频道记忆: `~/.openclaw/workspace-cycling/memory/cycling.md`
- 周期记忆: `~/.openclaw/workspace-cycling/memory/cycling.md` (Training Cycle Memory 部分)

---

## 参考资料

- intervals.icu API: [references/api.md](references/api.md)
- 功率训练知识: [references/power_training.md](references/power_training.md)
