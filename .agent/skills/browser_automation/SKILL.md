---
name: Automate Browser
description: A protocol and skill for controlling the browser sub-agent safely and effectively.
---

# Automate Browser

This skill defines the standard protocol for interacting with the `browser_subagent`.

## 1. Rules

*   **Fail Fast**: If a strategy fails twice, STOP and report.
*   **Explicit Scope**: Every task must have a clear "Definition of Done".
*   **Simple Instructions**: Use atomic steps, explicit waits, and avoid logic.

## 2. Browser Prompt Template

You MUST use the following structure for the `Task` argument:

```markdown
# Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

# Abort Conditions (MANDATORY)
- IF ANYTHING goes wrong (e.g., element not found, error, timeout, page not loading/white screen) -> CAPTURE SCREENSHOT AND LOGS -> STOP IMMEDIATELY.
```
