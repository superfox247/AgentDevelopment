---
name: Audit Security
description: Scans codebase for security risks (API Keys, Secrets, Vulnerable deps).
---

# Audit Security

Scan for:
1. Hardcoded Secrets (Regex terms)
2. Environment Inconsistencies (.env vs .env.example)
3. Dependency Health (Optional)

## 2. Security & Config Rules (The Law)
Strictly enforce separation of secrets and configuration:

### Secrets
*   **What**: API Keys, DB Passwords, Credentials.
*   **Where**: `.env` file ONLY.
*   **Rule**: NEVER check in secrets. Use `os.getenv()` in `config.py`, NOT in business logic.

### Configuration
*   **What**: URLs, Model Names, Timeouts, Prompts.
*   **Where**: `domain.yaml` or `config.py`.
*   **Rule**: Checked in. Strongly typed via Pydantic `BaseSettings`.

## 3. Cognitive Heuristics
**When to use:** Run before commits.

## 2. Load Context
- `.agent/skills/audit_security/audit_security.py`

## 3. Usage
```bash
uv run .agent/skills/audit_security/audit_security.py --check-deps
```

## 4. Verification Logic (Self-Correction)
**How to verify success:**
The script returns Exit 0 if clean. Returns Exit 1 with a list of compromised lines if found.

## 5. Implementation Steps (Manual Fallback)
If the script fails, follow the logic in `.agent/skills/audit_security/audit_security.py`.
