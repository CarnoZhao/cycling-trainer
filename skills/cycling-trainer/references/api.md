# Intervals.icu API 文档

## 认证

### API Key 获取
1. 登录 intervals.icu
2. 进入设置 → API
3. 创建新的 API Key

### 认证方式
```python
import base64

# Basic Auth 格式
basic_token = base64.b64encode(f"API_KEY:{api_key}".encode("ascii")).decode()
headers = {
    "Authorization": f"Basic {basic_token}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

---

## 核心 API 端点

### 1. 获取活动列表
```
GET /api/v1/athlete/{athlete_id}/activities
```

**参数:**
- `oldest`: 开始日期 ISO 格式 (如 "2025-01-01")
- `limit`: 返回数量 (最大500)

**响应示例:**
```json
[
  {
    "id": "i129182755",
    "start_date_local": "2026-03-03T19:31:48",
    "source": "OAUTH_CLIENT",
    "type": "VirtualRide",
    "name": "MyWhoosh - SS Rebuild"
  },
  {
    "id": "16589160080",
    "start_date_local": "2025-11-28T15:20:49",
    "source": "STRAVA",
    "_note": "STRAVA activities are not available via the API"
  }
]
```

**注意:** Strava 同步的活动在此端点只返回 stub（精简版），需要特殊处理获取完整数据。

---

### 2. 获取单个活动详情（标准 API）
```
GET /api/v1/activity/{activity_id}?intervals=true
```

**适用场景:** 室内训练数据 (`source=OAUTH_CLIENT`)

**参数:**
- `intervals=true`: 同时返回间歇数据

**响应:** 完整的活动数据，包含 `icu_intervals` 数组

---

### 3. 获取单个活动详情（浏览器模拟）

**适用场景:** Strava 同步的数据 (`source=STRAVA`)

由于 API 限制，Strava 数据需要通过模拟浏览器登录获取：

#### 步骤 1: 登录获取 Session
```
POST /api/login
Content-Type: application/x-www-form-urlencoded

email={email}&password={password}&deviceClass=desktop
```

#### 步骤 2: 获取活动基础数据
```
GET /api/activity/{activity_id}
Headers:
  Authorization: Basic {base64(API_KEY:token)}
  Referer: https://intervals.icu/activities/{activity_id}/data
  User-Agent: Mozilla/5.0 ...
```

#### 步骤 3: 获取 Intervals 数据
```
GET /api/activity/{activity_id}/intervals
Headers: (同上)
```

**响应结构:**
```json
{
  "id": "...",
  "analyzed": "...",
  "icu_intervals": [...],
  "icu_groups": [...]
}
```

**数据合并:** 需要将步骤 2 的基础数据与步骤 3 的 `icu_intervals`/`icu_groups` 合并，才能匹配标准 API 格式。

---

## 数据来源对比

| 来源 | 获取方式 | 端点 | 是否需要登录 |
|------|---------|------|-------------|
| **OAUTH_CLIENT** | 标准 API | `/api/v1/activity/{id}?intervals=true` | ❌ 不需要 |
| **STRAVA** | 浏览器模拟 | `/api/activity/{id}` + `/api/activity/{id}/intervals` | ✅ 需要 email/password |

---

## 关键字段说明

### 活动基础字段
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 活动唯一ID |
| `source` | string | 数据来源: STRAVA, OAUTH_CLIENT |
| `type` | string | 活动类型: Ride, VirtualRide |
| `name` | string | 活动名称 |
| `start_date_local` | string | 本地开始时间 |
| `moving_time` | int | 移动时间(秒) |
| `distance` | float | 距离(米) |
| `total_elevation_gain` | float | 爬升(米) |
| `average_watts` | float | 平均功率 |
| `icu_weighted_avg_watts` | float | 加权平均功率(NP) |
| `icu_training_load` | float | 训练负荷(TSS) |
| `icu_intensity` | float | 强度系数(IF) |

### Intervals 字段
| 字段 | 说明 |
|------|------|
| `icu_intervals` | 自动识别的间歇区间数组 |
| `icu_groups` | 分组统计信息 |
| `zone` | 功率区间编号 |
| `average_watts` | 区间平均功率 |
| `training_load` | 区间训练负荷 |

---

## 速率限制

- 未认证: 60请求/小时
- API Key: 600请求/小时

---

## 错误处理

常见错误码:

| 状态码 | 含义 | 处理建议 |
|--------|------|---------|
| 401 | 认证失败 | 检查 API Key 是否正确 |
| 403 | 禁止访问 | Strava 数据需要浏览器模拟方式 |
| 404 | 活动不存在 | 检查 activity_id |
| 429 | 请求过多 | 等待后重试 |

---

## 数据提取逻辑 (extract_data.py)

### 设计原则

**Python 只做数据提取，不做分析判断。** 所有分析、建议、计划生成由 LLM 通过专用 prompt 完成。

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Discord/TG    │────▶│  Python Extractor │────▶│      LLM        │
│   /ride-xxx     │     │  (extract_data.py)│     │  (Prompt-based) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                           │
                              ▼                           ▼
                        ┌──────────────┐           ┌──────────────┐
                        │ activities.json│          │  Analysis &  │
                        │ sync_state.json│          │Recommendations│
                        └──────────────┘           └──────────────┘
```

### 自动同步机制

所有提取命令（除 `--no-sync`）执行前会自动检查数据新鲜度：

```python
SYNC_INTERVAL_HOURS = 4  # 超过4小时触发同步

def check_and_sync(force=False):
    # 1. 读取 sync_state.json 获取上次同步时间
    # 2. 计算距离上次同步的小时数
    # 3. 如果 >= 4小时，自动调用 sync_intervals.py 增量同步
    # 4. 返回同步结果
```

