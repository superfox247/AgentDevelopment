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

### Workflow Guides

| Document | Purpose |
| :--- | :--- |
| [**Agent Development**](.agent/workflows/agent-development.md) | Complete workflow for creating, extending, and maintaining agents. |
| [**Agent Testing Checklist**](.agent/workflows/agent-testing-checklist.md) | Testing checklist for agent development. |

### Documentation Maintenance

- [**Documentation Maintenance Strategy**](docs/DOCUMENTATION_MAINTENANCE.md) - Guidelines and principles for documentation maintenance
- [**Documentation Maintenance Workflow**](.agent/workflows/documentation-maintenance.md) - Step-by-step workflow for agents to maintain documentation

**Note**: Work-in-progress summaries and review documents are archived in `docs/archive/`. For current information, always refer to the core documentation above.

## ⚡ Quick Start

### Prerequisites
*   **Docker Desktop**: Running and configured.
*   **Python**: 3.11+
*   **Node.js**: 20+ (for Dashboard)
*   **NVIDIA GPU**: Recommended (RTX 4090) for local inference.

### Running the Stack

1.  **Start the Local Cloud**:
    ```bash
    docker-compose up -d
    ```

2.  **Start the Dashboard** (API + UI):
    ```bash
    uv sync --dev
    cd frontend && pnpm install && cd ..
    uv run python frontend/server.py   # Terminal 1 → port 8010
    cd frontend && pnpm dev            # Terminal 2 → port 5173
    ```

3.  **Access Agent Central**:
    Open `http://localhost:5173` to manage your fleet.

**Local agent dev (no Docker):** Run the researcher agent with `make playground-researcher` or `uv run adk web agents/researcher_agent`. See [agents/researcher_agent/README.md](agents/researcher_agent/README.md) and [.agent/workflows/agent-development.md](.agent/workflows/agent-development.md).

**Cursor IDE**: Use **Terminal → Run Task** (e.g. **Dashboard API**, **Frontend: dev**) or see [docs/CURSOR_IDE.md](docs/CURSOR_IDE.md).

## Licensed
Internal Tool - Do Not Distribute.
