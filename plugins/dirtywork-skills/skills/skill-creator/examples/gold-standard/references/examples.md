# Examples

**Usage:** Worked examples demonstrating the gold standard skill patterns. Reference this when applying these patterns to your own skills.

---

## Example 1: Minimal Skill

**Scenario:** Creating a simple skill with minimal frontmatter.

**Input:**
```bash
scripts/init_skill.py skills/simple-skill --template minimal
```

**SKILL.md Output:**
```markdown
---
name: simple-skill
description: This skill should be used when the user asks to "use simple-skill" or other related phrases.
---

# Simple Skill

A simple skill for demonstration purposes.
```

**Characteristics:**
- Fastest way to get started
- Backward compatible with existing skills
- Expandable later to complete template

---

## Example 2: Complete Skill

**Scenario:** Creating a skill with all best practices from the start.

**Input:**
```bash
scripts/init_skill.py skills/my-skill --template complete
```

**Interactive Prompts:**
```
Author name [gogonuk]: gogonuk
Category [General]: Data Processing
Tags (comma-separated) [data,utilities]: data,processing,csv
Trigger phrases (one per line, empty line to finish):
  > process csv file
  > parse spreadsheet
  > convert csv to json
  >
```

**Generated SKILL.md:**
```markdown
---
name: my-skill
version: "1.0.0"
description: >
  This skill should be used when the user asks to "process csv file", "parse spreadsheet",
  or "convert csv to json". This skill enables CSV data processing capabilities.
  For similar tasks, see data-analyzer.
license: Apache-2.0
metadata:
  author: gogonuk
  version: "1.0.0"
  tags:
    - data
    - processing
    - csv
  triggers:
    - "process csv file"
    - "parse spreadsheet"
    - "convert csv to json"
  category: Data Processing
userInvocable: true
allowed-tools: []
---

# CSV Processor

A skill for processing CSV files with various transformations.

## Purpose

This skill handles CSV file operations including parsing, transformation, and format conversion.

## When to Use

Use this skill when you need to:
- Parse CSV files
- Convert CSV to JSON
- Transform CSV data
- Validate CSV structure

## Core Concepts

...
```

---

## Example 3: Adding References

**Scenario:** Your SKILL.md is getting too long. Move detailed content to references/.

**Before (SKILL.md - 450 lines):**
```markdown
## Technical Implementation

<!-- 100 lines of algorithm details -->

## Algorithm 1: Parsing

<!-- 50 lines of pseudocode -->

## Algorithm 2: Transformation

<!-- 50 lines of pseudocode -->

## Usage Examples

<!-- 100 lines of examples -->

...
```

**After (SKILL.md - 150 lines + references/):**

**SKILL.md:**
```markdown
## Technical Implementation

For detailed algorithm descriptions, see `references/techniques.md`.

For worked examples, see `references/examples.md`.
```

**references/techniques.md:**
```markdown
# Techniques

## Algorithm 1: Parsing

<!-- The 100 lines from before -->

## Algorithm 2: Transformation

<!-- The 50 lines from before -->
```

**references/examples.md:**
```markdown
# Examples

## Example 1: Basic Parsing

<!-- The examples from before -->
```

---

## Example 4: Creating Evaluations

**Scenario:** Adding test cases to ensure your skill works correctly.

**evals/evals.json:**
```json
{
  "evals": [
    {
      "id": "csv-parse-basic",
      "prompt": "Parse the CSV file data.csv and show me the first 3 rows",
      "expected_output": "Should display headers and first 3 data rows",
      "assertions": [
        {
          "type": "contains",
          "value": "name"
        },
        {
          "type": "contains",
          "value": "email"
        }
      ]
    },
    {
      "id": "csv-to-json",
      "prompt": "Convert data.csv to JSON format",
      "expected_output": "Valid JSON array with objects",
      "assertions": [
        {
          "type": "file_exists",
          "path": "output.json"
        },
        {
          "type": "json_path",
          "path": "$[0].name",
          "value": "John Doe"
        }
      ]
    }
  ]
}
```

**Running the evals:**
```bash
scripts/run_eval.py skills/my-skill evals/evals.json
```

---

## Example 5: Distribution Workflow

**Scenario:** Packaging your skill for distribution.

**Step 1: Generate marketplace.json**
```bash
scripts/generate_marketplace.py skills/my-skill --owner gogonuk
```

**Output (skills/my-skill/marketplace.json):**
```json
{
  "name": "my-skill",
  "owner": {
    "name": "gogonuk"
  },
  "plugins": [
    {
      "name": "my-skill",
      "source": {
        "source": "relative",
        "path": "./my-skill"
      },
      "description": "This skill should be used when the user asks to...",
      "version": "1.0.0",
      "keywords": ["data", "processing", "csv"],
      "category": "Data Processing",
      "strict": false
    }
  ]
}
```

**Step 2: Validate everything**
```bash
scripts/validate_all.py skills/my-skill
```

**Step 3: Package**
```bash
scripts/package_skill.py skills/my-skill --include-marketplace --owner gogonuk
```

**Output:**
```
📦 Packaging skill: skills/my-skill

🔍 Validating skill...
✅ Validation passed

  Added: my-skill/SKILL.md
  Added: my-skill/references/techniques.md
  Added: my-skill/references/examples.md
  Added: my-skill/evals/evals.json
  Added: my-skill/marketplace.json

✅ Successfully packaged skill to: my-skill.skill
```

---

## Example 6: Description Testing

**Scenario:** Optimizing your skill description for better triggering.

**test_prompts.txt:**
```
process my csv
csv file help
convert to json
parse spreadsheet data
extract data from csv
```

**Run description test:**
```bash
scripts/test_description.py skills/my-skill --prompts test_prompts.txt
```

**Output:**
```
============================================================
DESCRIPTION TEST RESULTS
============================================================

Description: This skill should be used when the user asks to...
Test Prompts: 5

Metrics:
  True Positives:  4
  False Positives:  0
  True Negatives:  1
  False Negatives:  0

  Precision:  1.00
  Recall:     0.80
  F1 Score:   0.89

💡 Suggestions:
   1. Consider adding "extract data from csv" to triggers
```

---

## Example 7: Usage Tracking

**Scenario:** Understanding which skills are most used.

**Install tracking hook:**
```bash
scripts/install_usage_hook.py
```

**Check status:**
```bash
scripts/install_usage_hook.py --status
```

**After using skills for a while, analyze:**
```bash
# Top skills
scripts/analyze_usage.py --top 10

# Daily breakdown
scripts/analyze_usage.py --daily

# Specific skill details
scripts/analyze_usage.py --skill csv-processor
```

---

## Testing Your Implementation

Use these examples to verify your skill follows best practices:

### Quick Validation

```bash
# Validate everything
scripts/validate_all.py skills/your-skill

# Test description with sample prompts
scripts/test_description.py skills/your-skill --prompts test_prompts.txt
```

### Complete Checklist

- [ ] Frontmatter has all required fields
- [ ] Description includes explicit trigger phrases
- [ ] Version follows semver
- [ ] License is valid SPDX identifier
- [ ] SKILL.md is under 300 lines
- [ ] references/ used for detailed content
- [ ] evals/ contains test cases
- [ ] marketplace.json generated
- [ ] All validations pass
