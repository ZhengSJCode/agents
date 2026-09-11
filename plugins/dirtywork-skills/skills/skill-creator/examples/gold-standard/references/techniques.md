# Techniques

**Usage:** Technical patterns used in this gold standard skill. Reference this when understanding implementation details.

---

## Overview

This skill demonstrates the following technical approaches:

1. **Complete Frontmatter** - Full YAML metadata with all recommended fields
2. **Progressive Disclosure** - Organizing content across SKILL.md and references/
3. **Evaluation Framework** - Test-driven skill development with evals/
4. **Distribution** - marketplace.json for easy sharing and installation

---

## Technique 1: Frontmatter Schema

**Purpose:** Define skill metadata for discovery, validation, and distribution.

### Schema

```yaml
---
# Required fields
name: skill-name                    # kebab-case identifier
description: >                      # Trigger phrases + capability
  This skill should be used when the user asks to "explicit trigger phrase"
  or other related phrases. This skill enables [capability]. For [related task],
  see related-skill.

# Recommended fields
version: "1.0.0"                    # Semantic versioning
license: Apache-2.0                 # SPDX identifier
metadata:
  author: username                  # GitHub username
  tags: [category, domain]          # Discoverability
  triggers:                         # Explicit phrases
    - "trigger phrase 1"
    - "explicit trigger phrase 2"
  category: Category                # Organization

# Conditional fields
userInvocable: true                 # If users can invoke directly
allowed-tools:                      # Tools this skill may use
  - ToolName1
  - ToolName2
---
```

### Field Validation

| Field | Required? | Format | Validation |
|-------|-----------|--------|------------|
| `name` | Yes | kebab-case | `^[a-z0-9-]+$` |
| `description` | Yes | Plain text | Min 50 chars, include trigger phrases |
| `version` | Recommended | semver | `^\d+\.\d+\.\d+$` |
| `license` | Recommended | SPDX | Use valid identifier |
| `metadata.tags` | Recommended | Array | 3-5 keywords |
| `metadata.triggers` | Recommended | Array | Quoted phrases in double quotes |

---

## Technique 2: Progressive Disclosure

**Purpose:** Keep SKILL.md scannable while providing depth when needed.

### Content Organization

```
SKILL.md (main instructions, ~300 lines ideal)
├── Purpose (what it does)
├── When to Use (trigger scenarios)
├── Core Concepts (key ideas)
└── References (links to detailed content)

references/
├── techniques.md (this file)     # Technical approaches
├── examples.md                   # Worked examples
├── checklist.md                  # Validation criteria
└── troubleshooting.md            # Common issues
```

### When to Use References

**Use references/ when:**
- SKILL.md exceeds 300 lines
- You have multiple algorithms to document
- Examples would break the flow
- Troubleshooting patterns exist

**Don't use references/ when:**
- Content fits naturally in SKILL.md
- Information is needed every invocation
- Skill is simple and straightforward

### Linking Pattern

In SKILL.md:

````markdown
## Core Concepts

For background on the techniques used, see `references/techniques.md`.

For worked examples, see `references/examples.md`.

## Validation

Use `references/checklist.md` to verify output quality.
````

---

## Technique 3: Evaluation Framework

**Purpose:** Test-driven skill development with reproducible test cases.

### Evals Structure

```json
{
  "evals": [
    {
      "id": "test-1",
      "prompt": "Test prompt here",
      "expected_output": "Expected result description",
      "assertions": [
        {
          "type": "contains",
          "value": "required content"
        }
      ]
    }
  ]
}
```

### Assertion Types

| Type | Purpose | Example |
|------|---------|---------|
| `contains` | Output must contain text | `{"type": "contains", "value": "error"}` |
| `equals` | Exact match | `{"type": "equals", "value": "42"}` |
| `json_path` | JSON field validation | `{"type": "json_path", "path": "$.status", "value": "success"}` |
| `file_exists` | Check file creation | `{"type": "file_exists", "path": "output.txt"}` |

### Running Evaluations

```bash
# Run all evals
scripts/run_eval.py skills/my-skill evals/evals.json

# Run specific eval
scripts/run_eval.py skills/my-skill evals/evals.json --filter test-1
```

---

## Technique 4: Distribution via Marketplace.json

**Purpose:** Enable easy skill sharing and installation.

### Marketplace Schema

```json
{
  "name": "skill-name",
  "owner": {
    "name": "username"
  },
  "plugins": [
    {
      "name": "skill-name",
      "source": {
        "source": "relative",
        "path": "./skill-name"
      },
      "description": "Skill description with trigger phrases",
      "version": "1.0.0",
      "keywords": ["category", "domain"],
      "category": "Category",
      "strict": false
    }
  ]
}
```

### Source Types

| Type | When to Use | Required Fields |
|------|-------------|-----------------|
| `relative` | Local path within marketplace | `path` |
| `github` | GitHub repository | `repo` |
| `url` | Direct git URL | `url` |
| `git-subdir` | Subdirectory of git repo | `url`, `path` |
| `npm` | npm package | `package` |

### Generation

```bash
# Auto-generate from frontmatter
scripts/generate_marketplace.py skills/my-skill --owner username

# Validate before distribution
scripts/validate_marketplace.py skills/my-skill/marketplace.json
```

---

## Best Practices

### Do's

- ✅ Use kebab-case for skill names
- ✅ Include explicit trigger phrases in description
- ✅ Follow semver for versioning
- ✅ Use SPDX license identifiers
- ✅ Keep SKILL.md under 300 lines
- ✅ Add references/ for detailed content
- ✅ Create evals/ for testing
- ✅ Generate marketplace.json for distribution

### Don'ts

- ❌ Include README.md (skills are for AI, not humans)
- ❌ Put auxiliary docs in skill root
- ❌ Use camelCase or PascalCase for names
- ❌ Skip version field
- ❌ Forget trigger phrases in description
- ❌ Make SKILL.md too long (>500 lines)

---

## References

- [Semantic Versioning](https://semver.org/)
- [SPDX License List](https://spdx.org/licenses/)
- [Claude Code Skills Documentation](https://docs.anthropic.com/claude/code/skills)
