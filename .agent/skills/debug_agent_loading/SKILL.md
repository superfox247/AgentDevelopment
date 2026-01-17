---
name: Debug Agent Loading
description: A diagnostic skill to identify why an agent is not appearing in the ADK Web UI.
---

# Debug Agent Loading

Use this skill when `adk web` doesn't show your agent.

## 1. Load Context
- `agent_platform/yaml_loader.py`: The discovery logic.
- `domains/[domain]/__init__.py`: Visibility.

## 2. Diagnostic Checklist

### A. Factory Name Verification (Critical)
The loader looks for **exactly** `def create_app():`.
- ❌ `def create_agent():` (Wrong)
- ❌ `app = YamlAgent(...)` (Global scope - Wrong)
- ✅ `def create_app():` (Correct)

### B. Duplicate Route Check
If two agents have the same name or route, one will kill the other.
- Check `agent.yaml` `name` field.
- Ensure `domains/A/agent.yaml` != `domains/B/agent.yaml`.

### C. File Structure & Init
Does every folder in the path have `__init__.py`?
`domains/` -> `course_creator/` -> `my_agent/`
(All 3 need `__init__.py`).

### D. Docker Mounts (The "Hidden" Killer)
If running in Docker, did you add the new folder to `docker-compose.yml` volumes?
If not, the container **cannot see** your new files even if they are on disk.

## 3. Validating Paths manually
Run this snippet to prove Python can see it:
```python
import importlib
mod = importlib.import_module("domains.course_creator.new_agent.agent")
print(mod.create_app())
```
If this fails, it is 100% a path/import error.
