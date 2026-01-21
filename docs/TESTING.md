# Testing Strategy

Complete testing architecture for the Agent Factory.

## Test Counts by Layer

| Layer | Tests | Run Command |
|-------|-------|-------------|
| **Unit** | ~15 | `uv run pytest tests/unit` |
| **Agent** | 3 | `uv run pytest tests/agents` |
| **Integration** | 2 | `uv run pytest tests/integration` |
| **Dashboard API** | 15 | `uv run pytest tests/dashboard` |
| **Component** | 37 | `cd tools/dashboard && pnpm test` |
| **E2E** | 2 | `cd tools/dashboard && pnpm test:smoke` |

## Quick Commands

```bash
# All backend tests
uv run pytest

# All frontend tests
cd tools/dashboard && pnpm test run

# Full CI
uv run pytest && cd tools/dashboard && pnpm test run && pnpm lint
```

## Pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
