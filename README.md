# Antigravity Agent Platform

Welcome to the **Antigravity Agent Platform**, a high-performance, local-first AI development environment designed for agentic workflows.

## 📖 Key Documentation
- **Constitution**: [GEMINI.md](./GEMINI.md) - The immutable laws and operational rules of the factory.
- **API Standards**: [docs/api_standards.md](./docs/api_standards.md) - The Envelope Pattern & SSE protocols.
- **UX Patterns**: [docs/ux_patterns.md](./docs/ux_patterns.md) - Antigravity Prime Design System.
- **Tech Stack**: [docs/tech_stack.md](./docs/tech_stack.md) - React 19 & Tailwind v4 architecture.
- **Models**: [docs/available_models.md](./docs/available_models.md) - Catalogue of available AI models (Gemini/Imagen/Veo).

## 🚀 Quick Start
1.  **Environment Setup**:
    ```powershell
    # Install dependencies
    uv sync
    npm install --prefix tools/dashboard
    ```
2.  **Launch Platform**:
    ```powershell
    # Start Backend & Dashboard
    uv run adk start
    ```

3.  **Verify System**:
    ```powershell
    uv run adk debug
    ```

## 🛠️ Developer Tools (ADK)
This project uses a custom CLI: `adk`.
*   `uv run adk list` - List agents.
*   `uv run adk test` - Run tests.
*   `uv run adk stop` - Stop platform.
*   `uv run adk reset` - Reset env.

## 🏗️ Architecture
The platform follows the **"Thin Agent"** architecture:
-   **Agents**: Thin logic wrappers in `domains/`.
-   **Platform Core**: Shared infrastructure in `agent_platform/`.
-   **Observability**: Centralized dashboard for logs and metrics.
-   **Skills**: Modular capabilities in `.agent/skills/`.

## 🤝 Contributing
All code changes must adhere to the standards defined in `GEMINI.md` and pass the [Code Review Skill](.agent/skills/review_code/SKILL.md) protocols.
