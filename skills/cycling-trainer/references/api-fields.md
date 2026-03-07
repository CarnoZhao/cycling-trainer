# Intervals.icu API 字段参考

> 基于真实 API 返回数据的字段映射文档
> 生成时间: 2026-03-07

## 说明

本文档记录 intervals.icu API 实际返回的字段路径，用于纠正 `extractors.py` 中的字段引用错误。

---

## 活动基础字段 (Activity Base Fields)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| id | `id` | string | 活动唯一ID |
| start_date_local | `start_date_local` | string | 本地开始时间 (ISO 8601) |
| start_date | `start_date` | string | UTC 开始时间 |
| type | `type` | string | 活动类型: Ride, VirtualRide 等 |
| name | `name` | string | 活动名称 |
| description | `description` | string | 活动描述 |
| source | `source` | enum | 数据来源: STRAVA, OAUTH_CLIENT, MANUAL 等 |
| sub_type | `sub_type` | enum | 子类型: NONE, COMMUTE, WARMUP, COOLDOWN, RACE |
| commute | `commute` | boolean | 是否为通勤 |
| race | `race` | boolean | 是否为比赛 |
| trainer | `trainer` | boolean | 是否为骑行台训练 |
| timezone | `timezone` | string | 时区 |

---

## 功率训练核心字段 (Power Training Core)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_ftp | `icu_ftp` | integer | 功能性阈值功率 (FTP) |
| icu_weighted_avg_watts | `icu_weighted_avg_watts` | integer | 加权平均功率 (NP) |
| icu_training_load | `icu_training_load` | integer | 训练负荷 (TSS) |
| icu_intensity | `icu_intensity` | number | 强度系数 (IF) |
| icu_ctl | `icu_ctl` | number | 慢性训练负荷 (CTL) |
| icu_atl | `icu_atl` | number | 急性训练负荷 (ATL) |
| icu_joules | `icu_joules` | integer | 总做功 (焦耳) |
| icu_joules_above_ftp | `icu_joules_above_ftp` | integer | FTP 以上做功 |
| icu_efficiency_factor | `icu_efficiency_factor` | number | 效率因子 (NP/avg HR) |
| icu_variability_index | `icu_variability_index` | number | 变异指数 (NP/avg Power) |
| icu_power_hr | `icu_power_hr` | number | 功率/心率比 |
| decoupling | `decoupling` | number | 功率-心率脱钩率 |

---

## 功率模型字段 (Power Model)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_pm_cp | `icu_pm_cp` | integer | 临界功率 (CP) |
| icu_pm_w_prime | `icu_pm_w_prime` | integer | W' (无氧工作能力) |
| icu_pm_p_max | `icu_pm_p_max` | integer | 最大功率 |
| icu_pm_ftp | `icu_pm_ftp` | integer | 模型计算的 FTP |
| icu_pm_ftp_secs | `icu_pm_ftp_secs` | integer | FTP 持续时间 |
| icu_pm_ftp_watts | `icu_pm_ftp_watts` | integer | FTP 功率值 |
| icu_w_prime | `icu_w_prime` | integer | W' 值 (简化) |
| p_max | `p_max` | integer | 最大功率 (简化) |

---

## 滚动统计字段 (Rolling Stats)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_rolling_cp | `icu_rolling_cp` | number | 滚动临界功率 |
| icu_rolling_w_prime | `icu_rolling_w_prime` | number | 滚动 W' |
| icu_rolling_p_max | `icu_rolling_p_max` | number | 滚动最大功率 |
| icu_rolling_ftp | `icu_rolling_ftp` | integer | 滚动 FTP |
| icu_rolling_ftp_delta | `icu_rolling_ftp_delta` | integer | FTP 变化量 |

---

## Sweet Spot 字段

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_sweet_spot_min | `icu_sweet_spot_min` | integer | Sweet Spot 下限 |
| icu_sweet_spot_max | `icu_sweet_spot_max` | integer | Sweet Spot 上限 |
| ss_p_max | `ss_p_max` | number | SS 区间最大功率 |
| ss_w_prime | `ss_w_prime` | number | SS 区间 W' |
| ss_cp | `ss_cp` | number | SS 区间临界功率 |

---

## 心率相关字段 (Heart Rate)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| has_heartrate | `has_heartrate` | boolean | 是否有心率数据 |
| average_heartrate | `average_heartrate` | integer | 平均心率 |
| max_heartrate | `max_heartrate` | integer | 最大心率 |
| lthr | `lthr` | integer | 乳酸阈值心率 |
| icu_resting_hr | `icu_resting_hr` | integer | 静息心率 |
| icu_hr_zones | `icu_hr_zones` | [integer] | 心率区间边界 |
| icu_hr_zone_times | `icu_hr_zone_times` | [integer] | 各心率区间时间(秒) |
| icu_ignore_hr | `icu_ignore_hr` | boolean | 是否忽略心率 |
| trimp | `trimp` | number | TRIMP 训练负荷 |

