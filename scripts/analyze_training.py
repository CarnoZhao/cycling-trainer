#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cycling Training Analysis Script
Professional cycling coach analysis functions
"""

import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("/root/.openclaw/workspace/data/cycling/activities.json")

def load_data():
    """Load local data"""
    if not DATA_FILE.exists():
        print("Error: No local data, please run sync first")
        sys.exit(1)
    with open(DATA_FILE) as f:
        data = json.load(f)
    return sorted(data, key=lambda x: x.get('start_date', ''), reverse=True)

def analyze_status():
    """Analyze current body status"""
    data = load_data()
    latest = data[0]
    
    ctl = latest.get('icu_ctl', 0)
    atl = latest.get('icu_atl', 0)
    tsb = ctl - atl
    
    # Status判断
    if tsb > 15:
        status = 'Peak - Ready for race'
        desc = 'Body is at peak condition, suitable for racing'
    elif tsb > 5:
        status = 'Building - Good form'
        desc = 'Fitness improving steadily'
    elif tsb > -10:
        status = 'Maintenance - Balanced'
        desc = 'Training load is balanced, maintain current form'
    elif tsb > -30:
        status = 'Recovery - Accumulating fatigue'
        desc = 'High recent training load, needs recovery'
    else:
        status = 'Overreaching - Rest needed'
        desc = 'Severe fatigue, must stop high intensity training'
    
    # 最近7天
    week = [a for a in data[:10] if a.get('type') in ['Ride', 'VirtualRide']]
    week_load = sum(a.get('icu_training_load', 0) for a in week[:7])
    week_time = sum(a.get('moving_time', 0) for a in week[:7]) / 60
    week_count = len([a for a in week[:7] if a.get('icu_training_load', 0) > 0])
    
    # FTP
    ftp = latest.get('icu_ftp', 280)
    weight = latest.get('icu_weight', 65) or 65
    
    result = {
        'date': latest.get('start_date_local', 'N/A')[:10],
        'ctl': round(ctl, 1),
        'atl': round(atl, 1),
        'tsb': round(tsb, 1),
        'status': status,
        'description': desc,
        'ftp': ftp,
        'ftp_kg': round(ftp / weight, 2),
        'week': {
            'count': week_count,
            'time_min': round(week_time, 0),
            'load': round(week_load, 0)
        }
    }
    
    return result

def analyze_latestRide():
    """Analyze latest ride"""
    data = load_data()
    
    # Find latest ride with intervals
    latest = None
    for a in data:
        if a.get('source') == 'OAUTH_CLIENT' and a.get('icu_intervals'):
            latest = a
            break
    
    if not latest:
        return None
    
    intervals = latest.get('icu_intervals', [])
    work_ints = [i for i in intervals if i.get('type') == 'WORK']
    recovery_ints = [i for i in intervals if i.get('type') == 'RECOVERY']
    
    # Power zones
    zones = {z['id']: z['secs'] for z in latest.get('icu_zone_times', [])}
    
    # Heart rate zones
    hr_zones = latest.get('icu_hr_zone_times', [])
    
    # Analyze WORK intervals
    work_details = []
    ftp = latest.get('icu_ftp', 280)
    zone_names = {1:'Z1',2:'Z2',3:'Z3(SS)',4:'Z4',5:'Z5',6:'Z6',7:'Z7'}
    
    for w in work_ints:
        duration = w.get('moving_time', 0)
        avg_w = w.get('average_watts', 0)
        max_w = w.get('max_watts', 0)
        avg_hr = w.get('average_heartrate', 0)
        zone = w.get('zone', 0)
        
        work_details.append({
            'duration_sec': duration,
            'avg_watts': avg_w,
            'max_watts': max_w,
            'avg_heartrate': avg_hr,
            'zone': zone,
            'zone_name': zone_names.get(zone, 'Z{}'.format(zone)),
            'ftp_pct': round(avg_w / ftp * 100, 0) if ftp else 0
        })
    
    result = {
        'name': latest.get('name'),
        'date': latest.get('start_date_local', 'N/A')[:10],
        'duration_min': round(latest.get('moving_time', 0) / 60, 0),
        'distance_km': round(latest.get('distance', 0) / 1000, 1),
        'avg_watts': latest.get('icu_weighted_avg_watts', 0),
        'avg_heartrate': latest.get('average_heartrate', 0),
        'max_heartrate': latest.get('max_heartrate', 0),
        'training_load': latest.get('icu_training_load', 0),
        'intensity': latest.get('icu_intensity', 0),
        'decoupling': latest.get('decoupling'),
        'efficiency_factor': latest.get('icu_efficiency_factor', 0),
        'intervals': {
            'total': len(intervals),
            'work': len(work_ints),
            'recovery': len(recovery_ints)
        },
        'work_details': work_details,
        'power_zones': {z: round(zones.get(z, 0)/60, 1) for z in ['Z1','Z2','Z3','Z4','Z5','Z6','Z7','SS']},
        'heartrate_zones': { 'Z{}'.format(i+1): round(hr_zones[i]/60, 1) if i < len(hr_zones) else 0 for i in range(7)}
    }
    
    return result

def analyze_trend():
    """Analyze 30-day trend"""
    data = load_data()
    recent = [a for a in data if a.get('icu_training_load') and a.get('icu_training_load', 0) > 0][:30]
    
    weeks = {}
    for a in recent:
        date = a.get('start_date_local', '')[:10]
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
            week = dt.isocalendar()[1]
            if week not in weeks:
                weeks[week] = {'count': 0, 'time_min': 0, 'load': 0}
            weeks[week]['count'] += 1
            weeks[week]['time_min'] += a.get('moving_time', 0) / 60
            weeks[week]['load'] += a.get('icu_training_load', 0)
        except:
            pass
    
    week_nums = sorted(weeks.keys(), reverse=True)[:4]
    labels = ['This week', 'Last week', '2 weeks ago', '3 weeks ago']
    
    results = []
    for i, w in enumerate(week_nums):
        results.append({
            'period': labels[i] if i < len(labels) else '{} weeks ago'.format(4-i),
            'count': weeks[w]['count'],
            'time_min': round(weeks[w]['time_min'], 0),
            'load': round(weeks[w]['load'], 0)
        })
    
    return results

def generate_plan(tsb, current_power=None):
    """Generate training plan based on TSB and current power ability
    
    Args:
        tsb: Training Stress Balance (CTL - ATL)
        current_power: Optional current sustainable power (e.g., 245w). 
                       If provided, adjusts zones based on actual ability.
    """
    
    # Adjust FTP based on current power ability
    effective_ftp = current_power if current_power else 280
    
    # Calculate adjusted power targets
    ss_min = int(effective_ftp * 0.84)
    ss_max = int(effective_ftp * 0.97)
    thresh_min = int(effective_ftp * 0.91)
    thresh_max = int(effective_ftp * 1.05)
    vo2min = int(effective_ftp * 1.06)
    
    def zone_str(min_w, max_w=None):
        if max_w:
            return f"@{min_w}-{max_w}w"
        return f"@{min_w}w"
    
    if tsb < -20:
        return {
            'phase': 'Recovery Week',
            'tsb_target': '+5 ~ +10',
            'focus': 'Complete rest or easy riding',
            'description': 'Body is fatigued, needs full recovery',
            'schedule': [
                {'day': 'Mon', 'training': 'Rest', 'target': 'Recovery'},
                {'day': 'Tue', 'training': '30min Z1', 'target': 'Active recovery'},
                {'day': 'Wed', 'training': 'Rest', 'target': '-'},
                {'day': 'Thu', 'training': '45min Z2', 'target': 'Aerobic'},
                {'day': 'Fri', 'training': 'Rest', 'target': '-'},
                {'day': 'Sat', 'training': '60min Z2', 'target': 'Endurance'},
                {'day': 'Sun', 'training': 'Rest', 'target': '-'}
            ],
            'weekly_load_target': '200-250'
        }
    elif tsb < 0:
        return {
            'phase': 'Build Week',
            'tsb_target': '+5 ~ +10',
            'focus': 'Increase aerobic base, reduce high intensity',
            'description': f'Balanced training (effective FTP: {effective_ftp}w)',
            'schedule': [
                {'day': 'Mon', 'training': 'Rest', 'target': '-'},
                {'day': 'Tue', 'training': f'4x8min@{thresh_min}', 'target': 'Threshold'},
                {'day': 'Wed', 'training': '60min Z2', 'target': 'Aerobic'},
                {'day': 'Thu', 'training': 'Rest', 'target': '-'},
                {'day': 'Fri', 'training': f'3x15min {ss_min}-{ss_max}w', 'target': 'Sweet Spot'},
                {'day': 'Sat', 'training': f'90min Z2 + 4x1min@{int(effective_ftp*1.1)}', 'target': 'Endurance + Sprints'},
                {'day': 'Sun', 'training': 'Rest', 'target': '-'}
            ],
            'weekly_load_target': '350-400',
            'effective_ftp': effective_ftp,
            'zones': {'ss': f'{ss_min}-{ss_max}w', 'threshold': f'{thresh_min}-{thresh_max}w', 'vo2max': f'{vo2min}+w'}
        }
    elif tsb < 10:
        return {
            'phase': 'Build Week',
            'tsb_target': '+10 ~ +15',
            'focus': 'Increase threshold and VO2max',
            'description': 'Form improving, can add intensity',
            'schedule': [
                {'day': 'Mon', 'training': 'Rest', 'target': '-'},
                {'day': 'Tue', 'training': '6x5min@290', 'target': 'VO2max'},
                {'day': 'Wed', 'training': '45min Z2', 'target': 'Recovery'},
                {'day': 'Thu', 'training': '2x20min@285', 'target': 'Threshold'},
                {'day': 'Fri', 'training': 'Rest', 'target': '-'},
                {'day': 'Sat', 'training': '100km Outdoor', 'target': 'Endurance'},
                {'day': 'Sun', 'training': 'Rest', 'target': '-'}
            ],
            'weekly_load_target': '400-450'
        }
    else:
        return {
            'phase': 'Peak Week',
            'tsb_target': '>+15',
            'focus': 'Race or FTP test',
            'description': 'Peak condition, suitable for racing or testing',
            'schedule': [
                {'day': 'Mon', 'training': 'Rest', 'target': '-'},
                {'day': 'Tue', 'training': 'FTP Test', 'target': 'Peak'},
                {'day': 'Wed', 'training': '30min Z1', 'target': 'Recovery'},
                {'day': 'Thu', 'training': '2x10min@280', 'target': 'Maintenance'},
                {'day': 'Fri', 'training': 'Rest', 'target': '-'},
                {'day': 'Sat', 'training': 'Race/Test', 'target': 'Peak'},
                {'day': 'Sun', 'training': 'Rest', 'target': '-'}
            ],
            'weekly_load_target': '300-350'
        }

def full_report():
    """Generate full report"""
    status = analyze_status()
    ride = analyze_latestRide()
    trend = analyze_trend()
    plan = generate_plan(status['tsb'])
    
    print("="*70)
    print("CARNO - Full Training Analysis Report")
    print("="*70)
    
    # 1. Body status
    print("\n[1] Current Body Status ({})".format(status['date']))
    print("  CTL: {} | ATL: {} | TSB: {}".format(status['ctl'], status['atl'], status['tsb']))
    print("  Status: {}".format(status['status']))
    print("  FTP: {}W | FTP/kg: {}".format(status['ftp'], status['ftp_kg']))
    print("  Last 7 days: {} sessions | {}min | load {}".format(
        status['week']['count'], status['week']['time_min'], status['week']['load']))
    
    # 2. Latest ride
    if ride:
        print("\n[2] Latest Ride ({})".format(ride['date']))
        print("  {}".format(ride['name']))
        print("  {}min | {}km | load {}".format(ride['duration_min'], ride['distance_km'], ride['training_load']))
        print("  Power: {}w | HR: {}bpm".format(ride['avg_watts'], ride['avg_heartrate']))
        print("  Decoupling: {}% | Efficiency: {}".format(ride['decoupling'], ride['efficiency_factor']))
        
        if ride['work_details']:
            print("  Intervals: {} sets".format(len(ride['work_details'])))
            for w in ride['work_details'][:3]:
                print("    {}s | {}w({}%) | {}".format(
                    w['duration_sec'], w['avg_watts'], w['ftp_pct'], w['zone_name']))
    
    # 4. Trend
    if trend:
        print("\n[4] 30-Day Trend")
        for t in trend:
            print("  {}: {} sessions | {}min | load {}".format(
                t['period'], t['count'], t['time_min'], t['load']))
    
    # 5. Plan
    print("\n[5] Training Plan Suggestion")
    print("  Phase: {}".format(plan['phase']))
    print("  Target TSB: {}".format(plan['tsb_target']))
    print("  Focus: {}".format(plan['focus']))
    print("  Weekly load target: {}".format(plan['weekly_load_target']))
    print("\n  Schedule:")
    for s in plan['schedule']:
        print("    {}: {} ({})".format(s['day'], s['training'], s['target']))
    
    print()
    return {
        'status': status,
        'latest_ride': ride,
        'trend': trend,
        'plan': plan
    }

def analyze_form_trend():
    """Analyze form trend - compare historical peak vs current performance
    
    Key insight: When same HR produces lower power, form has declined.
    This usually happens after period of low training volume.
    
    Analysis approach:
    1. Find high-intensity intervals (>=9min work, Z3+ or HR>=150)
    2. Compare power at similar HR ranges over time
    3. Calculate degradation percentage
    """
    data = load_data()
    
    # Find high-intensity intervals (>=9min work, Z3+ or HR>=150)
    intervals_data = []
    for a in data:
        intervals = a.get('icu_intervals') or []
        for i in intervals:
            if i.get('type') == 'WORK' and i.get('moving_time', 0) >= 540:  # >=9min
                hr = i.get('average_heartrate', 0)
                zone = i.get('zone', 0)
                if zone >= 3 or hr >= 150:  # Z3+ (SS) or high HR
                    intervals_data.append({
                        'date': a.get('start_date_local', '')[:10],
                        'name': a.get('name', ''),
                        'duration_min': round(i.get('moving_time', 0) / 60, 1),
                        'watts': i.get('average_watts', 0),
                        'hr': hr,
                        'zone': zone
                    })
    
    # Sort by date (ascending - oldest first for comparison)
    intervals_data.sort(key=lambda x: x['date'])
    
    # Group by HR range (160±5) to compare same effort level
    hr_160_group = [x for x in intervals_data if 155 <= x['hr'] <= 165]
    
    result = {
        'hr_160_comparison': [],
        'peak_vs_current': None,
        'degradation_pct': None,
        'reason': None
    }
    
    if hr_160_group:
        # Take last 15 entries to capture more history
        recent = hr_160_group[-15:]
        recent.sort(key=lambda x: x['date'])  # Sort oldest -> newest
        
        for r in recent:
            result['hr_160_comparison'].append({
                'date': r['date'],
                'name': r['name'][:30],
                'duration_min': r['duration_min'],
                'watts': r['watts'],
                'hr': r['hr']
            })
        
        # Compare peak (highest watts in history) vs current (most recent)
        if len(recent) >= 2:
            # Peak = highest watts in the HR160 range (best ever)
            peak = max(recent, key=lambda x: x['watts'] or 0)
            # Current = most recent entry
            current = recent[-1]
            
            if peak['watts'] and current['watts']:
                degradation = peak['watts'] - current['watts']
                degradation_pct = round(degradation / peak['watts'] * 100, 1)
                
                result['peak_vs_current'] = {
                    'peak_date': peak['date'],
                    'peak_watts': peak['watts'],
                    'peak_duration': peak['duration_min'],
                    'current_date': current['date'],
                    'current_watts': current['watts'],
                    'current_duration': current['duration_min'],
                    'degradation_watts': degradation,
                    'degradation_pct': degradation_pct
                }
                
                # Auto-generate reason
                if degradation_pct >= 10:
                    result['reason'] = "Significant form loss - likely due to reduced training volume in Jan-Feb"
                elif degradation_pct >= 5:
                    result['reason'] = "Moderate form loss - maintaining fitness with current training"
                else:
                    result['reason'] = "Form is stable"
    
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cycling training analysis')
    parser.add_argument('--status', action='store_true', help='Body status')
    parser.add_argument('--latest', action='store_true', help='Latest ride')
    parser.add_argument('--trend', action='store_true', help='Trend analysis')
    parser.add_argument('--plan', action='store_true', help='Training plan')
    parser.add_argument('--form', action='store_true', help='Form trend (peak vs current)')
    parser.add_argument('--power', type=int, help='Current power ability for plan adjustment')
    parser.add_argument('--full', action='store_true', help='Full report')
    
    args = parser.parse_args()
    
    if args.status:
        s = analyze_status()
        print(json.dumps(s, indent=2, ensure_ascii=False))
    elif args.latest:
        r = analyze_latestRide()
        print(json.dumps(r, indent=2, ensure_ascii=False))
    elif args.trend:
        t = analyze_trend()
        print(json.dumps(t, indent=2, ensure_ascii=False))
    elif args.form:
        f = analyze_form_trend()
        print(json.dumps(f, indent=2, ensure_ascii=False))
    elif args.plan:
        s = analyze_status()
        p = generate_plan(s['tsb'], args.power)
        print(json.dumps(p, indent=2, ensure_ascii=False))
    elif args.full:
        full_report()
    else:
        full_report()

if __name__ == "__main__":
    main()
