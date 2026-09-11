#!/usr/bin/env python3
"""
Master Skill Validator

Runs all validation checks on a skill, providing a comprehensive report.

Usage:
    validate_all.py <skill-path> [options]

Options:
    --test-description      Run description testing (requires prompts or evals)
    --prompts <file>        Text file with sample prompts for description testing
    --evals <path>          Path to evals.json for description testing
    --fix-frontend          Auto-fix simple frontmatter issues
    --strict                Treat warnings as errors
    --json                  Output as JSON

Exit codes:
    0: All checks pass
    1: Critical errors (missing required fields, invalid schema)
    2: Warnings present
    3: Suggestions only
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


def parse_frontmatter(skill_path):
    """Parse frontmatter from SKILL.md."""
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return None, f"SKILL.md not found at {skill_path}"

    content = skill_md.read_text()

    # Extract YAML frontmatter
    import re
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, "No YAML frontmatter found"

    frontmatter_yaml = match.group(1)

    try:
        import yaml
        frontmatter = yaml.safe_load(frontmatter_yaml)
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {e}"


def validate_frontmatter(frontmatter):
    """Validate skill frontmatter."""
    errors = []
    warnings = []
    suggestions = []

    # Required fields
    if 'name' not in frontmatter:
        errors.append("Missing required field: name")
    else:
        name = frontmatter['name']
        if not name:
            errors.append("Field 'name' is empty")
        elif not re.match(r'^[a-z0-9-]+$', name):
            warnings.append(f"Field 'name' should be kebab-case: {name}")

    if 'description' not in frontmatter:
        errors.append("Missing required field: description")
    else:
        description = frontmatter['description']
        if len(description) < 50:
            warnings.append("Description is too short (< 50 chars)")
        if 'when the user asks to' not in description.lower():
            suggestions.append("Add explicit trigger phrases: 'when the user asks to \"X\"'")

    # Optional but recommended fields
    if 'version' in frontmatter:
        version = frontmatter['version']
        if not re.match(r'^\d+\.\d+\.\d+', str(version)):
            warnings.append(f"Version should follow semver (e.g., 1.0.0): {version}")
    else:
        suggestions.append("Consider adding 'version' field (semver: 1.0.0)")

    if 'license' not in frontmatter:
        suggestions.append("Consider adding 'license' field (e.g., Apache-2.0)")

    # Metadata checks
    if 'metadata' in frontmatter:
        metadata = frontmatter['metadata']

        if 'author' in metadata and not metadata['author']:
            warnings.append("Field 'metadata.author' is empty")

        if 'tags' in metadata:
            tags = metadata['tags']
            if not isinstance(tags, list):
                errors.append("Field 'metadata.tags' must be an array")
            elif len(tags) == 0:
                warnings.append("Field 'metadata.tags' is empty")

        if 'triggers' in metadata:
            triggers = metadata['triggers']
            if not isinstance(triggers, list):
                errors.append("Field 'metadata.triggers' must be an array")
            elif len(triggers) == 0:
                suggestions.append("Field 'metadata.triggers' is empty")

    # Allowed tools validation
    if 'allowed-tools' in frontmatter:
        tools = frontmatter['allowed-tools']
        if not isinstance(tools, list):
            errors.append("Field 'allowed-tools' must be an array")

    return errors, warnings, suggestions


def validate_marketplace_json(skill_path):
    """Validate marketplace.json if it exists."""
    marketplace_path = skill_path / 'marketplace.json'

    if not marketplace_path.exists():
        return [], ["No marketplace.json found"], []

    try:
        with open(marketplace_path, 'r') as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in marketplace.json: {e}"], [], []

    errors = []
    warnings = []
    suggestions = []

    # Required top-level fields
    required_fields = ['name', 'owner', 'plugins']
    for field in required_fields:
        if field not in marketplace:
            errors.append(f"marketplace.json: Missing required field '{field}'")

    # Validate plugins
    if 'plugins' in marketplace:
        plugins = marketplace['plugins']
        if not isinstance(plugins, list):
            errors.append("marketplace.json: Field 'plugins' must be an array")
        elif len(plugins) == 0:
            errors.append("marketplace.json: Field 'plugins' array is empty")
        else:
            for i, plugin in enumerate(plugins):
                prefix = f"plugins[{i}]"

                if 'name' not in plugin:
                    errors.append(f"{prefix}: Missing required field 'name'")

                if 'source' not in plugin:
                    errors.append(f"{prefix}: Missing required field 'source'")
                else:
                    source = plugin['source']
                    if not isinstance(source, dict):
                        errors.append(f"{prefix}: Field 'source' must be an object")
                    else:
                        source_type = source.get('source')
                        valid_types = ['relative', 'github', 'url', 'git-subdir', 'npm']
                        if source_type not in valid_types:
                            errors.append(f"{prefix}: Invalid source type '{source_type}'")

    return errors, warnings, suggestions


def validate_skill_structure(skill_path):
    """Validate skill directory structure."""
    errors = []
    warnings = []
    suggestions = []

    # Required files
    if not (skill_path / 'SKILL.md').exists():
        errors.append("SKILL.md not found")

    # Check for references directory
    refs_dir = skill_path / 'references'
    if refs_dir.exists():
        ref_files = list(refs_dir.glob('*.md'))
        if len(ref_files) > 5:
            suggestions.append(f"Consider consolidating {len(ref_files)} reference files")

    # Check for scripts directory
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        script_files = list(scripts_dir.glob('*'))
        for script in script_files:
            if script.is_file() and not script.name.startswith('.'):
                # Check if executable
                if not script.stat().st_mode & 0o111:
                    warnings.append(f"Script not executable: scripts/{script.name}")

    return errors, warnings, suggestions


def run_description_test(skill_path, prompts_path=None, evals_path=None):
    """Run description testing if prompts or evals are provided."""
    if not prompts_path and not evals_path:
        return [], [], []

    test_script = Path(__file__).parent / 'test_description.py'

    if not test_script.exists():
        return [], ["test_description.py not found"], []

    import subprocess

    cmd = [sys.executable, str(test_script), str(skill_path)]

    if evals_path:
        cmd.extend(['--evals', str(evals_path)])
    elif prompts_path:
        cmd.extend(['--prompts', str(prompts_path)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            # test_description.py had an error
            return [f"Description test failed: {result.stderr}"], [], []

        # Parse output for suggestions
        output = result.stdout

        errors = []
        warnings = []
        suggestions = []

        # Look for metrics in output
        if 'Precision:' in output and 'Recall:' in output:
            # Extract precision and recall
            for line in output.split('\n'):
                if 'Precision:' in line:
                    try:
                        precision = float(line.split(':')[1].strip())
                        if precision < 0.8:
                            warnings.append(f"Low description precision: {precision:.2f}")
                    except (ValueError, IndexError):
                        pass
                if 'Recall:' in line:
                    try:
                        recall = float(line.split(':')[1].strip())
                        if recall < 0.5:
                            warnings.append(f"Low description recall: {recall:.2f}")
                    except (ValueError, IndexError):
                        pass

        return errors, warnings, suggestions

    except subprocess.TimeoutExpired:
        return ["Description test timed out"], [], []
    except Exception as e:
        return [f"Error running description test: {e}"], [], []


def fix_simple_issues(skill_path, frontmatter):
    """Auto-fix simple frontmatter issues."""
    import yaml

    skill_md = skill_path / 'SKILL.md'
    content = skill_md.read_text()

    # Extract YAML frontmatter
    import re
    match = re.match(r'^(---\n.*?\n---)', content, re.DOTALL)

    if not match:
        return False

    old_frontmatter_text = match.group(1)

    # Fix: add name if missing (derive from directory)
    if 'name' not in frontmatter:
        frontmatter['name'] = skill_path.name

    # Fix: add version if missing
    if 'version' not in frontmatter:
        frontmatter['version'] = '1.0.0'

    # Fix: add license if missing
    if 'license' not in frontmatter:
        frontmatter['license'] = 'Apache-2.0'

    # Generate new frontmatter
    new_frontmatter_text = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---"

    # Replace in content
    new_content = content.replace(old_frontmatter_text, new_frontmatter_text, 1)

    # Write back
    skill_md.write_text(new_content)

    return True


def print_report(all_errors, all_warnings, all_suggestions, verbose=True):
    """Print validation report."""
    total_errors = sum(len(e) for e in all_errors.values())
    total_warnings = sum(len(w) for w in all_warnings.values())
    total_suggestions = sum(len(s) for s in all_suggestions.values())

    if verbose:
        print("=" * 60)
        print("SKILL VALIDATION REPORT")
        print("=" * 60)
        print()

    # Errors by category
    for category, errors in all_errors.items():
        if errors:
            if verbose:
                print(f"❌ ERRORS ({category}):")
                for error in errors:
                    print(f"   • {error}")
                print()
            else:
                for error in errors:
                    print(f"ERROR [{category}]: {error}")

    # Warnings by category
    for category, warnings in all_warnings.items():
        if warnings:
            if verbose:
                print(f"⚠️  WARNINGS ({category}):")
                for warning in warnings:
                    print(f"   • {warning}")
                print()
            else:
                for warning in warnings:
                    print(f"WARNING [{category}]: {warning}")

    # Suggestions by category
    if verbose and total_suggestions > 0:
        print(f"💡 SUGGESTIONS:")
        for category, suggestions in all_suggestions.items():
            if suggestions:
                for suggestion in suggestions[:3]:  # Limit to 3 per category
                    print(f"   • {suggestion}")
        print()

    # Summary
    if verbose:
        print("-" * 40)
        print(f"Total Errors:     {total_errors}")
        print(f"Total Warnings:   {total_warnings}")
        print(f"Total Suggestions: {total_suggestions}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_all.py <skill-path> [options]")
        print("\nOptions:")
        print("  --test-description      Run description testing")
        print("  --prompts <file>        Text file with sample prompts")
        print("  --evals <path>          Path to evals.json")
        print("  --fix-frontend          Auto-fix simple frontmatter issues")
        print("  --strict                Treat warnings as errors")
        print("  --json                  Output as JSON")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    # Parse options
    test_description = False
    prompts_path = None
    evals_path = None
    fix_frontend = False
    strict = False
    output_json = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--test-description':
            test_description = True
            i += 1
        elif sys.argv[i] == '--prompts' and i + 1 < len(sys.argv):
            prompts_path = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--evals' and i + 1 < len(sys.argv):
            evals_path = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--fix-frontend':
            fix_frontend = True
            i += 1
        elif sys.argv[i] == '--strict':
            strict = True
            i += 1
        elif sys.argv[i] == '--json':
            output_json = True
            i += 1
        else:
            print(f"❌ Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    if not skill_path.exists():
        print(f"❌ Error: Skill path not found: {skill_path}")
        sys.exit(1)

    # Collect all validation results
    all_errors = {}
    all_warnings = {}
    all_suggestions = {}

    # 1. Parse frontmatter
    frontmatter, frontmatter_error = parse_frontmatter(skill_path)
    if frontmatter_error:
        all_errors['Frontmatter'] = [frontmatter_error]
    else:
        # 2. Validate frontmatter
        errors, warnings, suggestions = validate_frontmatter(frontmatter)
        if errors:
            all_errors['Frontmatter'] = errors
        if warnings:
            all_warnings['Frontmatter'] = warnings
        if suggestions:
            all_suggestions['Frontmatter'] = suggestions

        # 3. Fix simple issues if requested
        if fix_frontend:
            if fix_simple_issues(skill_path, frontmatter):
                print("✅ Fixed simple frontmatter issues")
                # Re-validate after fix
                frontmatter, _ = parse_frontmatter(skill_path)
                errors, warnings, suggestions = validate_frontmatter(frontmatter)
                if errors:
                    all_errors['Frontmatter'] = errors
                if warnings:
                    all_warnings['Frontmatter'] = warnings
                if suggestions:
                    all_suggestions['Frontmatter'] = suggestions

    # 4. Validate marketplace.json
    errors, warnings, suggestions = validate_marketplace_json(skill_path)
    if errors:
        all_errors['Marketplace'] = errors
    if warnings:
        all_warnings['Marketplace'] = warnings
    if suggestions:
        all_suggestions['Marketplace'] = suggestions

    # 5. Validate skill structure
    errors, warnings, suggestions = validate_skill_structure(skill_path)
    if errors:
        all_errors['Structure'] = errors
    if warnings:
        all_warnings['Structure'] = warnings
    if suggestions:
        all_suggestions['Structure'] = suggestions

    # 6. Run description testing if requested
    if test_description and (prompts_path or evals_path):
        errors, warnings, suggestions = run_description_test(skill_path, prompts_path, evals_path)
        if errors:
            all_errors['Description'] = errors
        if warnings:
            all_warnings['Description'] = warnings
        if suggestions:
            all_suggestions['Description'] = suggestions

    # Output results
    total_errors = sum(len(e) for e in all_errors.values())
    total_warnings = sum(len(w) for w in all_warnings.values())

    if output_json:
        report = {
            'timestamp': datetime.now().isoformat(),
            'skill_path': str(skill_path),
            'errors': all_errors,
            'warnings': all_warnings,
            'suggestions': all_suggestions,
            'summary': {
                'total_errors': total_errors,
                'total_warnings': total_warnings
            }
        }
        print(json.dumps(report, indent=2))
    else:
        print_report(all_errors, all_warnings, all_suggestions, verbose=True)

    # Determine exit code
    if total_errors > 0:
        sys.exit(1)
    elif strict and total_warnings > 0:
        sys.exit(1)
    elif total_warnings > 0:
        sys.exit(2)
    elif all_suggestions:
        sys.exit(3)
    else:
        print("✅ All validations passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
