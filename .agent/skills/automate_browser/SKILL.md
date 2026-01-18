---
name: Automate Browser
description: A protocol and skill for controlling the browser sub-agent safely and effectively.
---

# Automate Browser

This skill defines the standard protocol for interacting with the `browser_subagent`. STRICT ADHERENCE IS REQUIRED to prevent infinite loops and wasted resources.

## 1. Core Principles

*   **Fail Fast**: You must set a strict retry limit (Max 2). If a strategy fails twice, you MUST STOP and report the failure.
*   **Explicit Scope**: Every task must have a clear "Definition of Done" and "Abort Conditions".
*   **No Autopilot**: The sub-agent is a tactical executor, not a strategic planner. Do not ask it to "figure out" complex problems. Give it specific, granular tasks.

## 2. The Browser Prompt Template

You MUST use the following structure when crafting the `Task` argument for `browser_subagent`:

```markdown
# Objective
[Concise description of what to do, e.g., "Login to the dashboard and verify the settings switch."]

# Context
[Any necessary context, e.g., "We are already on the login page," or "Use the credentials found in .env"]

# Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

# Success Criteria (MANDATORY)
- [ ] Element X is visible.
- [ ] URL contains '/dashboard'.
- [ ] Text 'Settings Updated' appears.

# Abort Conditions (MANDATORY)
- IF selector '.login-btn' is not found after 5 seconds -> ABORT.
- IF 403 Forbidden error occurs -> ABORT.
- IF stuck on loading screen > 10s -> ABORT.
```

## 3. Standard Workflows

### A. Verification
When verifying a UI change:
1.  Navigate to the specific URL.
2.  Perform the specific interaction (click/type).
3.  **Capture the state**: Explicitly ask the agent to return a DOM snapshot or check for specific text.

### B. Debugging
When debugging a UI issue:
1.  Navigate to the broken page.
2.  Observe the state.
3.  **Do NOT attempt to fix it blindly**. Ask the sub-agent to gather info (console logs, screenshots) and RETURN.
4.  Analyze the artifacts *yourself* before sending a new task.

## 4. Safety Switch

If the `browser_subagent` returns failure twice for the same logical task, you are **FORBIDDEN** from trying a third time without user intervention or a fundamental change in strategy.
