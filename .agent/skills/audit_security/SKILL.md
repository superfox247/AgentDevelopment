---
name: Audit Security
description: Scans codebase for security risks (API Keys, Secrets, Vulnerable deps).
---

# Audit Security

Scans codebase for security risks (API Keys, Secrets, Vulnerable deps).

## 1. Cognitive Heuristics (Policy)
**When to use this skill:**
Run before every commit. Zero tolerance for leaks.

## 2. Load Context
- `scripts/audit_security.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run python scripts/audit_security.py --help
```

## 4. Verification Logic (Self-Correction)
**How to verify success:**
The script returns Exit 0 if clean. Returns Exit 1 with a list of compromised lines if found.

## 5. Implementation Steps (Manual Fallback)
If the script fails, follow the logic in `scripts/audit_security.py`.
