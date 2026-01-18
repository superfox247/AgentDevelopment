---
name: Debug System
description: A systematic skill for finding logs, tracing verification, and root cause analysis across the platform.
---

# Debug System

The "Sherlock Holmes" of the factory. Use this skill to methodically diagnose issues by analyzing logs, checking container health, and proposing fixes.

## 1. Cognitive Heuristics
**When to use:** 
- When an agent or service is failing or unresponsive.
- To find the root cause of an error (traceback analysis).
- To verify if the docker environment is healthy.

**Validation:** 
- Must identify the specific container or service causing the issue.
- Must provide the relevant log snippet (evidence).
- Should suggest a fix (e.g., restart container) if applicable.

## 2. Load Context
- `.agent/skills/debug_system/debug_system.py`: The automation script.
- `docker-compose.yml`: Service definitions.

## 3. Usage (Automated)

### Analyze All Services
Scans all containers for simple errors and health status.
```bash
uv run .agent/skills/debug_system/debug_system.py --target all
```

### Deep Dive into Specific Service
Fetches recent logs and analyzes them for stack traces.
```bash
uv run .agent/skills/debug_system/debug_system.py --target [service_name]
```
*Example:* `uv run .agent/skills/debug_system/debug_system.py --target orchestrator`

### Fix Issues
Attempts to fix common issues (e.g., restarts dead containers).
```bash
uv run .agent/skills/debug_system/debug_system.py --fix
```

## 4. Manual Debugging Cheatsheet
- **Global Errors**: `grep -r "ERROR" logs/`
- **Docker Logs**: `docker compose logs --tail=100 [service_name]`
- **Restart**: `docker compose restart [service_name]`
