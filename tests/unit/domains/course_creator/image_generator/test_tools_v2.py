
import pytest

"""
Advanced Unit Tests for Image Generator Service.

Verifies the service layer with improved mocking patterns (AsyncMock)
and stricter type checking for GenAI interactions.
"""
from unittest.mock import AsyncMock, Mock, patch
from google import genai
from google.genai import types

from domains.course_creator.image_generator.tools import ImageGeneratorService
from agent_platform.config import PlatformConfig

@pytest.fixture
def mock_client():
    """Returns a highly-configurable mock of the GenAI Client."""
    client = Mock(spec=genai.Client)
    client.aio = Mock()
    client.aio.models = Mock()
    client.aio.models.generate_content = AsyncMock()
    client.aio.models.generate_images = AsyncMock()
    return client

@pytest.fixture
def mock_config():
    """Returns a mock PlatformConfig with test keys and models."""
    config = Mock(spec=PlatformConfig)
    config.default_image_model = "models/gemini-2.0-flash"
    config.gemini_api_key = "test_key"
    return config

@pytest.fixture
def mock_persistence():
    """Returns a mock Persistence layer expecting save_image calls."""
    persistence = Mock()
    persistence.save_image = Mock(return_value="/path/to/image.png")
    return persistence

@pytest.mark.asyncio
async def test_generate_from_prompt_imagen(mock_client, mock_config, mock_persistence):
    service = ImageGeneratorService(mock_client, mock_config, mock_persistence)
    
    # Mock Imagen response
    mock_response = Mock()
    mock_image = Mock()
    mock_image.image_bytes = b"fake_image_bytes"
    mock_response.generated_images = [Mock()]
    mock_response.generated_images[0].image = mock_image
    
    mock_client.aio.models.generate_images.return_value = mock_response

    path = await service.generate_image_from_prompt("test prompt", "models/imagen-3")
    
    assert path == "/path/to/image.png"
    mock_client.aio.models.generate_images.assert_awaited_once()
    mock_persistence.save_image.assert_called_once()

@pytest.mark.asyncio
async def test_generate_from_prompt_gemini(mock_client, mock_config, mock_persistence):
    service = ImageGeneratorService(mock_client, mock_config, mock_persistence)
    
    # Mock Gemini response
    mock_response = Mock()
    mock_part = types.Part()
    mock_part.inline_data = types.Blob(data=b"fake_gemini_bytes", mime_type="image/png")
    
    mock_candidate = types.Candidate(content=types.Content(parts=[mock_part]))
    mock_response.candidates = [mock_candidate]
    
    mock_client.aio.models.generate_content.return_value = mock_response

    path = await service.generate_image_from_prompt("test prompt", "models/gemini-pro")
    
    assert path == "/path/to/image.png"
    mock_client.aio.models.generate_content.assert_awaited_once()
    args, kwargs = mock_client.aio.models.generate_content.call_args
    assert kwargs["model"] == "models/gemini-pro"
    assert kwargs["contents"] == "test prompt"

