import base64
import os
from pathlib import Path

from google import genai
from google.genai import types
from agent_platform.config import PlatformConfig

def generate_image_from_prompt(prompt: str, model: str = "models/gemini-2.5-flash-image") -> str:
    """
    Generates an image from a prompt using the specified Gemini/Imagen model.
    Returns the path to the generated image.
    """
    config = PlatformConfig()
    client = genai.Client(api_key=config.gemini_api_key)

    # Sanitize prompt for filename
    safe_prompt = "".join([c if c.isalnum() else "_" for c in prompt])[:50]
    filename = f"generated_{safe_prompt}_{model.replace('/', '_')}.png"
    
    # Ensure artifacts directory exists
    # We assume standard artifacts location relative to where this runs or a fixed path
    # For this agent, let's use a widely accessible temp or artifacts spot. 
    # In this factory, artifacts are usually in .gemini/brain/... but simple agents might output locally
    # Let's save to a "generated_images" folder in the workspace root for visibility or use a relative path
    # that the UI can pick up. 
    # The Protocol says: "The local file path to the generated image artifact."
    
    # We'll put it in a 'public' directory if possible, or just local `generated`
    output_dir = Path("generated_images")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / filename

    try:
        # Standardize call for image generation capability
        # Note: genai SDK usage for images varies by model type (Imagen vs Gemini).
        # We will attempt the standard generate_images method if available or generate_content 
        
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        
        if response.generated_images:
            image_bytes = response.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            return str(output_path.absolute())
            
        else:
            raise RuntimeError(f"No images returned for model {model}")

    except Exception as e:
        # Fallback or error reporting
        # For "Nano Banana" (Gemini 2.5 Flash Image), it might behave like a text model that outputs image URI?
        # Re-raise for now to see failure in logs if basic call fails
        raise RuntimeError(f"Image generation failed with model {model}: {e}")
