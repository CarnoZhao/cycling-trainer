#!/usr/bin/env python3
"""
Upload workouts to intervals.icu

NP calculation:
1. Calculate 30-second moving average of power data
2. Raise each value to the 4th power
3. Take the average of these values
4. Calculate the 4th root of the average

TSS = 100 * (NP/FTP)^2 * (duration/3600)

API Upload:
- URL: https://intervals.icu/api/v1/athlete/{athlete_id}/events/bulk?upsertOnUid=false&updatePlanApplied=false
- Auth: Basic Auth with base64 encoded "API_KEY:{api_key}"
- Method: POST
"""
import json
import os
import sys
import re
import math
import base64
import urllib.request
import urllib.error
from datetime import datetime

# Config
BASE_URL = "https://intervals.icu"


def get_config():
    """Read config from config.json"""
    config_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'config.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'),
        'config.json'
    ]
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except:
                pass
    return {}


def get_athlete_id():
    """Get athlete ID from config or environment"""
    # Try environment first
    athlete_id = os.environ.get('INTERVALS_ATHLETE_ID', '')
    if athlete_id:
        return athlete_id
    # Try config file
    config = get_config()
    return config.get('athlete_id', '')


def get_api_key():
    """Get API key from config or environment"""
    # Try environment first
    api_key = os.environ.get('INTERVALS_API_KEY', '')
    if api_key:
        return api_key
    # Try config file
    config = get_config()
    return config.get('api_key', '')


