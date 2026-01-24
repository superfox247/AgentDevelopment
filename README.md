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

| Document | Purpose |
| :--- | :--- |
| [**Architecture**](docs/ARCHITECTURE.md) | System design, components, and the "Local Cloud" topology. |
| [**Development**](docs/DEVELOPMENT.md) | Setting up the dev environment, building agents, and frontend workflow. |
| [**Standards**](docs/STANDARDS.md) | Coding style, API patterns, and the "Zero-Wrapper" policy. |
| [**Operations**](docs/OPERATIONS.md) | Running the stack, debugging, and infrastructure management. |

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

2.  **Start the Dashboard**:
    ```bash
    cd tools/dashboard
    npm run dev
    ```

3.  **Access Agent Central**:
    Open `http://localhost:5173` to manage your fleet.

## Licensed
Internal Tool - Do Not Distribute.
