"""
Middleware for FastAPI applications.

Provides:
- Rate limiting using slowapi
- CORS configuration
"""

from collections.abc import Callable
from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import Response

from agent_platform.config import get_config

# Initialize rate limiter with centralized config
config = get_config()
default_limits = [
    limit.strip() for limit in config.rate_limit.split(",") if limit.strip()
]
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=cast(list[str | Callable[..., str]], default_limits),
    storage_uri=config.rate_limit_storage,
)

# Rate limit exceeded handler
rate_limit_handler = _rate_limit_exceeded_handler


def get_rate_limiter() -> Limiter:
    """Get the configured rate limiter instance."""
    return limiter


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Setup rate limiting for a FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    app.state.limiter = limiter
    handler = cast(Callable[[Request, Exception], Response], rate_limit_handler)
    app.add_exception_handler(RateLimitExceeded, handler)


def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware for a FastAPI application.

    Configures CORS based on PlatformConfig:
    - Uses ALLOWED_ORIGINS from config
    - In development, automatically adds common localhost origins

    Args:
        app: The FastAPI application instance.
    """
    # Use the module-level config instance for consistency
    allowed_origins = [origin.strip() for origin in config.allowed_origins.split(",")]

    # In development, expand default origins but never use ["*"] for security
    if config.is_development:
        # Add common development origins if not already present
        dev_origins = [
            "http://localhost:5173",
            "http://localhost:8000",
            "http://localhost:8010",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8010",
        ]
        for origin in dev_origins:
            if origin not in allowed_origins:
                allowed_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
