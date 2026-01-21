# Antigravity Agent Platform

Welcome to the **Antigravity Agent Platform**, a high-performance, local-first AI development environment designed for agentic workflows.

## 📖 Key Documentation
- **Constitution**: [GEMINI.md](./GEMINI.md) - The immutable laws and operational rules of the factory.
- **API Standards**: [docs/api_standards.md](./docs/api_standards.md) - The Envelope Pattern & SSE protocols.
- **UX Patterns**: [docs/ux_patterns.md](./docs/ux_patterns.md) - Antigravity Prime Design System.
- **Tech Stack**: [docs/tech_stack.md](./docs/tech_stack.md) - React 19 & Tailwind v4 architecture.
- **Models**: [docs/available_models.md](./docs/available_models.md) - Catalogue of available AI models.

## 🚀 Quick Start

1. **Environment Setup**:
   ```bash
   uv sync
   cd tools/dashboard && pnpm install
   ```

2. **Launch Platform**:
   ```bash
   docker compose up -d          # Start agents
   cd tools/dashboard && pnpm dev  # Start dashboard
   ```

3. **Run Tests**:
   ```bash
   uv run pytest
   ```

## 🛠️ Developer Commands

All development operations use workflows (`.agent/workflows/`) or direct commands:

| Action | Command |
|--------|---------|
| **Build** | `/build` workflow or `uv sync && docker compose build` |
| **Test** | `/test` workflow or `uv run pytest` |
| **Lint** | `/lint` workflow or `uv run ruff check .` |
| **Start** | `docker compose up -d` |
| **Stop** | `docker compose down` |
| **Reset** | `docker compose down -v && docker compose build --no-cache` |
| **Debug** | Check `docker ps -a` and container logs |

## 🏗️ Architecture
The platform follows the **"Thin Agent"** architecture:
- **Agents**: Thin logic wrappers in `domains/`
- **Platform Core**: Shared infrastructure in `agent_platform/`
- **Dashboard**: Monitoring UI in `tools/dashboard/`
- **Skills**: Modular capabilities in `.agent/skills/`

## 🤝 Contributing
All code changes must adhere to the standards defined in `GEMINI.md` and pass the skill protocols.
