#!/usr/bin/env python3
"""
Marketplace.json Validator

Validates marketplace.json schema against Claude Code marketplace specifications.

Usage:
    validate_marketplace.py <path-to-marketplace.json>
    validate_marketplace.py --help

Exit codes:
    0: Validation passed
    1: Critical errors (missing required fields, invalid schema)
    2: Warnings present
"""

import re
import sys
import json
from pathlib import Path


def validate_marketplace_json(marketplace_path):
    """Validate marketplace.json against schema."""
    try:
        with open(marketplace_path, 'r') as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"], [], []
    except FileNotFoundError:
        return ["File not found"], [], []

    errors = []
    warnings = []
    suggestions = []

    # Validate required top-level fields
    required_fields = ['name', 'owner', 'plugins']
    for field in required_fields:
        if field not in marketplace:
            errors.append(f"Missing required field: {field}")

    # Validate name
    if 'name' in marketplace:
        name = marketplace['name']
        if not name:
            errors.append("Field 'name' is empty")
        elif not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Field 'name' must be kebab-case: {name}")

    # Validate owner
    if 'owner' in marketplace:
        owner = marketplace['owner']
        if not isinstance(owner, dict):
            errors.append("Field 'owner' must be an object")
        else:
            if 'name' not in owner:
                errors.append("Field 'owner.name' is required")
            elif not owner['name']:
                errors.append("Field 'owner.name' is empty")

    # Validate plugins array
    if 'plugins' in marketplace:
        plugins = marketplace['plugins']
        if not isinstance(plugins, list):
            errors.append("Field 'plugins' must be an array")
        elif len(plugins) == 0:
            errors.append("Field 'plugins' array is empty")
        else:
            for i, plugin in enumerate(plugins):
                plugin_prefix = f"plugins[{i}]"

                # Required plugin fields
                if 'name' not in plugin:
                    errors.append(f"{plugin_prefix}: Missing required field 'name'")
                else:
                    plugin_name = plugin['name']
                    if not plugin_name:
                        errors.append(f"{plugin_prefix}: Field 'name' is empty")

                # Validate source
                if 'source' not in plugin:
                    errors.append(f"{plugin_prefix}: Missing required field 'source'")
                else:
                    source = plugin['source']
                    if not isinstance(source, dict):
                        errors.append(f"{plugin_prefix}: Field 'source' must be an object")
                    else:
                        source_type = source.get('source')

                        # Validate source type
                        valid_types = ['relative', 'github', 'url', 'git-subdir', 'npm']
                        if source_type not in valid_types:
                            errors.append(f"{plugin_prefix}: Invalid source type '{source_type}'. Must be one of: {', '.join(valid_types)}")

                        # Type-specific validation
                        if source_type == 'relative':
                            if 'path' not in source:
                                errors.append(f"{plugin_prefix}: 'path' required for relative source")
                            elif not source['path'].startswith('./'):
                                errors.append(f"{plugin_prefix}: 'path' must start with './'")

                        elif source_type == 'github':
                            if 'repo' not in source:
                                errors.append(f"{plugin_prefix}: 'repo' required for github source")

                        elif source_type == 'url':
                            if 'url' not in source:
                                errors.append(f"{plugin_prefix}: 'url' required for url source")

                        elif source_type == 'git-subdir':
                            if 'url' not in source:
                                errors.append(f"{plugin_prefix}: 'url' required for git-subdir source")
                            if 'path' not in source:
                                errors.append(f"{plugin_prefix}: 'path' required for git-subdir source")

                        elif source_type == 'npm':
                            if 'package' not in source:
                                errors.append(f"{plugin_prefix}: 'package' required for npm source")

                # Optional fields
                if 'version' in plugin:
                    version = plugin['version']
                    # Basic semver check
                    if not re.match(r'^\d+\.\d+\.\d+', str(version)):
                        warnings.append(f"{plugin_prefix}: 'version' should follow semver (e.g., 1.0.0): {version}")

                if 'keywords' in plugin:
                    keywords = plugin['keywords']
                    if not isinstance(keywords, list):
                        errors.append(f"{plugin_prefix}: 'keywords' must be an array")

                if 'strict' in plugin and plugin['strict'] is not False:
                    # strict mode is set
                    warnings.append(f"{plugin_prefix}: 'strict: true' means marketplace entry overrides plugin.json. Ensure this is intended.")

    # Check for duplicates in plugin names
    if 'plugins' in marketplace:
        plugin_names = [p.get('name') for p in marketplace['plugins'] if 'name' in p]
        if len(plugin_names) != len(set(plugin_names)):
            errors.append("Duplicate plugin names found. Each plugin must have a unique name.")

    return errors, warnings, suggestions


def print_results(errors, warnings, suggestions):
    """Print validation results."""
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
        print("Usage: validate_marketplace.py <path-to-marketplace.json>")
        print("\nValidates marketplace.json against Claude Code marketplace schema.")
        print("\nExit codes:")
        print("  0: Validation passed")
        print("  1: Critical errors")
        print("  2: Warnings present")
        sys.exit(1)

    marketplace_path = Path(sys.argv[1])

    if not marketplace_path.exists():
        print(f"❌ Error: File not found: {marketplace_path}")
        sys.exit(1)

    print(f"🔍 Validating: {marketplace_path}")
    print()

    errors, warnings, suggestions = validate_marketplace_json(marketplace_path)
    print_results(errors, warnings, suggestions)

    if errors:
        print("❌ Validation failed with critical errors")
        sys.exit(1)
    elif warnings:
        print("⚠️  Validation passed with warnings")
        sys.exit(2)
    else:
        print("✅ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
