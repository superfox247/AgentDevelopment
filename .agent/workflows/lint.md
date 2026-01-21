---
description: Run Static Analysis and Linting
---

# Lint Workflow

> **Skill**: See `sdlc/review/SKILL.md` for review patterns

## Python

// turbo
```bash
uv run ruff check . --fix
```

## TypeScript

// turbo
```bash
cd tools/dashboard && pnpm lint
```

## Type Check

```bash
uv run mypy . && cd tools/dashboard && pnpm exec tsc --noEmit
```
