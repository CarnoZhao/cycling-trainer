"""
同步检查模块

负责检查数据新鲜度并触发同步
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 路径定义
SCRIPT_DIR = Path(__file__).parent.parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR.parent.parent / "data" / "cycling"
SYNC_STATE_FILE = DATA_DIR / "sync_state.json"

SYNC_INTERVAL_HOURS = 1  # 超过1小时触发同步


def check_and_sync(athlete_id, api_key, force=False):
    """
    检查是否需要同步数据，如果需要则执行同步
    
    Args:
        athlete_id: 骑手 ID
        api_key: API Key
        force: 强制同步，忽略时间间隔
    
    Returns:
        dict: 同步结果信息
    """
    should_sync = force
    last_sync_time = None
    
    # 读取 sync_state.json
    if SYNC_STATE_FILE.exists():
        try:
            with open(SYNC_STATE_FILE) as f:
                sync_state = json.load(f)
            last_sync_str = sync_state.get('last_sync')
            if last_sync_str:
                last_sync_time = datetime.fromisoformat(last_sync_str)
                hours_since_sync = (datetime.now() - last_sync_time).total_seconds() / 3600
                
                # 如果超过阈值，需要同步
                if hours_since_sync >= SYNC_INTERVAL_HOURS:
                    should_sync = True
                    print(f"[Sync Check] Last sync was {hours_since_sync:.1f} hours ago (>={SYNC_INTERVAL_HOURS}h threshold)", file=sys.stderr)
                else:
                    print(f"[Sync Check] Data is fresh ({hours_since_sync:.1f}h < {SYNC_INTERVAL_HOURS}h), skipping sync", file=sys.stderr)
        except Exception as e:
            print(f"[Sync Check] Error reading sync state: {e}", file=sys.stderr)
            should_sync = True
    else:
        # 没有 sync_state，需要同步
        print("[Sync Check] No sync state found, syncing...", file=sys.stderr)
        should_sync = True
    
    # 执行同步
    if should_sync:
        sync_script = SCRIPT_DIR / "sync_intervals.py"
        if sync_script.exists():
            try:
                print(f"[Sync] Running incremental sync...", file=sys.stderr)
                result = subprocess.run(
                    [sys.executable, str(sync_script), athlete_id, "--api-key", api_key],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"[Sync] Completed successfully", file=sys.stderr)
                    return {
                        "synced": True,
                        "last_sync_before": last_sync_time.isoformat() if last_sync_time else None,
                        "output": result.stdout.strip()
                    }
                else:
                    print(f"[Sync] Failed: {result.stderr}", file=sys.stderr)
                    return {"synced": False, "error": result.stderr}
            except subprocess.TimeoutExpired:
                print("[Sync] Timeout after 120s", file=sys.stderr)
                return {"synced": False, "error": "Sync timeout"}
            except Exception as e:
                print(f"[Sync] Error: {e}", file=sys.stderr)
                return {"synced": False, "error": str(e)}
        else:
            print(f"[Sync] Sync script not found at {sync_script}", file=sys.stderr)
            return {"synced": False, "error": "Sync script not found"}
    
    return {"synced": False, "reason": "Data is fresh"}
