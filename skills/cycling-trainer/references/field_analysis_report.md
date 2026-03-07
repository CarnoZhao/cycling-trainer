# Activities.json 字段分析报告

> 分析时间: 自动生成  
> 样本数量: 200 条活动记录

---

## 🔴 可以忽略的字段（100% 为 null/0/空/False）

这些字段在所有活动中都没有有效值，可以安全地从分析中移除。

| 字段名 | 总记录数 | null | 0 | [] | {{}} | False | 示例值 |
|--------|----------|------|---|----|------|-------|--------|
| `attachments` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `average_clouds` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `average_feels_like` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `average_weather_temp` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `average_wind_gust` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `average_wind_speed` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `avg_lr_balance` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `carbs_ingested` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `coach_tick` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `commute` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `crank_length` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `custom_zones` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `feel` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `file_sport_index` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `has_weather` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `headwind_percent` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `icu_color` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `icu_ignore_hr` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `icu_ignore_power` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `icu_ignore_time` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `icu_power_spike_threshold` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `icu_rolling_cp` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `icu_rpe` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `icu_sync_error` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `icu_w_prime` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `ignore_pace` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `ignore_parts` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `ignore_velocity` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `kg_lifted` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `lengths` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `lock_intervals` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `max_feels_like` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `max_rain` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `max_snow` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `max_weather_temp` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `min_feels_like` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `min_weather_temp` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `p_max` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `perceived_exertion` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `pool_length` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `power_meter` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `power_meter_battery` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `power_meter_serial` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `prevailing_wind_deg` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `race` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `recording_stops` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `route_id` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `session_rpe` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `sub_type` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `tags` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `tailwind_percent` | 200 | 200 | 0 | 0 | 0 | 0 | - |
| `use_elevation_correction` | 200 | 0 | 200 | 0 | 0 | 0 | - |
| `workout_shift_secs` | 200 | 200 | 0 | 0 | 0 | 0 | - |

## 🟠 基本可忽略的字段（≥90% 为 null/0/空/False）

这些字段在绝大多数活动中没有有效值，仅在极少数记录中有值。

