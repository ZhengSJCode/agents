---
name: gold-standard
version: "1.0.0"
description: >
  This is a gold standard example demonstrating all Claude Code skill best practices.
  Use this as a reference when creating new skills. For additional patterns, see skill-creator.
license: Apache-2.0
metadata:
  author: gogonuk
  version: "1.0.0"
  tags:
    - example
    - reference
    - documentation
  triggers:
    - "create a gold standard skill"
    - "skill best practices"
    - "show me a complete skill example"
  category: Reference
userInvocable: true
allowed-tools: []
---

# Gold Standard Skill

This is a reference implementation demonstrating all Claude Code skill best practices. Use it as a template when creating new skills.

## Purpose

This skill exists to demonstrate:
- Complete frontmatter with all recommended fields
- Well-structured SKILL.md content
- Progressive disclosure with references/ files
- Evaluation framework with evals/
- Distribution via marketplace.json

## When to Use This Reference

- You're creating a new skill and want to follow best practices
- You need to understand the complete skill structure
- You want to see how frontmatter fields should be populated
- You're setting up evaluation tests for your skill

## Core Concepts

### Frontmatter

The YAML frontmatter at the top of SKILL.md is critical for skill discovery:

```yaml
---
name: gold-standard                    # kebab-case, unique identifier
version: "1.0.0"                       # semver for versioning
description: >                         # Clear trigger phrases
  This skill should be used when the user asks to "create a gold standard skill"
  or other related phrases. This skill enables [capability]. For [related task],
  see related-skill.
license: Apache-2.0                    # SPDX identifier
metadata:
  author: gogonuk                      # Your GitHub username
  tags: [example, reference]           # Discoverability keywords
  triggers:                            # Explicit trigger phrases
    - "create a gold standard skill"
  category: Reference                  # Organization category
---
```

### Progressive Disclosure

Keep SKILL.md focused. Move detailed content to references/:

- **SKILL.md** - What the skill does, how to use it (~300 lines ideal)
- **references/techniques.md** - Technical approaches and methodologies
- **references/examples.md** - Worked examples
- **references/checklist.md** - Quality criteria and validation steps
- **references/troubleshooting.md** - Common issues and solutions

### Evaluation

The `evals/` directory contains test cases:

```json
{
  "evals": [
    {
      "id": "example-1",
      "prompt": "What should I include in skill frontmatter?",
      "expected_output": "Should mention name, version, description, license"
    }
  ]
}
```

## Usage Patterns

### Creating a New Skill

1. Start with the complete template
2. Customize frontmatter for your domain
3. Write focused SKILL.md content
4. Add references/ if content grows beyond ~300 lines
5. Create evals/ for testing
6. Generate marketplace.json for distribution

### Frontmatter Checklist

- [ ] `name`: kebab-case, unique
- [ ] `description`: includes "when the user asks to..." with quoted trigger phrases
- [ ] `version`: semver (1.0.0)
- [ ] `license`: SPDX identifier (Apache-2.0 recommended)
- [ ] `metadata.tags`: 3-5 relevant keywords
- [ ] `metadata.triggers`: explicit phrases users might say

### SKILL.md Structure

1. **Purpose** - One paragraph explaining what the skill does
2. **When to Use** - Clear trigger scenarios
3. **Core Concepts** - Key ideas and patterns
4. **Usage Patterns** - Common workflows
5. **References** - Links to references/ files

For detailed techniques, see `references/techniques.md`.

For worked examples, see `references/examples.md`.

## Validation

Run the master validator before distributing:

```bash
scripts/validate_all.py examples/gold-standard
```

Expected result: All validations pass.

## Distribution

This skill includes `marketplace.json` for easy installation. To package:

```bash
scripts/package_skill.py examples/gold-standard --include-marketplace --owner gogonuk
```

## Resources

For more information:

- `references/techniques.md` - Technical implementation details
- `references/examples.md` - Worked usage examples
- `references/checklist.md` - Quality validation criteria
- `evals/evals.json` - Test cases
- `marketplace.json` - Distribution configuration
