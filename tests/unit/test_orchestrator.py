from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# No more sys.path hacks or os.environ hacks needed here!
# Environment is handled by pytest.ini
# Imports are safe because server.py uses lazy initialization
from domains.course_creator.orchestrator.server import create_app


@pytest.fixture
def mock_runner_instance() -> MagicMock:
    """Mocks the ADK Runner instance."""
    runner = MagicMock()
    # Mock session service methods to be async
    runner.session_service.get_session = AsyncMock(return_value=None)
    runner.session_service.create_session = AsyncMock(return_value=AsyncMock(id="test_session"))
    return runner


@pytest.fixture
def client(mock_runner_instance: MagicMock) -> TestClient:

    from fastapi.testclient import TestClient

    # We patch the Runner class used inside create_app (via create_platform_app)
    with patch('agent_platform.server.Runner') as MockRunnerClass:

        MockRunnerClass.return_value = mock_runner_instance
        # Create the app (which uses the mocked Runner)
        app = create_app()
        return TestClient(app)

def test_chat_stream_endpoint(client: TestClient, mock_runner_instance: MagicMock) -> None:
    """Test the happy path for the /api/chat_stream endpoint."""

    # Define the generator behavior for this specific test
    async def mock_event_generator(*args: object, **kwargs: object) -> AsyncGenerator[AsyncMock, None]:


        mock_event = AsyncMock()
        mock_event.author = "researcher"
        mock_event.tool_calls = []
        mock_event.usage_metadata = None
        # Use Simple Namespace or Mock for parts to ensure text attribute is accessible string
        from unittest.mock import Mock
        part_mock = Mock()
        part_mock.text = "Hello world"
        mock_event.content.parts = [part_mock]
        mock_event.is_final_response.return_value = True
        yield mock_event

    mock_runner_instance.run_async.side_effect = mock_event_generator

    payload = {
        "message": "Create a course on Neural Networks",
        "user_id": "test_user",
        "session_id": "test_session"
    }

    response = client.post("/api/chat_stream", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"
    assert b"agent_thought" in response.content or b"Hello world" in response.content
