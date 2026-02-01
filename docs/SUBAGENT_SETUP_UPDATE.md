# Subagent System Setup Update

> **Date**: 2026-01-26  
> **Purpose**: Ensure orchestrator subagent is automatically used in new chats

## Problem

When starting a new chat in Cursor, the main agent wasn't automatically delegating to the orchestrator subagent, even though the orchestrator is designed to handle all development work.

## Solution

Based on [Cursor's subagent documentation](https://cursor.com/docs/context/subagents), we've made the following changes to ensure automatic delegation:

### 1. Created `.cursor/rules/orchestrator.md`

**Location**: `.cursor/rules/orchestrator.md`

This rule file explicitly instructs the main agent to:
- **Always delegate to the orchestrator subagent** for all development tasks
- Use the orchestrator for feature implementations, code changes, bug fixes, refactoring, testing, and documentation updates
- Not use the orchestrator for simple questions or trivial single-file changes

**Why this matters**: Cursor reads `.cursor/rules/` files to guide agent behavior. This ensures the main agent knows to delegate to the orchestrator even in new chats.

**Important Note**: The rule file includes a note for subagents to ignore it. Subagents have isolated context windows and shouldn't try to delegate back to the orchestrator. The rule is specifically for the main agent's use.

### 2. Enhanced Orchestrator Description

**File**: `.cursor/agents/orchestrator.md`

**Before**:
```yaml
description: Main orchestrator agent. Delegates all work to specialized subagents. Use proactively for all tasks.
```

**After**:
```yaml
description: Main orchestrator agent. Always use for all development tasks, feature implementations, code changes, and multi-phase work. Delegates all work to specialized subagents (understanding, development, code-quality, testing, verification). Use proactively for any coding task.
```

**Why this matters**: The `description` field is what Cursor uses to determine when to delegate. By including "Always use for" and listing specific use cases, we make it clear when the orchestrator should be invoked.

## How It Works

### Rules and Subagents

**Important**: `.cursor/rules/` files are primarily read by the main agent. Subagents have isolated context windows and typically don't inherit rules from the parent agent. The orchestrator rule file includes a note instructing subagents to ignore it, since they're already being orchestrated.

### Automatic Delegation

According to Cursor's documentation, Agent proactively delegates tasks based on:
1. **Task complexity and scope** - Complex tasks trigger delegation
2. **Custom subagent descriptions** - The `description` field determines when to delegate
3. **Current context and available tools** - Agent considers what's available

### Delegation Flow

```
👤 User Request
  │
  └─→ 🤖 Main Agent (Cursor)
        │
        ├─→ Reads .cursor/rules/orchestrator.md
        ├─→ Checks orchestrator description
        └─→ Delegates to 🎯 Orchestrator Subagent
              │
              └─→ Orchestrator delegates to specialized subagents
```

### Explicit Invocation

Users can also explicitly invoke the orchestrator using:

```
/orchestrator Implement login feature
```

or

```
Use the orchestrator to implement login feature
```

## Verification

### Subagent Descriptions Verified

All subagents have proper descriptions with "use proactively" or "use when" language:

- ✅ **orchestrator**: "Always use for all development tasks..."
- ✅ **understanding**: "Use when starting new work or exploring existing code"
- ✅ **development**: "Use when building new functionality or modifying existing code"
- ✅ **code-quality**: "Use proactively after code changes to ensure quality standards"
- ✅ **testing**: "Use proactively to run tests and fix failures"
- ✅ **verification**: "Use after tasks are marked done to confirm implementations are functional"
- ✅ **task-tracking**: "Use throughout all phases to track progress, decisions, and issues"
- ✅ **research**: "Use when understanding or development subagents need detailed research"
- ✅ **debugger**: "Use when encountering issues"
- ✅ **test-runner**: "Use proactively to run tests and fix failures"

## Testing

To verify the setup works:

1. **Start a new chat** in Cursor
2. **Request a development task** (e.g., "Implement login feature")
3. **Observe**: The main agent should delegate to the orchestrator subagent
4. **Check**: The orchestrator should then delegate to understanding → development → quality → testing → verification subagents

## Files Changed

1. **Created**: `.cursor/rules/orchestrator.md` - Rule file for orchestrator delegation
2. **Updated**: `.cursor/agents/orchestrator.md` - Enhanced description field

## References

- [Cursor Subagents Documentation](https://cursor.com/docs/context/subagents)
- [Subagent System Architecture](docs/SUBAGENT_SYSTEM.md)
- [Subagent System Guide](docs/SUBAGENT_SYSTEM_GUIDE.md)

## Next Steps

If automatic delegation still doesn't work in new chats:

1. **Check Cursor version**: Ensure you're on a version that supports subagents (requires Max Mode on legacy plans)
2. **Verify subagent discovery**: Check that `.cursor/agents/` directory is recognized
3. **Test explicit invocation**: Try `/orchestrator` syntax to verify subagents are available
4. **Review Cursor settings**: Check if there are any settings that might affect subagent behavior

---

**Last Updated**: 2026-01-26  
**Status**: Active
