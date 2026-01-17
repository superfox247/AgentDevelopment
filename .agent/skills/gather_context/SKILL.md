---
name: Gather Context
description: Helps the agent build code by finding relevant files and knowledge items.
---

# Gather Context

"Don't build in the dark." Use this skill to find related code before starting a task.

## 1. Context Philosophy (The Law)
*   **Seek-and-Read**: Do not read 5000-line files linearly. Use the `grep_search` tool and `view_code_item` to find specific logic.
*   **Workflows First**: Check `.agent/workflows/` before asking "How do I...?".
*   **Knowledge Items**: Check `knowledge/` before researching fresh topics.

## 2. Cognitive Heuristics
**When to use:**
- When starting a task involving a specific module ("agent_platform", "registry").
- When modifying a file, to see who imports it.
- When searching for "How to X" (Knowledge Items).

## 2. Load Context
- `.agent/skills/gather_context/gather_context.py`

## 3. Usage
```bash
uv run .agent/skills/gather_context/gather_context.py [term_or_file_path]
```
Example:
```bash
uv run .agent/skills/gather_context/gather_context.py "auth"
```