---

## 功率区间时间 (Zone Times)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_power_zones | `icu_power_zones` | [integer] | 功率区间边界 |
| icu_zone_times | `icu_zone_times` | [{id, secs}] | 各区时间分布 |
| icu_power_spike_threshold | `icu_power_spike_threshold` | integer | 功率尖峰阈值 |

**icu_zone_times 结构:**
```json
[
  {"id": "Z1", "secs": 120},
  {"id": "Z2", "secs": 1800},
  ...
]
```

---

## 间歇数据 (Intervals)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_intervals | `icu_intervals` | [object] | 自动识别的间歇区间 |
| icu_groups | `icu_groups` | [object] | 分组统计信息 |
| icu_lap_count | `icu_lap_count` | integer | 圈数 |
| icu_intervals_edited | `icu_intervals_edited` | boolean | 间歇是否被编辑 |
| lock_intervals | `lock_intervals` | boolean | 是否锁定间歇 |

**icu_intervals 数组元素结构:**
```json
{
  "id": integer,
  "type": "RECOVERY" | "WORK",
  "start_index": integer,
  "end_index": integer,
  "start_time": integer,
  "end_time": integer,
  "distance": number,
  "moving_time": integer,
  "elapsed_time": integer,
  "average_watts": integer,
  "max_watts": integer,
  "min_watts": integer,
  "average_watts_kg": number,
  "max_watts_kg": number,
  "weighted_average_watts": integer,
  "intensity": integer,
  "training_load": number,
  "joules": integer,
  "joules_above_ftp": integer,
  "w5s_variability": number,
  "zone": integer,
  "zone_min_watts": integer,
  "zone_max_watts": integer,
  "average_heartrate": integer,
  "min_heartrate": integer,
  "max_heartrate": integer,
  "average_cadence": number,
  "min_cadence": integer,
  "max_cadence": integer,
  "average_speed": number,
  "min_speed": number,
  "max_speed": number,
  "gap": number,
  "total_elevation_gain": number,
  "min_altitude": number,
  "max_altitude": number,
  "average_gradient": number,
  "average_temp": number,
  "decoupling": number,
  "avg_lr_balance": number,
  "wbal_start": integer,
  "wbal_end": integer,
  "ss_p_max": number,
  "ss_w_prime": number,
  "ss_cp": number,
  "strain_score": number,
  "label": string,
  "group_id": string
}
```

---

## 时间和距离字段 (Time & Distance)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| moving_time | `moving_time` | integer | 移动时间(秒) |
| elapsed_time | `elapsed_time` | integer | 总时间(秒) |
| icu_recording_time | `icu_recording_time` | integer | 记录时间 |
| coasting_time | `coasting_time` | integer | 滑行时间 |
| distance | `distance` | number | 距离(米) |
| icu_distance | `icu_distance` | number | ICU 计算距离 |
| total_elevation_gain | `total_elevation_gain` | number | 爬升(米) |
| total_elevation_loss | `total_elevation_loss` | number | 下降(米) |

---

## 速度字段 (Speed)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| average_speed | `average_speed` | number | 平均速度(m/s) |
| max_speed | `max_speed` | number | 最大速度(m/s) |

---

## 踏频字段 (Cadence)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| average_cadence | `average_cadence` | number | 平均踏频 |

---

## 设备信息 (Device)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| device_name | `device_name` | string | 设备名称 |
| device_watts | `device_watts` | boolean | 是否有功率计 |
| power_meter | `power_meter` | string | 功率计型号 |
| power_meter_serial | `power_meter_serial` | string | 功率计序列号 |
| power_meter_battery | `power_meter_battery` | string | 功率计电量 |
| crank_length | `crank_length` | number | 曲柄长度 |

---

## 体重和设置 (Athlete Settings)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_weight | `icu_weight` | number | 体重(kg) |
| icu_athlete_id | `icu_athlete_id` | string | 运动员ID |

---

## 能量和代谢 (Energy & Metabolism)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| calories | `calories` | integer | 卡路里 |
| carbs_used | `carbs_used` | integer | 碳水化合物消耗 |
| carbs_ingested | `carbs_ingested` | integer | 碳水化合物摄入 |

---

