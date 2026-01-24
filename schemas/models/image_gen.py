"""
Image Generation Models.

Defines the Pydantic schemas for Image Generation requests and responses,
inheriting from Google GenAI types where applicable.
"""

from google.genai import types
from pydantic import BaseModel, Field


class ImageGenerationRequest(types.GenerateImagesConfig):
    """Request model for generating an image."""

    prompt: str = Field(..., description="The description of the image to generate.")
    # aspect_ratio is inherited from GenerateImagesConfig
    style: str | None = Field(
        None, description="The artistic style (e.g., 'photorealistic', 'cartoon')."
    )


class ImageGenerationResponse(BaseModel):
    """Response model containing the generated image information."""

    image_url: str = Field(..., description="The URL of the generated image.")
    revised_prompt: str | None = Field(
        None, description="The prompt as revised by the model for better generation."
    )
