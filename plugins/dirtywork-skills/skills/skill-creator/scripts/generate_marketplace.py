#!/usr/bin/env python3
"""
Marketplace.json Generator

Auto-generates marketplace.json from skill frontmatter.

Usage:
    generate_marketplace.py <skill-path> --owner <username>
    generate_marketplace.py <skill-path> --source-type <type>

Examples:
    generate_marketplace.py skills/my-skill --owner myusername
    generate_marketplace.py skills/my-skill --source-type github --repo owner/repo

Exit codes:
    0: Marketplace.json generated successfully
    1: Error (missing skill, invalid frontmatter, etc.)
"""

import sys
import re
import json
from pathlib import Path
import yaml


def get_git_owner():
    """Get git username from config."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def parse_skill_frontmatter(skill_path):
    """Parse frontmatter from SKILL.md."""
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return None, f"SKILL.md not found at {skill_path}"

    content = skill_md.read_text()

    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, "No YAML frontmatter found"

    frontmatter_yaml = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_yaml)
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {e}"


def detect_source_type(skill_path, source_type=None, repo=None, url=None):
    """Detect or determine the source type for the skill."""
    if source_type:
        return source_type

    # Auto-detect based on path
    skill_path_resolved = Path(skill_path).resolve()

    # Check if inside a git repo
    try:
        import subprocess
        git_root = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            cwd=skill_path_resolved,
            text=True
        )
        if git_root.returncode == 0:
            git_root_path = Path(git_root.stdout.strip())
            relative_path = skill_path_resolved.relative_to(git_root_path)

            # Check if this looks like a github repo
            try:
                remote_url = subprocess.run(
                    ['git', 'config', '--get', 'remote.origin.url'],
                    capture_output=True,
                    cwd=git_root_path,
                    text=True
                )
                if remote_url.returncode == 0:
                    url = remote_url.stdout.strip()
                    if 'github.com' in url:
                        # Extract owner/repo from URL
                        match = re.search(r'github.com[:/]([^/]+)/([^/.]+?)(\.git)?$', url)
                        if match:
                            return 'github', match.group(1), match.group(2), str(relative_path)
            except Exception:
                pass

            return 'relative', None, None, str(relative_path)
    except Exception:
        pass

    # Default to relative
    return 'relative', None, None, skill_path_resolved.name


def generate_marketplace_json(skill_path, owner=None, source_type=None, repo=None, url=None):
    """Generate marketplace.json from skill frontmatter."""
    skill_path = Path(skill_path).resolve()

    # Parse frontmatter
    frontmatter, error = parse_skill_frontmatter(skill_path)
    if error:
        return None, error

    # Extract fields
    name = frontmatter.get('name', skill_path.name)
    version = frontmatter.get('version', '1.0.0')
    description = frontmatter.get('description', 'A skill for Claude Code')
    author = frontmatter.get('metadata', {}).get('author', owner)

    # Get owner
    if not owner:
        owner = get_git_owner()
        if not owner:
            owner = author or "your-username"

    # Detect source type
    detected_type, detected_owner, detected_repo, detected_path = detect_source_type(
        skill_path, source_type, repo, url
    )

    # Build marketplace.json
    marketplace = {
        "name": name,
        "owner": {
            "name": owner
        },
        "plugins": [
            {
                "name": name,
                "source": {},
                "description": description,
                "version": version
            }
        ]
    }

    # Configure source based on type
    plugin_entry = marketplace["plugins"][0]

    if detected_type == 'relative':
        plugin_entry["source"] = {
            "source": "relative",
            "path": f"./{skill_path.name}"
        }
    elif detected_type == 'github':
        plugin_entry["source"] = {
            "source": "github",
            "repo": f"{detected_owner}/{detected_repo}" if detected_repo else f"{owner}/{name}"
        }
    elif detected_type == 'url':
        plugin_entry["source"] = {
            "source": "url",
            "url": url or f"https://github.com/{owner}/{name}"
        }
    elif detected_type == 'git-subdir':
        plugin_entry["source"] = {
            "source": "git-subdir",
            "url": url or f"https://github.com/{detected_owner}/{detected_repo}.git",
            "path": detected_path
        }
    elif detected_type == 'npm':
        package_name = frontmatter.get('npm_package_name', f"@{owner}/{name}")
        plugin_entry["source"] = {
            "source": "npm",
            "package": package_name
        }

    # Add keywords from metadata tags
    tags = frontmatter.get('metadata', {}).get('tags', [])
    if tags:
        plugin_entry["keywords"] = tags

    # Add category if present
    category = frontmatter.get('metadata', {}).get('category')
    if category:
        plugin_entry["category"] = category

    # Add strict mode (default false)
    plugin_entry["strict"] = False

    return marketplace, None


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_marketplace.py <skill-path> [options]")
        print("\nOptions:")
        print("  --owner <username>      Owner name (default: git config or 'your-username')")
        print("  --source-type <type>     Source type: relative, github, url, git-subdir, npm")
        print("  --repo <owner/repo>     GitHub repo (for github/git-subdir sources)")
        print("  --url <url>             Git URL (for url/git-subdir sources)")
        print("\nExamples:")
        print("  generate_marketplace.py skills/my-skill --owner myusername")
        print("  generate_marketplace.py skills/my-skill --source-type github --repo owner/repo")
        print("  generate_marketplace.py skills/my-skill --source-type npm")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    owner = None
    source_type = None
    repo = None
    url = None

    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--owner' and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--source-type' and i + 1 < len(sys.argv):
            source_type = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--repo' and i + 1 < len(sys.argv):
            repo = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--url' and i + 1 < len(sys.argv):
            url = sys.argv[i + 1]
            i += 2
        else:
            print(f"❌ Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    print(f"📦 Generating marketplace.json for: {skill_path}")
    print()

    # Generate marketplace.json
    marketplace, error = generate_marketplace_json(skill_path, owner, source_type, repo, url)

    if error:
        print(f"❌ Error: {error}")
        sys.exit(1)

    # Write marketplace.json
    output_path = skill_path / 'marketplace.json'
    try:
        with open(output_path, 'w') as f:
            json.dump(marketplace, f, indent=2)
        print(f"✅ Created {output_path}")
        print()
        print("Marketplace configuration:")
        print(f"  Name: {marketplace['name']}")
        print(f"  Owner: {marketplace['owner']['name']}")
        print(f"  Plugin: {marketplace['plugins'][0]['name']}")
        print(f"  Version: {marketplace['plugins'][0]['version']}")
        print(f"  Source type: {marketplace['plugins'][0]['source'].get('source', 'relative')}")
    except Exception as e:
        print(f"❌ Error writing marketplace.json: {e}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
