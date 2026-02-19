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

from agent_platform.config import PlatformConfig  # noqa: E402
from agent_platform.middleware import setup_cors  # noqa: E402
from dashboard_api.dependencies import (  # noqa: E402
    get_docker_client,
    get_platform_config,
)
from dashboard_api.routers import agents, context_engine, docker, system, usage  # noqa: E402

logger = logging.getLogger(__name__)


def _build_connect_sources(config: PlatformConfig) -> str:
    """Build CSP connect-src values from configured allowed origins."""
    sources = {"'self'"}
    origins = [origin.strip() for origin in config.allowed_origins.split(",")]

    for origin in origins:
        if not origin:
            continue

        sources.add(origin)
        if origin.startswith("http://"):
            sources.add("ws://" + origin[len("http://") :])
        elif origin.startswith("https://"):
            sources.add("wss://" + origin[len("https://") :])

    return " ".join(sorted(sources))


def create_app(runtime_config: PlatformConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    config = runtime_config or get_platform_config()
    connect_sources = _build_connect_sources(config)

    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str | bool]:
        """Health check endpoint for container orchestration."""
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
        logger.warning("ValueError on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions globally."""
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
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
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob: https:; "
            f"connect-src {connect_sources}"
        )
        return response

    if config.docker_routes_enabled:
        app.include_router(docker.router)
    else:
        logger.info(
            "Docker routes disabled (ENV=%s, ENABLE_DOCKER_ROUTES=%s)",
            config.env,
            config.enable_docker_routes,
        )

    app.include_router(agents.router)
    app.include_router(context_engine.router)
    app.include_router(system.router)
    app.include_router(usage.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010)
