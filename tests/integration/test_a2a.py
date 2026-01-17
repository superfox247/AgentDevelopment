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
    # This verifies that the runner loop correctly invokes the remote agent proxy.
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from google.adk.events import Event
    from google.genai.types import Content, Part

    async def mock_researcher_run(
        *args: object, **kwargs: object
    ) -> AsyncGenerator[Event, None]:
        # Create a mock event simulating a response from the researcher
        content = Content(parts=[Part(text="AI History: Turing, Lovelace...")])
        yield Event(author="researcher", content=content)

    # Patch the class method to avoid instance attribute issues
    with patch.object(
        RemoteA2aAgent, "run_async", side_effect=mock_researcher_run
    ) as mock_run:
        response = client.post("/api/chat_stream", json=payload)

        assert response.status_code == 200
        assert "application/x-ndjson" in response.headers["content-type"]

        # Collect response lines
        lines = response.content.decode().splitlines()
        # Verify we got at least one line with our mock content
        assert any("AI History" in line for line in lines)

        # Verify the researcher was actually called
        mock_run.assert_called()
