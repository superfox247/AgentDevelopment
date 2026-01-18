---
name: Reset Development Environment
description: A skill to completely reset the project environment (Docker, Venv, Artifacts) to a clean state.
---

# Reset Development Environment

Use this skill when the environment is unstable.

## 1. Load Context
- `Makefile`: Clean targets.
- `tools/adk`: The CLI tool.

## 2. Choosing the Option

### A. Automatic Reset (Recommended)
Use the CLI to handle everything.
1.  **Action**: Run `adk reset`
2.  **Options**:
    - `uv run adk reset` (Standard reset)
    - `uv run adk reset --hard` (Also deletes .venv)

### B. Manual Cleanup (If CLI fails)
1.  `docker compose down -v` (Kill volumes).
2.  `docker system prune -f` (Kill dangling images).
3.  `Remove-Item -Recurse artifacts/*` (Kill app data).
4.  `rm -rf .venv` (Kill python env).

## 3. Rehydration
ALWAYS run these after a reset:
1.  `uv sync`
2.  `uv run adk debug` (Verify health)

