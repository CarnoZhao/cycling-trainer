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

## Workout 生成与上传流程

Workout 生成不是独立命令，而是 `/ride-plan` 后的持续对话交互。

### 流程

```
1. /ride-plan → 询问「需要生成 intervals.icu workout 吗？」
                    ↓ 肯定答复
2. 生成 **未来7天所有训练** 的 workouts
   - 包括：强度课 + Z2有氧 + 恢复周课程
   - **必须包含休息日**（标注为休息日，不生成 workout 描述）
   - **必须核对日期和星期几的对应关系**
   - 展示所有 workouts 供用户确认
                    ↓ 用户要求调整
3. 根据反馈调整（功率、时长、日期等）
                    ↓ 用户确认「上传」
4. 调用 API 上传到 intervals.icu → 完成
```

### Workout 生成规则

**生成范围**:
- 从今天起向后规划 **7天**（包括今天）
- 每一天都必须列出，即使是休息日
- 休息日标注为「🛌 完全休息」，无需 workout 描述

**日期核对**（关键！）:
- 生成前必须核对日期和星期几的对应关系
- 格式: `3/12 (周四)` — 确保日期和星期几匹配
- 今天是周二 → 明天是周三 → 后天是周四...

**课程类型覆盖**:
- 强度课（SS/Threshold/VO2max）：必须有 workout 描述
- Z2 有氧骑：必须有 workout 描述
- 恢复周课程：必须有 workout 描述
- 休息日：标注为「完全休息」，无 workout 描述

### 用户指令

| 阶段 | 用户回复 | 动作 |
|------|---------|------|
| 询问生成 | 「需要」、「生成」 | 进入生成阶段，生成**所有**未来训练 |
| 查看确认 | 「上传」或「调整」 | 确认后上传，或根据反馈调整 |
| 调整指令 | 「周四改成3组」、「缩短到80分钟」、「功率提到250w」等 | 修改对应 workout |
| 日期调整 | 「把周四的课改到周三」 | 调整日期，注意核对星期几 |

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

**Z2 Easy 恢复骑模板** (参考本周二课表):
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

| 数据 | 路径 |
|------|------|
| 活动数据 | `data/cycling/activities.json` |
| 同步状态 | `data/cycling/sync_state.json` |
| 频道/周期记忆 | `MEMORY.md` |

---

## 参考资料

- intervals.icu API: [references/api.md](references/api.md)
- 功率训练知识: [references/power_training.md](references/power_training.md)
