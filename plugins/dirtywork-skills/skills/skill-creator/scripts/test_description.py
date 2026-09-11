#!/usr/bin/env python3
"""
Description Testing Script

Tests skill descriptions against sample prompts to measure triggering precision
and provides improvement suggestions.

Usage:
    test_description.py <skill-path> [options]

Options:
    --evals <path>     Path to evals.json file
    --prompts <file>   Text file with sample prompts (one per line)
    --interactive      Interactive mode for testing prompts
    --output <file>     Save results to JSON file

Examples:
    test_description.py skills/my-skill
    test_description.py skills/my-skill --evals evals/evals.json
    test_description.py skills/my-skill --prompts test_prompts.txt
    test_description.py skills/my-skill --interactive

Exit codes:
    0: Testing completed
    1: Error (missing skill, invalid evals, etc.)
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime


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
        import yaml
        frontmatter = yaml.safe_load(frontmatter_yaml)
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {e}"


def load_eval_prompts(evals_path):
    """Load prompts from evals.json file."""
    try:
        with open(evals_path, 'r') as f:
            evals = json.load(f)

        prompts = []
        for eval_item in evals.get('evals', []):
            if 'prompt' in eval_item:
                prompts.append({
                    'id': eval_item.get('id'),
                    'prompt': eval_item['prompt'],
                    'expected': eval_item.get('expected_output', '')
                })
        return prompts, None
    except Exception as e:
        return None, f"Error loading evals.json: {e}"


def load_prompts_from_file(prompts_file):
    """Load prompts from text file (one per line)."""
    try:
        with open(prompts_file, 'r') as f:
            lines = f.readlines()

        prompts = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                prompts.append({
                    'id': i,
                    'prompt': line,
                    'expected': ''
                })
        return prompts, None
    except Exception as e:
        return None, f"Error loading prompts file: {e}"


def simulate_trigger(description, prompt):
    """
    Simulate whether a description would trigger for a given prompt.

    This is a heuristic simulation based on keyword matching.
    Real triggering uses more sophisticated NLP.
    """
    description_lower = description.lower()
    prompt_lower = prompt.lower()

    # Extract key phrases from description
    # Look for phrases in quotes like "when the user asks to X"
    trigger_phrases = re.findall(r'"([^"]+)"', description)

    # Also look for explicit trigger phrases in metadata.triggers (if we had them)
    # For now, extract keywords from description
    keywords = re.findall(r'\b(use|when|asks? to|for)\s+([a-z][a-z0-9-]+(?:\s+[a-z][a-z0-9-]+)*)', description_lower)

    # Check if any trigger phrase matches
    for phrase in trigger_phrases:
        if phrase.lower() in prompt_lower:
            return True, f"Matched trigger phrase: \"{phrase}\""

    # Check keyword matching - re.findall returns tuples with capture groups
    for keyword_tuple in keywords:
        # keyword_tuple is (trigger_word, following_phrase)
        if len(keyword_tuple) >= 2:
            keyword = keyword_tuple[1].strip()
            if len(keyword) >= 3 and keyword in prompt_lower:
                return True, f"Matched keyword: {keyword}"

    # Check for direct name matches
    skill_name = re.search(r'name:\s*(\S+)', description, re.IGNORECASE)
    if skill_name:
        skill_name_value = skill_name.group(1)
        if skill_name_value.lower().replace('-', ' ') in prompt_lower:
            return True, f"Matched skill name: {skill_name_value}"

    return False, "No match found"


def test_description_against_prompts(description, prompts):
    """
    Test description against a list of prompts.

    Returns:
        Dictionary with test results
    """
    results = {
        'description': description[:200] + '...' if len(description) > 200 else description,
        'test_prompts': len(prompts),
        'results': []
    }

    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for prompt_item in prompts:
        prompt = prompt_item['prompt']
        expected = prompt_item.get('expected', '')

        would_trigger, reason = simulate_trigger(description, prompt)

        # Determine if this is a true/false positive/negative
        # Since we don't have ground truth, we need heuristics
        is_expected = 'should_trigger' in expected.lower() or expected != ''

        result = {
            'prompt_id': prompt_item.get('id'),
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'would_trigger': would_trigger,
            'reason': reason,
            'expected_tag': expected[:50] + '...' if len(expected) > 50 else expected
        }
        results['results'].append(result)

        if would_trigger:
            true_positives += 1
        else:
            true_negatives += 1

    # Calculate metrics
    total = len(prompts)
    if total > 0:
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / total  # Using total as denominator since we don't have true ground truth
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    else:
        precision = 0
        recall = 0
        f1_score = 0

    results.update({
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    })

    return results


def generate_suggestions(results):
    """Generate improvement suggestions based on test results."""
    suggestions = []

    description = results.get('description', '')

    # Check for common issues

    # 1. Description too short
    if len(description) < 100:
        suggestions.append("Description is too short. Add more context about when to use this skill.")

    # 2. No explicit trigger phrases
    if '"when the user asks to"' not in description.lower() and 'use when' not in description.lower():
        suggestions.append("Add explicit trigger phrases using format: 'when the user asks to \"X\", \"Y\", or \"Z\"'")

    # 3. Low precision
    if results['precision'] < 0.8:
        suggestions.append(f"Low precision ({results['precision']:.2f}). Description may be too broad. Add more specific trigger criteria.")

    # 4. Low recall
    if results['recall'] < 0.5:
        suggestions.append(f"Low recall ({results['recall']:.2f}). Description may be too narrow. Add more trigger phrases.")

    # 5. Check for keywords
    if not re.search(r'\b(keyword|tags?:|triggers?:)', description, re.IGNORECASE):
        suggestions.append("Consider adding explicit trigger phrases or keywords to improve discoverability.")

    # 6. Check for examples
    if 'example' not in description.lower():
        suggestions.append("Add examples of specific user requests that should trigger this skill.")

    return suggestions


def interactive_description_test(skill_path):
    """Interactive mode for testing descriptions."""
    frontmatter, error = parse_skill_frontmatter(skill_path)
    if error:
        print(f"❌ Error: {error}")
        return None

    description = frontmatter.get('description', '')
    print(f"Current description:\n  {description}\n")

    print("Interactive Description Testing")
    print("Enter prompts to test (one per line). Enter 'done' to finish.\n")

    prompts = []
    prompt_id = 1

    while True:
        try:
            prompt = input(f"Prompt {prompt_id} (or 'done'): ").strip()
            if prompt.lower() in ['done', 'exit', 'quit', '']:
                break
            if prompt:
                prompts.append({'id': prompt_id, 'prompt': prompt, 'expected': ''})
                # Show immediate feedback
                would_trigger, reason = simulate_trigger(description, prompt)
                status = "✓ WOULD TRIGGER" if would_trigger else "✗ NO TRIGGER"
                print(f"  {status}: {reason}")
                prompt_id += 1
        except (EOFError, KeyboardInterrupt):
            break

    if not prompts:
        print("\nNo prompts entered.")
        return None

    print(f"\nTesting {len(prompts)} prompts...\n")

    results = test_description_against_prompts(description, prompts)

    print_results(results)

    return results


def print_results(results):
    """Print test results."""
    print("=" * 60)
    print("DESCRIPTION TEST RESULTS")
    print("=" * 60)

    print(f"\nDescription: {results['description']}")
    print(f"Test Prompts: {results['test_prompts']}")
    print()

    print("Metrics:")
    print(f"  True Positives:  {results['true_positives']}")
    print(f"  False Positives: {results['false_positives']}")
    print(f"  True Negatives:  {results['true_negatives']}")
    print(f"  False Negatives: {results['false_negatives']}")
    print()
    print(f"  Precision:  {results['precision']:.2f}")
    print(f"  Recall:     {results['recall']:.2f}")
    print(f"  F1 Score:   {results['f1_score']:.2f}")
    print()

    # Generate and display suggestions
    suggestions = generate_suggestions(results)
    if suggestions:
        print("💡 Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        print()

    # Show detailed results for false positives/negatives
    if results['false_positives'] > 0:
        print("⚠️  False Positives (triggered when shouldn't):")
        for result in results['results']:
            if result['would_trigger'] and 'should not' in result['expected_tag'].lower():
                print(f"   • [{result['prompt_id']}] {result['prompt']}")
                print(f"     Reason: {result['reason']}")
        print()

    if results['false_negatives'] > 0:
        print("⚠️  False Negatives (didn't trigger when should):")
        for result in results['results']:
            if not result['would_trigger'] and 'should trigger' in result['expected_tag'].lower():
                print(f"   • [{result['prompt_id']}] {result['prompt']}")
                print(f"     Reason: {result['reason']}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: test_description.py <skill-path> [options]")
        print("\nOptions:")
        print("  --evals <path>       Path to evals.json file")
        print("  --prompts <file>     Text file with sample prompts (one per line)")
        print("  --interactive        Interactive mode for testing prompts")
        print("  --output <file>      Save results to JSON file")
        print("\nExamples:")
        print("  test_description.py skills/my-skill")
        print("  test_description.py skills/my-skill --evals evals/evals.json")
        print("  test_description.py skills/my-skill --prompts test_prompts.txt")
        print("  test_description.py skills/my-skill --interactive")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    evals_path = None
    prompts_file = None
    interactive = False
    output_file = None

    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--evals' and i + 1 < len(sys.argv):
            evals_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--prompts' and i + 1 < len(sys.argv):
            prompts_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--interactive':
            interactive = True
            i += 1
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            print(f"❌ Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    # Validate skill exists
    if not (skill_path / 'SKILL.md').exists():
        print(f"❌ Error: SKILL.md not found at {skill_path}")
        sys.exit(1)

    print(f"🔍 Testing description for: {skill_path}")
    print()

    # Parse description
    frontmatter, error = parse_skill_frontmatter(skill_path)
    if error:
        print(f"❌ Error: {error}")
        sys.exit(1)

    description = frontmatter.get('description', '')
    print(f"Description: {description[:200]}{'...' if len(description) > 200 else ''}\n")

    # Interactive mode
    if interactive:
        results = interactive_description_test(skill_path)
        if results and output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"✅ Results saved to: {output_file}")
            except Exception as e:
                print(f"❌ Error saving results: {e}")
        sys.exit(0)

    # Load prompts from evals.json or prompts file
    prompts = None
    if evals_path:
        prompts, error = load_eval_prompts(evals_path)
        if error:
            print(f"❌ Error: {error}")
            sys.exit(1)
    elif prompts_file:
        prompts, error = load_prompts_from_file(prompts_file)
        if error:
            print(f"❌ Error: {error}")
            sys.exit(1)
    else:
        print("❌ Error: Please provide --evals or --prompts file, or use --interactive mode")
        sys.exit(1)

    if not prompts:
        print("❌ Error: No prompts to test")
        sys.exit(1)

    print(f"Testing {len(prompts)} prompts...\n")

    # Run tests
    results = test_description_against_prompts(description, prompts)

    # Print results
    print_results(results)

    # Save to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
