import logging
from typing import Optional

from google import genai
from google.genai import types
from starlette.concurrency import run_in_threadpool

from agent_platform.config import PlatformConfig
from .persistence import ImagePersistence, FileSystemImagePersistence

logger = logging.getLogger(__name__)


class ImageGeneratorService:
    """
    Service for generating images using Google GenAI (Imagen/Gemini).
    Uses Dependency Injection for testability.
    """

    def __init__(
        self,
        client: genai.Client,
        config: PlatformConfig,
        persistence: Optional[ImagePersistence] = None,
    ):
        self.client = client
        self.config = config
        self.persistence = persistence or FileSystemImagePersistence()

    async def generate_image_from_prompt(self, prompt: str, model: str | None = None) -> str:
        """
        Generates an image from a prompt using the specified Gemini/Imagen model.
        Returns the absolute path to the generated image.
        """
        model = model or self.config.default_image_model
        
        logger.info(f"Generating image. Model: {model}, Prompt: {prompt[:50]}...")

        # Routing logic
        # native async calls using client.aio
        if "imagen" in model.lower():
            image_bytes = await self._generate_with_imagen(model, prompt)
        else:
            image_bytes = await self._generate_with_gemini(model, prompt)

        # Persistence (File I/O is blocking, so we keep run_in_threadpool here)
        return await run_in_threadpool(
            self.persistence.save_image, image_bytes, prompt, model
        )

    async def _generate_with_imagen(self, model: str, prompt: str) -> bytes:
        logger.info("Calling Imagen API (generate_images)...")
        # Use Async client
        response = await self.client.aio.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1),
        )
        if not response.generated_images:
            raise RuntimeError("Imagen returned no images.")
        image = response.generated_images[0].image
        if not image or not image.image_bytes:
            raise RuntimeError("Imagen returned an image container but image_bytes was empty.")
        return image.image_bytes

    async def _generate_with_gemini(self, model: str, prompt: str) -> bytes:
        logger.info("Calling Gemini API (generate_content)...")
        # Use Async client
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt
        )

        if not response.candidates:
            raise RuntimeError("Gemini returned no candidates.")

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise RuntimeError("Gemini returned no content parts.")

        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data

        raise RuntimeError("Gemini response contained no inline_data (image).")


# Singleton instance for agent usage
_service_instance: Optional[ImageGeneratorService] = None

def get_service() -> ImageGeneratorService:
    global _service_instance
    if _service_instance is None:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)
        _service_instance = ImageGeneratorService(client=client, config=config)
    return _service_instance


async def generate_image_from_prompt(prompt: str, model: str | None = None) -> str:
    """
    Generates an image from a prompt using the specified Gemini/Imagen model.
    Returns the absolute path to the generated image.
    
    This wrapper function maintains the existing API contract for the agent.
    """
    service = get_service()
    return await service.generate_image_from_prompt(prompt, model)
