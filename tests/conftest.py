from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from tests.shared.doubles import FakeDockerClient

# Add orchestrator to sys.path so 'import agent' works in server.py
# sys.path hack removed - use absolute imports from domains.*


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sets up standard environment variables for testing."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "fake-project")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "false")
    monkeypatch.setenv("AGENT_HOST", "localhost")


@pytest.fixture
def mock_adk_runner() -> MagicMock:
    runner = MagicMock()
    runner.run_async.return_value = []
    return runner


@pytest.fixture
def mock_docker() -> FakeDockerClient:
    """Provides a shared FakeDockerClient for tests."""
    return FakeDockerClient()


@pytest.fixture
def client(mock_docker: FakeDockerClient) -> Iterator[TestClient]:
    """Provides a TestClient with standard dependency overrides."""
    # Local import to avoid circular dependencies
    from tools.dashboard.dependencies import get_docker_client
    from tools.dashboard.server import app

    app.dependency_overrides[get_docker_client] = lambda: mock_docker
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
