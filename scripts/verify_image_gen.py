import sys
import os
import asyncio
from unittest.mock import MagicMock, patch, mock_open

# Add project root to path
sys.path.append(os.getcwd())

# Ensure we can import the module (dependencies might need mocking if they fail import)
# We preemptively mock agent_platform.config to avoid environment errors during import
sys.modules["agent_platform.config"] = MagicMock()
from domains.course_creator.image_generator import tools

async def run_verification():
    print("Verifying generate_image_from_prompt...")

    # We patch the objects AS THEY ARE USED IN THE TOOLS MODULE
    with patch("domains.course_creator.image_generator.tools.genai") as mock_genai, \
         patch("domains.course_creator.image_generator.tools.Path") as MockPath, \
         patch("builtins.open", mock_open()) as mock_file:
        
        # Setup GenAI Mock
        mock_client_instance = MagicMock()
        mock_genai.Client.return_value = mock_client_instance
        
        mock_response = MagicMock()
        # Ensure image_bytes matches what existing code expects (bytes)
        mock_image_obj = MagicMock()
        mock_image_obj.image.image_bytes = b"fake_image_data"
        mock_response.generated_images = [mock_image_obj]
        
        mock_client_instance.models.generate_images.return_value = mock_response

        # Setup Path Mock
        mock_path_instance = MagicMock()
        MockPath.return_value = mock_path_instance
        # Mock the / operator behavior: path / "str" -> path
        mock_path_instance.__truediv__.return_value = mock_path_instance 
        # Mock absolute path return
        mock_path_instance.absolute.return_value = "/app/artifacts/generated_images/file.png"

        # Run the function
        path = await tools.generate_image_from_prompt("test prompt")
        
        print(f"Success! Output path: {path}")

        # Verify Client Call
        # Note: generate_image_from_prompt instantiates Client() then calls models.generate_images()
        mock_genai.Client.assert_called() 
        mock_client_instance.models.generate_images.assert_called_once()
        print("Verified: Client called.")

        # Verify File Write
        mock_file.assert_called()
        mock_file().write.assert_called_with(b"fake_image_data")
        print("Verified: File written.")
        
        # Verify Path Construction
        # Check that we tried to create the directory
        mock_path_instance.mkdir.assert_called()
        print("Verified: Directory created.")
        
        # Check constructor was called with the correct path
        MockPath.assert_called_with("/app/artifacts/generated_images")
        print("Verified: Path initialized.")

if __name__ == "__main__":
    asyncio.run(run_verification())
