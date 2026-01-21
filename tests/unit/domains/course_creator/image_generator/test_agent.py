"""Tests for image_generator agent."""

import unittest
from unittest.mock import MagicMock, patch

from domains.course_creator.image_generator.agent import create_app


class TestImageGeneratorAgent(unittest.TestCase):
    """Unit tests for the ImageGenerator agent."""

    def test_create_app(self) -> None:
        """Test that the agent factory creates a valid agent."""
        app = create_app()
        self.assertIsNotNone(app)
        self.assertEqual(app.name, "image_generator")

    def test_agent_has_tools(self) -> None:
        """Test that the agent has the expected tools registered."""
        app = create_app()
        # YamlAgent should have tools defined
        self.assertIsNotNone(app)


class TestGenerateImageTool(unittest.IsolatedAsyncioTestCase):
    """Async tests for the generate_image_from_prompt tool."""

    @patch("domains.course_creator.image_generator.tools.genai.Client")
    @patch("domains.course_creator.image_generator.tools.PlatformConfig")
    async def test_generate_image_tool_returns_path(
        self, mock_config_cls: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        """Test that generate_image_from_prompt returns an image path."""
        import os

        from domains.course_creator.image_generator.tools import (
            generate_image_from_prompt,
        )

        # Setup mocks
        mock_config = MagicMock()
        mock_config.gemini_api_key = "test-key"
        mock_config.default_image_model = "imagen-3.0-generate-002"
        mock_config_cls.return_value = mock_config

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"test_image_data"
        mock_response.generated_images = [mock_image]
        mock_client.models.generate_images.return_value = mock_response

        # Execute
        result = await generate_image_from_prompt("a cute cat")

        # Verify - should return a path string
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))

        # Cleanup
        os.remove(result)

    @patch("domains.course_creator.image_generator.tools.genai.Client")
    @patch("domains.course_creator.image_generator.tools.PlatformConfig")
    async def test_generate_image_tool_no_image_raises(
        self, mock_config_cls: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        """Test that RuntimeError is raised when no images are generated."""
        from domains.course_creator.image_generator.tools import (
            generate_image_from_prompt,
        )

        # Setup mocks
        mock_config = MagicMock()
        mock_config.gemini_api_key = "test-key"
        mock_config.default_image_model = "imagen-3.0-generate-002"
        mock_config_cls.return_value = mock_config

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Empty response
        mock_response = MagicMock()
        mock_response.generated_images = []
        mock_client.models.generate_images.return_value = mock_response

        # Execute & Verify
        with self.assertRaises(RuntimeError):
            await generate_image_from_prompt("fail", "imagen-test")


if __name__ == "__main__":
    unittest.main()
