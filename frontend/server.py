"""
Dashboard Server Entrypoint.

The main FastAPI application for the Operational Dashboard.
Provides APIs for:
- Docker Management (start/stop/logs)
- Agent Introspection (list agents/skills)
- System status and artifacts
"""

import logging
import sys
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Ensure root is in path for imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from agent_platform.middleware import setup_cors  # noqa: E402
from frontend.routers import agents, docker, system, usage  # noqa: E402

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Health check endpoint for container orchestration.

    Returns:
        dict: Health status with service name and dependency checks.
    """
    from frontend.dependencies import get_docker_client

    docker_available = get_docker_client() is not None

    return {
        "status": "healthy",
        "service": "dashboard",
        "docker_available": docker_available,
    }


# CORS Configuration
setup_cors(app)


# Global Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions globally."""
    logger.warning(f"ValueError on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions globally."""
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable) -> Response:
    """Add OWASP security headers."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Basic CSP - modify as needed for your specific resource needs
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' http://localhost:5173; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; connect-src 'self' http://localhost:8010 ws://localhost:8010 http://localhost:5173"
    )
    return response


# Include Routers
app.include_router(docker.router)
app.include_router(agents.router)
app.include_router(system.router)
app.include_router(usage.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010)
