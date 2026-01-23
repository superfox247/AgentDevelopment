from typing import Literal

from google.genai import types
from pydantic import BaseModel, Field

# We extend types.Model to add our specific metadata
class ModelInfo(BaseModel):
    # Map to types.Model fields where possible
    name: str = Field(alias="id") # "models/..."
    display_name: str
    
    # Extra metadata not in types.Model
    tier: Literal["lite", "flash", "pro", "ultra"]
    family: Literal["gemini", "imagen", "veo", "gemma"]
    version: str
    
    # Use standard field for capabilities
    supported_generation_methods: list[str] = Field(default_factory=list)
    
    is_experimental: bool = False
    is_preview: bool = False
    context_window: int = 1048576 # Default 1M for Gemini 1.5+

    @property
    def id(self) -> str:
        return self.name

    @property
    def is_production_ready(self) -> bool:
        return not (self.is_experimental or self.is_preview)

# --- The Catalogue ---

MODEL_CATALOGUE: list[ModelInfo] = [
    # --- Gemini 3 Family ---
    ModelInfo(
        id="models/gemini-3-flash-preview",
        display_name="Gemini 3 Flash Preview",
        tier="flash",
        family="gemini",
        version="3.0",
        is_preview=True,
        supported_generation_methods=["generateContent"],
    ),
    ModelInfo(
        id="models/gemini-3-pro-preview",
        display_name="Gemini 3 Pro Preview",
        tier="pro",
        family="gemini",
        version="3.0",
        is_preview=True,
        supported_generation_methods=["generateContent"],
    ),

    # --- Gemini 2.5 Family ---
    ModelInfo(
        id="models/gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        tier="flash",
        family="gemini",
        version="2.5",
        supported_generation_methods=["generateContent"],
    ),
    ModelInfo(
        id="models/gemini-2.5-flash-lite",
        display_name="Gemini 2.5 Flash-Lite",
        tier="lite",
        family="gemini",
        version="2.5",
        supported_generation_methods=["generateContent"],
    ),
    ModelInfo(
        id="models/gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        tier="pro",
        family="gemini",
        version="2.5",
        supported_generation_methods=["generateContent"],
    ),

    # --- Gemini 2.0 Family ---
    ModelInfo(
        id="models/gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        tier="flash",
        family="gemini",
        version="2.0",
        supported_generation_methods=["generateContent"],
    ),
     ModelInfo(
        id="models/gemini-2.0-flash-lite",
        display_name="Gemini 2.0 Flash-Lite",
        tier="lite",
        family="gemini",
        version="2.0",
        supported_generation_methods=["generateContent"],
    ),

    # --- Image Generation ---
    ModelInfo(
        id="models/gemini-2.5-flash-image",
        display_name="Nano Banana (Gemini 2.5 Image)",
        tier="flash",
        family="gemini",
        version="2.5",
        is_experimental=True,
        supported_generation_methods=["generateContent", "generateImages"],
    ),
    ModelInfo(
        id="models/imagen-4.0-generate-001",
        display_name="Imagen 4",
        tier="pro",
        family="imagen",
        version="4.0",
        supported_generation_methods=["generateImages"],
    ),
     ModelInfo(
        id="models/imagen-4.0-fast-generate-001",
        display_name="Imagen 4 Fast",
        tier="flash",
        family="imagen",
        version="4.0",
        supported_generation_methods=["generateImages"],
    ),
    ModelInfo(
        id="models/imagen-3.0-generate-001",
        display_name="Imagen 3",
        tier="pro",
        family="imagen",
        version="3.0",
        supported_generation_methods=["generateImages"],
    ),


]

def select_best_model(
    capabilities: list[str] = [],
    tier: Literal["lite", "flash", "pro", "ultra"] | None = None,
    family: str | None = None
) -> str:
    """
    Smart selection logic to find the best model ID based on requirements.

    Args:
        capabilities: List of required capabilities via supported_generation_methods (e.g. 'generateImages')
                      or legacy keywords 'image_generation', 'multimodal_input'.
        tier: Preferred tier (lite, flash, pro). If None, defaults to 'flash'.
        family: Optional family filter ('gemini', 'imagen').

    Returns:
        The model ID string.
    """
    candidates = MODEL_CATALOGUE

    # Default to text generation if nothing specified
    if not capabilities and not family:
        candidates = [m for m in candidates if "generateContent" in m.supported_generation_methods]

    # Filter by capabilities logic
    for cap in capabilities:
        if cap == 'image_generation':
            candidates = [m for m in candidates if "generateImages" in m.supported_generation_methods]
        elif cap == 'multimodal_input':
            # Generally all gemini models support multimodal.
            candidates = [m for m in candidates if "generateContent" in m.supported_generation_methods and m.family == "gemini"]
        elif cap == 'generateImages':
             candidates = [m for m in candidates if "generateImages" in m.supported_generation_methods]
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
            return tier_match[0].name

    # Default fallback logic if specific tier not found or not specified
    # Prefer Flash -> Pro -> Lite if not specified
    for target_tier in ["flash", "pro", "lite"]:
        match = [m for m in candidates if m.tier == target_tier]
        if match:
            return match[0].name

    return candidates[0].name
