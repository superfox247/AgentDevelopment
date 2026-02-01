# Task Execution Summaries

This directory contains detailed task execution summaries generated automatically during development work.

## Purpose

Task execution summaries provide comprehensive tracking of:
- Complete workflow execution
- Decisions made and rationale
- Workflow switches and context management
- Issues encountered and resolutions
- Phase-by-phase progress
- Final metrics and lessons learned

## Naming Convention

Task summaries follow the format: `TASK-[YYYY-MM-DD]-[TASK-ID].md`

Examples:
- `TASK-2026-01-26-image-gen-agent.md`
- `TASK-2026-01-27-api-refactor.md`
- `TASK-2026-01-28-frontend-component.md`

## Template

All task summaries are created from: `.agent/TASK_EXECUTION_TEMPLATE.md`

## Integration

Task summaries are:
- **Created automatically** at task start (from template)
- **Updated continuously** during workflow execution
- **Finalized** at task completion
- **Linked** in `.agent/system-tracking.md`
- **Referenced** for lessons learned and patterns

## Usage

When starting a new task:
1. Create task summary from template
2. Fill in task overview
3. Follow workflows (they automatically update the summary)
4. Complete final summary at task end
5. Link in system tracking

Task tracking is handled automatically by the `task-tracking` subagent (`.cursor/agents/task-tracking.md`). See [Subagent System](../docs/SUBAGENT_SYSTEM.md) for architecture details.
