# Cycling Trainer 单元测试

本目录包含 Cycling Trainer 技能的单元测试，使用 Python 标准库 `unittest` 编写。

## 测试结构

```
tests/
├── __init__.py                    # 测试包初始化
├── fixtures/                      # 测试数据
│   ├── sample_activities.json     # 示例活动数据
│   └── sample_cycle_memory.json   # 示例周期记忆
├── test_utils.py                  # utils 模块测试
├── test_cycle_memory.py           # cycle_memory 模块测试
├── test_config.py                 # config 模块测试
├── test_extract.py                # extract 模块测试
└── test_extractors.py             # extractors 模块测试
```

## 运行测试

### 运行所有测试

```bash
cd /root/.openclaw/workspace-cycling/skills/cycling-trainer
python3 -m unittest discover tests/
```

### 运行特定测试文件

```bash
python3 -m unittest tests.test_utils
python3 -m unittest tests.test_cycle_memory
python3 -m unittest tests.test_config
python3 -m unittest tests.test_extract
python3 -m unittest tests.test_extractors
```

### 运行特定测试类

```bash
python3 -m unittest tests.test_utils.TestStorage
python3 -m unittest tests.test_cycle_memory.TestCycleMemoryManager
```

### 运行特定测试方法

```bash
python3 -m unittest tests.test_utils.TestStorage.test_save_and_load_activities
```

### 详细输出模式

```bash
python3 -m unittest discover tests/ -v
```

## 测试覆盖范围

### 1. utils/ 模块 (test_utils.py)

**storage.py 测试:**
- `test_ensure_data_dir` - 测试数据目录创建
- `test_load_activities_empty` - 测试空数据加载
- `test_load_data_alias` - 测试 load_data 别名
- `test_save_and_load_activities` - 测试数据保存和加载
- `test_load_activities_invalid_json` - 测试损坏的 JSON 处理
- `test_merge_activities` - 测试活动数据合并
- `test_merge_activities_empty` - 测试空列表合并

**dates.py 测试:**
- `test_get_weekday_cn` - 测试中文星期转换
- `test_format_date_range` - 测试日期范围格式化
- `test_format_date_range_default` - 测试默认日期范围
- `test_get_week_start` - 测试周开始日期计算
- `test_get_week_start_default` - 测试默认周开始
- `test_parse_activity_date` - 测试日期解析
- `test_parse_activity_date_invalid` - 测试无效日期解析
- `test_is_date_in_range` - 测试日期范围检查
- `test_is_date_in_range_default` - 测试默认日期范围检查

### 2. cycle_memory 模块 (test_cycle_memory.py)

**TestCycleMemoryManager 类:**
- `test_load_memory_empty` - 测试空记忆加载
- `test_save_and_load_memory` - 测试保存和加载
- `test_save_updates_timestamp` - 测试时间戳更新
- `test_get_current_cycle` - 测试获取当前周期
- `test_get_current_cycle_empty` - 测试空数据获取周期
- `test_update_week_activity_existing` - 测试更新已有活动
- `test_update_week_activity_new` - 测试添加新活动
- `test_update_week_activity_no_memory` - 测试无数据更新
- `test_update_week_activity_recalculates_stats` - 测试统计重算
- `test_advance_week` - 测试进入下一周
- `test_advance_week_new_cycle` - 测试进入新周期
- `test_advance_week_no_memory` - 测试无数据进入下周
- `test_start_new_cycle` - 测试开始新周期
- `test_start_new_cycle_empty` - 测试空数据开始周期
- `test_export_to_markdown` - 测试 Markdown 导出
- `test_export_to_markdown_empty` - 测试空数据导出
- `test_create_default_memory` - 测试默认记忆创建

**TestCycleMemoryDataClasses 类:**
- `test_activity_to_dict` - 测试 Activity 转字典
- `test_activity_from_dict` - 测试 Activity 从字典创建
- `test_week_data_to_dict` - 测试 WeekData 转字典
- `test_cycle_memory_to_dict` - 测试 CycleMemory 转字典
- `test_cycle_memory_from_dict` - 测试 CycleMemory 从字典创建
- `test_invalid_data_rejected` - 测试无效数据拒绝

**TestCycleMemoryFunctions 类:**
- `test_load_memory_function` - 测试便捷函数 load_memory
- `test_export_to_markdown_function` - 测试便捷函数 export_to_markdown

### 3. config 模块 (test_config.py)

