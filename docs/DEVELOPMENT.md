# Development Guide

## 🛠 Prerequisites

Ensure you have the following installed:
*   **Docker Desktop**: Enabled with GPU support if available.
*   **Python 3.11+**: We recommend `uv` for package management.
*   **Node.js 20+**: For the Dashboard frontend.

## 🚀 The "Dev -> Deploy" Workflow

We treat local agents like microservices. You build them in the IDE, test them locally, and then "deploy" them to your local Docker stack.

1.  **Create/Modify Agent**: Work in `agents/<agent_name>/`.
2.  **Test Logic**: distinct unit tests in `tests/`.
3.  **Build Container**:
    ```bash
    docker build -t local-agent-name .
    ```
4.  **Run in Stack**: Update `docker-compose.yml` to include your new service.

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
npm install
npm run dev
```

## 🧪 Testing Strategy

> [!IMPORTANT]
> A comprehensive testing guide is available in [TESTING.md](TESTING.md).

We follow a strict **Test-Driven Development (TDD)** approach with **Colocated Unit Tests**.

1.  **Unit Tests (Backend)**: Colocated with source code (e.g., `agent_platform/test_config.py`).
2.  **Frontend Tests**: Vitest for components, Playwright for E2E.
3.  **Integration**: See `TESTING.md` for details.
