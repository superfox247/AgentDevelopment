# Developer Dashboard

This directory contains the source code for the Antigravity Developer Dashboard, a hybrid application serving as the control plane for the Agent Development Factory.

## Architecture

The dashboard consists of two parts:
1.  **Frontend (`src/`)**: A React + Vite Single Page Application (SPA) that provides the UI for managing agents, viewing artifacts, and monitoring system status.
2.  **Backend (`server.py`)**: A lightweight FastAPI server that bridges the frontend with the local file system, Docker runtime, and Agent Platform.

## Directory Structure

-   `src/`: React source code.
    -   `components/`: Reusable UI components and specific views (Models, Artifacts, etc.).
    -   `App.jsx`: Main routing and layout logic.
-   `server.py`: Python backend server.
-   `package.json`: Frontend dependencies and scripts.

## Setup & Running

1.  **Install Frontend Dependencies**:
    ```bash
    npm install
    ```

2.  **Run Development Server**:
    This command runs both the backend (on port 8010) and frontend (on port 5173).
    ```bash
    npm run dev
    ```

## features

-   **Model Explorer**: View available Gemini models and their limits.
-   **Agent Generator**: Interface for the Course Creator agents.
-   **Artifact Viewer**: Browse and view generated markdown and images.
-   **System Status**: Monitor Docker containers and service health.
-   **Benchmarks**: Run and view performance benchmarks.

