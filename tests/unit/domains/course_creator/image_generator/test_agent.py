from unittest.mock import MagicMock, patch

import pytest

from domains.course_creator.image_generator.agent import create_app
from domains.course_creator.image_generator.tools import generate_image_from_prompt


def test_create_app():
    app = create_app()
    assert app is not None
    assert app.name == "image_generator"


@patch("domains.course_creator.image_generator.tools.ImageGenerationModel")
def test_generate_image_tool(mock_model_cls):
    # Setup mock
    mock_model_instance = MagicMock()
    mock_model_cls.from_pretrained.return_value = mock_model_instance

    mock_image = MagicMock()
    mock_model_instance.generate_images.return_value = [mock_image]

    # Run tool
    result = generate_image_from_prompt("a cute cat")

    # Verify
    assert "generated_images" in result
    mock_model_instance.generate_images.assert_called_once()
    mock_image.save.assert_called_once()


@patch("domains.course_creator.image_generator.tools.ImageGenerationModel")
def test_generate_image_tool_no_image(mock_model_cls):
    mock_model_instance = MagicMock()
    mock_model_cls.from_pretrained.return_value = mock_model_instance
    mock_model_instance.generate_images.return_value = []

    with pytest.raises(RuntimeError):
        generate_image_from_prompt("fail")
