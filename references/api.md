# Intervals.icu API 文档

## 认证

### API Key 获取
1. 登录 intervals.icu
2. 进入设置 → API
3. 创建新的 API Key

### 认证方式
```python
headers = {"Authorization": f"Bearer {api_key}"}
```

## 核心 API 端点

### 1. 获取骑手信息
```
GET /api/v1/athlete/{athlete_id}
```

响应:
```json
{
  "id": "abc123",
  "name": "Carno",
  "ftp": {"value": 250, "updated": "2024-01-15"},
  "weight": 70,
  "zones": {...}
}
```

### 2. 获取活动列表
```
GET /api/v1/athlete/{athlete_id}/activities
```

参数:
- `oldest`: 开始日期 ISO 格式
- `newest`: 结束日期 ISO 格式
- `limit`: 返回数量 (最大500)

### 3. 获取单个活动详情
```
GET /api/v1/activity/{activity_id}
```

### 4. 获取分析数据
```
GET /api/v1/athlete/{athlete_id}/analysis
```

返回功率曲线、冲刺分析等。

## 关键字段

| 字段 | 说明 |
|------|------|
| `suffer_score` | 训练痛苦指数 |
| `moving_time` | 移动时间（秒）|
| `distance` | 距离（米）|
| `elevation_gain` | 爬升（米）|
| `avg_watts` | 平均功率 |
| `normalized_power` | 标准化功率 |
| `intensity_factor` | 强度系数 |

## 速率限制

- 未认证: 60请求/小时
- API Key: 600请求/小时