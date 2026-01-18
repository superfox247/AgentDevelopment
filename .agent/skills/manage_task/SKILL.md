---
name: Manage Task
description: The Standard Development Method. Ensures systematic progress, tracking, and resilience.
---

# Manage Task

**Purpose**: To turn "Chaos" into "Order". Defines how we work, track progress, and recover from interruptions.

## 1. The Resilient Task Loop (The Law)
All work MUST follow this cycle:

1.  **PLAN**: Understand the Goal.
    *   **Artifact**: `task.md` (Breakdown).
    *   **Artifact**: `implementation_plan.md` (Design).
    *   **Action**: `task_boundary(MODE=PLANNING)`.

2.  **EXECUTE**: build the thing.
    *   **Action**: Iteratively verify small steps.
    *   **Action**: `task_boundary(MODE=EXECUTION)`.

3.  **RECOVER**: Save State.
    *   **Rule**: Update `task.md` frequently. It is your "Save Game".
    *   **Trigger**: Before `notify_user` or context switch.

4.  **VERIFY**: Prove it works.
    *   **Action**: Run automated tests, build check, or verify script execution.
    *   **Artifact**: `walkthrough.md` (Evidence).
    *   **Trigger**: Automatic Check-in via `manage_git` Protocol.
    *   **Action**: `task_boundary(MODE=VERIFICATION)`.

## 2. Artifact Standards
*   **task.md**: The "Living Checklist". Statuses: `[ ]`, `[/]`, `[x]`.
*   **implementation_plan.md**: The "Blueprint". Must be approved by user for complex tasks.
*   **walkthrough.md**: The "Receipt". Screenshots, logs, diffs proving completion.

## 3. Cognitive Heuristics
**When to use:**
- ALWAYS. This is the operating system for the Agent.
- Especially when "Lost" or Resuming a session.
