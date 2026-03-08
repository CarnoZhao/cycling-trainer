"""
周期记忆数据提取
读取 memory/cycling.md 中的周期训练状态
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


def get_memory_path() -> Path:
    """获取记忆文件路径"""
    # 从脚本位置向上查找
    script_dir = Path(__file__).parent.parent.parent.parent.parent
    memory_path = script_dir / "memory" / "cycling.md"
    return memory_path


def parse_cycle_state(content: str) -> Optional[Dict[str, Any]]:
    """解析 CYCLE_STATE 注释块"""
    pattern = r'<!--\s*CYCLE_STATE\s*\n(.*?)\n-->'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def extract_cycle_memory() -> Dict[str, Any]:
    """
    提取周期记忆数据
    
    Returns:
        {
            "has_cycle_memory": bool,
            "cycle_state": {...} or None,
            "raw_content": str or None
        }
    """
    memory_path = get_memory_path()
    
    if not memory_path.exists():
        return {
            "has_cycle_memory": False,
            "cycle_state": None,
            "raw_content": None,
            "error": "Memory file not found"
        }
    
    try:
        content = memory_path.read_text(encoding='utf-8')
        cycle_state = parse_cycle_state(content)
        
        return {
            "has_cycle_memory": cycle_state is not None,
            "cycle_state": cycle_state,
            "raw_content": content if cycle_state is None else None
        }
    except Exception as e:
        return {
            "has_cycle_memory": False,
            "cycle_state": None,
            "raw_content": None,
            "error": str(e)
        }


def update_cycle_memory(new_state: Dict[str, Any]) -> bool:
    """
    更新周期记忆状态
    
    Args:
        new_state: 新的周期状态字典
        
    Returns:
        bool: 是否成功更新
    """
    memory_path = get_memory_path()
    
    if not memory_path.exists():
        return False
    
    try:
        content = memory_path.read_text(encoding='utf-8')
        
        # 将新状态格式化为 JSON
        new_state_json = json.dumps(new_state, indent=2, ensure_ascii=False)
        
        # 替换现有的 CYCLE_STATE 块
        pattern = r'(<!--\s*CYCLE_STATE\s*\n).*?(\n\s*-->)'
        replacement = f'<!-- CYCLE_STATE\n{new_state_json}\n-->'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 如果没有找到现有块，在 Training Cycle Memory 部分添加
        if new_content == content:
            # 在 ### Current Cycle Status 后面添加
            section_pattern = r'(### Current Cycle Status\s*\n)'
            new_section = f'### Current Cycle Status\n\n<!-- CYCLE_STATE\n{new_state_json}\n-->\n'
            new_content = re.sub(section_pattern, new_section, content)
        
        memory_path.write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"Error updating cycle memory: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    import sys
    result = extract_cycle_memory()
    print(json.dumps(result, indent=2, ensure_ascii=False))
