import warnings
from unittest.mock import MagicMock, patch

import pytest

from domains.image_gen.image_generator.agent import create_app
from registry.models.image_gen import ImageGenerationRequest

# Suppress "Pydantic serializer warnings" for mocked objects
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


@pytest.fixture
def agent():
    return create_app()


@pytest.mark.asyncio
async def test_image_generator_process(agent):
    # Mock Input
    request = ImageGenerationRequest(prompt="A futuristic city")

    # Mock the LLM response to simulate the tool call flow
    # Since YamlAgent uses the standard run loop, we want to ensure it calls our tool.
    # However, specialized testing of the tool execution itself is better done by mocking the tool function.

    with patch("registry.tools.image_generation.genai") as mock_genai:
        # Mock Client
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        # Mock Response
        mock_response = MagicMock()
        mock_image_obj = MagicMock()
        mock_image_obj.image.image_bytes = b"fake_image_bytes"
        mock_response.generated_images = [mock_image_obj]

        mock_client.models.generate_images.return_value = mock_response

        # Let's test the tool function directly to ensure it works as expected
        from registry.tools.image_generation import generate_image

        result = generate_image("test prompt")

        assert "Image generated successfully" in result
        mock_client.models.generate_images.assert_called_once()

        # Now, test the agent instantiation to ensure no config errors
        assert agent.name == "image_generator"
        assert len(agent.tools) == 1
        assert agent.tools[0].__name__ == "generate_image"
