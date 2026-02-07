# Automated Task Execution Tracking

**Status**: Implemented | **Last Updated**: 2026-01-26

## Overview

Automatic task execution tracking generates detailed summaries as agents execute tasks, providing visibility into decisions, workflows, issues, context management, and metrics.

## Components

- **Template**: `.agent/TASK_EXECUTION_TEMPLATE.md` - Task summary template
- **Subagent**: `task-tracking` subagent (`.cursor/agents/task-tracking.md`) - Handles tracking automatically
- **Storage**: `.agent/tasks/` - Task summaries (`TASK-[YYYY-MM-DD]-[ID].md`)

## Usage

1. **Start**: Copy template to `.agent/tasks/TASK-[DATE]-[ID].md`, fill initial sections
2. **During**: Record decisions/issues immediately; update progress periodically
3. **Complete**: Fill remaining sections, calculate metrics, update `.agent/system-tracking.md`

## Tracking Format

**Decisions**: Options considered, decision, rationale, result  
**Workflow Switches**: Trigger, from/to, context maintained  
**Issues**: Status, description, resolution (recorded in both `issues.md` and task summary)  
**Context**: Size/complexity, what's carried/discarded at phase boundaries

## Integration

- **Issues**: Documented in both `issues.md` and task summary
- **System Tracking**: Task summaries linked in `system-tracking.md`
- **Documentation**: Task findings update core docs

---

**See**: [Subagent System](SUBAGENT_SYSTEM.md) for architecture details. Task tracking is handled automatically by the `task-tracking` subagent.
