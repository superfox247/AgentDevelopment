import base64
import os
from pathlib import Path
from starlette.concurrency import run_in_threadpool

from google import genai
from google.genai import types
from agent_platform.config import PlatformConfig

import logging

logger = logging.getLogger(__name__)

async def generate_image_from_prompt(prompt: str, model: str | None = None) -> str:
    """
    Generates an image from a prompt using the specified Gemini/Imagen model.
    Returns the path to the generated image.
    """
    config = PlatformConfig()
    if model is None:
        model = config.default_image_model

    logger.info(f"Generating image with model: {model}, prompt: {prompt}")

    client = genai.Client(api_key=config.gemini_api_key)

    # Sanitize prompt for filename
    safe_prompt = "".join([c if c.isalnum() else "_" for c in prompt])[:50]
    filename = f"generated_{safe_prompt}_{model.replace('/', '_')}.png"
    
    # REQUIRED: Save to /app/artifacts for Docker volume persistence
    # This path is mounted to the host's ./artifacts directory
    output_dir = Path("/app/artifacts/generated_images")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    def _generate_sync():
        logger.info("Executing sync generation request...")
        if "gemini" in model.lower():
            # Gemini 2.5 Flash Image uses generate_content
            # Note: We must verify if this model supports tools or pure content generation
            return client.models.generate_content(
                model=model,
                contents=prompt,
                # No specific config needed for default image generation
            )
        else:
            # Imagen models use generate_images
            return client.models.generate_images(
                model=model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )

    try:
        # Run blocking GenAI call in a threadpool to avoid blocking the asyncio event loop
        response = await run_in_threadpool(_generate_sync)
        logger.info(f"Generation successful. Response type: {type(response)}")
        
        image_bytes = None

        # Case A: Imagen Response (generate_images)
        if hasattr(response, "generated_images") and response.generated_images:
            logger.info("Extracting image from 'generated_images' (Imagen flow)...")
            image_bytes = response.generated_images[0].image.image_bytes
            
        # Case B: Gemini Response (generate_content)
        elif hasattr(response, "candidates") and response.candidates:
             logger.info("Extracting image from 'candidates' (Gemini flow)...")
             parts = response.candidates[0].content.parts
             logger.info(f"Found {len(parts)} parts in content.")
             for i, part in enumerate(parts):
                 # Check for inline data (image)
                 if part.inline_data:
                     logger.info(f"Part {i} has inline_data. Extracting bytes...")
                     image_bytes = part.inline_data.data
                     break
                 else:
                     logger.info(f"Part {i} has no inline_data. Text: {part.text[:50] if part.text else 'None'}")
        
        if image_bytes:
            def _write_image():
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
            
            await run_in_threadpool(_write_image)
            logger.info(f"Image saved to: {output_path}")
            return str(output_path.absolute())
            
        else:
            logger.error("No image bytes found in response.")
            raise RuntimeError(f"No images returned for model {model} (Response type: {type(response)})")

    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        # Capture full error context
        raise RuntimeError(f"Image generation failed with model {model}. Error: {e}")
