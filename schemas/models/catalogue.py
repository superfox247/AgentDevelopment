"""
Model Catalogue and Selection Logic.

Defines the available Google AI models (Gemini, Imagen) with metadata
about their capabilities, tiers, and versions.
"""

from typing import Literal

from google.genai import types


# We extend types.Model to add our specific metadata
class ModelInfo(types.Model):
    """Extended Model metadata for the catalogue."""
    # Tier and Family are custom taxonomy, so we keep them.
    tier: Literal["lite", "flash", "pro", "ultra"] | None = None
    family: Literal["gemini", "imagen", "veo", "gemma"] | None = None

    @property
    def id(self) -> str:
        return self.name or ""

    @property
    def is_production_ready(self) -> bool:
        # Simple heuristic based on name if needed
        name = self.name or ""
        return "preview" not in name and "experimental" not in name

# --- The Catalogue ---

MODEL_CATALOGUE: list[ModelInfo] = [
    # --- Gemini 3 Family ---
    ModelInfo(
        name="models/gemini-3-flash-preview",
        display_name="Gemini 3 Flash Preview",
        tier="flash",
        family="gemini",
        version="3.0",
        supported_actions=["generateContent"],
    ),
    ModelInfo(
        name="models/gemini-3-pro-preview",
        display_name="Gemini 3 Pro Preview",
        tier="pro",
        family="gemini",
        version="3.0",
        supported_actions=["generateContent"],
    ),

    # --- Gemini 2.5 Family ---
    ModelInfo(
        name="models/gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        tier="flash",
        family="gemini",
        version="2.5",
        supported_actions=["generateContent"],
    ),
    ModelInfo(
        name="models/gemini-2.5-flash-lite",
        display_name="Gemini 2.5 Flash-Lite",
        tier="lite",
        family="gemini",
        version="2.5",
        supported_actions=["generateContent"],
    ),
    ModelInfo(
        name="models/gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        tier="pro",
        family="gemini",
        version="2.5",
        supported_actions=["generateContent"],
    ),

    # --- Gemini 2.0 Family ---
    ModelInfo(
        name="models/gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        tier="flash",
        family="gemini",
        version="2.0",
        supported_actions=["generateContent"],
    ),
     ModelInfo(
        name="models/gemini-2.0-flash-lite",
        display_name="Gemini 2.0 Flash-Lite",
        tier="lite",
        family="gemini",
        version="2.0",
        supported_actions=["generateContent"],
    ),

    # --- Image Generation ---
    ModelInfo(
        name="models/gemini-2.5-flash-image",
        display_name="Nano Banana (Gemini 2.5 Image)",
        tier="flash",
        family="gemini",
        version="2.5",
        supported_actions=["generateContent", "generateImages"],
    ),
    ModelInfo(
        name="models/imagen-4.0-generate-001",
        display_name="Imagen 4",
        tier="pro",
        family="imagen",
        version="4.0",
        supported_actions=["generateImages"],
    ),
     ModelInfo(
        name="models/imagen-4.0-fast-generate-001",
        display_name="Imagen 4 Fast",
        tier="flash",
        family="imagen",
        version="4.0",
        supported_actions=["generateImages"],
    ),
    ModelInfo(
        name="models/imagen-3.0-generate-001",
        display_name="Imagen 3",
        tier="pro",
        family="imagen",
        version="3.0",
        supported_actions=["generateImages"],
    ),
]

def _filter_by_capability(candidates: list[ModelInfo], capability: str) -> list[ModelInfo]:
    """Filters candidates based on a specific capability."""
    if capability in ['image_generation', 'generateImages']:
        return [m for m in candidates if m.supported_actions and "generateImages" in m.supported_actions]
    elif capability == 'multimodal_input':
        return [m for m in candidates if m.supported_actions and "generateContent" in m.supported_actions and m.family == "gemini"]
    return candidates

def _find_by_tier(candidates: list[ModelInfo], tier: str) -> ModelInfo | None:
    """Finds the first candidate matching the given tier."""
    for m in candidates:
        if m.tier == tier:
            return m
    return None

def _get_base_candidates(
    capabilities: list[str], family: str | None
) -> list[ModelInfo]:
    """Retrieves initial candidates based on capabilities and family."""
    candidates = MODEL_CATALOGUE
    if not capabilities and not family:
        candidates = [
            m
            for m in candidates
            if m.supported_actions and "generateContent" in m.supported_actions
        ]

    for cap in capabilities:
        candidates = _filter_by_capability(candidates, cap)

    if family:
        candidates = [m for m in candidates if m.family == family]

    return candidates


def _sort_candidates_by_version(candidates: list[ModelInfo]) -> list[ModelInfo]:
    """Sorts candidates by version descending."""
    return sorted(candidates, key=lambda m: m.version or "", reverse=True)


def select_best_model(
    capabilities: list[str] = [],
    tier: Literal["lite", "flash", "pro", "ultra"] | None = None,
    family: str | None = None
) -> str:
    """
    Smart selection logic to find the best model ID based on requirements.

    Args:
        capabilities: List of required capabilities via supported_actions.
        tier: Preferred tier (lite, flash, pro).
        family: Optional family filter ('gemini', 'imagen').

    Returns:
        The model ID string.
    """
    candidates = _get_base_candidates(capabilities, family)

    if not candidates:
        raise ValueError(
            f"No models found matching criteria: {capabilities}, {tier}, {family}"
        )

    candidates = _sort_candidates_by_version(candidates)

    # 1. Exact Tier Match
    if tier:
        if match := _find_by_tier(candidates, tier):
            return match.name or ""

    # 2. Fallback Tier Strategy (Flash -> Pro -> Lite)
    for target_tier in ["flash", "pro", "lite"]:
        if match := _find_by_tier(candidates, target_tier):
            return match.name or ""

    # 3. Last Resort
    return candidates[0].name or ""
