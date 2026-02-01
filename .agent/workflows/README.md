# Subagent System

This directory previously contained workflow files, but those have been removed in favor of the **subagent architecture**.

## Current Architecture

All development work is handled by the **Orchestrator subagent** (`.cursor/agents/orchestrator.md`), which delegates to specialized subagents:

- **Understanding** → `understanding` subagent
- **Development** → `development` subagent
- **Code Quality** → `code-quality` subagent
- **Testing** → `testing` subagent
- **Verification** → `verification` subagent
- **Task Tracking** → `task-tracking` subagent (background)

## Subagent Locations

All subagents are located in: `.cursor/agents/*.md`

- `orchestrator.md` - Main orchestrator (delegates all work)
- `understanding.md` - Understanding phase
- `development.md` - Development phase
- `code-quality.md` - Code quality checks
- `testing.md` - Testing phase
- `verification.md` - Verification phase
- `task-tracking.md` - Task tracking (background)
- `research.md` - Deep research (nested)
- `debugger.md` - Debugging (nested)
- `test-runner.md` - Test automation (nested)

## Benefits

- ✅ **Context Isolation** - Each subagent has clean context
- ✅ **Parallel Execution** - Multiple subagents can run simultaneously
- ✅ **Specialized Expertise** - Focused subagents = better results
- ✅ **Reusability** - Subagents work across projects
- ✅ **Modularity** - Easy to add new subagent types

## Task Execution Tracking

Task tracking is handled automatically by the `task-tracking` subagent:
- **Template**: `.agent/TASK_EXECUTION_TEMPLATE.md`
- **Location**: `.agent/tasks/TASK-[YYYY-MM-DD]-[TASK-ID].md`
- **Subagent**: `task-tracking` subagent handles all tracking automatically

**See**: [Subagent System](../docs/SUBAGENT_SYSTEM.md) for full architecture details.
