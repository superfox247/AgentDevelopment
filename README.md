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
| [**Documentation Index**](docs/README.md) | Canonical map of current docs and compatibility aliases. |
| [**Platform Guide**](docs/PLATFORM_GUIDE.md) | Architecture, CI/CD, deployment, operations, and runbooks. |
| [**Product Features Guide**](docs/PRODUCT_FEATURES.md) | Detailed feature behavior, flows, and capability coverage. |
| [**Diagram Index**](docs/DIAGRAMS.md) | Diagram-first index of system, feature, CI/CD, and roadmap flows. |
| [**Refactoring & Simplification**](docs/REFACTORING_SIMPLIFICATION.md) | Prioritized simplification backlog discovered during docs consolidation. |
| [**Standards**](docs/STANDARDS.md) | Coding style, API patterns, and the "Zero-Wrapper" policy. |
| [**Config Files**](docs/setup/CONFIG_FILES.md) | Configuration file reference and environment variables. |
| [**Roadmap**](docs/ROADMAP.md) | Future improvements, planned enhancements, and improvement organization strategy. |
| [**Technical Debt**](docs/TECHNICAL_DEBT.md) | Known technical debt and refactoring needs. |
| [**Codex Development**](docs/setup/CODEX_DEVELOPMENT.md) | Running productive dev loops in Codex/constrained environments. |

### Documentation Maintenance

- [**Documentation Index**](docs/README.md) - Canonical docs and compatibility redirects.

**Note**: Summaries and reviews → `docs/archive/`. Use core docs for current info.

### Project Health & Improvement Tracking

- [**Changelog**](CHANGELOG.md) - History of changes
- [**Technical Debt**](docs/TECHNICAL_DEBT.md) - Known debt, refactors
- [**Improvement Organization**](docs/ROADMAP.md#-improvement-organization) - How we track improvements
- [**ADRs**](docs/adr/) - Architecture decisions
- [**System tracking & lessons**](.agent/system-tracking.md) - Runs, what worked, durable lessons

## ⚡ Quick Start

### Prerequisites
*   **Docker Desktop**: Running and configured.
*   **Python**: 3.11+
*   **Node.js**: 20+ (for Dashboard)
*   **NVIDIA GPU**: Recommended (RTX 4090) for local inference.

### Running the Stack

> [!NOTE]
> **Windows Users**: Use the `.ps1` PowerShell scripts. Unix/Mac users use the `.sh` shell scripts.
> All commands work identically across platforms.

1.  **Install dependencies**:
    ```bash
    # Unix/Linux/Mac
    ./setup.sh
    
    # Windows PowerShell
    .\setup.ps1
    ```

2.  **Start the Local Cloud** (Docker containers):
    ```bash
    # Unix/Linux/Mac
    ./dev.sh up
    
    # Windows PowerShell
    .\dev.ps1 up
    ```
    This starts all Docker services and waits for them to be healthy.

3.  **Start the Dashboard** (API + UI in separate terminals):
    ```bash
    # Terminal 1: Dashboard API
    uv run python dashboard_api/server.py   # → port 8010
    
    # Terminal 2: Frontend
    cd frontend && pnpm dev                  # → port 5173
    ```

4.  **Open the Dashboard**:
    Open `http://localhost:5173` to chat with the Researcher or Customer Service agent.

### Development Workflow

**Dev environment management:**
```bash
# Unix/Linux/Mac
./dev.sh up           # Start containers
./dev.sh down         # Stop containers
./dev.sh reset        # Reset (rebuild, restart, health check)
./dev.sh health       # Check service health
./dev.sh logs         # Follow live logs
./dev.sh logs-recent  # Show last 50 lines

# Windows PowerShell
.\dev.ps1 up
.\dev.ps1 down
.\dev.ps1 reset
.\dev.ps1 health
.\dev.ps1 logs
.\dev.ps1 logs-recent
```

**Code quality checks:**
```bash
# Unix/Linux/Mac
./lint.sh all       # Lint + type check (backend + frontend)
./lint.sh fix       # Auto-fix linting issues
./lint.sh check     # Backend check only

# Windows PowerShell
.\lint.ps1 all
.\lint.ps1 fix
.\lint.ps1 check
```

**Testing:**
```bash
# Unix/Linux/Mac
./test.sh backend       # Backend tests (full)
./test.sh backend-fast  # Backend tests (skip evals)
./test.sh frontend      # Frontend component tests
./test.sh e2e           # Frontend e2e tests (requires dev stack)
./test.sh all           # All tests

# Windows PowerShell
.\test.ps1 backend
.\test.ps1 backend-fast
.\test.ps1 frontend
.\test.ps1 e2e
.\test.ps1 all
```

**Important**: Changes cannot be considered complete without:
- ✅ Lint/fix/build passing
- ✅ Unit tests passing
- ✅ E2E tests passing against Docker stack
- ✅ UI verification in browser
- ✅ Logs showing services started correctly

**Logging is integrated throughout the workflow** - you'll see container status, recent logs, and error details automatically during startup, health checks, and on failures. This ensures you can quickly identify and fix issues.

See [docs/PLATFORM_GUIDE.md](docs/PLATFORM_GUIDE.md) for complete Docker workflow and operations details.

**Local agent dev (no Docker):** Run the researcher agent with `uv run adk web agents/researcher_agent`. See [agents/researcher_agent/README.md](agents/researcher_agent/README.md) for structure and run instructions.

**Cursor IDE**: Use **Terminal → Run Task** (e.g. **Dashboard API**, **Frontend: dev**). See [Platform Guide](docs/PLATFORM_GUIDE.md) for the canonical runbook. You can also run scripts directly:
- `./dev.sh up` or `.\dev.ps1 up` (Windows) to start containers
- `./lint.sh all` or `.\lint.ps1 all` to run code quality checks
- `./test.sh backend` or `.\test.ps1 backend` to run tests

## Licensed
Internal Tool - Do Not Distribute.
