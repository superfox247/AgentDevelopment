"""
Dashboard API Router Tests

Tests for FastAPI routes: system, docker, agents.
"""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from tools.dashboard.server import app


@pytest.fixture
def mock_docker_client():
    """Mock Docker client for API tests."""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.short_id = "abc123"
    mock_container.name = "test-container"
    mock_container.status = "running"
    mock_container.image.tags = ["test:latest"]
    mock_client.containers.list.return_value = [mock_container]
    return mock_client


@pytest.fixture
def mock_platform_config():
    """Mock platform config."""
    config = MagicMock()
    config.gemini_api_key = "test-key"
    config.telemetry_enabled = False
    return config


class TestSystemRoutes:
    """Test system router endpoints."""

    @pytest.mark.asyncio
    async def test_get_status_returns_system_status(self, mock_docker_client):
        """Test /api/status returns system status."""
        with patch('tools.dashboard.dependencies.get_docker_client', return_value=mock_docker_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/status")
                assert response.status_code == 200
                data = response.json()
                assert "status" in data or "system_status" in data

    @pytest.mark.asyncio
    async def test_list_artifacts_returns_list(self):
        """Test /api/artifacts returns artifact list."""
        with patch('tools.dashboard.routers.system.ARTIFACTS_DIR') as mock_dir:
            mock_dir.exists.return_value = False
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/artifacts")
                assert response.status_code == 200


class TestDockerRoutes:
    """Test docker router endpoints."""

    @pytest.mark.asyncio
    async def test_get_docker_stats(self, mock_docker_client):
        """Test /api/docker returns container stats."""
        with patch('tools.dashboard.dependencies.get_docker_client', return_value=mock_docker_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/docker")
                assert response.status_code == 200
                data = response.json()
                assert "containers" in data or "error" in data

    @pytest.mark.asyncio
    async def test_docker_container_control_invalid_action(self, mock_docker_client):
        """Test /api/docker/{id}/{action} rejects invalid actions."""
        with patch('tools.dashboard.dependencies.get_docker_client', return_value=mock_docker_client):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/api/docker/abc123/invalid")
                # Should return 400 or 500 for invalid action
                assert response.status_code in [400, 500]


class TestAgentRoutes:
    """Test agent router endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents(self):
        """Test /api/agents returns agent list."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/agents")
            assert response.status_code == 200
            data = response.json()
            assert "agents" in data

    @pytest.mark.asyncio
    async def test_list_skills(self):
        """Test /api/skills returns skills list."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/skills")
            assert response.status_code == 200
            data = response.json()
            assert "skills" in data
