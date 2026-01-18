---
name: Debug System
description: A systematic skill for finding logs, tracing verification, and root cause analysis across the platform.
---

# Debug System

The "Sherlock Holmes" of the factory. Use this skill to methodically diagnose issues by analyzing logs, checking container health, validating web server connectivity, and proposing fixes.

## 1. Cognitive Heuristics
**When to use:** 
- When an agent or service is failing or unresponsive.
- To find the root cause of an error (traceback analysis).
- To verify if the docker environment AND web UIs are healthy.
- **When dealing with STALE DATA or weird state**: Use the rebuild capability.

**Validation:** 
- Must identify the specific container or service causing the issue.
- Must provide the relevant log snippet (evidence).
- Must report status of web endpoints (Dashboard, ADK, Phoenix).
- Should suggest a fix (e.g., restart container) if applicable.

## 2. Load Context
- `.agent/skills/debug_system/debug_system.py`: The automation script.
- `docker-compose.yml`: Service definitions.

## 3. Usage (Automated)

### Analyze Everything (Default)
Scans all containers, web servers, and logs.
```bash
uv run .agent/skills/debug_system/debug_system.py --target all
```

### Deep Dive into Specific Service
Fetches recent logs and analyzes them for stack traces.
```bash
uv run .agent/skills/debug_system/debug_system.py --target [service_name]
```

### 🛑 Advanced Recovery (Clean Rebuild)
Use this when you suspect **stale code** or **stale data** in a container.
It forces a rebuild and recreation of the container.
```bash
uv run .agent/skills/debug_system/debug_system.py --rebuild [service_name]
```
*Example:* `uv run .agent/skills/debug_system/debug_system.py --rebuild image_generator`
*Example (Nuke it all):* `uv run .agent/skills/debug_system/debug_system.py --rebuild all`

### Auto-Fix
Attempts to fix common issues (e.g., restarts dead containers).
```bash
uv run .agent/skills/debug_system/debug_system.py --fix
```
