"""
Persistence layer for Image Generator.

Handles the saving of generated image bytes to the file system (or other providers).
"""

import logging
import re
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


class ImagePersistence(Protocol):
    """Protocol for saving generated images."""

    def save_image(self, image_bytes: bytes, prompt: str, model: str) -> str:
        """Saves image bytes and returns the absolute path to the file."""
        ...


class FileSystemImagePersistence:
    """Saves images to the local file system."""

    def __init__(self, output_dir: Path | str = "artifacts/generated_images"):
        self.output_dir = Path(output_dir)

    def save_image(self, image_bytes: bytes, prompt: str, model: str) -> str:
        """Saves the image to disk with a sanitized filename."""
        # Sanitize prompt for filename
        # Replace non-alphanumeric (except space) with underscore, then truncate
        safe_prompt = re.sub(r"[^a-zA-Z0-9 ]", "_", prompt).replace(" ", "_")[:50]
        safe_model = model.replace("/", "_")
        filename = f"generated_{safe_prompt}_{safe_model}.png"

        # Ensure directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_path = self.output_dir / filename

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Image saved to: {output_path}")
        return str(output_path.absolute())
