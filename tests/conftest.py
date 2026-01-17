from unittest.mock import MagicMock

import pytest

# Add orchestrator to sys.path so 'import agent' works in server.py
# sys.path hack removed - use absolute imports from domains.*


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sets up standard environment variables for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "fake-project")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "false")
    monkeypatch.setenv("AGENT_HOST", "localhost")


@pytest.fixture
def mock_adk_runner() -> MagicMock:
    """Mocks the ADK Runner to prevent actual model calls."""
    runner = MagicMock()
    runner.run_async.return_value = []
    return runner