def upload_workouts_to_api(payload, athlete_id, api_key):
    """
    Upload workouts to intervals.icu via API
    
    Auth: Basic Auth with base64 encoded "API_KEY:{api_key}"
    URL: /api/v1/athlete/{athlete_id}/events/bulk?upsertOnUid=false&updatePlanApplied=false
    """
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        print("Error: API key not found. Set INTERVALS_API_KEY env var or config.json", file=sys.stderr)
        return None
    
    # Build auth header: base64("API_KEY:api_key")
    auth_str = f"API_KEY:{api_key}"
    auth_bytes = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    url = f"{BASE_URL}/api/v1/athlete/{athlete_id}/events/bulk?upsertOnUid=false&updatePlanApplied=false"
    
    headers = {
        'accept': '*/*',
        'authorization': f'Basic {auth_bytes}',
        'content-type': 'application/json'
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error uploading: {e}", file=sys.stderr)
        return None

def parse_workout_steps(description):
    """
    Parse workout description into individual steps with power and duration.
    Returns list of (duration_seconds, power_watts) tuples.
    """
    steps = []
    lines = description.strip().split('\n')
    in_repeat_block = False
    repeat_count = 1
    block_steps = []

    for line in lines:
        line = line.strip()

        # Empty line ends repeat block
        if not line:
            if in_repeat_block and block_steps:
                # Repeat the block steps
                for _ in range(repeat_count):
                    steps.extend(block_steps)
                in_repeat_block = False
                repeat_count = 1
                block_steps = []
            continue

        # Check for repeat marker (e.g., "4x", "2x")
        repeat_match = re.match(r'^(\d+)x\s*$', line)
        if repeat_match:
            in_repeat_block = True
            repeat_count = int(repeat_match.group(1))
            block_steps = []
            continue

        # Parse fixed power: - {duration}m @{power}w or - {duration}m {power}w
        fixed_match = re.search(r'-\s*(\d+)m\s*(?:@\s*)?(\d+)w', line)
        if fixed_match:
            minutes = int(fixed_match.group(1))
            power = int(fixed_match.group(2))
            seconds = minutes * 60

            if in_repeat_block:
                block_steps.append((seconds, power))
            else:
                steps.append((seconds, power))
            continue

        # Parse ramp: - {duration}m [@] ramp {start}w-{end}w
        ramp_match = re.search(r'-\s*(\d+)m\s*@?\s*ramp\s*(\d+)w-(\d+)w', line)
        if ramp_match:
            minutes = int(ramp_match.group(1))
            start_power = int(ramp_match.group(2))
            end_power = int(ramp_match.group(3))
            seconds = minutes * 60

            # For ramp, use average power
            avg_power = (start_power + end_power) / 2

            if in_repeat_block:
                block_steps.append((seconds, avg_power))
            else:
                steps.append((seconds, avg_power))
            continue

    # Add final block if still in repeat
    if in_repeat_block and block_steps:
        for _ in range(repeat_count):
            steps.extend(block_steps)

    return steps

def calculate_np(steps):
    """
    Calculate Normalized Power using the standard algorithm:
    1. Expand workout into 1-second power samples
    2. Calculate 30-second rolling average at each second (0-30, 1-31, 2-32...)
    3. Raise each 30s average to the 4th power
    4. Take the average of these values
    5. Calculate the 4th root

    Note: The last incomplete 30-second window is discarded.
    """
    if not steps:
        return 0

    # Expand steps into 1-second power samples
    power_samples = []
    for duration, power in steps:
        power_samples.extend([float(power)] * int(duration))

    total_seconds = len(power_samples)
    if total_seconds == 0:
        return 0

    window_size = 30

    # Need at least 30 seconds of data
    if total_seconds < window_size:
        # For short workouts, use simple average
        avg_power = sum(power_samples) / total_seconds
        return avg_power

    # Calculate 30-second rolling averages
    # Window positions: 0-29, 1-30, 2-31, ..., (N-30)-(N-1)
    # Discard the last incomplete window (< 30 seconds)
    num_windows = total_seconds - window_size + 1
    rolling_averages = []

    for i in range(num_windows):
        window = power_samples[i:i + window_size]
        window_avg = sum(window) / window_size
        rolling_averages.append(window_avg)

    # Raise each rolling average to the 4th power
    fourth_powers = [avg ** 4 for avg in rolling_averages]

    # Take the average of these values
    avg_fourth_power = sum(fourth_powers) / len(fourth_powers)

    # Calculate the 4th root
    np = avg_fourth_power ** 0.25

    return np

def calculate_tss(steps, ftp):
    """
    Calculate TSS using the standard formula:
    TSS = 100 * (NP/FTP)^2 * (duration/3600)
    """
    if not steps or ftp <= 0:
        return 0

    total_seconds = sum(duration for duration, _ in steps)
    if total_seconds == 0:
        return 0

    np = calculate_np(steps)
    duration_hours = total_seconds / 3600

    tss = 100 * ((np / ftp) ** 2) * duration_hours
    return round(tss)

def build_api_payload(workouts, ftp):
    """Build the API payload for bulk upload"""
    events = []

    for workout in workouts:
        name = workout.get('name', 'Workout')
        date_str = workout.get('date', '')
        description = workout.get('description', '')

        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            date = datetime.now()

        # Parse steps and calculate metrics
        steps = parse_workout_steps(description)
        total_seconds = sum(duration for duration, _ in steps)
        tss = calculate_tss(steps, ftp)

        # Format date for API (start of day)
        start_date_local = date.strftime('%Y-%m-%dT00:00:00')

        event = {
            "category": "WORKOUT",
            "start_date_local": start_date_local,
            "type": "Ride",
            "name": name,
            "description": description,
            "moving_time": total_seconds,
            "target": "POWER",
            "icu_training_load": tss,
            "workout_doc": {}
        }
        events.append(event)

    return events

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: upload_workouts.py '<workouts_json>' [ftp]", file=sys.stderr)
        sys.exit(1)

    workouts_json = sys.argv[1]
    ftp = int(sys.argv[2]) if len(sys.argv) > 2 else 260

    try:
        workouts = json.loads(workouts_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing workouts JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(workouts, list):
        workouts = [workouts]

    # Calculate metrics for display
    for workout in workouts:
        desc = workout.get('description', '')
        steps = parse_workout_steps(desc)
        total_seconds = sum(duration for duration, _ in steps)
        np = calculate_np(steps)
        tss = calculate_tss(steps, ftp)

        workout['_metrics'] = {
            'duration_seconds': total_seconds,
            'duration_min': round(total_seconds / 60, 1),
            'np': round(np, 1),
            'tss': tss
        }

    payload = build_api_payload(workouts, ftp)

    # Output summary
    print("WORKOUT_SUMMARY:")
    for i, workout in enumerate(workouts):
        metrics = workout.get('_metrics', {})
        print(f"  {workout.get('date')} - {workout.get('name')}: "
              f"{metrics.get('duration_min')}min, NP={metrics.get('np')}w, TSS={metrics.get('tss')}")

    # Check if upload flag is set
    upload_flag = os.environ.get('UPLOAD_WORKOUTS', '').lower() in ('1', 'true', 'yes')
    
    if upload_flag:
        athlete_id = get_athlete_id()
        api_key = get_api_key()
        
        if not athlete_id:
            print("Error: Athlete ID not found. Set INTERVALS_ATHLETE_ID env var or config.json", file=sys.stderr)
            sys.exit(1)
        
        print("\n📤 Uploading to intervals.icu...")
        result = upload_workouts_to_api(payload, athlete_id, api_key)
        if result:
            print(f"✅ Successfully uploaded {len(result)} workouts")
            for item in result:
                print(f"   - {item.get('start_date_local', '')[:10]}: {item.get('name', '')} (ID: {item.get('id', '')})")
        else:
            print("❌ Upload failed")
            sys.exit(1)
    else:
        print("\nPAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("\n💡 To upload, set UPLOAD_WORKOUTS=1 or call via agent with upload flag")

if __name__ == "__main__":
    main()
