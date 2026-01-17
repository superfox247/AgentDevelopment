---
name: Smart Lint
description: A unified skill to run static analysis (codespell, ruff, mypy) with one command.
---

# Smart Lint

"Clean code is happy code." Use this skill to ensure the codebase meets standards.

## 2. Code Style & Quality (The Law)
**Authority**: These rules are enforced by `ruff` and `mypy`.

### Python Standards
*   **Style**: PEP8.
*   **Formatting**: Auto-formatted on save (Black/Ruff formatter).
*   **Imports**: Sorted and grouped (isort/Ruff).
*   **Quotes**: Double quotes `"` preferred.

### Typing Standards
*   **Strictness**: `mypy --strict`. All functions MUST have type hints.
*   **No Any**: Avoid `Any`. Use `Protocol` or `TypedDict` for duck typing.

## 3. Cognitive Heuristics
**When to use:**
- Before pushing code.
- When "lint" or "formatting" errors occur.
- Use `--fix` to auto-repair.

## 2. Load Context
- `.agent/skills/smart_lint/smart_lint.py`

## 3. Usage
Check for errors:
```bash
uv run .agent/skills/smart_lint/smart_lint.py
```

Auto-fix:
```bash
uv run .agent/skills/smart_lint/smart_lint.py --fix
```
