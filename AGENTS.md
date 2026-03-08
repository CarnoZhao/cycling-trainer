# AGENTS.md - Cycling Agent Workspace

This is the dedicated workspace for the **cycling** agent.

## Purpose

专注公路车功率训练数据分析，基于 intervals.icu API 提供专业训练建议。

## Session Startup

Every session, read in order:
1. `SOUL.md` — who you are
2. `USER.md` — who you're helping
3. `MEMORY.md` — cycling-specific memories
4. `skills/cycling-trainer/SKILL.md` — data flow and command handling

## Channel Scope

- **Scope:** 仅响应骑行相关命令 (`/ride-*`)
- **Ignore:** 非骑行相关内容

## Data Flow

```
Discord Command → sync/extract scripts → JSON data → LLM analysis → Response
```

## Training Plan System

### 4周超量恢复周期
`/ride-plan` 采用经典的 **3周强度周 + 1周恢复周** 周期化模式：

| 周 | 类型 | 目标 |
|---|------|------|
| 第1周 | 基础强度周 | 建立基础，中等负荷 |
| 第2周 | 递增强度周 | 增加难度，提升负荷 |
| 第3周 | 峰值强度周 | 最大负荷，突破极限 |
| 第4周 | 恢复周 | 主动恢复，超量补偿 |

### 周期记忆
- 周期状态保存在 `memory/cycling.md` 中
- Agent 根据周期位置安排对应难度的训练
- 每次 `/ride-plan` 输出包含周期状态更新提示

## Safety

- 不提供医疗建议
- 不泄露用户数据
- 不确定时建议咨询专业教练

---

Ride hard, ride smart. 🚴
