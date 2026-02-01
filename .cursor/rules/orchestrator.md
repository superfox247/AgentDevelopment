# Orchestrator Rule

**CRITICAL: This rule applies to the MAIN AGENT only. Always delegate to the orchestrator subagent for all development tasks.**

> **Note for Subagents**: If you are reading this as a subagent (understanding, development, code-quality, testing, verification, etc.), ignore this rule. You are already being orchestrated by the orchestrator subagent. Continue with your specialized work.

## Default Behavior (Main Agent Only)

When a user requests any development work, coding task, or feature implementation:

1. **Immediately delegate to the `orchestrator` subagent** - Do not attempt to do the work yourself
2. The orchestrator will coordinate all phases (Understanding → Development → Quality → Testing → Verification)
3. The orchestrator delegates to specialized subagents for each phase

## When to Use Orchestrator

Use the orchestrator subagent for:
- ✅ All feature implementations
- ✅ Code changes or modifications
- ✅ Bug fixes
- ✅ Refactoring tasks
- ✅ Testing tasks
- ✅ Documentation updates that require code changes
- ✅ Any task requiring multiple phases

## When NOT to Use Orchestrator

You can handle directly (no orchestrator needed):
- ❌ Simple questions about the codebase
- ❌ Reading documentation
- ❌ Explaining existing code
- ❌ Single-file, trivial changes (e.g., fixing a typo)

## How to Delegate

To delegate to the orchestrator, use the `/orchestrator` syntax or mention it naturally:

```
/orchestrator Implement login feature
```

or

```
Use the orchestrator to implement login feature
```

## Why This Matters

The orchestrator ensures:
- Proper phase execution (Understanding → Development → Quality → Testing → Verification)
- Context isolation (each phase runs in its own context window)
- Specialized expertise (each phase handled by domain experts)
- Comprehensive tracking (task-tracking subagent records everything)

**Remember**: The orchestrator never does the work itself - it delegates to specialized subagents. This is by design for better context management and parallel execution.
