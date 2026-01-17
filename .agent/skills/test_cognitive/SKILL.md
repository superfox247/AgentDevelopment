---
name: Test Cognitive
description: Verifying cognitive upgrade
---

# Test Cognitive

Verifying cognitive upgrade

## 1. Cognitive Heuristics (Policy)
**When to use this skill:**
Use for testing only

## 2. Load Context
- `scripts/test_cognitive.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run python scripts/test_cognitive.py --help
```

## 4. Verification Logic (Self-Correction)
**How to verify success:**
Check for SKILL.md sections

## 5. Implementation Steps (Manual Fallback)
If the script fails, follow the logic in `scripts/test_cognitive.py`.
