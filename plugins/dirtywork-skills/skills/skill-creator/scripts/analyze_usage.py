#!/usr/bin/env python3
"""
Skill Usage Analyzer

Analyzes skill usage logs to provide insights into skill utilization.

Usage:
    analyze_usage.py [options]

Options:
    --log-path <path>   Path to usage log file (default: ~/.claude/skill-usage.log)
    --top N             Show top N most used skills (default: 10)
    --since DATE        Filter logs since DATE (YYYY-MM-DD)
    --skill NAME        Show details for specific skill
    --daily             Show daily breakdown
    --json              Output as JSON

Exit codes:
    0: Success
    1: Error (file not found, invalid date, etc.)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter


def get_default_log_path():
    """Get the default log path."""
    return Path.home() / ".claude" / "skill-usage.log"


def parse_log_line(line):
    """
    Parse a log line.

    Expected format: TIMESTAMP USER SKILL ARGS
    Example: 1698765432 username my-skill --arg value
    """
    parts = line.strip().split()
    if len(parts) < 3:
        return None

    try:
        timestamp = int(parts[0])
        user = parts[1]
        skill = parts[2]
        args = ' '.join(parts[3:]) if len(parts) > 3 else ''

        return {
            'timestamp': timestamp,
            'user': user,
            'skill': skill,
            'args': args,
            'datetime': datetime.fromtimestamp(timestamp, tz=timezone.utc)
        }
    except (ValueError, IndexError):
        return None


def load_logs(log_path, since=None):
    """Load and parse log entries."""
    if not log_path.exists():
        return []

    entries = []
    with open(log_path, 'r') as f:
        for line in f:
            entry = parse_log_line(line)
            if entry:
                if since is None or entry['datetime'] >= since:
                    entries.append(entry)

    return entries


def analyze_usage(entries):
    """Perform basic analysis on log entries."""
    skill_counts = Counter(e['skill'] for e in entries)
    user_counts = Counter(e['user'] for e in entries)

    # Group by skill with first/last use
    skill_details = {}
    for entry in entries:
        skill = entry['skill']
        if skill not in skill_details:
            skill_details[skill] = {
                'count': 0,
                'first_use': entry['datetime'],
                'last_use': entry['datetime'],
                'users': set()
            }
        skill_details[skill]['count'] += 1
        if entry['datetime'] < skill_details[skill]['first_use']:
            skill_details[skill]['first_use'] = entry['datetime']
        if entry['datetime'] > skill_details[skill]['last_use']:
            skill_details[skill]['last_use'] = entry['datetime']
        skill_details[skill]['users'].add(entry['user'])

    # Convert sets to counts for JSON serialization
    for skill in skill_details:
        skill_details[skill]['users'] = len(skill_details[skill]['users'])

    return {
        'total_invocations': len(entries),
        'unique_skills': len(skill_counts),
        'unique_users': len(user_counts),
        'skill_counts': skill_counts,
        'skill_details': skill_details
    }


def daily_breakdown(entries):
    """Generate daily usage breakdown."""
    daily = defaultdict(lambda: {'count': 0, 'skills': Counter()})

    for entry in entries:
        date_key = entry['datetime'].strftime('%Y-%m-%d')
        daily[date_key]['count'] += 1
        daily[date_key]['skills'][entry['skill']] += 1

    # Convert to sorted list
    result = []
    for date in sorted(daily.keys()):
        result.append({
            'date': date,
            'count': daily[date]['count'],
            'top_skills': daily[date]['skills'].most_common(5)
        })

    return result


def skill_detail(entries, skill_name):
    """Show detailed information for a specific skill."""
    skill_entries = [e for e in entries if e['skill'] == skill_name]

    if not skill_entries:
        return None

    # Find most common args
    args_counter = Counter(e['args'] for e in skill_entries if e['args'])

    return {
        'skill': skill_name,
        'total_uses': len(skill_entries),
        'first_use': min(e['datetime'] for e in skill_entries),
        'last_use': max(e['datetime'] for e in skill_entries),
        'unique_users': len(set(e['user'] for e in skill_entries)),
        'common_args': args_counter.most_common(10)
    }


def print_analysis(analysis, top_n=10):
    """Print analysis results."""
    print("=" * 60)
    print("SKILL USAGE ANALYSIS")
    print("=" * 60)
    print()

    print(f"Total Invocations: {analysis['total_invocations']}")
    print(f"Unique Skills: {analysis['unique_skills']}")
    print(f"Unique Users: {analysis['unique_users']}")
    print()

    print(f"TOP {top_n} MOST USED SKILLS:")
    print("-" * 40)
    for skill, count in analysis['skill_counts'].most_common(top_n):
        details = analysis['skill_details'][skill]
        first = details['first_use'].strftime('%Y-%m-%d')
        last = details['last_use'].strftime('%Y-%m-%d')
        users = details['users']
        print(f"  {count:4d}  {skill}")
        print(f"         Users: {users} | {first} → {last}")
    print()


def print_daily_breakdown(daily_data):
    """Print daily breakdown."""
    print("=" * 60)
    print("DAILY BREAKDOWN")
    print("=" * 60)
    print()

    for day in daily_data[-7:]:  # Show last 7 days
        print(f"{day['date']}: {day['count']} invocations")
        if day['top_skills']:
            print("  Top skills:")
            for skill, count in day['top_skills'][:3]:
                print(f"    {count:3d}  {skill}")
        print()


def print_skill_detail(detail):
    """Print detailed information for a skill."""
    print("=" * 60)
    print(f"SKILL DETAIL: {detail['skill']}")
    print("=" * 60)
    print()

    print(f"Total Uses: {detail['total_uses']}")
    print(f"Unique Users: {detail['unique_users']}")
    print(f"First Used: {detail['first_use'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Last Used: {detail['last_use'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()

    if detail['common_args']:
        print("Common Arguments:")
        for args, count in detail['common_args'][:5]:
            if args:
                print(f"  {count:3d}  {args}")
        print()


def main():
    log_path = None
    top_n = 10
    since_date = None
    skill_name = None
    daily = False
    output_json = False

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--log-path' and i + 1 < len(sys.argv):
            log_path = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--top' and i + 1 < len(sys.argv):
            top_n = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--since' and i + 1 < len(sys.argv):
            try:
                since_date = datetime.strptime(sys.argv[i + 1], '%Y-%m-%d')
            except ValueError:
                print(f"❌ Error: Invalid date format '{sys.argv[i + 1]}', use YYYY-MM-DD")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == '--skill' and i + 1 < len(sys.argv):
            skill_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--daily':
            daily = True
            i += 1
        elif sys.argv[i] == '--json':
            output_json = True
            i += 1
        else:
            print(f"❌ Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    if log_path is None:
        log_path = get_default_log_path()

    if not log_path.exists():
        print(f"❌ Error: Log file not found: {log_path}")
        print()
        print("To install the usage tracking hook, run:")
        print("  scripts/install_usage_hook.py")
        sys.exit(1)

    # Load logs
    entries = load_logs(log_path, since_date)

    if not entries:
        print("No log entries found")
        sys.exit(0)

    # Skill detail mode
    if skill_name:
        detail = skill_detail(entries, skill_name)
        if not detail:
            print(f"❌ Error: Skill '{skill_name}' not found in logs")
            sys.exit(1)

        if output_json:
            # Convert datetime to string for JSON
            detail['first_use'] = detail['first_use'].isoformat()
            detail['last_use'] = detail['last_use'].isoformat()
            print(json.dumps(detail, indent=2))
        else:
            print_skill_detail(detail)
        sys.exit(0)

    # Daily breakdown mode
    if daily:
        daily_data = daily_breakdown(entries)
        if output_json:
            print(json.dumps(daily_data, indent=2))
        else:
            print_daily_breakdown(daily_data)
        sys.exit(0)

    # Standard analysis mode
    analysis = analyze_usage(entries)

    if output_json:
        # Convert datetime objects to strings for JSON
        for skill, details in analysis['skill_details'].items():
            details['first_use'] = details['first_use'].isoformat()
            details['last_use'] = details['last_use'].isoformat()
        print(json.dumps(analysis, indent=2))
    else:
        print_analysis(analysis, top_n)

    sys.exit(0)


if __name__ == "__main__":
    main()
