"""
周期记忆数据提取
从 JSON 数据库读取周期训练状态
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 导入新的 cycle_memory 模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cycle_memory import CycleMemoryManager, CycleMemory


def get_memory_path() -> Path:
    """获取记忆文件路径（JSON 格式）"""
    script_dir = Path(__file__).parent.parent.parent.parent.parent
    memory_path = script_dir / "data" / "cycling" / "cycle_memory.json"
    return memory_path


def extract_cycle_memory() -> Dict[str, Any]:
    """
    提取周期记忆数据（保持向后兼容的接口）
    
    Returns:
        {
            "has_cycle_memory": bool,
            "cycle_state": {...} or None,
            "raw_content": str or None
        }
    """
    manager = CycleMemoryManager()
    memory = manager.load_memory()
    
    if not memory:
        return {
            "has_cycle_memory": False,
            "cycle_state": None,
            "raw_content": None,
            "error": "Cycle memory not found"
        }
    
    # 转换为向后兼容的格式
    cycle_state = {
        "cycle_number": memory.current_cycle.cycle_number,
        "start_date": memory.current_cycle.start_date,
        "current_week": memory.current_cycle.current_week,
        "week_type": memory.current_cycle.week_type,
        "ftp": memory.current_cycle.ftp,
        "this_week": memory.this_week.to_dict(),
        "last_week": memory.last_week.to_dict() if memory.last_week else None,
        "week_before_last": memory.week_before_last.to_dict() if memory.week_before_last else None,
        "cycle_history": [h.to_dict() for h in memory.cycle_history]
    }
    
    return {
        "has_cycle_memory": True,
        "cycle_state": cycle_state,
        "raw_content": None
    }


def update_cycle_memory(new_state: Dict[str, Any]) -> bool:
    """
    更新周期记忆状态（保持向后兼容的接口）
    
    Args:
        new_state: 新的周期状态字典
        
    Returns:
        bool: 是否成功更新
    """
    manager = CycleMemoryManager()
    
    try:
        # 将新状态转换为 CycleMemory 对象
        memory_data = {
            "version": new_state.get("version", 1),
            "updated_at": new_state.get("updated_at", ""),
            "current_cycle": {
                "cycle_number": new_state.get("cycle_number", 1),
                "start_date": new_state.get("start_date", ""),
                "current_week": new_state.get("current_week", 1),
                "week_type": new_state.get("week_type", "base"),
                "ftp": new_state.get("ftp", 250)
            },
            "this_week": new_state.get("this_week", {}),
            "last_week": new_state.get("last_week"),
            "week_before_last": new_state.get("week_before_last"),
            "cycle_history": new_state.get("cycle_history", [])
        }
        
        memory = CycleMemory.from_dict(memory_data)
        return manager.save_memory(memory)
        
    except Exception as e:
        print(f"Error updating cycle memory: {e}", file=sys.stderr)
        return False


def get_cycle_memory_manager() -> CycleMemoryManager:
    """获取周期记忆管理器实例"""
    return CycleMemoryManager()


if __name__ == "__main__":
    result = extract_cycle_memory()
    print(json.dumps(result, indent=2, ensure_ascii=False))
