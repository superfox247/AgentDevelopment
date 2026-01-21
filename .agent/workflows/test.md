---
description: Standard Testing Workflow
---

# Testing Workflow

> **Skill**: See `sdlc/test/SKILL.md` for test patterns

## Quick Commands

// turbo-all

### Backend (Python)
```bash
uv run pytest tests/unit
```

### Frontend (Dashboard)
```bash
cd tools/dashboard && pnpm test run
```

### All Tests
```bash
uv run pytest && cd tools/dashboard && pnpm test run
```

## Product-Specific

| Product | Command |
|---------|---------|
| course_creator | `uv run pytest tests/agents` |
| dashboard | `cd tools/dashboard && pnpm test` |
