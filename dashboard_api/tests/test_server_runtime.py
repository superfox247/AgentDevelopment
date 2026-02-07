"""Tests for runtime-aware router mounting in the dashboard API app factory."""

from __future__ import annotations

from fastapi import FastAPI

from agent_platform.config import PlatformConfig
from dashboard_api.server import create_app


def _config(**overrides: object) -> PlatformConfig:
    return PlatformConfig.model_validate(overrides)


def _route_paths(app: FastAPI) -> set[str]:
    return {str(route.path) for route in app.routes if hasattr(route, "path")}


def test_docker_routes_enabled_by_default_in_development() -> None:
    """Development runtime should mount Docker management endpoints."""
    app = create_app(_config(env="development"))
    paths = _route_paths(app)

    assert "/api/docker" in paths
    assert "/api/logs/{container_name}" in paths


def test_docker_routes_disabled_by_default_in_production() -> None:
    """Production runtime should not expose Docker management endpoints by default."""
    app = create_app(_config(env="production"))
    paths = _route_paths(app)

    assert "/api/docker" not in paths
    assert "/api/logs/{container_name}" not in paths


def test_docker_routes_can_be_explicitly_enabled_in_production() -> None:
    """Production runtime can opt in to Docker routes via explicit flag."""
    app = create_app(_config(env="production", enable_docker_routes=True))
    paths = _route_paths(app)

    assert "/api/docker" in paths
