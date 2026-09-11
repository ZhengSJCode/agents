#!/usr/bin/env python3
"""
Frontmatter Validation Script

Validates SKILL.md frontmatter against Claude Code skill best practices.

Usage:
    validate_frontmatter.py <skill-path>
    validate_frontmatter.py --help

Examples:
    validate_frontmatter.py skills/my-skill
    validate_frontmatter.py .  # Validate current directory

Exit codes:
    0: All validations pass
    1: Critical errors (missing required fields)
    2: Warnings present
    3: Suggestions only
"""

import sys
import re
from pathlib import Path
import yaml


# SPDX license identifiers (subset of common licenses)
SPDX_LICENSES = {
    "Apache-2.0", "MIT", "GPL-3.0", "BSD-3-Clause", "BSD-2-Clause",
    "ISC", "MPL-2.0", "CDDL-1.0", "EPL-2.0", "LGPL-3.0", "LGPL-2.1",
    "AGPL-3.0", "Unlicense", "0BSD", "CC-BY-4.0", "CC-BY-SA-4.0",
    "CC0-1.0", "Proprietary"
}

# Common tool names in Claude Code
COMMON_TOOLS = [
    "Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch",
    "LSP", "McpServers", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion",
    "Agent", "Skill", "NotebookEdit", "CronCreate", "CronList", "CronDelete",
    "Present", "ExitPlanMode", "EnterWorktree", "ExitWorktree"
]


def parse_frontmatter(skill_md_path):
    """Parse YAML frontmatter from SKILL.md."""
    content = skill_md_path.read_text()

    # Check for YAML frontmatter delimiter
    if not content.startswith('---'):
        return None, "No YAML frontmatter found (missing opening ---)"

    # Extract frontmatter between --- delimiters
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, "No YAML frontmatter found (missing closing ---)"

    frontmatter_yaml = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_yaml)
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {e}"


def validate_required_fields(frontmatter):
    """Validate required fields are present."""
    errors = []
    warnings = []

    # Required fields
    if 'name' not in frontmatter:
        errors.append("Missing required field: name")
    elif not frontmatter['name']:
        errors.append("Field 'name' is empty")
    elif not re.match(r'^[a-z0-9-]+$', frontmatter['name']):
        errors.append(f"Field 'name' must be kebab-case (lowercase, digits, hyphens): {frontmatter['name']}")

    if 'description' not in frontmatter:
        errors.append("Missing required field: description")
    elif not frontmatter['description']:
        errors.append("Field 'description' is empty")
    elif len(frontmatter['description']) < 20:
        warnings.append("Field 'description' is too short (< 20 chars) for effective triggering")

    return errors, warnings


def validate_version(frontmatter):
    """Validate version field (semver)."""
    errors = []
    warnings = []

    if 'version' in frontmatter:
        version = str(frontmatter['version'])
        # Semver regex: major.minor.patch with optional -prerelease and +build
        semver_pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?$'
        if not re.match(semver_pattern, version):
            errors.append(f"Field 'version' must be semantic versioning (e.g., 1.0.0): {version}")
    else:
        warnings.append("Missing 'version' field (recommended for tracking changes)")

    return errors, warnings


def validate_license(frontmatter):
    """Validate license field (SPDX)."""
    errors = []
    warnings = []

    if 'license' in frontmatter:
        license_str = str(frontmatter['license'])
        if license_str not in SPDX_LICENSES:
            warnings.append(f"Field 'license' should be SPDX identifier. Common: Apache-2.0, MIT, GPL-3.0. Got: {license_str}")
    else:
        warnings.append("Missing 'license' field (recommended: Apache-2.0)")

    return errors, warnings


def validate_allowed_tools(frontmatter):
    """Validate allowed-tools field."""
    errors = []
    warnings = []

    if 'allowed-tools' in frontmatter:
        allowed_tools = frontmatter['allowed-tools']
        if not isinstance(allowed_tools, list):
            errors.append("Field 'allowed-tools' must be an array")
        else:
            for tool in allowed_tools:
                if tool not in COMMON_TOOLS:
                    warnings.append(f"Tool '{tool}' in allowed-tools not recognized (may be valid)")

    return errors, warnings


