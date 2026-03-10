# Cycling Trainer Skill - 技术路线图

## 当前已完成优化

### P0 - 架构重构 ✅
- [x] Prompt 模块化（core/ templates/ commands/ 分层）
- [x] 周期记忆 JSON 化（Markdown → JSON 数据库）

### P1 - 代码精简 ✅
- [x] Python 代码精简（合并 storage、提取工具函数）
- [x] 安全漏洞修复（移除硬编码凭据）

### P2 - 测试覆盖 ⏳
- [ ] 单元测试（进行中，subagent 执行中）

---

## 下一阶段：LLM + Python 混合架构

### 问题定义

LLM 擅长：训练计划制定、课程结构设计、根据状态调整  
LLM 不擅长：日期计算、TSS/NP 精确计算、workout 语法格式

### 解决方案：分层流水线

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: LLM 战略层（只做决策）                              │
│  ─────────────────────────────                               │
│  • 根据周期位置决定课程类型（SS/Threshold/VO2max）            │
│  • 确定组数、时长、功率百分比                                  │
│  • 输出结构化意图（JSON）                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Python 计算层（精确执行）                           │
│  ─────────────────────────────────                           │
│  • 日期计算：today → 未来7天，精确匹配星期几                   │
│  • 功率计算：%FTP → 绝对功率值                                │
│  • TSS/NP 计算：标准算法（30秒滑动窗口）                      │
│  • 时长计算：workout 步骤累加                                 │
│  • 语法生成：intervals.icu 格式                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 展示层（人类可读）                                  │
│  ─────────────────────────                                   │
│  • 合并 LLM 的决策理由 + Python 的精确数据                    │
│  • 格式化输出表格/列表                                        │
└─────────────────────────────────────────────────────────────┘
```

### 数据结构

#### LLM 输出（结构化意图）
```json
{
  "plan_date": "2026-03-12",
  "rationale": "第3周峰值强度，Threshold 主课",
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
      "intensity_pct": 115,
      "rest_min": 3
    }
  ]
}
```

#### Python 计算输出
```json
{
  "date": "2026-03-12",
  "weekday": "周四",
  "name": "Threshold 2x20min@260w",
  "description": "-10m ramp 125w-185w\n\n2x\n-20m @260w\n-5m @150w\n\n-10m ramp 185w-125w",
  "duration_min": 70,
  "tss": 96,
  "np": 260,
  "rationale": "第3周峰值强度，Threshold 主课"
}
```

### 实现计划

#### 新增文件
- `scripts/workout_calculator.py` - 核心计算模块
  - `WorkoutCalculator` 类
  - `calculate()` - 主计算函数
  - `_generate_description()` - workout 语法生成
  - `_calculate_tss()` - TSS 标准算法
  - `_calculate_np()` - NP 标准算法

#### 修改文件
- `prompts/commands/plan_generation.md` - 改为输出 JSON 意图而非完整描述
- `prompts/commands/workout_generation.md` - 改为输出 JSON 意图
- `SKILL.md` - 更新 workflow 说明

#### 调用流程
```
用户: /ride-plan

1. Agent 读取周期记忆、当前状态
2. 调用 LLM（带 prompt）→ 输出 JSON 意图
3. Python 计算层处理 → 精确日期、TSS、NP、workout 语法
4. 合并展示 → 用户看到完整计划
5. 询问: "需要调整还是上传？"

用户: "周四改成3组"
→ 修改 JSON → 重算 → 展示新结果
```

### 关键优势

| 优势 | 说明 |
|------|------|
| **日期准确** | Python 计算，无幻觉 |
| **TSS/NP 精确** | 标准算法，非估算 |
| **格式一致** | 模板化输出，不会语法错误 |
| **可调整** | 用户说"周四改成3组"→改 JSON →重算 |
| **可验证** | JSON 是中间态，可检查 LLM 决策 |

---

## 未来可能优化

### 数据流优化（暂缓）
- [ ] 计算缓存（当前数据量小，暂不急需）

### 功能扩展
- [ ] 自动识别活动类型（从 intervals 数据自动分类）
- [ ] 训练效果预测（基于 CTL/TSB 趋势）
- [ ] 多周期对比分析

### 集成增强
- [ ] 与 Strava API 直接同步
- [ ] 支持 Garmin Connect 数据导入
- [ ] 训练计划日历订阅（ICS 格式）

---

## 记录时间
- 创建: 2026-03-10
- 最后更新: 2026-03-10
