from collections.abc import Iterator
from unittest.mock import MagicMock

"""
Pytest Configuration and Fixtures.

Provides shared fixtures for:
- Environment Variable mocking (12-Factor app simulation)
- Docker Client mocking (via FakeDockerClient)
- ADK Runner mocking
- TestClient configuration
"""

import pytest
from fastapi.testclient import TestClient
from google import genai
from google.genai import types

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
def mock_genai_client() -> MagicMock:
    """Provides a mocked Google GenAI Client adhering to strict strict SDK mocking."""
    client = MagicMock(spec=genai.Client)
    
    # Mock models.list to return concrete types.Model objects
    mock_model = types.Model(
        name="models/gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        description="Fast model",
        input_token_limit=1000,
        output_token_limit=1000,
        top_p=0.9,
        temperature=0.7
    )
    client.models = MagicMock()
    client.models.list.return_value = [mock_model]
    
    # Mock models.get to succeed for known models
    client.models.get.return_value = mock_model
    
    # Mock models.generate_content (sync) to return candidates
    # This is used by _test_single_model
    mock_response = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    parts=[types.Part(text="ok")]
                )
            )
        ]
    )
    client.models.generate_content.return_value = mock_response

    return client


@pytest.fixture
def mock_docker() -> FakeDockerClient:
    """Provides a shared FakeDockerClient for tests."""
    return FakeDockerClient()


@pytest.fixture
def client(mock_docker: FakeDockerClient, mock_genai_client: MagicMock) -> Iterator[TestClient]:
    """Provides a TestClient with standard dependency overrides."""
    # Local import to avoid circular dependencies
    from tools.dashboard.dependencies import get_docker_client, get_genai_client
    from tools.dashboard.server import app

    app.dependency_overrides[get_docker_client] = lambda: mock_docker
    app.dependency_overrides[get_genai_client] = lambda: mock_genai_client
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
