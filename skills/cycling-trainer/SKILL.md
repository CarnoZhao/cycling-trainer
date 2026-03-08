---
name: cycling-trainer
description: 公路车骑行训练数据分析与规划工具。使用 intervals.icu API 进行训练数据获取、同步、持久化保存。Python只负责数据提取，所有分析判断由LLM通过不同prompt完成。
---

# Cycling Trainer - 公路车训练助手

## 架构设计

```
Discord/TG Command → extract_data.py → JSON Data + Prompt → LLM Analysis
```

**核心原则**: Python只做数据提取，不做判断。所有分析由LLM通过专用prompt完成。

---

## Agent 执行流程

收到 `/ride-xxx` 命令时（除 `/ride-sync`）：
1. 调用 `extract_data.py` 提取数据（自动检查同步）
2. 读取对应 prompt 文件
3. 结合数据进行分析并回复

**特殊流程 - `/ride-plan`:**
1. 调用 `extract_data.py --plan` 提取数据
2. 读取 `MEMORY.md` 中的 **Training Cycle Memory** 部分
3. 读取 `plan_generation.md` prompt
4. **后台更新 `MEMORY.md`** 周期记忆（用户不可见）
5. 生成训练计划并回复用户（最后一步，确保用户看到的是完整计划）

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
| `/ride-plan [FTP]` | 训练计划 | `--plan` | `plan_generation.md` |
| `/ride-full` | 完整报告 | `--full` | 组合prompt |

> 所有提取命令默认启用自动同步检查

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

| 数据 | 路径 |
|------|------|
| 活动数据 | `data/cycling/activities.json` |
| 同步状态 | `data/cycling/sync_state.json` |
| 频道/周期记忆 | `MEMORY.md` |

---

## 参考资料

- intervals.icu API: [references/api.md](references/api.md)
- 功率训练知识: [references/power_training.md](references/power_training.md)
