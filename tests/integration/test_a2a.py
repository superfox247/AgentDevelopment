"""Integration tests for A2A (Agent-to-Agent) delegation flow.

Tests the Orchestrator's ability to route requests and delegate to remote agents.
"""

import logging
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from domains.course_creator.orchestrator.server import create_app

logger = logging.getLogger(__name__)


def create_mock_genai_response(text: str) -> MagicMock:
    """Create a properly structured mock genai response.
    
    This helper creates a mock that mimics google.genai response structure
    with all required fields properly nullified to avoid MagicMock warnings.
    """
    mock = MagicMock()
    mock.model_version = "gemini-2.0-flash"
    
    # Usage metadata
    mock.usage_metadata.prompt_token_count = 10
    mock.usage_metadata.candidates_token_count = 10
    mock.usage_metadata.total_token_count = 20
    mock.usage_metadata.cached_content_token_count = 0
    mock.usage_metadata.trafficType = mock.usage_metadata.traffic_type = None
    
    # Response content
    mock.candidates = [MagicMock()]
    mock.candidates[0].content.parts = [MagicMock()]
    mock.candidates[0].content.parts[0].text = text
    mock.candidates[0].content.role = "model"
    mock.candidates[0].finish_reason = "STOP"
    mock.candidates[0].avg_logprobs = 0.0
    
    # Nullify optional fields to prevent auto-MagicMock creation
    part = mock.candidates[0].content.parts[0]
    for field in ['inlineData', 'inline_data', 'functionCall', 'function_call',
                  'functionResponse', 'function_response', 'fileData', 'file_data',
                  'executableCode', 'executable_code', 'codeExecutionResult', 
                  'code_execution_result', 'videoMetadata', 'video_metadata',
                  'thoughtSignature', 'thought_signature', 'mediaResolution', 'media_resolution']:
        setattr(part, field, None)
    
    candidate = mock.candidates[0]
    candidate.groundingMetadata = candidate.grounding_metadata = None
    candidate.citationMetadata = candidate.citation_metadata = None
    candidate.safetyRatings = candidate.safety_ratings = []
    
    return mock


@pytest.fixture
def integration_app() -> FastAPI:
    """Create the app with mocked A2A agents for integration testing."""
    return create_app()


@pytest.fixture
def client(integration_app: FastAPI) -> TestClient:
    return TestClient(integration_app)


@pytest.mark.asyncio
async def test_a2a_delegation_flow(client: TestClient) -> None:
    """Test Orchestrator correctly delegates to Researcher agent."""
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from google.adk.events import Event
    from google.genai.types import Content, Part

    payload = {
        "message": "Research the history of AI",
        "user_id": "test_user",
        "session_id": "test_session",
    }

    # Mock genai client
    mock_client = MagicMock()
    mock_response = create_mock_genai_response('{"intent": "research_request", "topic": "history of AI"}')
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    async def mock_researcher_run(*args, **kwargs) -> AsyncGenerator[Event, None]:
        content = Content(parts=[Part(text="AI History: Turing, Lovelace...")])
        yield Event(author="researcher", content=content)

    with patch("google.genai.Client", return_value=mock_client), \
         patch.object(RemoteA2aAgent, "run_async", side_effect=mock_researcher_run) as mock_run:
        
        response = client.post("/api/chat_stream", json=payload)

        assert response.status_code == 200
        assert "application/x-ndjson" in response.headers["content-type"]
        assert any("AI History" in line for line in response.content.decode().splitlines())
        mock_run.assert_called()
