"""Integration tests for A2A (Agent-to-Agent) delegation flow.

Tests the Orchestrator's ability to route requests and delegate to remote agents.
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from domains.course_creator.orchestrator.server import create_app

logger = logging.getLogger(__name__)


def create_mock_genai_response(text: str) -> MagicMock:
    """Create a properly structured mock genai response using strict types.
    
    Returns a MagicMock that behaves like a types.GenerateContentResponse,
    populated with real google.genai.types objects.
    """
    from google.genai import types

    # Create the nested structure using real types
    part = types.Part(text=text)
    content = types.Content(role="model", parts=[part])
    candidate = types.Candidate(
        content=content,
        finish_reason="STOP",
        avg_logprobs=0.0,
        safety_ratings=[],
        citation_metadata=None,
        grounding_metadata=None
    )

    # Create the top level response object
    # We use a MagicMock to wrap the response because the client.aio.models.generate_content
    # might be expected to be awaitable or have other client-specific behaviors in some contexts,
    # but here we primarily need the returned object to hold the data.
    # However, to be "strict", we should try to return the actual object if possible,
    # but the test setup 'mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)'
    # expects a return value.

    response = types.GenerateContentResponse(
        candidates=[candidate],
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=10,
            candidates_token_count=10,
            total_token_count=20,
        ),
        model_version="gemini-2.0-flash"
    )

    return response


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
    mock_response = create_mock_genai_response(
        '{"message": "I will start researching that.", "intent": "research_request", "topic": "history of AI", "content_type": "Article", "tone": "Professional"}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    async def mock_researcher_run(*args: Any, **kwargs: Any) -> AsyncGenerator[Event, None]:
        content = Content(parts=[Part(text="AI History: Turing, Lovelace...")])
        yield Event(author="researcher", content=content)

    with patch("google.genai.Client", return_value=mock_client), \
         patch.object(RemoteA2aAgent, "run_async", side_effect=mock_researcher_run) as mock_run:

        response = client.post("/api/chat_stream", json=payload)

        assert response.status_code == 200
        assert "application/x-ndjson" in response.headers["content-type"]
        assert any("AI History" in line for line in response.content.decode().splitlines())
        mock_run.assert_called()
