import sys
import os
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add workspace root to python path
sys.path.append(os.getcwd())

from domains.course_creator.image_generator.tools import generate_image_from_prompt
from google.genai import types

async def verify_image_tool():
    print("Verifying generate_image_from_prompt...")
    
    # Mock PlatformConfig to avoid needing real API key
    with patch("domains.course_creator.image_generator.tools.PlatformConfig") as MockConfig:
        MockConfig.return_value.gemini_api_key = "fake_key"
        MockConfig.return_value.default_image_model = "mock-default-model"
        
        # Mock genai.Client
        with patch("domains.course_creator.image_generator.tools.genai.Client") as MockClient:
            mock_client_instance = MockClient.return_value
            mock_response = MagicMock()
            
            # Setup mock response structure
            mock_image = MagicMock()
            mock_image.image.image_bytes = b"fake_image_data"
            mock_response.generated_images = [mock_image]
            
            mock_client_instance.models.generate_images.return_value = mock_response
            
            # TEST 1: Check Explicit Model
            print("Running Test 1: Explicit Model...")
            result_path = await generate_image_from_prompt("test prompt", "explicit-model")
            
            # Verify explicit model was used
            mock_client_instance.models.generate_images.assert_called_with(
                model="explicit-model",
                prompt="test prompt",
                config=types.GenerateImagesConfig(number_of_images=1)
            )
            print("SUCCESS: Explicit model used correctly.")

            # TEST 2: Check Default Model
            print("Running Test 2: Default Model...")
            result_path_2 = await generate_image_from_prompt("test prompt 2") # No model arg
            
            # Verify default model was used from config
            mock_client_instance.models.generate_images.assert_called_with(
                model="mock-default-model",
                prompt="test prompt 2",
                config=types.GenerateImagesConfig(number_of_images=1)
            )
            print("SUCCESS: Default model from config used correctly.")
            
            # Verify Path Persistence (on the last result)
            path_obj = Path(result_path_2)
            
            # Check if 'artifacts/generated_images' is in the path parts
            if "artifacts" in path_obj.parts and "generated_images" in path_obj.parts:
                 print("SUCCESS: Output path contains 'artifacts/generated_images'")
            else:
                 print(f"FAILURE: Output path {result_path_2} does not look persistent.")
                 sys.exit(1)

            print("All checks passed.")

if __name__ == "__main__":
    asyncio.run(verify_image_tool())
