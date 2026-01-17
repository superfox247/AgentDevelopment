---
name: Compliance Check
description: Scans codebase for GEMINI.md violations (Print, Any, Hardcoded Env).
---

# Compliance Check

Scans codebase for GEMINI.md violations (Print, Any, Hardcoded Env).

## 1. Cognitive Heuristics (Policy)
**When to use this skill:**
Run this before every commit or whenever you add new code.

## 2. Load Context
- `scripts/compliance_check.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run python scripts/compliance_check.py --help
```

## 4. Verification Logic (Self-Correction)
**How to verify success:**
The script returns Exit Code 0 and prints 'No violations found'. If violations exist, it lists them with file paths.

## 5. Implementation Steps (Manual Fallback)
If the script fails, follow the logic in `scripts/compliance_check.py`.
