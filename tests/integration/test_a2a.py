import logging
from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from domains.course_creator.orchestrator.server import create_app

logger = logging.getLogger(__name__)


@pytest.fixture
def integration_app() -> FastAPI:
    """Created the app with mocked A2A agents for integration testing."""
    # We want to test the ROUTING logic and the fact that it CALLS the remote agent.
    # We DO NOT want to actually make network calls to localhost:8001 in this test suite yet
    # unless we spin up those containers. For "Integration Test for A2A", we usually mean
    # testing the Orchestrator's *side* of the integration (headers, payload format).

    app = create_app()
    return app


@pytest.fixture
def client(integration_app: FastAPI) -> TestClient:
    return TestClient(integration_app)


@pytest.mark.asyncio
async def test_a2a_delegation_flow(client: TestClient) -> None:
    """
    Test that the Orchestrator correctly delegates a task to the Researcher agent
    and processes the response.
    """
    # Payload simulating a user request
    payload = {
        "message": "Research the history of AI",
        "user_id": "test_integration_user",
        "session_id": "test_integration_session",
    }

    # Mocking the researcher agent's execution to return a predefined response
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

    from google.adk.events import Event
    from google.genai.types import Content, Part
    # Patch google.genai.Client to prevent ANY network calls and simulate the Customer Service response
    # The Orchestrator calls Customer Service -> Calls LLM -> Returns JSON with "intent"
    
    # We need a mock that behaves like the genai Client
    from unittest.mock import AsyncMock, MagicMock
    
    mock_client_instance = MagicMock()
    mock_aio = MagicMock()
    mock_models = MagicMock()
    
    # Define the mock response for generate_content
    # The Customer Service agent expects the model to output JSON with "intent": "research_request"
    mock_response = MagicMock()
    mock_response.model_version = "gemini-1.5-flash"
    mock_response.usage_metadata = MagicMock(prompt_token_count=10, candidates_token_count=10, total_token_count=20)
    
    # Structure: response.candidates[0].content.parts[0].text
    mock_part = MagicMock()
    mock_part.text = '{"intent": "research_request", "topic": "history of AI"}'
    # Explicitly nullify optional fields (both camel and snake case) to avoid MagicMock creation
    mock_part.inlineData = mock_part.inline_data = None
    mock_part.functionCall = mock_part.function_call = None
    mock_part.functionResponse = mock_part.function_response = None
    mock_part.fileData = mock_part.file_data = None
    mock_part.executableCode = mock_part.executable_code = None
    mock_part.codeExecutionResult = mock_part.code_execution_result = None
    mock_part.videoMetadata = mock_part.video_metadata = None
    mock_part.thoughtSignature = mock_part.thought_signature = None
    
    mock_content = MagicMock()
    mock_content.parts = [mock_part]
    mock_content.role = "model"

    mock_candidate = MagicMock()
    mock_candidate.content = mock_content
    mock_candidate.finish_reason = "STOP"
    mock_candidate.avg_logprobs = 0.0
    # Nullify candidate metadata (both cases)
    mock_candidate.groundingMetadata = mock_candidate.grounding_metadata = None
    mock_candidate.citationMetadata = mock_candidate.citation_metadata = None
    mock_candidate.safetyRatings = mock_candidate.safety_ratings = []


    
    mock_response.candidates = [mock_candidate]
    
    # Set up async generate_content
    mock_generate_content = AsyncMock(return_value=mock_response)
    mock_models.generate_content = mock_generate_content
    mock_aio.models = mock_models
    mock_client_instance.aio = mock_aio
    
    async def mock_researcher_run(
        *args: object, **kwargs: object
    ) -> AsyncGenerator[Event, None]:
        # Create a mock event simulating a response from the researcher
        content = Content(parts=[Part(text="AI History: Turing, Lovelace...")])
        yield Event(author="researcher", content=content)

    # Patch Client constructor to return our mock instance
    with patch("google.genai.Client", return_value=mock_client_instance), \
         patch.object(RemoteA2aAgent, "run_async", side_effect=mock_researcher_run) as mock_run:
        response = client.post("/api/chat_stream", json=payload)

        assert response.status_code == 200
        assert "application/x-ndjson" in response.headers["content-type"]

        # Collect response lines
        lines = response.content.decode().splitlines()
        # Verify we got at least one line with our mock content
        assert any("AI History" in line for line in lines)

        # Verify the researcher was actually called
        mock_run.assert_called()
