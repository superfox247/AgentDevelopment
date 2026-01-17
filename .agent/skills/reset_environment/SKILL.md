---
name: Reset Development Environment
description: A skill to completely reset the project environment (Docker, Venv, Artifacts) to a clean state.
---

# Reset Development Environment

Use this skill when the environment is unstable.

## 1. Load Context
- `Makefile`: Clean targets.
- `.agent/skills/reset_environment/reset_dev_env.ps1`: The script.

## 2. Choosing the Option

### A. Soft Reset (Fast)
Use when Python dependencies are weird or a new package isn't showing up.
1.  **Action**: Delete `.venv` and re-sync.
2.  **Command**: `rm -rf .venv && uv sync` (Bash) or `Remove-Item .venv -Recurse; uv sync` (PS).

### B. Hard Reset (The "Nuclear" Option)
Use when Docker is stuck, artifacts are corrupt, or everything is broken.
⚠️ **WARNING: DATA LOSS**. This deletes all `artifacts/` and Docker volumes.
1.  **Backup**: Ensure `.env` is safe (it usually is, but check).
2.  **Action**: Run existing script.
    `powershell -ExecutionPolicy Bypass -File .agent/skills/reset_environment/reset_dev_env.ps1`

## 3. Manual Cleanup (If script fails)
1.  `docker compose down -v` (Kill volumes).
2.  `docker system prune -f` (Kill dangling images).
3.  `Remove-Item -Recurse artifacts/*` (Kill app data).

## 4. Rehydration
ALWAYS run these after a reset:
1.  `uv sync`
2.  `uv run adk check`
