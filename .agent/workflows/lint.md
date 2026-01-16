---
description: Run Static Analysis and Linting
---

# Linting Workflow

Ensure code quality before committing. This runs `ruff` (formatting/linting), `mypy` (types), and `codespell` (typos).

## 1. Run All Checks

// turbo
```bash
make lint
```

## 2. Fix Formatting Issues
If `ruff` complains, you can auto-fix many issues:

```bash
uv run ruff format .
uv run ruff check . --fix
```
