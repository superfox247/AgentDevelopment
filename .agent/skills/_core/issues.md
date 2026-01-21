---
name: Issue Tracker
description: Logs problems agents encounter for continuous improvement
---

# Issue Tracker

## Purpose
Track problems agents encounter so skills can be improved.

## Issue Log Location
`.agent/tracking/issues.md`

## What to Log

| Category | Examples |
|----------|----------|
| **Command Failures** | `pnpm` not found, build errors |
| **Missing References** | Skill paths that don't exist |
| **Type Errors** | Mock data missing fields |
| **API Mismatches** | Frontend/backend contract issues |
| **Skill Gaps** | No skill covers the task |

## Issue Format

```markdown
## [Date] - [Category] - [Brief Title]

**Context**: What was being attempted
**Error**: Exact error message or symptom
**Root Cause**: Why it happened (if known)
**Resolution**: How it was fixed
**Skill Update**: Which skill should be updated to prevent this
**Status**: open | pending-review | resolved | wontfix
```

## Auto-Logging Protocol

When encountering issues:
1. Log immediately to `issues.md`
2. Continue with workaround if possible
3. Mark for skill improvement
4. **Run Pre-Update Review** → `_core/review_skill.md` (automated)
5. Apply skill update based on review decision

## Review Cycle

Weekly: Review open issues → Update skills → Close resolved
