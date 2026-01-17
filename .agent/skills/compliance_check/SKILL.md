---
name: Compliance Check
description: Scans codebase for GEMINI.md violations (Print, Any, Hardcoded Env).
---

# Compliance Check

Scans codebase for GEMINI.md violations (Print, Any, Hardcoded Env).

## 1. Cognitive Heuristics (Policy)
**When to use this skill:**
Run this before every commit or whenever you add new code.

## 2. Enforced Rules (The Law)
The following patterns are strictly forbidden in `domains/` to maintain the **Separation of Concerns**:

| Violation Type | Description | Forbidden Pattern |
| :--- | :--- | :--- |
| **Infra Leak** | Domain code usage of container runtime | `import docker`, `from docker import ...` |
| **Platform Leak** | accessing platform internals | `agent_platform.tools.debug`, `agent_platform.server` |
| **Process Leak** | Spawning subprocesses directly | `subprocess.run` (use Platform tools instead) |
| **Noise** | Unstructured logging | `print(...)` |
| **Config** | Hardcoded dependencies | `os.getenv(...)` (use `domain.yaml`) |

## 3. Load Context
- `.agent/skills/compliance_check/compliance_check.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run .agent/skills/compliance_check/compliance_check.py --help
```

## 4. Verification Logic (Self-Correction)
**How to verify success:**
The script returns Exit Code 0 and prints 'No violations found'. If violations exist, it lists them with file paths.

## 5. Implementation Steps (Manual Fallback)
If the script fails, follow the logic in `.agent/skills/compliance_check/compliance_check.py`.
