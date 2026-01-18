import base64
import os
from pathlib import Path
from starlette.concurrency import run_in_threadpool

from google import genai
from google.genai import types
from agent_platform.config import PlatformConfig

async def generate_image_from_prompt(prompt: str, model: str | None = None) -> str:
    """
    Generates an image from a prompt using the specified Gemini/Imagen model.
    Returns the path to the generated image.
    """
    config = PlatformConfig()
    if model is None:
        model = config.default_image_model

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
        
        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            
            def _write_image():
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
            
            await run_in_threadpool(_write_image)
            return str(output_path.absolute())
            
        else:
            raise RuntimeError(f"No images returned for model {model}")

    except Exception as e:
        # Capture full error context
        raise RuntimeError(f"Image generation failed with model {model}. Error: {e}")