def validate_metadata(frontmatter):
    """Validate metadata section."""
    errors = []
    warnings = []

    if 'metadata' not in frontmatter:
        warnings.append("Missing 'metadata' section (recommended for searchability)")
        return errors, warnings

    metadata = frontmatter['metadata']

    if not isinstance(metadata, dict):
        errors.append("Field 'metadata' must be an object/dictionary")
        return errors, warnings

    # Check for recommended metadata fields
    if 'tags' in metadata:
        tags = metadata['tags']
        if not isinstance(tags, list):
            errors.append("Field 'metadata.tags' must be an array")
        elif len(tags) == 0:
            warnings.append("Field 'metadata.tags' is empty")
        else:
            for tag in tags:
                if not re.match(r'^[a-z0-9-]+$', str(tag)):
                    warnings.append(f"Tag '{tag}' should be kebab-case")
    else:
        warnings.append("Missing 'metadata.tags' field (recommended for discovery)")

    if 'triggers' in metadata:
        triggers = metadata['triggers']
        if not isinstance(triggers, list):
            errors.append("Field 'metadata.triggers' must be an array")
        elif len(triggers) == 0:
            warnings.append("Field 'metadata.triggers' is empty")
    else:
        warnings.append("Missing 'metadata.triggers' field (recommended for trigger precision)")

    if 'category' in metadata:
        category = metadata['category']
        if not category:
            warnings.append("Field 'metadata.category' is empty")

    if 'author' in metadata:
        author = metadata['author']
        if not author:
            warnings.append("Field 'metadata.author' is empty")

    return errors, warnings


def validate_description_quality(frontmatter):
    """Validate description quality for effective triggering."""
    warnings = []

    if 'description' not in frontmatter:
        return warnings

    description = str(frontmatter['description'])

    # Check for common description issues
    if len(description) < 50:
        warnings.append("Description is short (< 50 chars). Include more context for better triggering.")

    if len(description) > 500:
        warnings.append("Description is long (> 500 chars). Consider using progressive disclosure.")

    # Check for trigger phrases
    if " when " not in description.lower() and " use " not in description.lower():
        warnings.append("Description lacks 'when to use' context. Include trigger phrases.")

    return warnings


def print_results(errors, warnings, suggestions):
    """Print validation results with appropriate formatting."""
    if errors:
        print("❌ CRITICAL ERRORS:")
        for error in errors:
            print(f"   • {error}")
        print()

    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    if suggestions:
        print("💡 SUGGESTIONS:")
        for suggestion in suggestions:
            print(f"   • {suggestion}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_frontmatter.py <skill-path>")
        print("\nValidates SKILL.md frontmatter against best practices.")
        print("\nExit codes:")
        print("  0: All validations pass")
        print("  1: Critical errors (missing required fields)")
        print("  2: Warnings present")
        print("  3: Suggestions only")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found at {skill_md}")
        sys.exit(1)

    print(f"🔍 Validating: {skill_md}")
    print()

    # Parse frontmatter
    frontmatter, parse_error = parse_frontmatter(skill_md)
    if parse_error:
        print(f"❌ {parse_error}")
        sys.exit(1)

    # Run validations
    all_errors = []
    all_warnings = []
    all_suggestions = []

    # Required fields
    errors, warnings = validate_required_fields(frontmatter)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Version
    errors, warnings = validate_version(frontmatter)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # License
    errors, warnings = validate_license(frontmatter)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Allowed tools
    errors, warnings = validate_allowed_tools(frontmatter)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Metadata
    errors, warnings = validate_metadata(frontmatter)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Description quality
    warnings = validate_description_quality(frontmatter)
    all_warnings.extend(warnings)

    # Print results
    print_results(all_errors, all_warnings, all_suggestions)

    # Determine exit code
    if all_errors:
        print("❌ Validation failed with critical errors")
        sys.exit(1)
    elif all_warnings:
        print("⚠️  Validation passed with warnings")
        sys.exit(2)
    else:
        print("✅ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
