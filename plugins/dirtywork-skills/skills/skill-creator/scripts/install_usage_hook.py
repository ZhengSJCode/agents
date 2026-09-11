#!/usr/bin/env python3
"""
Skill Usage Hook Installer

Installs a PreToolUse hook to track skill invocations for analytics.

Usage:
    install_usage_hook.py [options]

Options:
    --uninstall    Remove the usage tracking hook
    --status       Check if hook is installed
    --log-path     Custom log path (default: ~/.claude/skill-usage.log)

Exit codes:
    0: Success
    1: Error (permissions, file not found, etc.)
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def get_settings_path():
    """Get the path to Claude Code settings.json."""
    home = Path.home()
    return home / ".claude" / "settings.json"


def get_hook_path():
    """Get the path to the skill usage hook script."""
    home = Path.home()
    return home / ".claude" / "hooks" / "log-skill.sh"


def get_log_path():
    """Get the default log path."""
    home = Path.home()
    return home / ".claude" / "skill-usage.log"


def install_hook(log_path=None):
    """Install the usage tracking hook."""
    settings_path = get_settings_path()
    hook_path = get_hook_path()

    if log_path is None:
        log_path = get_log_path()
    else:
        log_path = Path(log_path)

    # Ensure hooks directory exists
    hook_path.parent.mkdir(parents=True, exist_ok=True)

    # Create the hook script
    hook_content = f'''#!/bin/bash
# Skill Usage Tracking Hook
# Logs skill invocations for analytics

payload=$(cat)
skill=$(jq -r '.tool_input.skill // empty' <<< "$payload")
args=$(jq -r '.tool_input.args // ""' <<< "$payload")

if [[ -n "$skill" ]]; then
    echo "$(date -u +%s) $USER $skill $args" >> {log_path}
fi

# Return original payload for other hooks
echo "$payload"
'''

    # Write hook script
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)

    # Load or create settings.json
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in {settings_path}")
            return False
    else:
        settings = {}

    # Add PreToolUse hook
    if "hooks" not in settings:
        settings["hooks"] = {}

    if "preToolUse" not in settings["hooks"]:
        settings["hooks"]["preToolUse"] = []

    # Add our hook if not already present
    hook_entry = str(hook_path)
    if hook_entry not in settings["hooks"]["preToolUse"]:
        settings["hooks"]["preToolUse"].append(hook_entry)

    # Write updated settings
    settings_path.write_text(json.dumps(settings, indent=2))

    # Create log file if it doesn't exist
    if not log_path.exists():
        log_path.touch()
        log_path.chmod(0o600)

    return True


def uninstall_hook():
    """Remove the usage tracking hook."""
    settings_path = get_settings_path()
    hook_path = get_hook_path()

    if not settings_path.exists():
        print("⚠️  Settings file not found, nothing to uninstall")
        return True

    # Load settings
    try:
        settings = json.loads(settings_path.read_text())
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {settings_path}")
        return False

    # Remove hook from settings
    if "hooks" in settings and "preToolUse" in settings["hooks"]:
        hook_entry = str(hook_path)
        settings["hooks"]["preToolUse"] = [
            h for h in settings["hooks"]["preToolUse"] if h != hook_entry
        ]

    # Write updated settings
    settings_path.write_text(json.dumps(settings, indent=2))

    # Remove hook script
    if hook_path.exists():
        hook_path.unlink()

    return True


def check_status():
    """Check if the hook is installed."""
    settings_path = get_settings_path()
    hook_path = get_hook_path()
    log_path = get_log_path()

    hook_installed = False
    in_settings = False

    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
            hook_entry = str(hook_path)
            if "hooks" in settings and "preToolUse" in settings["hooks"]:
                in_settings = hook_entry in settings["hooks"]["preToolUse"]
        except json.JSONDecodeError:
            pass

    hook_installed = hook_path.exists() and in_settings

    print("🔍 Skill Usage Hook Status")
    print()

    if hook_installed:
        print("✅ Hook Status: INSTALLED")
        print(f"   Hook script: {hook_path}")
        print(f"   Registered in settings.json: {in_settings}")

        if log_path.exists():
            # Count entries
            try:
                line_count = len(log_path.read_text().strip().split('\n')) if log_path.read_text().strip() else 0
                print(f"   Log file: {log_path}")
                print(f"   Log entries: {line_count}")
            except:
                print(f"   Log file: {log_path}")
                print(f"   Log entries: (unable to read)")
        else:
            print(f"   Log file: {log_path} (not yet created)")
    else:
        print("❌ Hook Status: NOT INSTALLED")
        if hook_path.exists():
            print(f"   ⚠️  Hook script exists but not in settings: {hook_path}")
        else:
            print(f"   Hook script not found: {hook_path}")

    return hook_installed


def main():
    uninstall = False
    status_only = False
    log_path = None

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--uninstall':
            uninstall = True
            i += 1
        elif sys.argv[i] == '--status':
            status_only = True
            i += 1
        elif sys.argv[i] == '--log-path' and i + 1 < len(sys.argv):
            log_path = sys.argv[i + 1]
            i += 2
        else:
            print(f"❌ Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    if status_only:
        is_installed = check_status()
        sys.exit(0 if is_installed else 1)

    if uninstall:
        print("🔧 Uninstalling skill usage hook...")
        if uninstall_hook():
            print("✅ Hook uninstalled successfully")
            sys.exit(0)
        else:
            print("❌ Failed to uninstall hook")
            sys.exit(1)

    # Install hook
    print("🔧 Installing skill usage hook...")
    if install_hook(log_path):
        print("✅ Hook installed successfully")
        print()
        print("   The hook will log skill invocations to:")
        print(f"   {log_path or get_log_path()}")
        print()
        print("   To analyze usage, run:")
        print("   scripts/analyze_usage.py")
        sys.exit(0)
    else:
        print("❌ Failed to install hook")
        sys.exit(1)


if __name__ == "__main__":
    main()
