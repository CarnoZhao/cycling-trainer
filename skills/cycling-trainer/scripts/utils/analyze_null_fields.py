#!/usr/bin/env python3
"""
分析 activities.json 中哪些字段的值一直都是 0 或 null
这些字段可以被忽略，不需要在后续分析中使用
"""

import json
from collections import defaultdict

def analyze_null_fields(json_file_path):
    """分析 JSON 文件中所有字段，统计哪些字段一直为 0 或 null"""
    
    # 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        activities = json.load(f)
    
    print(f"总共分析了 {len(activities)} 条活动记录")
    
    # 收集所有可能的字段
    all_fields = set()
    for activity in activities:
        all_fields.update(activity.keys())
    
    # 统计每个字段的情况
    field_stats = defaultdict(lambda: {
        'total': 0,
        'null_count': 0,
        'zero_count': 0,
        'empty_list_count': 0,
        'empty_dict_count': 0,
        'false_count': 0,
        'has_value_count': 0,
        'sample_values': []
    })
    
    for activity in activities:
        for field in all_fields:
            field_stats[field]['total'] += 1
            value = activity.get(field)
            
            if value is None:
                field_stats[field]['null_count'] += 1
            elif value == 0 or value == 0.0:
                field_stats[field]['zero_count'] += 1
            elif value == []:
                field_stats[field]['empty_list_count'] += 1
            elif value == {}:
                field_stats[field]['empty_dict_count'] += 1
            elif value is False:
                field_stats[field]['false_count'] += 1
            else:
                field_stats[field]['has_value_count'] += 1
                # 保存一些示例值（最多3个）
                if len(field_stats[field]['sample_values']) < 3:
                    # 截断长字符串
                    sample = value
                    if isinstance(sample, str) and len(sample) > 50:
                        sample = sample[:50] + '...'
                    field_stats[field]['sample_values'].append(sample)
    
    # 分类字段
    always_null_or_empty = []  # 一直为 null/0/空
    mostly_null = []           # 90%以上为 null/0/空
    partially_null = []        # 有值但有不少 null
    always_has_value = []      # 一直有值
    
    for field, stats in field_stats.items():
        total = stats['total']
        empty_count = stats['null_count'] + stats['zero_count'] + stats['empty_list_count'] + stats['empty_dict_count'] + stats['false_count']
        empty_ratio = empty_count / total
        
        field_info = {
            'field': field,
            'total': total,
            'null_count': stats['null_count'],
            'zero_count': stats['zero_count'],
            'empty_list_count': stats['empty_list_count'],
            'empty_dict_count': stats['empty_dict_count'],
            'false_count': stats['false_count'],
            'has_value_count': stats['has_value_count'],
            'empty_ratio': empty_ratio,
            'sample_values': stats['sample_values']
        }
        
        if empty_ratio == 1.0:
            always_null_or_empty.append(field_info)
        elif empty_ratio >= 0.9:
            mostly_null.append(field_info)
        elif empty_ratio >= 0.5:
            partially_null.append(field_info)
        else:
            always_has_value.append(field_info)
    
    # 按 empty_ratio 排序
    always_null_or_empty.sort(key=lambda x: x['field'])
    mostly_null.sort(key=lambda x: x['empty_ratio'], reverse=True)
    partially_null.sort(key=lambda x: x['empty_ratio'], reverse=True)
    always_has_value.sort(key=lambda x: x['empty_ratio'])
    
    return {
        'always_null_or_empty': always_null_or_empty,
        'mostly_null': mostly_null,
        'partially_null': partially_null,
        'always_has_value': always_has_value,
        'total_activities': len(activities)
    }


