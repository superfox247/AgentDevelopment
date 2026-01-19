import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Ensure we can import from tools
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from tools.dashboard.server import app
from tools.dashboard.dependencies import get_docker_client
from tools.dashboard.models import DockerStatsResponse

client = TestClient(app)

# --- Mock Data ---

def mock_get_docker_client():
    mock_client = MagicMock()
    
    # Mock container
    mock_container = MagicMock()
    mock_container.short_id = "12345678"
    mock_container.name = "course_creator-orchestrator"
    mock_container.status = "running"
    mock_container.image.tags = ["image:latest"]
    
    # Mock list
    mock_client.containers.list.return_value = [mock_container]
    
    # Mock get
    mock_client.containers.get.return_value = mock_container
    
    return mock_client

def mock_get_docker_client_offline():
    return None

# --- Tests ---

def test_get_docker_stats():
    app.dependency_overrides[get_docker_client] = mock_get_docker_client
    response = client.get("/api/docker")
    assert response.status_code == 200
    data = response.json()
    assert "containers" in data
    assert len(data["containers"]) == 1
    assert data["containers"][0]["name"] == "course_creator-orchestrator"
    app.dependency_overrides = {}

def test_get_docker_stats_offline():
    app.dependency_overrides[get_docker_client] = mock_get_docker_client_offline
    response = client.get("/api/docker")
    assert response.status_code == 200
    assert response.json() == {"error": "Docker not connected"}
    app.dependency_overrides = {}

def test_control_container():
    app.dependency_overrides[get_docker_client] = mock_get_docker_client
    response = client.post("/api/docker/12345678/restart")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    app.dependency_overrides = {}

def test_get_status():
    app.dependency_overrides[get_docker_client] = mock_get_docker_client
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    # Orchestrator should be online based on name match 'course_creator-orchestrator'
    assert data["orchestrator"] == "online"
    app.dependency_overrides = {}

def test_list_agents():
    # This hits the real filesystem, assuming project structure exists
    response = client.get("/api/agents")
    assert response.status_code == 200
    # We might not check specific content as it depends on local files, 
    # but structure should be valid
    data = response.json()
    assert "agents" in data

def test_list_skills():
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
