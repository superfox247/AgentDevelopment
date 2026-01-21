"""Tests for image generator tools."""

import os
import unittest
from unittest.mock import MagicMock, patch


class TestImageGenerator(unittest.IsolatedAsyncioTestCase):
    """Tests for generate_image_from_prompt function."""

    @patch("domains.course_creator.image_generator.tools.genai.Client")
    @patch("domains.course_creator.image_generator.tools.PlatformConfig")
    async def test_generate_image_with_imagen_success(
        self, mock_config_cls: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        """Test successful image generation with Imagen model."""
        # Import inside test to avoid issues with mocking
        from domains.course_creator.image_generator.tools import (
            generate_image_from_prompt,
        )

        # Setup config mock
        mock_config = MagicMock()
        mock_config.gemini_api_key = "test-key"
        mock_config.default_image_model = "imagen-3.0-generate-002"
        mock_config_cls.return_value = mock_config

        # Setup client mock
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"fake_image_data"
        mock_response.generated_images = [mock_image]
        mock_client.models.generate_images.return_value = mock_response

        # Execute
        prompt = "test prompt for imagen"
        model = "imagen-3.0-generate-002"
        result_path = await generate_image_from_prompt(prompt, model)

        # Verify
        mock_client.models.generate_images.assert_called_once()
        call_args = mock_client.models.generate_images.call_args
        self.assertEqual(call_args.kwargs["model"], model)
        self.assertEqual(call_args.kwargs["prompt"], prompt)

        self.assertTrue(os.path.exists(result_path))
        with open(result_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"fake_image_data")

        # Cleanup
        os.remove(result_path)

    @patch("domains.course_creator.image_generator.tools.genai.Client")
    @patch("domains.course_creator.image_generator.tools.PlatformConfig")
    async def test_generate_image_with_gemini_success(
        self, mock_config_cls: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        """Test successful image generation with Gemini model."""
        from domains.course_creator.image_generator.tools import (
            generate_image_from_prompt,
        )

        # Setup config mock
        mock_config = MagicMock()
        mock_config.gemini_api_key = "test-key"
        mock_config.default_image_model = "gemini-2.0-flash-exp"
        mock_config_cls.return_value = mock_config

        # Setup client mock
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Mock Gemini response with inline_data
        mock_part = MagicMock()
        mock_part.inline_data.data = b"gemini_image_bytes"
        mock_content = MagicMock()
        mock_content.parts = [mock_part]
        mock_candidate = MagicMock()
        mock_candidate.content = mock_content
        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        # Execute
        prompt = "test prompt for gemini"
        model = "gemini-2.0-flash-exp"
        result_path = await generate_image_from_prompt(prompt, model)

        # Verify
        mock_client.models.generate_content.assert_called_once()
        self.assertTrue(os.path.exists(result_path))

        # Cleanup
        os.remove(result_path)


if __name__ == "__main__":
    unittest.main()
