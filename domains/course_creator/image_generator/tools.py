import logging
from pathlib import Path

from google import genai
from google.genai import types
from starlette.concurrency import run_in_threadpool

from agent_platform.config import PlatformConfig

logger = logging.getLogger(__name__)



async def generate_image_from_prompt(prompt: str, model: str | None = None) -> str:
    """
    Generates an image from a prompt using the specified Gemini/Imagen model.
    Returns the absolute path to the generated image.
    """
    config = PlatformConfig()
    model = model or config.default_image_model
    client = genai.Client(api_key=config.gemini_api_key)

    logger.info(f"Generating image. Model: {model}, Prompt: {prompt[:50]}...")

    # Route to appropriate handler
    if "imagen" in model.lower():
        image_bytes = await run_in_threadpool(_generate_with_imagen, client, model, prompt)
    else:
        # Default to Gemini (Nano Banana / Flash Image) protocols
        image_bytes = await run_in_threadpool(_generate_with_gemini, client, model, prompt)

    # Persistence
    result = await run_in_threadpool(_save_image, image_bytes, prompt, model)
    return result


def _generate_with_imagen(client: genai.Client, model: str, prompt: str) -> bytes:
    logger.info("Calling Imagen API (generate_images)...")
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1)
    )
    if not response.generated_images:
        raise RuntimeError("Imagen returned no images.")
    return response.generated_images[0].image.image_bytes


def _generate_with_gemini(client: genai.Client, model: str, prompt: str) -> bytes:
    logger.info("Calling Gemini API (generate_content)...")
    # Gemini image gen optimization: explicitly ask for image generation if not implied
    # But usually 'prompt' is enough.
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    if not response.candidates:
         raise RuntimeError("Gemini returned no candidates.")

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data

    raise RuntimeError("Gemini response contained no inline_data (image).")


def _save_image(image_bytes: bytes, prompt: str, model: str) -> str:
    # Sanitize prompt for filename
    safe_prompt = "".join([c if c.isalnum() else "_" for c in prompt])[:50]
    safe_model = model.replace("/", "_")
    filename = f"generated_{safe_prompt}_{safe_model}.png"

    # Use relative path which works for both Local (Root) and Docker (/app)
    # assuming CWD is set correctly in both environments.
    output_dir = Path("artifacts/generated_images")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    logger.info(f"Image saved to: {output_path}")
    return str(output_path.absolute())
