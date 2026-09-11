#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python utils/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python utils/package_skill.py skills/public/my-skill
    python utils/package_skill.py skills/public/my-skill ./dist
"""

import fnmatch
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill

# Patterns to exclude when packaging skills.
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
# Directories excluded only at the skill root (not when nested deeper).
ROOT_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    # rel_path is relative to skill_path.parent, so parts[0] is the skill
    # folder name and parts[1] (if present) is the first subdir.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def generate_marketplace_for_skill(skill_path, owner=None):
    """
    Generate marketplace.json for a skill before packaging.

    Args:
        skill_path: Path to the skill folder
        owner: Optional owner name (defaults to git config or 'your-username')

    Returns:
        True if successful, False otherwise
    """
    generate_script = Path(__file__).parent / 'generate_marketplace.py'

    if not generate_script.exists():
        print("  ⚠️  generate_marketplace.py not found, skipping marketplace.json generation")
        return False

    # Build command
    cmd = [sys.executable, str(generate_script), str(skill_path)]
    if owner:
        cmd.extend(['--owner', owner])

    # Run generate_marketplace.py
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # marketplace.json was created
            marketplace_path = skill_path / 'marketplace.json'
            if marketplace_path.exists():
                print(f"  Generated: marketplace.json")
                return True
        else:
            print(f"  ⚠️  marketplace.json generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ⚠️  marketplace.json generation error: {e}")
        return False

    return False
    """Check if a path should be excluded from packaging."""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    # rel_path is relative to skill_path.parent, so parts[0] is the skill
    # folder name and parts[1] (if present) is the first subdir.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_path, output_dir=None, include_marketplace=False, owner=None):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)
        include_marketplace: Whether to generate marketplace.json before packaging
        owner: Owner name for marketplace.json

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Generate marketplace.json if requested
    if include_marketplace:
        print("📦 Generating marketplace.json...")
        generate_marketplace_for_skill(skill_path, owner)
        print()

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory, excluding build artifacts
            for file_path in skill_path.rglob('*'):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    print(f"  Skipped: {arcname}")
                    continue
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python utils/package_skill.py <path/to/skill-folder> [output-directory] [options]")
        print("\nOptions:")
        print("  --include-marketplace    Generate marketplace.json before packaging")
        print("  --owner <username>       Owner name for marketplace.json")
        print("\nExample:")
        print("  python utils/package_skill.py skills/public/my-skill")
        print("  python utils/package_skill.py skills/public/my-skill ./dist")
        print("  python utils/package_skill.py skills/public/my-skill --include-marketplace")
        print("  python utils/package_skill.py skills/public/my-skill --include-marketplace --owner username")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = None
    include_marketplace = False
    owner = None

    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--include-marketplace':
            include_marketplace = True
            i += 1
        elif sys.argv[i] == '--owner' and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
            i += 2
        elif not sys.argv[i].startswith('-'):
            # Positional argument for output_dir
            output_dir = sys.argv[i]
            i += 1
        else:
            print(f"❌ Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    if include_marketplace:
        print(f"   Include marketplace.json: yes")
    if owner:
        print(f"   Owner: {owner}")
    print()

    result = package_skill(skill_path, output_dir, include_marketplace, owner)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
