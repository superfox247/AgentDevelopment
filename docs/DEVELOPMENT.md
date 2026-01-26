# Development Guide

> **Last verified**: 2026-01-25

## 🛠 Prerequisites

Ensure you have the following installed:
*   **Docker Desktop**: Enabled with GPU support if available.
*   **Python 3.11+**: We recommend `uv` for package management.
*   **Node.js 20+**: For the Dashboard frontend.

## 🚀 The "Dev -> Deploy" Workflow

We treat local agents like microservices. You build them in the IDE, test them locally, and then "deploy" them to your local Docker stack.

1.  **Create/Modify Agent**: Work in `agents/<agent_name>/`. Follow the [agent-development workflow](../.agent/workflows/agent-development.md) for structure, tools, callbacks, evals, and collocated unit tests (`agents/<agent_name>/tests/`).
2.  **Test Logic**: Unit tests live under `agents/<agent_name>/tests/` (collocated). Repo-level integration tests live in `tests/` where applicable.
3.  **Build Container**:
    ```bash
    docker build -t local-agent-name .
    ```
4.  **Run in Stack**: Update `docker-compose.yml` to include your new service.

## 🐳 Docker Development Workflow

Docker is central to this codebase. After making changes, you need to reset and verify the deployed dev environment. The Makefile provides comprehensive Docker workflow commands.

### Quick Commands

```bash
# Reset dev environment (stop, rebuild, start, wait for health)
make dev-reset

# Start dev stack (Docker containers)
make dev-up

# Stop dev stack
make dev-down

# Check health of all services
make dev-health

# View logs from all services (live/follow mode)
make dev-logs

# View recent logs from all services (last 50 lines)
make dev-logs-recent

# View logs from a specific service (live/follow mode)
make dev-logs-service SERVICE=phoenix

# View recent logs from a specific service
make dev-logs-service-recent SERVICE=phoenix

# Build all Docker services
make dev-build

# Full verification: lint, build, test, e2e
make dev-verify
```

### Logging and Feedback

All commands now include comprehensive logging as part of the feedback loop:

- **During startup**: Commands show container status and recent logs automatically
- **During health checks**: Logs are displayed periodically (every 30s) and on failure
- **On failure**: Recent logs (50-100 lines) are automatically shown for debugging
- **Manual inspection**: Use `dev-logs` commands to view logs anytime

**Example workflow with logging:**
```bash
# Start stack - logs shown during startup
make dev-up
# Output includes:
# - Container status
# - Recent logs (last 10 lines)
# - Periodic status updates during health check
# - Final container status

# If something fails, logs are automatically shown
# You can also manually check:
make dev-logs-recent          # See what happened recently
make dev-logs-service SERVICE=phoenix  # Focus on specific service
```

**Note on API and Frontend Server Logs:**

The Docker container logs are automatically shown, but the API and Frontend servers run as separate processes:

- **Dashboard API** (`uv run python dashboard_api/server.py`): Logs appear in the terminal where you run it
- **Frontend Dev Server** (`cd frontend && pnpm dev`): Logs appear in the terminal where you run it

For production-like testing, both servers should be running in separate terminals so you can see their logs in real-time. The health check and e2e tests verify these services are accessible.

### Complete Development Cycle

After making changes to code, Docker containers, or configuration:

1. **Reset the environment**:
   ```bash
   make dev-reset
   ```
   This will:
   - Stop all containers
   - Remove volumes (clean state)
   - Rebuild all images (no cache)
   - Start containers
   - Wait for services to be healthy

2. **Start API and Frontend** (in separate terminals):
   ```bash
   # Terminal 1: Dashboard API
   uv run python dashboard_api/server.py
   
   # Terminal 2: Frontend
   cd frontend && pnpm dev
   ```

3. **Verify everything works**:
   ```bash
   make dev-health
   ```

4. **Run full verification** (lint, build, test, e2e):
   ```bash
   make dev-verify
   ```

### E2E Testing Against Docker Stack

