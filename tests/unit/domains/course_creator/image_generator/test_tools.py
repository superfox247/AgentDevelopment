"""
Unit Tests for Image Generator Tools.

Verifies:
- Routing logic between Gemini and Imagen models
- Error handling for API failures
- Persistence layer integration (via mocks)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from google import genai
from google.genai import types

# Target module
from domains.course_creator.image_generator import tools
from domains.course_creator.image_generator.persistence import ImagePersistence


@pytest.fixture
def mock_platform_config():
    """Returns a mocked PlatformConfig."""
    config = MagicMock()
    config.gemini_api_key = "fake_key"
    config.default_image_model = "gemini-2.0-flash-exp"
    return config

@pytest.fixture
def mock_genai_client():
    """Returns a mocked Google GenAI Client with sync and async interfaces."""
    client = MagicMock(spec=genai.Client)
    client.aio = MagicMock()
    client.aio.models = MagicMock()
    client.aio.models.generate_images = AsyncMock()
    client.aio.models.generate_content = AsyncMock()

    # Keep sync mocks for safety if needed elsewhere, but mainly use aio
    client.models = MagicMock()
    return client

@pytest.fixture
def mock_persistence():
    """Returns a mocked ImagePersistence layer."""
    persistence = MagicMock(spec=ImagePersistence)
    persistence.save_image.return_value = "/path/to/generated_image.png"
    return persistence

@pytest.fixture
def img_service(mock_genai_client, mock_platform_config, mock_persistence):
    """Provides an instance of ImageGeneratorService with mocked dependencies."""
    return tools.ImageGeneratorService(
        client=mock_genai_client,
        config=mock_platform_config,
        persistence=mock_persistence
    )

@pytest.mark.asyncio
async def test_generate_image_routing_imagen(img_service, mock_genai_client, mock_persistence):
    """Verify that 'imagen' model routes to the Imagen handler."""
    # Setup - Imagen Logic Mocking
    mock_response = types.GenerateImagesResponse(
        generated_images=[
            types.GeneratedImage(
                image=types.Image(image_bytes=b"fake_imagen_bytes")
            )
        ]
    )
    mock_genai_client.aio.models.generate_images.return_value = mock_response

    # Execute
    result = await img_service.generate_image_from_prompt("test prompt", model="imagen-3.0-generate-001")

    # Verify
    mock_genai_client.aio.models.generate_images.assert_called_once()
    mock_persistence.save_image.assert_called_once_with(b"fake_imagen_bytes", "test prompt", "imagen-3.0-generate-001")
    assert result == "/path/to/generated_image.png"
    # Ensure Gemini handler was NOT called
    mock_genai_client.aio.models.generate_content.assert_not_called()

@pytest.mark.asyncio
async def test_generate_image_routing_gemini_default(img_service, mock_genai_client, mock_persistence):
    """Verify that default model (non-imagen) routes to the Gemini handler."""
    # Setup - Gemini Logic Mocking
    mock_part = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=b"fake_gemini_bytes"
        )
    )
    mock_candidate = types.Candidate(
        content=types.Content(parts=[mock_part])
    )
    mock_response = types.GenerateContentResponse(
        candidates=[mock_candidate]
    )

    mock_genai_client.aio.models.generate_content.return_value = mock_response

    # Execute (using default model from config fixture)
    result = await img_service.generate_image_from_prompt("test prompt")

    # Verify
    mock_genai_client.aio.models.generate_content.assert_called_once()
    mock_persistence.save_image.assert_called_once_with(b"fake_gemini_bytes", "test prompt", "gemini-2.0-flash-exp")
    assert result == "/path/to/generated_image.png"
    # Ensure Imagen handler was NOT called
    mock_genai_client.aio.models.generate_images.assert_not_called()

@pytest.mark.asyncio
async def test_imagen_failure_empty_images(img_service, mock_genai_client):
    """Test Imagen path failure when no images returned."""
    mock_response = types.GenerateImagesResponse(generated_images=[])
    mock_genai_client.aio.models.generate_images.return_value = mock_response

    with pytest.raises(RuntimeError, match="Imagen returned no images"):
        await img_service.generate_image_from_prompt("test prompt", model="imagen-3.0")

@pytest.mark.asyncio
async def test_imagen_failure_empty_bytes(img_service, mock_genai_client):
    """Test Imagen path failure when image bytes are missing."""
    mock_response = types.GenerateImagesResponse(
        generated_images=[
            types.GeneratedImage(image=types.Image(image_bytes=None))
        ]
    )
    mock_genai_client.aio.models.generate_images.return_value = mock_response

    with pytest.raises(RuntimeError, match="image_bytes was empty"):
        await img_service.generate_image_from_prompt("test prompt", model="imagen-3.0")

@pytest.mark.asyncio
async def test_gemini_failure_no_candidates(img_service, mock_genai_client):
    """Test Gemini path failure when no candidates returned."""
    mock_response = types.GenerateContentResponse(candidates=[])
    mock_genai_client.aio.models.generate_content.return_value = mock_response

    with pytest.raises(RuntimeError, match="Gemini returned no candidates"):
        await img_service.generate_image_from_prompt("test prompt", model="gemini-2.0")

@pytest.mark.asyncio
async def test_gemini_failure_no_inline_data(img_service, mock_genai_client):
    """Test Gemini path failure when inline_data is missing."""
    mock_part = types.Part(text="I cannot generate that image.")
    mock_candidate = types.Candidate(content=types.Content(parts=[mock_part]))
    mock_response = types.GenerateContentResponse(candidates=[mock_candidate])
    mock_genai_client.aio.models.generate_content.return_value = mock_response

    with pytest.raises(RuntimeError, match="Gemini response contained no inline_data"):
        await img_service.generate_image_from_prompt("test prompt", model="gemini-2.0")

def test_legacy_wrapper_exists():
    """Ensure the top-level function still exists for agent compatibility."""
    assert hasattr(tools, "generate_image_from_prompt")
    assert callable(tools.generate_image_from_prompt)
