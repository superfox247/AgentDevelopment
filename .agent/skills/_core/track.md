---
name: Task Tracker
description: Track all work through structured task management
---

# Task Tracker

## Purpose
All work flows through task tracking. No untracked changes.

## Task States

```
[ ] Pending
[/] In Progress
[x] Complete
[!] Blocked
[-] Cancelled
```

## Task File Location

```
.agent/tracking/
├── active.md           # Current session tasks
├── backlog.md          # Pending work
└── archive/
    └── YYYY-MM-DD.md   # Completed tasks
```

## Task Format

```markdown
## [Task ID] - [Title]

**Product**: dashboard | course_creator | platform
**Branch**: develop | test | review | ...
**Status**: [/]
**Started**: 2026-01-20T22:15:00Z

### Objective
What needs to be done

### Checklist
- [x] Step 1
- [/] Step 2
- [ ] Step 3

### Artifacts
- Created: `path/to/file.ts`
- Modified: `path/to/other.py`

### Notes
Any relevant context
```

## Auto-Tracking

1. **On Task Start**: Create entry in active.md
2. **On File Change**: Add to Artifacts list
3. **On Task Complete**: Move to archive, update knowledge

## Integration

- `task_boundary` tool → updates active.md
- Skill execution → logs under current task
- Knowledge updates → link to originating task
