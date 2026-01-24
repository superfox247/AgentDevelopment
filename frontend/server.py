"""
Dashboard Server Entrypoint.

The main FastAPI application for the Operational Dashboard.
Provides APIs for:
- Docker Management (start/stop/logs)
- Agent Introspection (list agents/skills)
- System status and artifacts
"""

import sys
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Ensure root is in path for imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from frontend.routers import agents, docker, system, usage  # noqa: E402

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
