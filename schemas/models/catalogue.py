from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ModelCapabilities(BaseModel):
    multimodal_input: bool = Field(default=False, description="Can accept images, audio, video as input")
    image_generation: bool = Field(default=False, description="Can generate images")
    audio_generation: bool = Field(default=False, description="Can generate audio")
    tool_use: bool = Field(default=True, description="Supports function calling")
    json_mode: bool = Field(default=True, description="Supports structured JSON output")

class ModelInfo(BaseModel):
    id: str
    display_name: str
    tier: Literal["lite", "flash", "pro", "ultra"]
    family: Literal["gemini", "imagen", "veo", "gemma"]
    version: str
    capabilities: ModelCapabilities
    is_experimental: bool = False
    is_preview: bool = False
    context_window: int = 1048576 # Default 1M for Gemini 1.5+

    @property
    def is_production_ready(self) -> bool:
        return not (self.is_experimental or self.is_preview)

# --- The Catalogue ---

MODEL_CATALOGUE: List[ModelInfo] = [
    # --- Gemini 3 Family ---
    ModelInfo(
        id="models/gemini-3-flash-preview",
        display_name="Gemini 3 Flash Preview",
        tier="flash",
        family="gemini",
        version="3.0",
        is_preview=True,
        capabilities=ModelCapabilities(multimodal_input=True),
    ),
    ModelInfo(
        id="models/gemini-3-pro-preview",
        display_name="Gemini 3 Pro Preview",
        tier="pro",
        family="gemini",
        version="3.0",
        is_preview=True,
        capabilities=ModelCapabilities(multimodal_input=True),
    ),

    # --- Gemini 2.5 Family ---
    ModelInfo(
        id="models/gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        tier="flash",
        family="gemini",
        version="2.5",
        capabilities=ModelCapabilities(multimodal_input=True),
    ),
    ModelInfo(
        id="models/gemini-2.5-flash-lite",
        display_name="Gemini 2.5 Flash-Lite",
        tier="lite",
        family="gemini",
        version="2.5",
        capabilities=ModelCapabilities(multimodal_input=True),
    ),
    ModelInfo(
        id="models/gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        tier="pro",
        family="gemini",
        version="2.5",
        capabilities=ModelCapabilities(multimodal_input=True),
    ),
    
    # --- Gemini 2.0 Family ---
    ModelInfo(
        id="models/gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        tier="flash",
        family="gemini",
        version="2.0",
        capabilities=ModelCapabilities(multimodal_input=True),
    ),
     ModelInfo(
        id="models/gemini-2.0-flash-lite",
        display_name="Gemini 2.0 Flash-Lite",
        tier="lite",
        family="gemini",
        version="2.0",
        capabilities=ModelCapabilities(multimodal_input=True),
    ),

    # --- Image Generation ---
    ModelInfo(
        id="models/gemini-2.5-flash-image",
        display_name="Nano Banana (Gemini 2.5 Image)",
        tier="flash",
        family="gemini",
        version="2.5",
        is_experimental=True,
        capabilities=ModelCapabilities(multimodal_input=True, image_generation=True),
    ),
    ModelInfo(
        id="models/imagen-4.0-generate-001",
        display_name="Imagen 4",
        tier="pro",
        family="imagen",
        version="4.0",
        capabilities=ModelCapabilities(image_generation=True, tool_use=False, json_mode=False),
    ),
     ModelInfo(
        id="models/imagen-4.0-fast-generate-001",
        display_name="Imagen 4 Fast",
        tier="flash",
        family="imagen",
        version="4.0",
        capabilities=ModelCapabilities(image_generation=True, tool_use=False, json_mode=False),
    ),
    ModelInfo(
        id="models/imagen-3.0-generate-001",
        display_name="Imagen 3",
        tier="pro",
        family="imagen",
        version="3.0",
        capabilities=ModelCapabilities(image_generation=True, tool_use=False, json_mode=False),
    ),
    

]

    capabilities: List[str] = [],
    tier: Literal["lite", "flash", "pro", "ultra"] | None = None,
    family: str | None = None
) -> str:
    """
    Smart selection logic to find the best model ID based on requirements.
    
    Args:
        capabilities: List of required capabilities (e.g. 'image_generation', 'multimodal_input')
        tier: Preferred tier (lite, flash, pro). If None, defaults to 'flash'.
        prefer_latest: If True, prefers higher version numbers.
        family: Optional family filter ('gemini', 'imagen').
    
    Returns:
        The model ID string.
    """
    candidates = MODEL_CATALOGUE
    
    # If no specific capabilities requested, assume we want a general purpose text/multimodal model
    if not capabilities and not family:
        candidates = [m for m in candidates if m.capabilities.multimodal_input]

    # Filter by capabilities
    for cap in capabilities:
        if cap == 'image_generation':
            candidates = [m for m in candidates if m.capabilities.image_generation]
        elif cap == 'multimodal_input':
            candidates = [m for m in candidates if m.capabilities.multimodal_input]
        # Add more capability checks as needed
            
    if not candidates:
        raise ValueError(f"No models found matching criteria: {capabilities}, {tier}, {family}")

    # Sort by version (descending)
    candidates.sort(key=lambda m: m.version, reverse=True)
    
    # Filter/Sort by Tier
    if tier:
        # strict match first
        tier_match = [m for m in candidates if m.tier == tier]
        if tier_match:
            return tier_match[0].id
            
    # Default fallback logic if specific tier not found or not specified
    # Prefer Flash -> Pro -> Lite if not specified
    for target_tier in ["flash", "pro", "lite"]:
        match = [m for m in candidates if m.tier == target_tier]
        if match:
            return match[0].id
            
    return candidates[0].id
