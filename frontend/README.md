# Developer Dashboard

This directory contains the source code for the Antigravity Developer Dashboard, a hybrid application serving as the control plane for the Agent Development Factory.

## Architecture

The dashboard frontend is a React + Vite Single Page Application (SPA) that provides the UI for managing agents, viewing artifacts, and monitoring system status.

**Note**: The backend API has been moved to `dashboard_api/` for better separation of concerns. See [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for details.

## Directory Structure

-   `src/`: React source code.
    -   `components/`: Reusable UI components and specific views (Models, Artifacts, etc.).
    -   `App.tsx`: Main routing and layout logic.
    -   `api/`: API client and schemas for communicating with the backend.
-   `package.json`: Frontend dependencies and scripts.

## Setup & Running

1.  **Install Frontend Dependencies**:
    ```bash
    pnpm install
    ```

2.  **Run Development** (two processes):
    - **Dashboard API** (from repo root): `uv run python dashboard_api/server.py` → port 8010
    - **Frontend**: `pnpm dev` → port 5173, proxies `/api` to 8010

3.  **Cursor IDE**: See [CURSOR_IDE.md](../docs/CURSOR_IDE.md) for tasks and troubleshooting.

## features

-   **Model Explorer**: View available Gemini models and their limits.
-   **Agent Generator**: Interface for the Course Creator agents.
-   **Artifact Viewer**: Browse and view generated markdown and images.
-   **System Status**: Monitor Docker containers and service health.
-   **Benchmarks**: Run and view performance benchmarks.

