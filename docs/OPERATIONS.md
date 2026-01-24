# Operations & Troubleshooting

## 🐳 Docker Management

The entire "Local Cloud" lives in Docker.

### Essential Commands
*   **Start All**: `docker-compose up -d`
*   **View Logs**: `docker-compose logs -f [service_name]`
*   **Rebuild specific agent**: `docker-compose up -d --build [service_name]`
*   **Stop**: `docker-compose down`

## 🔍 Observability

### Phoenix (Traceability)
*   **URL**: `http://localhost:6006`
*   **Usage**: View LLM traces, token usage, and latency for all agent interactions.

### Dashboard Logs
The Orchestrator provides a curated view of logs at `http://localhost:5173/logs`.

## 🛠 Common Issues & Fixes

### 1. "Agent Offline" in Dashboard
*   **Cause**: Docker container died or backend lost sync.
*   **Fix**:
    1.  Check container status: `docker ps`
    2.  Force re-init: `docker-compose up -d` (Triggers backend re-scan).

### 2. Browser Tool Failure
*   **Cause**: `headless-shell` crashed or environment missing.
*   **Fix**:
    1.  Restart browser service: `docker-compose restart browser`
    2.  Verify connection: Check logs for `browserless/chrome`.

### 3. "Python Environment Corrupt"
*   **Cause**: Interrupted `uv sync` or bad `pip` mix.
*   **Fix (Nuke & Pave)**:
    1.  Kill python processes.
    2.  Delete `.venv` folder.
    3.  Run `uv sync`.

## 🔐 API Keys & Secrets

*   **Location**: `.env` file in project root.
*   **Standard**: Use `GEMINI_API_KEY` as the canonical key name. Do not duplicate as `GOOGLE_API_KEY`.
