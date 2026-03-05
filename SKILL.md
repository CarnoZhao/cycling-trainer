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

## 快速开始

### 1. 数据同步

```bash
# 首次全量同步
python3 scripts/sync_intervals.py <athlete_id> --api-key <key> --full

# 增量同步
python3 scripts/sync_intervals.py <athlete_id> --api-key <key>

# 强制同步最近N天
python3 scripts/sync_intervals.py <athlete_id> --api-key <key> --days 7
```

### 2. 数据提取（供LLM使用）

```bash
# 提取状态数据
python3 scripts/extract_data.py --status

# 提取状态走势数据
python3 scripts/extract_data.py --form

# 提取趋势数据
python3 scripts/extract_data.py --trend

# 提取最近一次骑行
python3 scripts/extract_data.py --latest

# 提取本周数据
python3 scripts/extract_data.py --week

# 提取全部数据
python3 scripts/extract_data.py --full
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
| `prompts/plan_generation.md` | 个性化训练计划 | `/ride-plan` |

---

## 命令列表

在 Discord/Telegram 骑行频道中直接发送以下命令：

| 命令 | 功能 | 数据提取 | Prompt |
|------|------|---------|--------|
| `/ride-sync [天数]` | 同步数据 | `sync_intervals.py` | - |
| `/ride-stats` | 当前训练状态 | `--status` | `status_analysis.md` |
| `/ride-form` | 状态走势分析 | `--form` | `form_analysis.md` |
| `/ride-trend` | 30天趋势分析 | `--trend` | `trend_analysis.md` |
| `/ride-week` | 本周训练总结 | `--week` | `week_summary.md` |
| `/ride-latest` | 最近一次骑行分析 | `--latest` | `latest_ride_analysis.md` |
| `/ride-plan [FTP]` | 个性化训练计划 | `--status` + `--week` | `plan_generation.md` |
| `/ride-full` | 完整报告 | `--full` | 组合多个prompt |

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

- 活动数据: `/root/.openclaw/workspace/data/cycling/activities.json`
- 同步状态: `/root/.openclaw/workspace/data/cycling/sync_state.json`
- 频道记忆: `/root/.openclaw/workspace/memory/cycling.md`

---

## 参考资料

- intervals.icu API: [references/api.md](references/api.md)
- 功率训练知识: [references/power_training.md](references/power_training.md)
