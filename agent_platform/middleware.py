"""
Middleware for FastAPI applications.

Provides:
- Rate limiting using slowapi
- CORS configuration
"""

import os
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=os.environ.get("RATE_LIMIT", "100/minute").split(","),
    storage_uri=os.environ.get("RATE_LIMIT_STORAGE", "memory://"),
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
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware for a FastAPI application.
    
    Configures CORS based on environment variables:
    - ALLOWED_ORIGINS: Comma-separated list of allowed origins (default: localhost URLs)
    - ENV: Environment name (development/production)
    - CORS_ALLOW_ALL: If "true" and ENV=development, allows all origins
    
    Args:
        app: The FastAPI application instance.
    """
    allowed_origins_str = os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000"
    )
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    
    # In development, allow all origins if explicitly set
    if (
        os.environ.get("ENV", "development").lower() == "development"
        and os.environ.get("CORS_ALLOW_ALL", "false").lower() == "true"
    ):
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
