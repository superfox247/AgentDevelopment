---
name: Debug System
description: A systematic skill for finding logs, tracing verification, and root cause analysis across the platform.
---

# Debug System

The "Sherlock Holmes" of the factory. Use this skill to methodically diagnose issues.

## 1. Load Context
- `error.log`: Global error capture.
- `error_pipeline.log`: Pipeline failures.
- `docker-compose.yml`: Service definitions.

## 2. Systematic Debugging Process

### Phase 1: Observability (Find the Evidence)
DO NOT guess. Find the log.

#### Cheatsheet for finding logs:
- **Global Errors**: `grep_search "ERROR" error.log`
- **Specific Trace**: `grep_search "[trace_id]" *.log`
- **Docker Logs**: `docker compose logs --tail=100 [service_name]`
- **Recursive Search**: `grep -r "mypattern" . --exclude-dir=.venv`

#### Distributed Tracing Logic
If the system spans multiple containers (e.g., ADK + Orchestrator):
1.  Find the `trace_id` in the first container's log.
2.  Grep for that SAME `trace_id` in the second container's log.
3.  **Time Correlation**: If no trace ID, match timestamps (+/- 1 second).

### Phase 2: Isolation (Bisect)
1.  **Code vs Config**: Did `domain.yaml` change? or `agent.py`?
2.  **Network**: Can `adk` reach `orchestrator`? (Ping check).
3.  **State**: Is the database locked?

### Phase 3: Reproduction (Minimal Repro)
Create `reproduce_issue.py`:
```python
import logging
from domains.course_creator.orchestrator.agent import create_app

# Mimic the environment
app = create_app()

try:
    # Run the exact failing function
    app.process(breaking_input)
except Exception:
    logging.exception("Caught it!")
```

## 3. Common Signatures
- **"ModuleNotFoundError"**: Python path. Check `sys.path` or `__init__.py`.
- **"404 Not Found"**: Route missing. Did you register it in `server.py`?
- **"Connection Refused"**: Docker network issue. Use service names (e.g., `http://orchestrator:8000`), NOT `localhost`.
