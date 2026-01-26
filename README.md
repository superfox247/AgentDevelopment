# Antigravity: Agentic Personal Assistant

**The "Super Powered IDE" that turns your local machine into an Enterprise-Grade Agent Cloud.**

> [!NOTE]
> This project evolves the concept of an AI coding assistant from a simple chat interface into a **Specialist Agent Orchestrator**. It runs a local fleet of Dockerized agents that perform background work (research, content creation, debugging) while you code.

## 🚀 Vision

Unlike typical AI tools that just generate text, Antigravity acts as a **Control Plane** for your digital life. It orchestrates a "Local Cloud" of services—Vector DBs, Graph DBs, and Specialist Agents—to deliver capabilities far beyond standard tools.

*   **Local Cloud**: Your machine acts as a private cloud region. Agents run as persistent Docker services.
*   **Hybrid Intelligence**: Combines massive online models (Gemini Ultra, GPT-4o) with high-speed local inference (Ollama/RTX 4090).
*   **Context Engineering**: A dedicated "Brain" manages long-term memory and project context using Knowledge Graphs.

## 📚 Documentation

### Core Documentation

| Document | Purpose |
| :--- | :--- |
| [**Architecture**](docs/ARCHITECTURE.md) | System design, components, and the "Local Cloud" topology. |
| [**Development**](docs/DEVELOPMENT.md) | Setting up the dev environment, building agents, and frontend workflow. |
| [**Standards**](docs/STANDARDS.md) | Coding style, API patterns, and the "Zero-Wrapper" policy. |
| [**Operations**](docs/OPERATIONS.md) | Running the stack, debugging, and infrastructure management. |
| [**Deployment**](docs/DEPLOYMENT.md) | Production deployment guide, security, and scaling. |
| [**Testing**](docs/TESTING.md) | Testing strategy, TDD workflow, and test coverage. |
| [**Config Files**](docs/CONFIG_FILES.md) | Configuration file reference and environment variables. |
| [**Cursor IDE**](docs/CURSOR_IDE.md) | IDE-specific setup and task configuration. |
| [**Roadmap**](docs/ROADMAP.md) | Future improvements and planned enhancements. |
| [**Technical Debt**](docs/TECHNICAL_DEBT.md) | Known technical debt and refactoring needs. |
| [**Improvement Organization**](docs/IMPROVEMENT_ORGANIZATION.md) | Strategy for organizing and tracking improvements. |

### Workflow Guides

| Document | Purpose |
| :--- | :--- |
| [**Main Development Workflow**](.agent/workflows/main-development.md) | Primary entry point for all development work - orchestrates complete lifecycle. |
| [**Agent Development**](.agent/workflows/agent-development.md) | Complete workflow for creating, extending, and maintaining agents. |
| [**Agent Testing Checklist**](.agent/workflows/agent-testing-checklist.md) | Testing checklist for agent development. |
| [**Workflow Index**](.agent/workflows/README.md) | Overview of all agentic development workflows. |

### Documentation Maintenance

- [**Doc maintenance**](docs/DOCUMENTATION_MAINTENANCE.md) - Strategy; root = `README.md` only
- [**Doc workflow**](.agent/workflows/documentation-maintenance.md) - Step-by-step for agents

**Note**: Summaries and reviews → `docs/archive/`. Use core docs for current info.

### Project Health & Improvement Tracking

- [**Changelog**](CHANGELOG.md) - History of changes
- [**Technical Debt**](docs/TECHNICAL_DEBT.md) - Known debt, refactors
- [**Improvement Organization**](docs/IMPROVEMENT_ORGANIZATION.md) - How we track improvements
- [**ADRs**](docs/adr/) - Architecture decisions
- [**System tracking & lessons**](.agent/system-tracking.md) - Runs, what worked, durable lessons

## ⚡ Quick Start

### Prerequisites
*   **Docker Desktop**: Running and configured.
*   **Python**: 3.11+
*   **Node.js**: 20+ (for Dashboard)
*   **NVIDIA GPU**: Recommended (RTX 4090) for local inference.

### Running the Stack

1.  **Install dependencies**:
    ```bash
    make install
    ```

2.  **Start the Local Cloud** (Docker containers):
    ```bash
    make dev-up
    ```
    This starts all Docker services and waits for them to be healthy.

3.  **Start the Dashboard** (API + UI in separate terminals):
    ```bash
    # Terminal 1: Dashboard API
    uv run python dashboard_api/server.py   # → port 8010
    
    # Terminal 2: Frontend
    cd frontend && pnpm dev                  # → port 5173
    ```

4.  **Access Agent Central**:
    Open `http://localhost:5173` to manage your fleet.

### Development Workflow

After making changes, reset and verify the dev environment:

```bash
# Reset dev environment (rebuilds containers, waits for health, shows logs)
make dev-reset

# Check health of all services (with status and logs)
make dev-health

# View logs from all services (live)
make dev-logs

# View recent logs (last 50 lines)
make dev-logs-recent

# Run full verification (lint, build, test, e2e)
make dev-verify
```

**Important**: Changes cannot be considered complete without:
- ✅ Lint/fix/build passing
- ✅ Unit tests passing
- ✅ E2E tests passing against Docker stack
- ✅ UI verification in browser
- ✅ Logs showing services started correctly

**Logging is integrated throughout the workflow** - you'll see container status, recent logs, and error details automatically during startup, health checks, and on failures. This ensures you can quickly identify and fix issues.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for complete Docker workflow details.

**Local agent dev (no Docker):** Run the researcher agent with `make playground-researcher` or `uv run adk web agents/researcher_agent`. See [agents/researcher_agent/README.md](agents/researcher_agent/README.md) and [.agent/workflows/agent-development.md](.agent/workflows/agent-development.md).

**Cursor IDE**: Use **Terminal → Run Task** (e.g. **Dashboard API**, **Frontend: dev**) or see [docs/CURSOR_IDE.md](docs/CURSOR_IDE.md).

## Licensed
Internal Tool - Do Not Distribute.
