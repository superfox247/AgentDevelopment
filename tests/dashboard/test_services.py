
from typing import cast

"""
Service Layer Tests for Dashboard.

Verifies the ImageGenerationService logic, including:
- Event extraction (JSON vs Tool vs Content Part)
- Error handling
- Mocking the Runner/Event stream
"""

import pytest
from google.adk.runners import Runner

from tests.shared.doubles import (
    FakeContent,
    FakeEvent,
    FakeFunctionResponse,
    FakePart,
    FakeResponse,
    FakeRunner,
    FakeToolResponse,
)
from tools.dashboard.services import ImageGenerationService


@pytest.fixture
def fake_runner() -> FakeRunner:
    return FakeRunner()

@pytest.fixture
def service(fake_runner: FakeRunner) -> ImageGenerationService:
    # Cast FakeRunner to Runner to satisfy type checker while injecting the fake
    return ImageGenerationService(cast(Runner, fake_runner))

@pytest.mark.asyncio
async def test_generate_image_success_json(service: ImageGenerationService, fake_runner: FakeRunner) -> None:
    # Mock event stream with a JSON response
    event = FakeEvent(
        response=FakeResponse(
            content='Here is the image: ```json\n{"image_path": "artifacts/images/test.png"}\n```'
        )
    )
    fake_runner.set_mock_events([event])

    path = await service.generate_image("user", "session", "prompt", "model")
    assert path == "artifacts/images/test.png"

@pytest.mark.asyncio
async def test_generate_image_success_tool(service: ImageGenerationService, fake_runner: FakeRunner) -> None:
    # Mock event stream with a tool response
    fake_tool_resp = FakeToolResponse(
        name="generate_image_from_prompt",
        response={"image_path": "artifacts/images/tool.png"}
    )

    event = FakeEvent(
        tool_response=[fake_tool_resp]
    )
    fake_runner.set_mock_events([event])

    path = await service.generate_image("user", "session", "prompt", "model")
    assert path == "artifacts/images/tool.png"

@pytest.mark.asyncio
async def test_generate_image_failure_no_path(service: ImageGenerationService, fake_runner: FakeRunner) -> None:
    # Mock empty event stream (default for FakeRunner is empty list)
    fake_runner.set_mock_events([])

    with pytest.raises(Exception) as exc:
        await service.generate_image("user", "session", "prompt", "model")

    assert "no image path found" in str(exc.value)

@pytest.mark.asyncio
async def test_generate_image_from_content_parts(service: ImageGenerationService, fake_runner: FakeRunner) -> None:
    # New test case covering the 3rd extraction path (Content Parts) which was hard to mock before

    fake_part = FakePart(
        function_response=FakeFunctionResponse(
            name="generate_image_from_prompt",
            response={"result": "artifacts/images/parts.png"}
        )
    )

    event = FakeEvent(
        content=FakeContent(parts=[fake_part])
    )
    fake_runner.set_mock_events([event])

    path = await service.generate_image("user", "session", "prompt", "model")
    assert path == "artifacts/images/parts.png"
