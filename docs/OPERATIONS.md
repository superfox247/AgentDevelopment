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

*   **Location**: `.env` file in project root (development) or secrets management (production).
*   **Standard**: Use `GEMINI_API_KEY` as the canonical key name. Do not duplicate as `GOOGLE_API_KEY`.
*   **Production**: Never mount `.env` files in Docker. Use Docker secrets or environment variables.

## 🚨 Additional Troubleshooting

### 4. "Rate Limit Exceeded" Errors
*   **Cause**: Too many requests in a short time period.
*   **Fix**:
    1.  Check rate limit configuration: `RATE_LIMIT` environment variable
    2.  Implement request queuing or backoff in client
    3.  Review rate limit logs

### 5. "CORS Error" in Browser
*   **Cause**: Frontend origin not in `ALLOWED_ORIGINS`.
*   **Fix**:
    1.  Check `ALLOWED_ORIGINS` environment variable
    2.  Ensure frontend URL matches exactly (including protocol and port)
    3.  In development, set `CORS_ALLOW_ALL=true` if needed (never in production)

### 6. "Authentication Failed" Errors
*   **Cause**: Missing or invalid `AGENT_API_KEY`.
*   **Fix**:
    1.  Verify `AGENT_API_KEY` is set in environment
    2.  Check that `AUTH_DISABLED` is not set to `true` in production
    3.  Ensure API key matches between client and server

### 7. Container Health Check Failures
*   **Cause**: Service not responding on health endpoint.
*   **Fix**:
    1.  Check service logs: `docker-compose logs [service_name]`
    2.  Verify service is listening on correct port
    3.  Check resource limits (may be OOM killed)
    4.  Test health endpoint manually: `curl http://localhost:[port]/health`

### 8. "Connection Refused" to Phoenix
*   **Cause**: Phoenix service not running or network issue.
*   **Fix**:
    1.  Verify Phoenix container is running: `docker ps | grep phoenix`
    2.  Check Phoenix logs: `docker-compose logs phoenix`
    3.  Verify `PHOENIX_COLLECTOR_ENDPOINT` environment variable

### 9. High Memory Usage
*   **Cause**: Memory leaks or insufficient resource limits.
*   **Fix**:
    1.  Check container memory usage: `docker stats`
    2.  Review resource limits in `docker-compose.yml`
    3.  Increase limits if needed or optimize code
    4.  Check for memory leaks in application logs

### 10. Slow API Responses
*   **Cause**: External API latency, rate limiting, or resource constraints.
*   **Fix**:
    1.  Check Gemini API status and latency
    2.  Review rate limiting configuration
    3.  Check container CPU usage
    4.  Implement caching where appropriate
    5.  Review database/connection pool settings

### 11. Frontend Build Failures
*   **Cause**: Missing dependencies or TypeScript errors.
*   **Fix**:
    1.  Clear node_modules and reinstall: `rm -rf node_modules && pnpm install`
    2.  Check TypeScript errors: `pnpm exec tsc --noEmit`
    3.  Verify Node.js version matches requirements (20+)
    4.  Clear build cache: `rm -rf dist .vite`

### 12. Environment Variable Not Loading
*   **Cause**: Variable not set or wrong format.
*   **Fix**:
    1.  Verify variable is in `.env` file (development) or environment (production)
    2.  Check for typos in variable names
    3.  Ensure no extra spaces or quotes
    4.  Restart containers after changing environment variables

## 🔍 Debugging Commands

```bash
# View all container status
docker-compose ps

# View logs for specific service
docker-compose logs -f [service_name]

# Check container resource usage
docker stats

# Execute command in running container
docker-compose exec [service_name] /bin/sh

# Restart specific service
docker-compose restart [service_name]

# View environment variables in container
docker-compose exec [service_name] env

# Test health endpoint
curl http://localhost:[port]/health
```