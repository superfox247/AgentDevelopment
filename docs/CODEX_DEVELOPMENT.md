# Codex Development Guide

This guide focuses on the issues that commonly block full development loops in Codex-style environments.

## 1) Run preflight first

```bash
make codex-preflight
```

This validates:
- `uv`, `node`, and `pnpm`
- Docker availability and daemon access
- frontend dependency installation
- Playwright browser cache presence

## 2) Install dependencies

```bash
make install
```

## 3) Choose your workflow based on environment capability

### Full-stack workflow (Docker available)

```bash
make dev-up
uv run python dashboard_api/server.py
cd frontend && pnpm dev
```

### API + frontend workflow (no Docker)

Use this path in constrained Codex environments when Docker is unavailable.

```bash
uv run python dashboard_api/server.py
cd frontend && pnpm dev
```

Then run fast verification:

```bash
make frontend-lint
make type-check-frontend
make frontend-test
uv run pytest dashboard_api/tests/test_agents_router.py
```

## 4) Browser automation stability

If Playwright fails to launch browsers, run:

```bash
cd frontend
pnpm exec playwright install --with-deps chromium
```

If the environment still crashes Chromium (SIGSEGV or missing host libs), continue with component tests and API tests, and run E2E only in CI runners known to support Playwright.

## 5) Chat endpoint compatibility

`POST /api/chat/{name}` supports two modes:

- **Streaming (default):** NDJSON event stream for incremental frontend rendering
- **Legacy JSON:** `?stream=false` for clients expecting a single JSON response

Use legacy mode while migrating older scripts/clients.

## 6) Ongoing improvement backlog

Backlog is tracked in `.agent/issues.md` under **Discovery Backlog (Iterative)**.
Update this list as new constraints are discovered.
