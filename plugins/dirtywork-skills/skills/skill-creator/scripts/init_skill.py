#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-api-helper --path skills/private
    init_skill.py custom-skill --path /custom/location
"""

import sys
from pathlib import Path


SKILL_TEMPLATE_MINIMAL = r"""---
name: {skill_name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" → "Reading" → "Creating" → "Editing"
- Structure: ## Overview → ## Workflow Decision Tree → ## Step 1 → ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" → "Merge PDFs" → "Split PDFs" → "Extract Text"
- Structure: ## Overview → ## Quick Start → ## Task Category 1 → ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" → "Colors" → "Typography" → "Features"
- Structure: ## Overview → ## Guidelines → ## Specifications → ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" → numbered capability list
- Structure: ## Overview → ## Core Capabilities → ### 1. Feature → ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
"""


SKILL_TEMPLATE_COMPLETE = r"""---
name: {skill_name}
version: "1.0.0"
description: This skill should be used when the user asks to "{primary_trigger}" or {additional_triggers}. {purpose_statement}. For {related_task}, see {related_skill}.
license: Apache-2.0
compatibility: Claude Code ≥1.0. No system packages required.
metadata:
  author: {author_name}
  version: "1.0.0"
  tags:
    - {primary_category}
    - {secondary_category}
  triggers:
    - "{primary_trigger}"
    - "{trigger_2}"
    - "{trigger_3}"
  category: {category}
  userInvocable: true
allowed-tools: []
---

# {skill_title}

> **Best Practices**: This skill follows Claude Code skill best practices with complete frontmatter.

## When to Use This Skill

Use this skill when:
- {use_case_1}
- {use_case_2}
- {use_case_3}

## What This Skill Does

1. **{capability_1}**: {capability_1_desc}
2. **{capability_2}**: {capability_2_desc}
3. **{capability_3}**: {capability_3_desc}

## How to Use

### Basic Usage

```
{example_command_1}
```

```
{example_command_2}
```

### Advanced Usage

{advanced_usage_instructions}

## Structuring This Skill

Choose the structure that best fits this skill's purpose:

**1. Workflow-Based** (best for sequential processes)
- Clear step-by-step procedures
- Structure: Overview → Workflow Decision Tree → Step 1 → Step 2...

**2. Task-Based** (best for tool collections)
- Different operations/capabilities
- Structure: Overview → Quick Start → Task Category 1 → Task Category 2...

**3. Reference/Guidelines** (best for standards)
- Brand guidelines, coding standards, requirements
- Structure: Overview → Guidelines → Specifications → Usage...

**4. Capabilities-Based** (best for integrated systems)
- Multiple interrelated features
- Structure: Overview → Core Capabilities → 1. Feature → 2. Feature...

Delete this section after choosing your structure.

## [First Main Section]

[TODO: Add content here. Include code samples, decision trees, concrete examples.]

## Resources

This skill includes example resource directories:

### scripts/
Executable code for automation, data processing, or specific operations.

### references/
Documentation loaded into context to inform Claude's process.

### assets/
Files used in output, not loaded into context.

Delete unused directories.

## Validation Checkpoints

### Input Validation
- [ ] Validation checkpoint 1
- [ ] Validation checkpoint 2

### Output Validation
- [ ] Output validation checkpoint 1
- [ ] Output validation checkpoint 2

## Example

**Input**: [Example input]

**Output**:
```
[Example output]
```

## Tips for Success

1. **Tip 1**: [Guidance]
2. **Tip 2**: [Guidance]
3. **Tip 3**: [Guidance]

## Related Skills

- [related-skill-1](../related-skill-1/) — [Brief description]
- [related-skill-2](../related-skill-2/) — [Brief description]

---

**Frontmatter Reference**:
- `version`: Semantic versioning (major.minor.patch)
- `license`: SPDX identifier (Apache-2.0, MIT, GPL-3.0, etc.)
- `allowed-tools`: Array of tool names this skill may use
- `metadata.tags`: Searchability tags for discovery
- `metadata.triggers`: Explicit phrases that trigger this skill
- `metadata.category`: Higher-level organization category
- `userInvocable`: Whether users can invoke via /command
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.

Example real scripts from other skills:
- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields
- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images
"""

def main():
    print("This is an example script for {skill_name}")
    # TODO: Add actual script logic here
    # This could be data processing, file conversion, API calls, etc.

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

Example real reference docs from other skills:
- product-management/references/communication.md - Comprehensive guide for status updates
- product-management/references/context_building.md - Deep-dive on gathering context
- bigquery/references/ - API references and query examples

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes
- Rate limits

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Common patterns
- Troubleshooting
- Best practices
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the output Claude produces.

Example asset files from other skills:
- Brand guidelines: logo.png, slides_template.pptx
- Frontend builder: hello-world/ directory with HTML/React boilerplate
- Typography: custom-font.ttf, font-family.woff2
- Data: sample_data.csv, test_dataset.json

## Common Asset Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual assets can be any file type.
"""


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path, template="minimal", metadata=None):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        template: Template type ("minimal" or "complete")
        metadata: Dict with metadata fields for complete template

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    # Select template
    if template == "complete":
        skill_template = SKILL_TEMPLATE_COMPLETE
    else:
        skill_template = SKILL_TEMPLATE_MINIMAL

    # Prepare template variables
    skill_title = title_case_skill_name(skill_name)
    template_vars = {
        "skill_name": skill_name,
        "skill_title": skill_title
    }

    # Add metadata for complete template
    if template == "complete":
        metadata = metadata or {}
        template_vars.update({
            "author_name": metadata.get("author", "Your Name"),
            "version": metadata.get("version", "1.0.0"),
            "primary_category": metadata.get("primary_category", "general"),
            "secondary_category": metadata.get("secondary_category", "utilities"),
            "category": metadata.get("category", "General"),
            "primary_trigger": metadata.get("primary_trigger", f"use {skill_name}"),
            "additional_triggers": metadata.get("additional_triggers", "other related phrases"),
            "purpose_statement": metadata.get("purpose", f"This skill enables {skill_title} capabilities"),
            "related_skill": metadata.get("related_skill", "related-skill"),
            "related_task": metadata.get("related_task", "similar tasks"),
            "trigger_2": metadata.get("trigger_2", "second trigger phrase"),
            "trigger_3": metadata.get("trigger_3", "third trigger phrase"),
            "use_case_1": metadata.get("use_case_1", "First use case scenario"),
            "use_case_2": metadata.get("use_case_2", "Second use case scenario"),
            "use_case_3": metadata.get("use_case_3", "Third use case scenario"),
            "capability_1": metadata.get("capability_1", "First capability"),
            "capability_1_desc": metadata.get("capability_1_desc", "Description of first capability"),
            "capability_2": metadata.get("capability_2", "Second capability"),
            "capability_2_desc": metadata.get("capability_2_desc", "Description of second capability"),
            "capability_3": metadata.get("capability_3", "Third capability"),
            "capability_3_desc": metadata.get("capability_3_desc", "Description of third capability"),
            "example_command_1": metadata.get("example_command_1", f"Example: {skill_name} command"),
            "example_command_2": metadata.get("example_command_2", f"Example: Another {skill_name} usage"),
            "advanced_usage_instructions": metadata.get("advanced_usage", "Advanced usage instructions here")
        })

    # Create SKILL.md from template
    try:
        skill_content = skill_template.format(**template_vars)
        skill_md_path = skill_dir / 'SKILL.md'
        skill_md_path.write_text(skill_content)
        print(f"✅ Created SKILL.md (template: {template})")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    # Create resource directories with example files
    try:
        # Create scripts/ directory with example script
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("✅ Created scripts/example.py")

        # Create references/ directory with example reference doc
        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'api_reference.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ Created references/api_reference.md")

        # Create assets/ directory with example asset placeholder
        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        example_asset = assets_dir / 'example_asset.txt'
        example_asset.write_text(EXAMPLE_ASSET)
        print("✅ Created assets/example_asset.txt")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    # Print next steps
    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    print("2. Customize or delete the example files in scripts/, references/, and assets/")
    print("3. Run the validator when ready to check the skill structure")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path> [--template <minimal|complete>]")
        print("\nSkill name requirements:")
        print("  - Kebab-case identifier (e.g., 'my-data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 64 characters")
        print("  - Must match directory name exactly")
        print("\nTemplate options:")
        print("  minimal   - Basic template with essential fields (default)")
        print("  complete  - Full best-practices template with all metadata")
        print("\nExamples:")
        print("  init_skill.py my-new-skill --path skills/public")
        print("  init_skill.py my-api-helper --path skills/private --template complete")
        print("  init_skill.py custom-skill --path /custom/location --template minimal")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    # Parse optional template flag
    template = "minimal"  # default for backward compatibility
    metadata = {}

    if len(sys.argv) > 4:
        if sys.argv[4] == '--template':
            if len(sys.argv) < 6:
                print("❌ Error: --template requires a value (minimal or complete)")
                sys.exit(1)
            template = sys.argv[5]
            if template not in ["minimal", "complete"]:
                print(f"❌ Error: Invalid template '{template}'. Use 'minimal' or 'complete'")
                sys.exit(1)

    # For complete template, could prompt for metadata or use defaults
    # For now, use defaults - user can edit SKILL.md afterward

    print(f"🚀 Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    print(f"   Template: {template}")
    print()

    result = init_skill(skill_name, path, template=template, metadata=metadata)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