To run end-to-end tests against the actual Docker stack (not just the dev server):

1. **Ensure dev stack is running**:
   ```bash
   make dev-up
   # Start API and frontend in separate terminals
   ```

2. **Run e2e tests**:
   ```bash
   make frontend-e2e-docker
   # Or manually:
   cd frontend && pnpm exec playwright test --config=playwright.docker.config.ts
   ```

The Docker-based e2e tests:
- Verify services are healthy before running
- Test against the actual deployed stack
- Use the production-like environment
- Can be run in CI/CD pipelines

### Health Check Utility

A Python script is available for programmatic health checks with built-in logging:

```bash
# Check all services (120s timeout, shows logs automatically)
python scripts/health_check.py

# Custom timeout
python scripts/health_check.py --timeout 60

# Check only API services (skip Docker containers)
python scripts/health_check.py --api-only

# Check specific service
python scripts/health_check.py --service dashboard_api

# Disable automatic log display
python scripts/health_check.py --no-logs

# Custom log display interval (default: 30s)
python scripts/health_check.py --log-interval 15
```

The health check script automatically:
- Shows initial container status and logs
- Displays logs periodically during wait (every 30s by default)
- Shows final logs on timeout or failure
- Provides clear feedback on service status

### Docker stack vs. local agent dev

The full Docker stack (`docker compose up`) expects agents in the `agents/` directory. For **local agent development without Docker**:

*   **Researcher agent**: `make playground-researcher` or `uv run adk web agents/researcher_agent --port 8501`. No Docker required; set `GOOGLE_API_KEY` in `agents/researcher_agent/.env`.
*   **Other agents**: Use `uv run adk web agents/<agent_name>` from the repo root. See the [agent-development workflow](../.agent/workflows/agent-development.md) and [researcher_agent](../agents/researcher_agent/README.md) for structure and run instructions.

## 🖥 Frontend Development (Dashboard)

The Dashboard is a modern React v19 application located in `frontend/`.

### Tech Stack
*   **Framework**: React v19 + Vite.
*   **Styling**: Tailwind CSS v4.
*   **State**: React Query (Server State) + React Context (UI State).

### Usage Standards
*   **Components**: Use functional components with TypeScript interfaces.
*   **Styling**: Use utility classes (Tailwind). Avoid custom CSS files unless necessary (`index.css` handles theme).
*   **API**: Use the centralized `apiClient` (`src/api/client.ts`). Do not use `fetch` directly in components.

### Running Frontend
```bash
cd frontend
pnpm install
pnpm dev
```
The Dashboard UI (port 5173) proxies `/api` to the FastAPI backend. Run `uv run python dashboard_api/server.py` from the repo root for the API (port 8010).

**Cursor IDE**: Use **Terminal → Run Task** (e.g. **Frontend: dev**, **Dashboard API**) or see [CURSOR_IDE.md](CURSOR_IDE.md).

## 🧪 Testing Strategy

> [!IMPORTANT]
> A comprehensive testing guide is available in [TESTING.md](TESTING.md).

We follow a strict **Test-Driven Development (TDD)** approach with **Colocated Unit Tests**.

1.  **Unit Tests (Backend)**: Colocated with source code (e.g., `agent_platform/test_config.py`).
2.  **Frontend Tests**: Vitest for components, Playwright for E2E.
3.  **Integration**: See `TESTING.md` for details.

### E2E Testing with Docker

E2E tests can run in two modes:

1. **Dev Server Mode** (default): Tests against `pnpm dev` server
   ```bash
   cd frontend && pnpm test:e2e
   ```

2. **Docker Stack Mode**: Tests against the full deployed Docker stack
   ```bash
   make frontend-e2e-docker
   ```

The Docker stack mode is required for:
- Verifying changes work in the actual deployed environment
- Testing agent interactions through Docker containers
- CI/CD pipeline validation
- Production-like testing scenarios

**Important**: Changes cannot be considered complete without verification through the Docker stack and successful e2e tests.
