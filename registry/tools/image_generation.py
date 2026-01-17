import logging
from typing import Optional

from google.api_core.exceptions import GoogleAPICallError
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

from agent_platform.config import config

logger = logging.getLogger(__name__)

def generate_image(prompt: str, aspect_ratio: str = "1:1", style: Optional[str] = None) -> str:
    """
    Generates an image using Google's Vertex AI Imagen model.
    
    Args:
        prompt: The text description of the image to generate.
        aspect_ratio: The aspect ratio of the image (e.g., "1:1", "16:9", "9:16", "3:4", "4:3"). Defaults to "1:1".
        style: The artistic style of the image (e.g., "photorealistic", "cartoon", "sketch"). Defaults to None.
        
    Returns:
        The URL of the generated image (stored in GCS or similar, depending on the SDK response handling).
        Note: The current vertexai SDK `generate_images` returns an `ImageGenerationResponse` containing `images`.
        The `images[0]._generated_image` object has methods to save or view.
        However, for this tool to work in the context of an agent, we typically need a URL or a base64 string.
        The `vertexai` library's `Image` class allows `save()`. 
        
        CRITICAL: Since we don't have a persistent public storage bucket configured in this simple tool, 
        we will simulate the URL return by logging the generation and returning a placeholder or local path if possible.
        BUT, the requirement is "gives back a picture". 
        
        Let's try to verify if `show()` or `squeezed` output is possible. 
        Actually, for an API based agent, we should probably return a path to a saved file if running locally,
        or a GCS URI if configured.
        
        Given the environment is local dev, I will save it to a local 'generated_images' folder and return the file path.
    """
    try:
        # Initialize Vertex AI
        vertexai.init(project=config.google_cloud_project, location=config.google_cloud_location)
        
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        full_prompt = prompt
        if style:
            full_prompt = f"{style} style: {prompt}"
            
        logger.info(f"Generating image with prompt: {full_prompt}")
        
        images = model.generate_images(
            prompt=full_prompt,
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            language="en",
        )
        
        if not images:
             return "Error: No images generated."

        # Save to a local directory for now
        output_dir = "generated_images"
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Simple filename based on prompt hash or timestamp would be better, but keeping it simple
        import time
        filename = f"{output_dir}/image_{int(time.time())}.png"
        images[0].save(location=filename, include_generation_parameters=False)
        
        # Convert absolute path for clarity
        abs_path = os.path.abspath(filename)
        return f"Image generated successfully and saved to: {abs_path}"

    except GoogleAPICallError as e:
        logger.error(f"Vertex AI API Error: {e}")
        return f"Error generating image: {e.message}"
    except Exception as e:
        logger.exception("Unexpected error in image generation")
        return f"Error generating image: {str(e)}"
