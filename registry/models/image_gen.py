from pydantic import BaseModel, Field
from typing import Optional, List

class ImageGenerationRequest(BaseModel):
    """Request model for generating an image."""
    prompt: str = Field(..., description="The description of the image to generate.")
    aspect_ratio: str = Field("1:1", description="The desired aspect ratio of the image (e.g., '16:9', '1:1').")
    style: Optional[str] = Field(None, description="The artistic style (e.g., 'photorealistic', 'cartoon').")

class ImageGenerationResponse(BaseModel):
    """Response model containing the generated image information."""
    image_url: str = Field(..., description="The URL of the generated image.")
    revised_prompt: Optional[str] = Field(None, description="The prompt as revised by the model for better generation.")