- `test_load_config_empty` - 测试空配置加载
- `test_load_config_valid` - 测试有效配置加载
- `test_load_config_invalid_json` - 测试损坏配置处理
- `test_get_credentials_from_config` - 测试从配置读取凭据
- `test_get_credentials_from_env` - 测试从环境变量读取凭据
- `test_get_credentials_priority_env_over_config` - 测试优先级（环境 > 配置）
- `test_get_credentials_priority_args_over_env` - 测试优先级（参数 > 环境）
- `test_get_credentials_with_dict_args` - 测试字典参数
- `test_get_credentials_missing` - 测试凭据缺失
- `test_get_credentials_partial_missing` - 测试部分凭据缺失
- `test_get_credentials_with_email_password` - 测试 email/password 凭据
- `test_get_credentials_email_password_from_config` - 测试从配置读取 email/password
- `test_get_credentials_only_athlete_id_from_env` - 测试仅 athlete_id
- `test_get_credentials_only_api_key_from_env` - 测试仅 api_key

### 4. extract 模块 (test_extract.py)

**TestExtractStatusData 类:**
- `test_extract_status_data_structure` - 测试返回结构
- `test_extract_status_data_empty_data` - 测试空数据处理
- `test_extract_status_data_week_activities_structure` - 测试周活动结构
- `test_extract_status_data_fitness_history_structure` - 测试健身历史结构

**TestExtractWeekData 类:**
- `test_extract_week_data_structure` - 测试返回结构
- `test_extract_week_data_empty_data` - 测试空数据处理
- `test_extract_week_data_activities_structure` - 测试活动结构
- `test_extract_week_data_summary_calculation` - 测试统计计算

**TestExtractPlannedData 类:**
- `test_extract_planned_data_structure` - 测试返回结构
- `test_extract_planned_data_credentials_missing` - 测试凭据缺失处理
- `test_extract_planned_data_empty_workouts` - 测试空训练计划

### 5. extractors 模块 (test_extractors.py)

**TestExtractorsStatusData 类:**
- `test_extract_status_data_empty_list` - 测试空列表
- `test_extract_status_data_single_activity` - 测试单条活动
- `test_extract_status_data_no_training_load` - 测试无训练负荷过滤
- `test_extract_status_data_tsb_calculation` - 测试 TSB 计算

**TestExtractorsWeekData 类:**
- `test_extract_week_data_empty_list` - 测试空列表
- `test_extract_week_data_no_week_activities` - 测试本周无活动
- `test_extract_week_data_multiple_days` - 测试多天活动
- `test_extract_week_data_current_status_empty` - 测试空状态

**TestExtractorsLatestRideData 类:**
- `test_extract_latest_ride_data_empty` - 测试空数据
- `test_extract_latest_ride_data_no_valid_ride` - 测试无有效骑行
- `test_extract_latest_ride_data_structure` - 测试返回结构
- `test_extract_latest_ride_data_max_watts_from_intervals` - 测试最大功率提取
- `test_extract_latest_ride_data_zone_times_conversion` - 测试区间时间转换
- `test_extract_latest_ride_data_intervals_classification` - 测试间歇分类

**TestExtractorsBoundaryCases 类:**
- `test_extract_form_data_empty` - 测试空 form 数据
- `test_extract_form_data_no_intervals` - 测试无间歇数据
- `test_extract_trend_data_empty` - 测试空 trend 数据
- `test_extract_trend_data_no_valid_activities` - 测试无有效活动
- `test_extract_status_data_missing_fields` - 测试缺失字段处理

## 测试原则

1. **独立性** - 每个测试独立运行，不依赖其他测试
2. **隔离性** - 使用临时目录，不污染真实数据
3. **Mock 数据** - 使用 fixtures 中的模拟数据，不调用真实 API
4. **清理** - 每个测试后清理临时文件
5. **文档** - 每个测试有清晰的 docstring 说明测试目的

## 添加新测试

1. 在对应的测试文件中添加测试类或方法
2. 使用 `setUp()` 和 `tearDown()` 管理测试环境
3. 使用临时目录存放测试数据
4. 为每个测试添加清晰的 docstring
5. 运行测试确保通过

## 注意事项

- 所有测试使用 mock 数据，不调用真实 API
- 测试结束后自动清理临时文件
- 环境变量测试会临时修改环境，测试后恢复
- 配置文件测试使用临时目录隔离
