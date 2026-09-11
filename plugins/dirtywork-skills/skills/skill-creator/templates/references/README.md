# References Directory Templates

This directory contains templates for creating progressive disclosure reference files in your skills.

## What Are References?

References are optional documentation files stored in a `references/` subdirectory within your skill. They contain detailed information that supplements the main SKILL.md:

- **techniques.md** - Methodologies, algorithms, and technical approaches
- **examples.md** - Worked examples demonstrating the skill in action
- **checklist.md** - Pre-flight checks, validation criteria, and quality standards
- **troubleshooting.md** - Common issues, error scenarios, and their solutions

## Why Use References?

**Progressive Disclosure** - Keep SKILL.md focused and scannable. Move detailed content to references/ where it's available when needed but doesn't clutter the main instructions.

**When to Use References:**
- SKILL.md exceeds 300 lines
- You have multiple algorithms or approaches to document
- You have extensive examples that would break flow
- You have troubleshooting patterns or edge cases

**When NOT to Use References:**
- Simple skills with straightforward logic
- Content that fits naturally in SKILL.md
- Information the AI needs on every invocation

## Usage

### When Creating a New Skill

```bash
# Create references directory
mkdir -p skills/my-skill/references

# Copy templates
cp templates/references/*.template skills/my-skill/references/

# Rename and customize
mv skills/my-skill/references/techniques.md.template skills/my-skill/references/techniques.md
```

### Linking From SKILL.md

Add references to your SKILL.md where relevant:

````markdown
## Approach

For background on the techniques used, see `references/techniques.md`.

For worked examples, see `references/examples.md`.

## Validation

Use `references/checklist.md` to verify output quality.

## Troubleshooting

If you encounter issues, consult `references/troubleshooting.md`.
````

## Template Customization

Each template includes:

1. **Usage Header** - When to use this reference file
2. **Structure Guidance** - How to organize content
3. **Example Content** - Demonstrative entries
4. **Best Practices** - Writing guidelines

Replace placeholder content with your skill-specific information. Remove sections that don't apply. Add new sections as needed.

## File Naming

Use these conventional names (or create your own):

- `techniques.md` - Technical approaches and methodologies
- `examples.md` - Worked examples with expected outputs
- `checklist.md` - Quality criteria and validation steps
- `troubleshooting.md` - Common issues and solutions
- `api.md` - API reference for external services
- `glossary.md` - Domain-specific terminology
- `changelog.md` - Version history and changes

Remember: These are optional. Use only what your skill needs.
