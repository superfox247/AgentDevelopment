import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from domains.course_creator.image_generator.tools import generate_image_from_prompt

class TestImageGenerator(unittest.TestCase):
    @patch("domains.course_creator.image_generator.tools.genai.Client")
    @patch("domains.course_creator.image_generator.tools.PlatformConfig")
    def test_generate_image_success(self, mock_config, mock_client_cls):
        # Setup mocks
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_response = MagicMock()
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"fake_image_data"
        mock_response.generated_images = [mock_image]
        
        mock_client.models.generate_images.return_value = mock_response
        
        # Execute
        prompt = "test prompt"
        model = "models/test-model"
        result_path = generate_image_from_prompt(prompt, model)
        
        # Verify
        mock_client.models.generate_images.assert_called_once()
        call_args = mock_client.models.generate_images.call_args
        self.assertEqual(call_args.kwargs['model'], model)
        self.assertEqual(call_args.kwargs['prompt'], prompt)
        
        self.assertTrue(os.path.exists(result_path))
        with open(result_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"fake_image_data")
        
        # Cleanup
        os.remove(result_path)

if __name__ == "__main__":
    unittest.main()
