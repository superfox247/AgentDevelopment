"""
Given: Docker client is unavailable (offline).
When: /api/status is called AND port 8501 is open (local process running).
Then: Orchestrator status should be 'online (local)'.
"""


import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from tools.dashboard.dependencies import get_docker_client
from tools.dashboard.server import app

client = TestClient(app)

def mock_get_docker_client_none():
    return None

def test_status_local_mode_success():
    app.dependency_overrides[get_docker_client] = mock_get_docker_client_none

    # Mock socket.create_connection to simulate open port
    with patch("socket.create_connection") as mock_socket:
        # Successful connection returns a socket object (or at least doesn't raise)
        mock_socket.return_value = MagicMock()

        response = client.get("/api/status")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "online" # Overall status is online if local fallback succeeds
        assert data["orchestrator"] == "online (local)"

    app.dependency_overrides = {}

def test_status_local_mode_failure():
    """
    Given: Docker client is unavailable (offline).
    When: /api/status is called AND port 8501 is closed.
    Then: Orchestrator status should be 'offline'.
    """
    app.dependency_overrides[get_docker_client] = mock_get_docker_client_none

    # Mock socket.create_connection to simulate closed port (raise ConnectionRefusedError)
    with patch("socket.create_connection") as mock_socket:
        mock_socket.side_effect = ConnectionRefusedError("Connection refused")

        response = client.get("/api/status")

        assert response.status_code == 200
        data = response.json()

        assert data["orchestrator"] == "offline"

    app.dependency_overrides = {}
