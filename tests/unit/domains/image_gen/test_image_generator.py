import pytest
import warnings
from unittest.mock import MagicMock, AsyncMock, patch
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
    
    with patch("registry.tools.image_generation.vertexai") as mock_vertex: # Mock Vertex AI
        with patch("registry.tools.image_generation.ImageGenerationModel") as mock_model_cls:
            # Mock the image generation model
            mock_model = MagicMock()
            mock_model_cls.from_pretrained.return_value = mock_model
            
            # Mock generate_images response
            mock_image = MagicMock()
            mock_image.save = MagicMock() # Mock save
            mock_model.generate_images.return_value = [mock_image]
            
            # IMPORTANT: We are testing the tool logic here essentially if we call the tool function directly
            # OR we rely on the agent to call it. 
            # For a UNIT test of the agent, we might just want to verify it CAN process a request.
            # But since it's an LLM agent, mocking the LLM decision to call the tool is complex without a real LLM.
            # So standard practice: Test the tool function separately, and assume Agent works if Config is valid.
            
            # Let's test the tool function directly to ensure it works as expected
            from registry.tools.image_generation import generate_image
            result = generate_image("test prompt")
            
            assert "Image generated successfully" in result
            mock_model.generate_images.assert_called_once()
            
            # Now, test the agent instantiation to ensure no config errors
            assert agent.name == "image_generator"
            assert len(agent.tools) == 1
            assert agent.tools[0].__name__ == "generate_image"