def generate_markdown_report(results, output_path):
    """生成 Markdown 报告"""
    
    lines = []
    lines.append("# Activities.json 字段分析报告")
    lines.append("")
    lines.append(f"> 分析时间: 自动生成  ")
    lines.append(f"> 样本数量: {results['total_activities']} 条活动记录")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 1. 可以忽略的字段（一直为 null/0/空）
    lines.append("## 🔴 可以忽略的字段（100% 为 null/0/空/False）")
    lines.append("")
    lines.append("这些字段在所有活动中都没有有效值，可以安全地从分析中移除。")
    lines.append("")
    
    if results['always_null_or_empty']:
        lines.append("| 字段名 | 总记录数 | null | 0 | [] | {{}} | False | 示例值 |")
        lines.append("|--------|----------|------|---|----|------|-------|--------|")
        for info in results['always_null_or_empty']:
            samples = str(info['sample_values'][:1]) if info['sample_values'] else '-'
            if len(samples) > 40:
                samples = samples[:40] + '...'
            lines.append(f"| `{info['field']}` | {info['total']} | {info['null_count']} | {info['zero_count']} | {info['empty_list_count']} | {info['empty_dict_count']} | {info['false_count']} | {samples} |")
    else:
        lines.append("*无此类字段*")
    lines.append("")
    
    # 2. 基本可忽略的字段（90%以上为 null/0/空）
    lines.append("## 🟠 基本可忽略的字段（≥90% 为 null/0/空/False）")
    lines.append("")
    lines.append("这些字段在绝大多数活动中没有有效值，仅在极少数记录中有值。")
    lines.append("")
    
    if results['mostly_null']:
        lines.append("| 字段名 | 空值比例 | null | 0 | [] | {{}} | False | 有效值 | 示例值 |")
        lines.append("|--------|----------|------|---|----|------|-------|--------|--------|")
        for info in results['mostly_null']:
            ratio_pct = f"{info['empty_ratio']*100:.1f}%"
            samples = str(info['sample_values'][:1]) if info['sample_values'] else '-'
            if len(samples) > 30:
                samples = samples[:30] + '...'
            lines.append(f"| `{info['field']}` | {ratio_pct} | {info['null_count']} | {info['zero_count']} | {info['empty_list_count']} | {info['empty_dict_count']} | {info['false_count']} | {info['has_value_count']} | {samples} |")
    else:
        lines.append("*无此类字段*")
    lines.append("")
    
    # 3. 部分为空的字段（50%-90%）
    lines.append("## 🟡 部分为空的字段（50%-90% 为 null/0/空/False）")
    lines.append("")
    lines.append("这些字段在部分活动中有值，使用时需要做空值检查。")
    lines.append("")
    
    if results['partially_null']:
        lines.append("| 字段名 | 空值比例 | null | 0 | [] | {{}} | False | 有效值 | 示例值 |")
        lines.append("|--------|----------|------|---|----|------|-------|--------|--------|")
        for info in results['partially_null']:
            ratio_pct = f"{info['empty_ratio']*100:.1f}%"
            samples = str(info['sample_values'][:1]) if info['sample_values'] else '-'
            if len(samples) > 30:
                samples = samples[:30] + '...'
            lines.append(f"| `{info['field']}` | {ratio_pct} | {info['null_count']} | {info['zero_count']} | {info['empty_list_count']} | {info['empty_dict_count']} | {info['false_count']} | {info['has_value_count']} | {samples} |")
    else:
        lines.append("*无此类字段*")
    lines.append("")
    
    # 4. 一直有值的字段（<50%为空）
    lines.append("## 🟢 核心字段（<50% 为空，数据质量高）")
    lines.append("")
    lines.append("这些字段在大多数活动中都有有效值，是分析的主要数据来源。")
    lines.append("")
    
    if results['always_has_value']:
        lines.append("| 字段名 | 空值比例 | null | 0 | [] | {{}} | False | 有效值 | 示例值 |")
        lines.append("|--------|----------|------|---|----|------|-------|--------|--------|")
        for info in results['always_has_value']:
            ratio_pct = f"{info['empty_ratio']*100:.1f}%"
            samples = str(info['sample_values'][:1]) if info['sample_values'] else '-'
            if len(samples) > 30:
                samples = samples[:30] + '...'
            lines.append(f"| `{info['field']}` | {ratio_pct} | {info['null_count']} | {info['zero_count']} | {info['empty_list_count']} | {info['empty_dict_count']} | {info['false_count']} | {info['has_value_count']} | {samples} |")
    else:
        lines.append("*无此类字段*")
    lines.append("")
    
    # 5. 建议的忽略字段列表
    lines.append("---")
    lines.append("")
    lines.append("## 📋 建议忽略的字段列表（用于代码优化）")
    lines.append("")
    lines.append("```python")
    lines.append("# 可以安全忽略的字段（100% 为空）")
    lines.append("IGNORED_FIELDS_100 = [")
    for info in results['always_null_or_empty']:
        lines.append(f"    '{info['field']}',")
    lines.append("]")
    lines.append("")
    lines.append("# 基本可忽略的字段（≥90% 为空）")
    lines.append("IGNORED_FIELDS_90 = [")
    for info in results['mostly_null']:
        lines.append(f"    '{info['field']}',  # {info['empty_ratio']*100:.1f}% 为空")
    lines.append("]")
    lines.append("```")
    lines.append("")
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n报告已生成: {output_path}")


if __name__ == '__main__':
    json_file = '/root/.openclaw/workspace-cycling/data/cycling/activities.json'
    output_file = '/root/.openclaw/workspace-cycling/skills/cycling-trainer/references/field_analysis_report.md'
    
    print("开始分析字段...")
    results = analyze_null_fields(json_file)
    generate_markdown_report(results, output_file)
    
    print(f"\n统计摘要:")
    print(f"  - 可忽略字段(100%空): {len(results['always_null_or_empty'])} 个")
    print(f"  - 基本可忽略(≥90%空): {len(results['mostly_null'])} 个")
    print(f"  - 部分为空(50-90%): {len(results['partially_null'])} 个")
    print(f"  - 核心字段(<50%空): {len(results['always_has_value'])} 个")
