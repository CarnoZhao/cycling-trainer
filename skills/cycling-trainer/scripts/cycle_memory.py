"""
周期记忆管理模块
提供 JSON 数据库存储的周期记忆读写 API
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


# 默认数据路径
# scripts/cycle_memory.py -> workspace/data/cycling/
DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "cycling"
DEFAULT_MEMORY_FILE = DEFAULT_DATA_DIR / "cycle_memory.json"


@dataclass
class Activity:
    """训练活动"""
    date: str  # YYYY-MM-DD
    weekday: str
    content: str
    type: str
    load: int
    status: str  # completed, planned, in_progress

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Activity":
        return cls(**data)


@dataclass
class WeekData:
    """周训练数据"""
    week_number: int
    week_type: str  # base, build, peak, recovery
    intensity_target: int
    intensity_completed: int
    total_load: int
    tsb: Optional[float]
    status: str  # completed, in_progress, planned
    activities: List[Activity]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "week_number": self.week_number,
            "week_type": self.week_type,
            "intensity_target": self.intensity_target,
            "intensity_completed": self.intensity_completed,
            "total_load": self.total_load,
            "tsb": self.tsb,
            "status": self.status,
            "activities": [a.to_dict() for a in self.activities]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeekData":
        activities = [Activity.from_dict(a) for a in data.get("activities", [])]
        return cls(
            week_number=data["week_number"],
            week_type=data["week_type"],
            intensity_target=data["intensity_target"],
            intensity_completed=data["intensity_completed"],
            total_load=data["total_load"],
            tsb=data.get("tsb"),
            status=data["status"],
            activities=activities
        )


@dataclass
class CurrentCycle:
    """当前周期信息"""
    cycle_number: int
    start_date: str  # YYYY-MM-DD
    current_week: int
    week_type: str
    ftp: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurrentCycle":
        return cls(**data)


@dataclass
class CycleHistoryEntry:
    """周期历史条目"""
    cycle_number: int
    start_date: str
    end_date: str
    completed: bool
    weeks: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "cycle_number": self.cycle_number,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "completed": self.completed
        }
        if self.weeks:
            result["weeks"] = self.weeks
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CycleHistoryEntry":
        return cls(
            cycle_number=data["cycle_number"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            completed=data["completed"],
            weeks=data.get("weeks")
        )


@dataclass
class CycleMemory:
    """周期记忆完整数据结构"""
    version: int
    updated_at: str
    current_cycle: CurrentCycle
    this_week: WeekData
    last_week: Optional[WeekData]
    week_before_last: Optional[WeekData]
    cycle_history: List[CycleHistoryEntry]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "updated_at": self.updated_at,
            "current_cycle": self.current_cycle.to_dict(),
            "this_week": self.this_week.to_dict(),
            "last_week": self.last_week.to_dict() if self.last_week else None,
            "week_before_last": self.week_before_last.to_dict() if self.week_before_last else None,
            "cycle_history": [h.to_dict() for h in self.cycle_history]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CycleMemory":
        return cls(
            version=data["version"],
            updated_at=data["updated_at"],
            current_cycle=CurrentCycle.from_dict(data["current_cycle"]),
            this_week=WeekData.from_dict(data["this_week"]),
            last_week=WeekData.from_dict(data["last_week"]) if data.get("last_week") else None,
            week_before_last=WeekData.from_dict(data["week_before_last"]) if data.get("week_before_last") else None,
            cycle_history=[CycleHistoryEntry.from_dict(h) for h in data.get("cycle_history", [])]
        )


class CycleMemoryManager:
    """周期记忆管理器"""

    def __init__(self, memory_file: Optional[Path] = None):
        self.memory_file = memory_file or DEFAULT_MEMORY_FILE
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

    def load_memory(self) -> Optional[CycleMemory]:
        """加载周期记忆"""
        if not self.memory_file.exists():
            return None
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return CycleMemory.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading cycle memory: {e}")
            return None

    def save_memory(self, memory: CycleMemory) -> bool:
        """保存周期记忆"""
        try:
            # 更新时间戳
            memory.updated_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving cycle memory: {e}")
            return False

    def get_current_cycle(self) -> Optional[Dict[str, Any]]:
        """获取当前周期信息"""
        memory = self.load_memory()
        if not memory:
            return None
        return memory.current_cycle.to_dict()

    def update_week_activity(self, date: str, activity_data: Dict[str, Any]) -> bool:
        """更新本周活动"""
        memory = self.load_memory()
        if not memory:
            return False
        
        # 查找并更新活动
        updated = False
        for activity in memory.this_week.activities:
            if activity.date == date:
                activity.content = activity_data.get("content", activity.content)
                activity.type = activity_data.get("type", activity.type)
                activity.load = activity_data.get("load", activity.load)
                activity.status = activity_data.get("status", activity.status)
                updated = True
                break
        
        # 如果没找到，添加新活动
        if not updated:
            new_activity = Activity.from_dict(activity_data)
            memory.this_week.activities.append(new_activity)
        
        # 重新计算本周统计
        self._recalculate_week_stats(memory.this_week)
        
        return self.save_memory(memory)

    def _recalculate_week_stats(self, week: WeekData):
        """重新计算周统计"""
        week.total_load = sum(a.load for a in week.activities if a.status == "completed")
        week.intensity_completed = sum(
            1 for a in week.activities 
            if a.status == "completed" and a.type in ["SS", "Threshold", "VO2max", "Anaerobic"]
        )

    def advance_week(self) -> bool:
        """进入下一周"""
        memory = self.load_memory()
        if not memory:
            return False
        
        # 将本周移到上周
        memory.week_before_last = memory.last_week
        memory.last_week = memory.this_week
        
        # 创建新的本周
        new_week_number = memory.current_cycle.current_week + 1
        
        # 判断周类型 (4周周期: base, build, peak, recovery)
        week_types = ["base", "build", "peak", "recovery"]
        week_type_index = (new_week_number - 1) % 4
        new_week_type = week_types[week_type_index]
        
        # 如果是新周期的第一周
        if new_week_number > 4:
            # 完成当前周期
            self._complete_current_cycle(memory)
            new_week_number = 1
            new_week_type = "base"
        
        memory.current_cycle.current_week = new_week_number
        memory.current_cycle.week_type = new_week_type
        
        # 创建新的本周数据（空）
        memory.this_week = WeekData(
            week_number=new_week_number,
            week_type=new_week_type,
            intensity_target=2 if new_week_type in ["build", "peak"] else 1,
            intensity_completed=0,
            total_load=0,
            tsb=None,
            status="planned",
            activities=[]
        )
        
        return self.save_memory(memory)

    def _complete_current_cycle(self, memory: CycleMemory):
        """完成当前周期并添加到历史"""
        # 计算周期结束日期
        start_date = datetime.strptime(memory.current_cycle.start_date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=27)  # 4周周期
        
        history_entry = CycleHistoryEntry(
            cycle_number=memory.current_cycle.cycle_number,
            start_date=memory.current_cycle.start_date,
            end_date=end_date.strftime("%Y-%m-%d"),
            completed=True,
            weeks=[
                {"week_number": i+1, "week_type": w, "completed": True}
                for i, w in enumerate(["base", "build", "peak", "recovery"])
            ]
        )
        memory.cycle_history.append(history_entry)
        
        # 更新当前周期
        memory.current_cycle.cycle_number += 1
        memory.current_cycle.start_date = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")

    def start_new_cycle(self, ftp: Optional[int] = None, start_date: Optional[str] = None) -> bool:
        """开始新周期"""
        memory = self.load_memory()
        if not memory:
            # 创建全新的周期记忆
            memory = self._create_default_memory()
        
        # 完成当前周期（如果有）
        if memory.this_week.status == "in_progress":
            self._complete_current_cycle(memory)
        
        # 设置新周期
        memory.current_cycle.cycle_number += 1
        memory.current_cycle.start_date = start_date or datetime.now().strftime("%Y-%m-%d")
        memory.current_cycle.current_week = 1
        memory.current_cycle.week_type = "base"
        if ftp:
            memory.current_cycle.ftp = ftp
        
        # 重置周数据
        memory.week_before_last = None
        memory.last_week = None
        memory.this_week = WeekData(
            week_number=1,
            week_type="base",
            intensity_target=2,
            intensity_completed=0,
            total_load=0,
            tsb=None,
            status="in_progress",
            activities=[]
        )
        
        return self.save_memory(memory)

    def _create_default_memory(self) -> CycleMemory:
        """创建默认周期记忆结构"""
        now = datetime.now()
        return CycleMemory(
            version=1,
            updated_at=now.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            current_cycle=CurrentCycle(
                cycle_number=0,
                start_date=now.strftime("%Y-%m-%d"),
                current_week=1,
                week_type="base",
                ftp=250
            ),
            this_week=WeekData(
                week_number=1,
                week_type="base",
                intensity_target=2,
                intensity_completed=0,
                total_load=0,
                tsb=None,
                status="planned",
                activities=[]
            ),
            last_week=None,
            week_before_last=None,
            cycle_history=[]
        )

    def export_to_markdown(self) -> str:
        """导出为 Markdown 格式（用于显示）"""
        memory = self.load_memory()
        if not memory:
            return "## Training Cycle Memory\n\n暂无周期记忆数据。"
        
        lines = [
            "## Training Cycle Memory",
            "",
            f"**当前周期**: 第 {memory.current_cycle.cycle_number} 周期",
            f"**周期开始日期**: {memory.current_cycle.start_date}",
            f"**当前周**: 第 {memory.current_cycle.current_week} 周 ({self._get_week_type_name(memory.current_cycle.week_type)})",
            f"**FTP**: {memory.current_cycle.ftp}w",
            ""
        ]
        
        # 本周训练记录
        week_type_emoji = "🔄" if memory.this_week.status == "in_progress" else "✅"
        lines.extend([
            f"### 本周训练记录 (第 {memory.this_week.week_number} 周 - {self._get_week_type_name(memory.this_week.week_type)}) {week_type_emoji} {self._get_status_name(memory.this_week.status)}",
            "",
            "| 日期 | 训练内容 | 类型 | 负荷 | 状态 |",
            "|------|---------|------|------|------|"
        ])
        
        for activity in memory.this_week.activities:
            date_short = activity.date[5:].replace('-', '/')
            date_display = f"{date_short} ({activity.weekday})"
            status_emoji = self._get_status_emoji(activity.status)
            lines.append(f"| {date_display} | {activity.content} | {activity.type} | {activity.load} TSS | {status_emoji} {self._get_status_name(activity.status)} |")
        
        lines.extend([
            "",
            f"**本周强度课**: {memory.this_week.intensity_completed}/{memory.this_week.intensity_target} 节完成",
            f"**本周累计负荷**: {memory.this_week.total_load} TSS",
            f"**周期定位**: 第{memory.this_week.week_number}周{self._get_week_type_name(memory.this_week.week_type)}",
        ])
        
        if memory.this_week.tsb is not None:
            lines.append(f"**当前状态**: TSB {memory.this_week.tsb}")
        
        lines.append("")
        
        # 上周训练记录
        if memory.last_week:
            lines.extend([
                f"### 上周训练记录 (第 {memory.last_week.week_number} 周 - {self._get_week_type_name(memory.last_week.week_type)}) ✅ 已完成",
                "",
                "| 日期 | 训练内容 | 类型 | 负荷 | 状态 |",
                "|------|---------|------|------|------|"
            ])
            
            for activity in memory.last_week.activities:
                date_short = activity.date[5:].replace('-', '/')
                date_display = f"{date_short} ({activity.weekday})"
                status_emoji = self._get_status_emoji(activity.status)
                lines.append(f"| {date_display} | {activity.content} | {activity.type} | {activity.load} TSS | {status_emoji} {self._get_status_name(activity.status)} |")
            
            lines.extend([
                "",
                f"**上周强度课**: {memory.last_week.intensity_completed}/{memory.last_week.intensity_target} 节完成",
                f"**上周总负荷**: {memory.last_week.total_load} TSS",
                ""
            ])
        
        # 上上周训练记录
        if memory.week_before_last:
            lines.extend([
                f"### 上上周训练记录 (第 {memory.week_before_last.week_number} 周 - {self._get_week_type_name(memory.week_before_last.week_type)}) ✅ 已完成",
                "",
                "| 日期 | 训练内容 | 类型 | 负荷 | 状态 |",
                "|------|---------|------|------|------|"
            ])
            
            for activity in memory.week_before_last.activities:
                date_short = activity.date[5:].replace('-', '/')
                date_display = f"{date_short} ({activity.weekday})"
                status_emoji = self._get_status_emoji(activity.status)
                lines.append(f"| {date_display} | {activity.content} | {activity.type} | {activity.load} TSS | {status_emoji} {self._get_status_name(activity.status)} |")
            
            lines.extend([
                "",
                f"**上上周强度课**: {memory.week_before_last.intensity_completed}/{memory.week_before_last.intensity_target} 节完成",
                f"**上上周总负荷**: {memory.week_before_last.total_load} TSS",
                ""
            ])
        
        # 周期历史
        if memory.cycle_history:
            lines.extend([
                "### 周期历史",
                ""
            ])
            
            for history in memory.cycle_history:
                lines.append(f"**第 {history.cycle_number} 周期** ({history.start_date} ~ {history.end_date})")
                if history.weeks:
                    for week in history.weeks:
                        lines.append(f"- 第 {week['week_number']} 周: {self._get_week_type_name(week['week_type'])} {'✓' if week['completed'] else '○'}")
                lines.append("")
        
        return "\n".join(lines)

    def _get_week_type_name(self, week_type: str) -> str:
        """获取周类型中文名"""
        names = {
            "base": "基础强度周",
            "build": "递增强度周",
            "peak": "峰值强度周",
            "recovery": "恢复周"
        }
        return names.get(week_type, week_type)

    def _get_status_name(self, status: str) -> str:
        """获取状态中文名"""
        names = {
            "completed": "完成",
            "planned": "计划中",
            "in_progress": "进行中"
        }
        return names.get(status, status)

    def _get_status_emoji(self, status: str) -> str:
        """获取状态表情"""
        emojis = {
            "completed": "✅",
            "planned": "📋",
            "in_progress": "🔄"
        }
        return emojis.get(status, "⏳")


# 便捷函数接口（保持向后兼容）
def load_memory() -> Optional[Dict[str, Any]]:
    """加载周期记忆（返回字典格式）"""
    manager = CycleMemoryManager()
    memory = manager.load_memory()
    return memory.to_dict() if memory else None


def save_memory(data: Dict[str, Any]) -> bool:
    """保存周期记忆"""
    manager = CycleMemoryManager()
    memory = CycleMemory.from_dict(data)
    return manager.save_memory(memory)


def get_current_cycle() -> Optional[Dict[str, Any]]:
    """获取当前周期信息"""
    manager = CycleMemoryManager()
    return manager.get_current_cycle()


def update_week_activity(date: str, activity_data: Dict[str, Any]) -> bool:
    """更新本周活动"""
    manager = CycleMemoryManager()
    return manager.update_week_activity(date, activity_data)


def advance_week() -> bool:
    """进入下一周"""
    manager = CycleMemoryManager()
    return manager.advance_week()


def start_new_cycle(ftp: Optional[int] = None, start_date: Optional[str] = None) -> bool:
    """开始新周期"""
    manager = CycleMemoryManager()
    return manager.start_new_cycle(ftp, start_date)


def export_to_markdown() -> str:
    """导出为 Markdown"""
    manager = CycleMemoryManager()
    return manager.export_to_markdown()


if __name__ == "__main__":
    # 测试代码
    manager = CycleMemoryManager()
    
    # 加载并显示
    memory = manager.load_memory()
    if memory:
        print("Current cycle:", json.dumps(memory.current_cycle.to_dict(), indent=2, ensure_ascii=False))
        print("\nMarkdown export preview:")
        print(manager.export_to_markdown()[:500] + "...")
    else:
        print("No cycle memory found")
