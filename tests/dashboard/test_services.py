
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from tools.dashboard.services import ImageGenerationService
from google.genai.types import Content

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.session_service = AsyncMock()
    runner.run_async = MagicMock() # Will return async generator
    return runner

@pytest.fixture
def service(mock_runner):
    return ImageGenerationService(mock_runner)

@pytest.mark.asyncio
async def test_generate_image_success_json(service, mock_runner):
    # Mock event stream with a JSON response
    mock_event = MagicMock()
    mock_event.response.content = 'Here is the image: ```json\n{"image_path": "artifacts/images/test.png"}\n```'
    
    async def event_gen(*args, **kwargs):
        yield mock_event

    mock_runner.run_async.side_effect = event_gen

    path = await service.generate_image("user", "session", "prompt", "model")
    assert path == "artifacts/images/test.png"

@pytest.mark.asyncio
async def test_generate_image_success_tool(service, mock_runner):
    # Mock event stream with a tool response
    mock_event = MagicMock()
    # Ensure it doesn't trigger the JSON check
    mock_event.response = None 
    
    mock_tool_resp = MagicMock()
    mock_tool_resp.name = "generate_image_from_prompt"
    mock_tool_resp.response = {"image_path": "artifacts/images/tool.png"}
    
    mock_event.tool_response = [mock_tool_resp]

    async def event_gen(*args, **kwargs):
        yield mock_event

    mock_runner.run_async.side_effect = event_gen

    path = await service.generate_image("user", "session", "prompt", "model")
    assert path == "artifacts/images/tool.png"

@pytest.mark.asyncio
async def test_generate_image_failure_no_path(service, mock_runner):
    # Mock empty event stream
    async def event_gen(*args, **kwargs):
        # Async generator that yields nothing
        if False: yield None 

    mock_runner.run_async.side_effect = event_gen

    with pytest.raises(Exception) as exc:
        await service.generate_image("user", "session", "prompt", "model")
    
    assert "no image path found" in str(exc.value)