## 温度和环境 (Environment)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| average_temp | `average_temp` | number | 平均温度 |
| min_temp | `min_temp` | integer | 最低温度 |
| max_temp | `max_temp` | integer | 最高温度 |
| has_weather | `has_weather` | boolean | 是否有天气数据 |
| average_weather_temp | `average_weather_temp` | number | 天气平均温度 |
| min_weather_temp | `min_weather_temp` | number | 天气最低温度 |
| max_weather_temp | `max_weather_temp` | number | 天气最高温度 |
| average_feels_like | `average_feels_like` | number | 体感温度 |
| average_wind_speed | `average_wind_speed` | number | 平均风速 |
| average_wind_gust | `average_wind_gust` | number | 阵风 |
| prevailing_wind_deg | `prevailing_wind_deg` | integer | 主导风向 |
| headwind_percent | `headwind_percent` | number | 逆风百分比 |
| tailwind_percent | `tailwind_percent` | number | 顺风百分比 |
| average_clouds | `average_clouds` | integer | 云量 |
| max_rain | `max_rain` | number | 最大降雨量 |
| max_snow | `max_snow` | number | 最大降雪量 |

---

## 海拔字段 (Altitude)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| average_altitude | `average_altitude` | number | 平均海拔 |
| min_altitude | `min_altitude` | number | 最低海拔 |
| max_altitude | `max_altitude` | number | 最高海拔 |

---

## 恢复和疲劳 (Recovery & Fatigue)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_warmup_time | `icu_warmup_time` | integer | 热身时间 |
| icu_cooldown_time | `icu_cooldown_time` | integer | 放松时间 |
| icu_hrr | `icu_hrr` | object | 心率恢复数据 |
| icu_max_wbal_depletion | `icu_max_wbal_depletion` | integer | 最大 W' 消耗 |
| feel | `feel` | integer | 主观感受评分 |
| icu_rpe | `icu_rpe` | integer | RPE 评分 |
| session_rpe | `session_rpe` | integer | 训练 RPE |

---

## 成就和标记 (Achievements)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_achievements | `icu_achievements` | [object] | 成就列表 |

---

## 同步相关 (Sync)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| icu_sync_date | `icu_sync_date` | date-time | 同步时间 |
| icu_sync_error | `icu_sync_error` | string | 同步错误信息 |
| external_id | `external_id` | string | 外部ID (Strava ID 等) |
| strava_id | `strava_id` | string | Strava ID |

---

## 时间戳字段 (Timestamps)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| created | `created` | date-time | 创建时间 |
| analyzed | `analyzed` | date-time | 分析时间 |

---

## 标记和标签 (Tags)

| 字段名 | JSON 路径 | 类型 | 说明 |
|--------|-----------|------|------|
| tags | `tags` | [string] | 标签列表 |
| icu_color | `icu_color` | string | 活动颜色标记 |

---

## 错误字段识别 (Non-existent Fields)

以下字段在 `extractors.py` 中被引用，但在真实 API 中**不存在**:

| 错误字段名 | 所在代码位置 | 应替换为 |
|-----------|-------------|---------|
| `icu_normalized_watts` | extract_latest_ride_data | `icu_weighted_avg_watts` |
| `max_watts` (activity level) | extract_latest_ride_data | 需从 intervals 中计算或使用 `p_max` |
| `start_date` (用于筛选) | extract_status_data | `start_date_local` |

---

## 常用字段提取示例

### TSB 计算
```python
tsb = round(icu_ctl - icu_atl, 1)
```

### 功率区间时间转换 (秒 → 分钟)
```python
zone_times_min = {}
for z in activity.get('icu_zone_times', []):
    zone_id = z.get('id', '')
    secs = z.get('secs', 0)
    zone_times_min[zone_id] = round(secs / 60, 1)
```

### 心率区间时间转换
```python
hr_zones = activity.get('icu_hr_zone_times', [])
hr_zone_times = {
    f"Z{i+1}": round(hr_zones[i]/60, 1) 
    if i < len(hr_zones) else 0 
    for i in range(7)
}
```

### 间歇分类 (WORK vs RECOVERY)
```python
work_intervals = []
recovery_intervals = []

for i in activity.get('icu_intervals', []):
    interval_data = {
        "type": i.get('type'),
        "duration_min": round(i.get('moving_time', 0) / 60, 1),
        "avg_watts": i.get('average_watts', 0),
        "max_watts": i.get('max_watts', 0),
        "avg_hr": i.get('average_heartrate', 0),
        "zone": i.get('zone', 0),
        "training_load": i.get('training_load', 0),
    }
    if i.get('type') == 'WORK':
        work_intervals.append(interval_data)
    else:
        recovery_intervals.append(interval_data)
```

---

## 版本记录

- v1.0 (2026-03-07): 初始版本，基于真实 API schema 创建
