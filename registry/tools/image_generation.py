import logging
import os
import time

from google import genai
from google.genai import types

from agent_platform.config import config

logger = logging.getLogger(__name__)


def generate_image(
    prompt: str, aspect_ratio: str = "1:1", style: str | None = None
) -> str:
    """
    Generates an image using Google's Gemini API (Imagen 3).

    Args:
        prompt: The text description of the image to generate.
        aspect_ratio: The aspect ratio of the image (e.g., "1:1", "16:9", "9:16", "3:4", "4:3"). Defaults to "1:1".
        style: The artistic style of the image (e.g., "photorealistic", "cartoon", "sketch"). Defaults to None.

    Returns:
        The file path to the generated image.
    """
    try:
        client = genai.Client(api_key=config.gemini_api_key)

        full_prompt = prompt
        if style:
            full_prompt = f"{style} style: {prompt}"

        logger.info(f"Generating image with prompt: {full_prompt}")

        # Call Imagen 3 model
        response = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
            ),
        )

        if not response.generated_images:
            return "Error: No images generated."

        # Save to a local directory
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)

        # Simple filename based on timestamp
        filename = f"{output_dir}/image_{int(time.time())}.png"

        # Save the image bytes
        first_image = response.generated_images[0]
        if not first_image.image or not first_image.image.image_bytes:
            return "Error: Image generation returned no data."

        image_bytes = first_image.image.image_bytes
        with open(filename, "wb") as f:
            f.write(image_bytes)

        # Convert absolute path for clarity
        abs_path = os.path.abspath(filename)
        return f"Image generated successfully and saved to: {abs_path}"

    except Exception as e:
        logger.exception("Unexpected error in image generation")
        return f"Error generating image: {e!s}"
