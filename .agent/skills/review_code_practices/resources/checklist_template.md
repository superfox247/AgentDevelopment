# Code Review Checklist

## Setup
- [ ] **Context Loading**: Loaded `patterns/tech_stack.md`.
- [ ] **Pattern Check**: Checked for existing patterns for all technologies.

## Code Quality
- [ ] **Linting**: No lint errors (`npm run lint` / `ruff check`).
- [ ] **Imports**: No unused imports.
- [ ] **Types**: Type hints present and correct (Python).

## Architecture & Patterns
- [ ] **Separation of Concerns**: Logic separated from UI/Infrastructure.
- [ ] **Configuration**: No hardcoded secrets or config values (use env vars).
- [ ] **Error Handling**: Proper try/except and logging (no `print`).

## Specific Files
### [File 1]
- [ ] Checked against `patterns/[tech].md`.
- [ ] Specific Logic verified.

### [File 2]
- [ ] Checked against `patterns/[tech].md`.
- [ ] Specific Logic verified.