| 字段名 | 空值比例 | null | 0 | [] | {{}} | False | 有效值 | 示例值 |
|--------|----------|------|---|----|------|-------|--------|--------|
| `p30s_exponent` | 99.5% | 199 | 0 | 0 | 0 | 0 | 1 | [2.9643836] |
| `icu_chat_id` | 99.5% | 199 | 0 | 0 | 0 | 0 | 1 | [1145218] |
| `icu_rolling_ftp_delta` | 96.5% | 5 | 188 | 0 | 0 | 0 | 7 | [22] |
| `icu_achievements` | 93.5% | 168 | 0 | 19 | 0 | 0 | 13 | [[{'id': 'lthr', 'type': 'LTHR... |

## 🟡 部分为空的字段（50%-90% 为 null/0/空/False）

这些字段在部分活动中有值，使用时需要做空值检查。

| 字段名 | 空值比例 | null | 0 | [] | {{}} | False | 有效值 | 示例值 |
|--------|----------|------|---|----|------|-------|--------|--------|
| `icu_intervals_edited` | 89.5% | 48 | 131 | 0 | 0 | 0 | 21 | [True] |
| `gap_zone_times` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [[59, 348, 1054, 831, 154, 179... |
| `pace_zones` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [[77.5, 87.7, 94.3, 100.0, 103... |
| `pace_load_type` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | ['RUN'] |
| `use_gap_zone_times` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [True] |
| `threshold_pace` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [3.9525692] |
| `gap` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [3.7220936] |
| `pace_zone_times` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [[50, 224, 1236, 1042, 137, 47... |
| `pace_load` | 84.0% | 168 | 0 | 0 | 0 | 0 | 32 | [68] |
| `compliance` | 75.0% | 136 | 14 | 0 | 0 | 0 | 50 | [99.01961] |
| `paired_event_id` | 75.0% | 150 | 0 | 0 | 0 | 0 | 50 | [95849641] |
| `strava_id` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | ['17613204480'] |
| `oauth_client_id` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | [60] |
| `power_field_names` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | [['power']] |
| `icu_distance` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | [46448.32] |
| `power_field` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | ['power'] |
| `file_type` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | ['fit'] |
| `group` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | ['dfb874f3'] |
| `oauth_client_name` | 73.5% | 147 | 0 | 0 | 0 | 0 | 53 | ['MyWhoosh'] |
| `icu_hrr` | 70.0% | 140 | 0 | 0 | 0 | 0 | 60 | [{'start_index': 1091, 'end_in... |
| `max_temp` | 63.0% | 126 | 0 | 0 | 0 | 0 | 74 | [19] |
| `min_temp` | 63.0% | 126 | 0 | 0 | 0 | 0 | 74 | [6] |
| `average_temp` | 63.0% | 126 | 0 | 0 | 0 | 0 | 74 | [11.633673] |
| `trainer` | 56.5% | 0 | 113 | 0 | 0 | 0 | 87 | [True] |
| `icu_max_wbal_depletion` | 50.0% | 74 | 26 | 0 | 0 | 0 | 100 | [597] |
| `ss_p_max` | 50.0% | 74 | 26 | 0 | 0 | 0 | 100 | [0.0015913525] |
| `ss_w_prime` | 50.0% | 74 | 26 | 0 | 0 | 0 | 100 | [0.18292102] |

## 🟢 核心字段（<50% 为空，数据质量高）

这些字段在大多数活动中都有有效值，是分析的主要数据来源。

| 字段名 | 空值比例 | null | 0 | [] | {{}} | False | 有效值 | 示例值 |
|--------|----------|------|---|----|------|-------|--------|--------|
| `start_date_local` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['2026-03-05T20:29:05'] |
| `analyzed` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['2026-03-05T13:49:20.840+00:0... |
| `athlete_max_hr` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [187] |
| `id` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['i129725312'] |
| `source` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['OAUTH_CLIENT'] |
| `icu_resting_hr` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [57] |
| `type` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['VirtualRide'] |
| `icu_recording_time` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [4811] |
| `icu_sync_date` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['2026-03-05T13:49:20.840+00:0... |
| `icu_median_time_delta` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [1] |
| `calories` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [1016] |
| `gap_model` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['NONE'] |
| `name` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['MyWhoosh - sub-threshold Reb... |
| `elapsed_time` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [4812] |
| `stream_types` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [['time', 'watts', 'cadence', ... |
| `has_segments` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [True] |
| `created` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['2026-03-05T13:49:20.341+00:0... |
| `moving_time` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [4812] |
| `icu_hr_zones` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [[135, 150, 156, 167, 172, 177... |
| `icu_lap_count` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [8] |
| `tiz_order` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['POWER_HR_PACE'] |
| `icu_weight` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [65.0] |
| `lthr` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [168] |
| `icu_ctl` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [41.39275] |
| `start_date` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['2026-03-05T12:29:05Z'] |
| `external_id` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['MyNewActivity-5.6.1.fit'] |
| `icu_atl` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | [47.494007] |
| `icu_athlete_id` | 0.0% | 0 | 0 | 0 | 0 | 0 | 200 | ['i216809'] |
| `hr_load` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | [90] |
| `hr_load_type` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | ['HRSS'] |
| `skyline_chart_bytes` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | ['CAcSDt0EgAexAv4GsQKAB5AHGgc6... |
| `has_heartrate` | 0.5% | 0 | 1 | 0 | 0 | 0 | 199 | [True] |
| `icu_hr_zone_times` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | [[1090, 1043, 261, 2381, 38, 0... |
| `icu_intensity` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | [86.92308] |
| `icu_training_load_data` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | [100] |
| `max_heartrate` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | [169] |
| `average_heartrate` | 0.5% | 1 | 0 | 0 | 0 | 0 | 199 | [149] |
| `icu_training_load` | 1.0% | 1 | 1 | 0 | 0 | 0 | 198 | [101] |
| `device_name` | 1.5% | 3 | 0 | 0 | 0 | 0 | 197 | ['MYWHOOSH 3570'] |
| `icu_rolling_ftp` | 2.5% | 5 | 0 | 0 | 0 | 0 | 195 | [268] |
| `icu_sweet_spot_min` | 2.5% | 0 | 5 | 0 | 0 | 0 | 195 | [84] |
| `icu_rolling_w_prime` | 2.5% | 5 | 0 | 0 | 0 | 0 | 195 | [23004.596] |
| `icu_power_zones` | 2.5% | 5 | 0 | 0 | 0 | 0 | 195 | [[55, 75, 90, 105, 120, 150, 9... |
| `icu_sweet_spot_max` | 2.5% | 0 | 5 | 0 | 0 | 0 | 195 | [97] |
| `icu_rolling_p_max` | 2.5% | 5 | 0 | 0 | 0 | 0 | 195 | [713.31793] |
| `icu_ftp` | 2.5% | 5 | 0 | 0 | 0 | 0 | 195 | [260] |
| `gear` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [{'id': 'b14461654', 'name': N... |
| `icu_average_watts` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [211] |
| `average_cadence` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [87.90879] |
| `icu_efficiency_factor` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [1.5167785] |
| `device_watts` | 3.5% | 5 | 2 | 0 | 0 | 0 | 193 | [True] |
| `icu_power_hr` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [1.4161074] |
| `icu_zone_times` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [[{'id': 'Z1', 'secs': 452}, {... |
| `icu_variability_index` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [1.0710901] |
| `icu_pm_p_max` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [277] |
| `icu_weighted_avg_watts` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [226] |
| `icu_joules` | 3.5% | 7 | 0 | 0 | 0 | 0 | 193 | [1015243] |
| `decoupling` | 4.0% | 8 | 0 | 0 | 0 | 0 | 192 | [6.980198] |
| `power_load` | 4.0% | 7 | 1 | 0 | 0 | 0 | 192 | [101] |
| `icu_pm_cp` | 5.0% | 10 | 0 | 0 | 0 | 0 | 190 | [232] |
| `icu_pm_ftp_secs` | 5.0% | 10 | 0 | 0 | 0 | 0 | 190 | [2100] |
| `icu_pm_ftp` | 5.0% | 10 | 0 | 0 | 0 | 0 | 190 | [237] |
| `icu_pm_ftp_watts` | 5.0% | 10 | 0 | 0 | 0 | 0 | 190 | [241] |
| `icu_pm_w_prime` | 5.0% | 10 | 0 | 0 | 0 | 0 | 190 | [19913] |
| `average_speed` | 16.5% | 0 | 33 | 0 | 0 | 0 | 167 | [6.843] |
| `pace` | 16.5% | 33 | 0 | 0 | 0 | 0 | 167 | [9.652602] |
| `max_speed` | 16.5% | 0 | 33 | 0 | 0 | 0 | 167 | [14.096] |
| `distance` | 16.5% | 33 | 0 | 0 | 0 | 0 | 167 | [46448.32] |
| `average_altitude` | 17.0% | 0 | 34 | 0 | 0 | 0 | 166 | [-0.80465406] |
| `max_altitude` | 17.5% | 0 | 35 | 0 | 0 | 0 | 165 | [6.8] |
| `icu_joules_above_ftp` | 18.5% | 7 | 30 | 0 | 0 | 0 | 163 | [1715] |
| `min_altitude` | 19.5% | 0 | 39 | 0 | 0 | 0 | 161 | [-7.0] |
| `average_stride` | 20.0% | 40 | 0 | 0 | 0 | 0 | 160 | [3.2940738] |
| `carbs_used` | 20.0% | 40 | 0 | 0 | 0 | 0 | 160 | [221] |
| `total_elevation_loss` | 20.5% | 0 | 41 | 0 | 0 | 0 | 159 | [66.4] |
| `total_elevation_gain` | 21.0% | 0 | 42 | 0 | 0 | 0 | 158 | [61.600002] |
| `description` | 21.0% | 42 | 0 | 0 | 0 | 0 | 158 | ['◾️ 24, February Training sta... |
| `interval_summary` | 24.0% | 48 | 0 | 0 | 0 | 0 | 152 | [['3x 14m55s 254w']] |
| `icu_warmup_time` | 24.5% | 0 | 49 | 0 | 0 | 0 | 151 | [1200] |
| `icu_cooldown_time` | 24.5% | 0 | 49 | 0 | 0 | 0 | 151 | [600] |
| `icu_intervals` | 24.5% | 49 | 0 | 0 | 0 | 0 | 151 | [[{'start_index': 0, 'distance... |
| `icu_cadence_z2` | 25.0% | 50 | 0 | 0 | 0 | 0 | 150 | [85] |
| `icu_power_hr_z2` | 25.0% | 50 | 0 | 0 | 0 | 0 | 150 | [1.1547813] |
| `icu_power_hr_z2_mins` | 25.0% | 50 | 0 | 0 | 0 | 0 | 150 | [11] |
| `timezone` | 26.5% | 53 | 0 | 0 | 0 | 0 | 147 | ['(GMT+08:00) Asia/Shanghai'] |
| `coasting_time` | 32.0% | 7 | 57 | 0 | 0 | 0 | 136 | [6] |
| `icu_groups` | 37.0% | 74 | 0 | 0 | 0 | 0 | 126 | [[{'start_index': 605, 'distan... |
| `strain_score` | 37.0% | 74 | 0 | 0 | 0 | 0 | 126 | [104.57424] |
| `ss_cp` | 37.0% | 74 | 0 | 0 | 0 | 0 | 126 | [104.389725] |
| `trimp` | 41.0% | 82 | 0 | 0 | 0 | 0 | 118 | [141.35292] |
| `polarization_index` | 44.5% | 38 | 51 | 0 | 0 | 0 | 111 | [1.74] |

---

## 📋 建议忽略的字段列表（用于代码优化）

```python
# 可以安全忽略的字段（100% 为空）
IGNORED_FIELDS_100 = [
    'attachments',
    'average_clouds',
    'average_feels_like',
    'average_weather_temp',
    'average_wind_gust',
    'average_wind_speed',
    'avg_lr_balance',
    'carbs_ingested',
    'coach_tick',
    'commute',
    'crank_length',
    'custom_zones',
    'feel',
    'file_sport_index',
    'has_weather',
    'headwind_percent',
    'icu_color',
    'icu_ignore_hr',
    'icu_ignore_power',
    'icu_ignore_time',
    'icu_power_spike_threshold',
    'icu_rolling_cp',
    'icu_rpe',
    'icu_sync_error',
    'icu_w_prime',
    'ignore_pace',
    'ignore_parts',
    'ignore_velocity',
    'kg_lifted',
    'lengths',
    'lock_intervals',
    'max_feels_like',
    'max_rain',
    'max_snow',
    'max_weather_temp',
    'min_feels_like',
    'min_weather_temp',
    'p_max',
    'perceived_exertion',
    'pool_length',
    'power_meter',
    'power_meter_battery',
    'power_meter_serial',
    'prevailing_wind_deg',
    'race',
    'recording_stops',
    'route_id',
    'session_rpe',
    'sub_type',
    'tags',
    'tailwind_percent',
    'use_elevation_correction',
    'workout_shift_secs',
]

# 基本可忽略的字段（≥90% 为空）
IGNORED_FIELDS_90 = [
    'p30s_exponent',  # 99.5% 为空
    'icu_chat_id',  # 99.5% 为空
    'icu_rolling_ftp_delta',  # 96.5% 为空
    'icu_achievements',  # 93.5% 为空
]
```
