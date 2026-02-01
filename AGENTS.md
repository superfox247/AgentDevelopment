# Agent Instructions

**⚠️ Use the Orchestrator subagent for all development work. The orchestrator delegates to specialized subagents.**

## Entry Point

The orchestrator subagent (`.cursor/agents/orchestrator.md`) handles all work by delegating to specialized subagents:
- **Understanding** → `understanding` subagent
- **Development** → `development` subagent
- **Code Quality** → `code-quality` subagent
- **Testing** → `testing` subagent
- **Verification** → `verification` subagent
- **Task Tracking** → `task-tracking` subagent (automatic, background)

## Execution Phases

Understanding → Development → Code Quality → Testing → Verification

The orchestrator automatically coordinates these phases by delegating to the appropriate subagents.

## Quick Reference

- **Subagents**: `.cursor/agents/` - Subagent definitions
- **Commands**: `docs/COMMANDS.md` - Command reference for subagents (Makefile commands)
- **Task Tracking**: Automatic via `task-tracking` subagent
- **Standards**: `docs/STANDARDS.md`
- **Testing**: `docs/TESTING.md`
- **Issues**: `.agent/issues.md`

**See**: [Subagent System](docs/SUBAGENT_SYSTEM.md) for full architecture details.
