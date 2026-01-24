"""
Schemas and Model Registry.

Contains:
- Global Pydantic Models (Protocol, ImageGen)
- Model Catalogue (Availability, Pricing, Capability definitions)
"""
# Registry Package
from .models.image_gen import ImageGenerationRequest as ImageGenerationRequest
from .models.image_gen import ImageGenerationResponse as ImageGenerationResponse
