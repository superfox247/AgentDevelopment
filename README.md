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
| [**Refactoring & Simplification**](docs/REFACTORING_SIMPLIFICATION.md) | Prioritized simplification backlog discovered during docs consolidation. |
| [**Standards**](docs/STANDARDS.md) | Coding style, API patterns, and the "Zero-Wrapper" policy. |
| [**Config Files**](docs/CONFIG_FILES.md) | Configuration file reference and environment variables. |
| [**Roadmap**](docs/ROADMAP.md) | Future improvements, planned enhancements, and improvement organization strategy. |
| [**Technical Debt**](docs/TECHNICAL_DEBT.md) | Known technical debt and refactoring needs. |
| [**Codex Development**](docs/CODEX_DEVELOPMENT.md) | Running productive dev loops in Codex/constrained environments. |

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
*   **make** (Windows users): Install via `.\setup-make-windows.ps1` or see [Windows Setup Guide](docs/WINDOWS_SETUP.md)

### Running the Stack

> [!NOTE]
> **Windows Users**: 
> - **Option 1 (Recommended)**: Install `make` using `.\setup-make-windows.ps1` - then use standard `make` commands
> - **Option 2**: Use `.\make.ps1` instead of `make` - see [Windows Compatibility Guide](docs/WINDOWS_COMPATIBILITY.md)
> - See [Windows Setup Guide](docs/WINDOWS_SETUP.md) for all options

1.  **Install dependencies**:
    ```bash
    # Unix/Linux/Mac
    make install
    
    # Windows (after installing make)
    make install
    
    # Windows (if make not installed, use PowerShell script)
    .\make.ps1 install
    ```
    
    **Windows users**: First install `make` by running `.\setup-make-windows.ps1`

2.  **Start the Local Cloud** (Docker containers):
    ```bash
    # All platforms (after installing make on Windows)
    make dev-up
    ```
    This starts all Docker services and waits for them to be healthy.
    
    **Windows users**: If `make` is not installed, use `.\make.ps1 dev-up` instead.

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

After making changes, reset and verify the dev environment:

```bash
# Unix/Linux/Mac
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

```powershell
# Windows PowerShell
# Reset dev environment (rebuilds containers, waits for health, shows logs)
.\make.ps1 dev-reset

# Check health of all services (with status and logs)
.\make.ps1 dev-health

# View logs from all services (live)
.\make.ps1 dev-logs

# View recent logs (last 50 lines)
.\make.ps1 dev-logs-recent

# Run full verification (lint, build, test, e2e)
.\make.ps1 dev-verify
```

**Important**: Changes cannot be considered complete without:
- ✅ Lint/fix/build passing
- ✅ Unit tests passing
- ✅ E2E tests passing against Docker stack
- ✅ UI verification in browser
- ✅ Logs showing services started correctly

**Logging is integrated throughout the workflow** - you'll see container status, recent logs, and error details automatically during startup, health checks, and on failures. This ensures you can quickly identify and fix issues.

See [docs/PLATFORM_GUIDE.md](docs/PLATFORM_GUIDE.md) for complete Docker workflow and operations details.

**Local agent dev (no Docker):** Run the researcher agent with `make playground-researcher` (Unix) or `.\make.ps1 playground-researcher` (Windows), or `uv run adk web agents/researcher_agent`. See [agents/researcher_agent/README.md](agents/researcher_agent/README.md) for structure and run instructions.

**Cursor IDE**: Use **Terminal → Run Task** (e.g. **Dashboard API**, **Frontend: dev**). See [Platform Guide](docs/PLATFORM_GUIDE.md) for the canonical runbook.

## Licensed
Internal Tool - Do Not Distribute.
