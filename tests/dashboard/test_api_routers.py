"""
Sync Tests for Dashboard API Routers.

Verifies API endpoints using FastAPI TestClient (synchronous).
Focuses on response structure and status codes.
"""

# Ensure we can import from tools
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from frontend.dependencies import get_docker_client  # noqa: E402
from frontend.server import app  # noqa: E402
from tests.shared.doubles import FakeDockerClient  # noqa: E402

# --- Mock Data ---


def mock_get_docker_client_offline() -> None:
    return None


# --- Tests ---


def test_get_docker_stats(client: TestClient) -> None:
    """Verifies that the docker stats endpoint returns container info.

    Asserts that the response status is 200 and contains the expected container
    from the mock environment.
    """
    response = client.get("/api/docker")
    assert response.status_code == 200
    data = response.json()
    assert "containers" in data
    assert len(data["containers"]) == 1
    assert data["containers"][0]["name"] == "content_creation-orchestrator"


def test_get_docker_stats_offline(client: TestClient) -> None:
    """Verifies that the endpoint handles Docker connection failures gracefully.

    Sets a dependency override to simulate an offline Docker client and asserts
    that the endpoint returns the standard error JSON.
    """
    # Explicitly override for this specific test scenario
    app.dependency_overrides[get_docker_client] = mock_get_docker_client_offline

    response = client.get("/api/docker")
    assert response.status_code == 200
    assert response.json() == {"error": "Docker not connected"}

    # Fixture teardown will handle clearing overrides, but good practice to reset if we wanted
    # but here we rely on the fixture's finalizer.


def test_control_container(client: TestClient, mock_docker: FakeDockerClient) -> None:
    """Verifies container control actions (restart).

    Uses the mock docker client to get a valid container ID, sends a restart command,
    and asserts success.
    """
    # Use the ID from mock_docker which is the shared source of truth
    container_id = mock_docker.containers.list()[0].short_id

    response = client.post(f"/api/docker/{container_id}/restart")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_status(client: TestClient) -> None:
    """Verifies the system status endpoint.

    Asserts that the overall system status is 'online' and that the orchestrator
    component is correctly reported as 'online'.
    """
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    # Orchestrator should be online based on name match 'course_creator-orchestrator'
    assert data["orchestrator"] == "online (docker)"


def test_list_agents(client: TestClient) -> None:
    # This hits the real filesystem, assuming project structure exists
    response = client.get("/api/agents")
    assert response.status_code == 200
    # We might not check specific content as it depends on local files,
    # but structure should be valid
    data = response.json()
    assert "agents" in data


def test_list_skills(client: TestClient) -> None:
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data


def test_diagnostics_models_structure(client: TestClient) -> None:
    """Test that diagnostics endpoint returns properly structured response."""
    # This test hits the real API but validates response structure
    response = client.get("/api/diagnostics/models")
    assert response.status_code == 200
    data = response.json()

    # Check required top-level fields
    assert "timestamp" in data
    assert "api_key_configured" in data
    assert "categories" in data

    # If API key is configured, should have summary
    if data.get("api_key_configured"):
        assert "summary" in data
        summary = data["summary"]
        assert "total" in summary
        assert "available" in summary
        assert "functional" in summary
        assert "rate_limited" in summary