### 提取命令列表

| 参数 | 功能 | 输出数据结构 |
|------|------|-------------|
| `--status` | 当前训练状态 | `athlete_id`, `latest_activity`, `week_activities`, `fitness_history` |
| `--form` | 状态走势对比 | `all_intervals`, `hr_grouped` |
| `--trend` | 30天趋势 | `daily_data`, `weekly_summary` |
| `--latest` | 单次骑行详情 | `activity`, `metrics`, `power`, `heart_rate`, `efficiency`, `zones`, `intervals` |
| `--week` | 本周数据 | `week_start`, `today`, `activities`, `summary`, `current_status` |
| `--planned` | 已安排计划 | `count`, `date_range`, `workouts` |
| `--full` | 全部数据 | 组合以上所有 |

### 核心提取函数详解

#### extract_status_data()

提取当前状态数据，用于 `/ride-stats` 和 `/ride-plan`。

**逻辑流程：**
1. 加载 `activities.json`，按日期倒序排列
2. 获取最近一条活动作为 `latest_activity`
3. 筛选最近7天活动（`start_date >= today - 7d`）
4. 筛选最近30天 CTL/ATL 历史（用于趋势图）
5. 计算每条记录的星期几（中文）

**关键字段计算：**
```python
# TSB = CTL - ATL
tsb = round(ctl - atl, 1)

# 星期几转换
weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][dt.weekday()]
```

#### extract_form_data()

提取状态走势数据，用于对比巅峰 vs 当前表现。

**逻辑流程：**
1. 遍历所有活动的 `icu_intervals`
2. 筛选 `type == 'WORK'` 且 `moving_time >= 540s`（≥9分钟）的间歇
3. 提取：日期、时长、功率、心率、区间
4. 按心率分组（5bpm一个组），便于相同努力程度对比
5. 取每组最近5条记录

**用途：** 分析同样心率下，功率是否下降（疲劳）或上升（进步）。

#### extract_trend_data()

提取30天趋势数据。

**逻辑流程：**
1. 筛选最近30天有训练负荷的活动
2. 提取每日详细数据：时长、距离、爬升、负荷、强度、功率、心率等
3. 按 ISO 周汇总统计：
   - 每周活动数量
   - 总时长、总距离、总负荷
   - 平均强度

**周汇总计算：**
```python
week_key = dt.isocalendar()[:2]  # (year, week)
# 例如: (2026, 9) 表示 2026年第9周
```

#### extract_latest_ride_data()

提取最近一次骑行的完整详情。

**逻辑流程：**
1. 找到第一条 `icu_training_load > 0` 的活动
2. 提取功率区间时间（`icu_zone_times`）
3. 提取心率区间时间（`icu_hr_zone_times`）
4. 解析 `icu_intervals`，分离 WORK 和 RECOVERY
5. 结构化输出：活动信息、基础指标、功率数据、心率数据、效率指标、区间分布、间歇详情

**间歇分类：**
```python
if interval['type'] == 'WORK':
    work_intervals.append({...})
else:
    recovery_intervals.append({...})
```

#### extract_week_data()

提取本周数据（周一到当天）。

**逻辑流程：**
1. 计算本周一日期：`today - timedelta(days=today.weekday())`
2. 筛选 `start_date_local >= 本周一` 的活动
3. 计算汇总统计：总次数、总时长、总距离、总负荷、平均强度
4. 当前状态取最新一条活动的 CTL/ATL/TSB/FTP

#### extract_planned_data()

从 API 获取已安排的训练计划。

**API 端点：**
```
GET /api/v1/athlete/{athlete_id}/eventscsv?oldest={today}&newest={today+7d}&category=WORKOUT
```

**返回字段：**
- `name`, `description`: 计划名称和描述
- `duration_min`, `training_load`: 预计时长和负荷
- `ftp`, `intensity`: 目标 FTP 和强度
- `indoor`: 是否为室内训练
- `entered`: 是否已完成
- `paired_activity_id`: 关联的实际活动ID（如果已完成）
- `steps`: 课表步骤数
- `zones`: 功率区间时间分布

### 数据字段映射

#### 原始数据 → 提取后字段

| 原始字段 | 提取字段 | 说明 |
|---------|---------|------|
| `icu_ctl` | `ctl` | 慢性训练负荷 |
| `icu_atl` | `atl` | 急性训练负荷 |
| `icu_weighted_avg_watts` | `avg_watts` | 加权平均功率(NP) |
| `icu_training_load` | `training_load` | 训练负荷(TSS) |
| `icu_intensity` | `intensity` | 强度系数(IF) |
| `icu_ftp` | `ftp` | 功能性阈值功率 |
| `icu_intervals` | `intervals.work_details/recovery_details` | 间歇详情 |
| `icu_zone_times` | `zones.power_zone_times_min` | 功率区间时间 |
| `icu_hr_zone_times` | `zones.hr_zone_times_min` | 心率区间时间 |
| `decoupling` | `efficiency.decoupling_pct` | 功率心率脱钩率 |
| `icu_efficiency_factor` | `efficiency.efficiency_factor` | 效率因子 |
| `icu_variability_index` | `efficiency.variability_index` | 变异指数 |

### 本地数据文件

| 文件 | 用途 | 更新时机 |
|------|------|---------|
| `activities.json` | 所有活动原始数据 | 同步时写入 |
| `sync_state.json` | 同步状态（时间、最后ID、数量） | 同步后更新 |
| `config.json` | 用户配置（athlete_id, api_key, email, password） | 手动配置 |
