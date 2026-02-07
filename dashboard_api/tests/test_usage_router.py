"""Unit tests for usage and quota API routes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from agent_platform.config import PlatformConfig
from dashboard_api.routers import usage


def _config(**overrides: Any) -> PlatformConfig:
    return PlatformConfig.model_validate(overrides)


def _build_client(config_factory: Callable[[], PlatformConfig]) -> TestClient:
    app = FastAPI()
    app.include_router(usage.router)
    app.dependency_overrides[usage.get_platform_config] = config_factory
    return TestClient(app)


def test_usage_returns_clear_error_when_project_not_configured() -> None:
    """`/api/usage` should return a non-throwing unconfigured response."""
    client = _build_client(lambda: _config(gcp_project_id=None))
    response = client.get("/api/usage")
    data = response.json()

    assert response.status_code == 200
    assert data["project_id"] == "unconfigured"
    assert "GCP_PROJECT_ID is not configured" in data["errors"]


def test_usage_reads_project_and_service_from_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configured usage scope should be passed into quota/metric fetchers."""
    calls: dict[str, tuple[str, str]] = {}

    def fake_fetch_quotas(
        project_id: str,
        service: str,
    ) -> tuple[list[usage.QuotaInfo], list[str]]:
        calls["quota"] = (project_id, service)
        return [], []

    def fake_fetch_usage_metrics(
        project_id: str,
        service: str,
    ) -> tuple[list[usage.UsageMetric], list[str]]:
        calls["metrics"] = (project_id, service)
        return [], []

    monkeypatch.setattr(usage, "_fetch_quotas", fake_fetch_quotas)
    monkeypatch.setattr(usage, "_fetch_usage_metrics", fake_fetch_usage_metrics)

    def fake_telemetry_status() -> str:
        return "inactive"

    monkeypatch.setattr(usage, "_check_telemetry_status", fake_telemetry_status)

    def config() -> PlatformConfig:
        return _config(
            gcp_project_id="project-123",
            gcp_usage_service="aiplatform.googleapis.com",
        )

    client = _build_client(config)

    response = client.get("/api/usage")
    data = response.json()

    assert response.status_code == 200
    assert data["project_id"] == "project-123"
    assert data["service"] == "aiplatform.googleapis.com"
    assert calls["quota"] == ("project-123", "aiplatform.googleapis.com")
    assert calls["metrics"] == ("project-123", "aiplatform.googleapis.com")


def test_quota_detail_requires_project_configuration() -> None:
    """`/api/usage/quota/*` should fail fast without configured project id."""
    client = _build_client(lambda: _config(gcp_project_id=None))
    response = client.get("/api/usage/quota/gemini-test")

    assert response.status_code == 400
    assert response.json()["detail"] == "GCP_PROJECT_ID is not configured"


def test_metric_timeseries_requires_project_configuration() -> None:
    """`/api/usage/metrics/*/timeseries` should fail fast without project id."""
    client = _build_client(lambda: _config(gcp_project_id=None))
    response = client.get("/api/usage/metrics/token_usage/timeseries")

    assert response.status_code == 400
    assert response.json()["detail"] == "GCP_PROJECT_ID is not configured"
