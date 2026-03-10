"""
生成 MEMORY.md 文件
从 JSON 数据源自动生成 Markdown 格式的周期记忆
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from cycle_memory import CycleMemoryManager


def generate_memory_md() -> str:
    """生成完整的 MEMORY.md 内容"""
    manager = CycleMemoryManager()
    
    # 基础头部信息
    header = """# MEMORY.md - Cycling Agent Memory

## Channel Binding

- **Agent Role:** 仅响应骑行相关指令，忽略其他消息

## User Profile

- **Name:** Carno
- **Timezone:** GMT+8

## Data Files

- 活动数据: `~/.openclaw/workspace-cycling/data/cycling/activities.json`
- 同步状态: `~/.openclaw/workspace-cycling/data/cycling/sync_state.json`
- 周期记忆: `~/.openclaw/workspace-cycling/data/cycling/cycle_memory.json`

## Recent Context

_(由 agent 自动更新)_

---

"""
    
    # 生成周期记忆部分
    cycle_section = manager.export_to_markdown()
    
    # 恢复骑模板（固定内容）
    recovery_template = """

### 恢复骑模板（Z2 Easy）

**来源**: 2026-03-10 周二 MyWhoosh - 60min Easy
**用途**: 低强度恢复日，强度课后主动恢复
**功率区间**: Z1-Z2 (125w-175w for FTP 260w)

```
-10m ramp 125w-175w

4x
-5m 165w
-5m 175w

-10m ramp 175w-125w
```

**结构说明**:
- 10分钟 ramp 热身：从 Z1 过渡到 Z2
- 4组交替：5分钟 @ 165w + 5分钟 @ 175w，保持踏频和 engagement
- 10分钟 ramp 冷身：逐渐降低功率

**适用场景**:
- 强度课后的恢复日
- TSB 负值时的主动恢复
- 恢复周的轻松骑

---

**注意:** 此 memory 文件由 `cycle_memory.json` 自动生成，请勿直接编辑。
编辑周期记忆请使用 `cycle_memory.py` API 或修改 JSON 数据文件。
"""
    
    return header + cycle_section + recovery_template


def write_memory_md(output_path: Optional[Path] = None) -> bool:
    """
    写入 MEMORY.md 文件
    
    Args:
        output_path: 输出路径，默认为 workspace 根目录的 MEMORY.md
        
    Returns:
        bool: 是否成功写入
    """
    if output_path is None:
        # scripts/ -> skills/cycling-trainer/ -> workspace/
        output_path = Path(__file__).parent.parent.parent.parent / "MEMORY.md"
    
    try:
        content = generate_memory_md()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"MEMORY.md generated successfully at: {output_path}")
        return True
    except Exception as e:
        print(f"Error writing MEMORY.md: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate MEMORY.md from cycle_memory.json')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    args = parser.parse_args()
    
    output_path = Path(args.output) if args.output else None
    success = write_memory_md(output_path)
    sys.exit(0 if success else 1)
