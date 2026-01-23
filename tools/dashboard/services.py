
import json
import logging
from typing import Any

from google.adk.runners import Runner
from google.genai.types import Content, Part

# Configure logging
logger = logging.getLogger(__name__)

class ImageGenerationService:
    def __init__(self, runner: Runner):
        self.runner = runner

    async def generate_image(self, user_id: str, session_id: str, prompt: str, model: str) -> str:
        # DEBUG LOGGING
        """
        Generates an image using the Image Generator Agent and returns the path to the generated image.

        Args:
            user_id: The user ID.
            session_id: The session ID.
            prompt: The image generation prompt.
            model: The model to use.

        Returns:
            str: The relative path to the generated image artifact.

        Raises:
            Exception: If generation fails or no image is returned.
        """
        # Ensure session exists (idempotent)
        try:
            await self.runner.session_service.create_session(
                app_name="image_generator",
                user_id=user_id,
                session_id=session_id,
            )
        except Exception:
            pass  # Session might already exist

        message = f"Generate an image. Prompt: {prompt}. Model: {model}"
        msg = Content(role="user", parts=[Part.from_text(text=message)])

        image_path = None

        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=msg
            ):
                logger.info(f"Received agent event: {event}")

                image_path = self._extract_image_path(event) or image_path

        except Exception as e:
            logger.error(f"Error running image agent: {e}", exc_info=True)
            raise e

        if not image_path:
             logger.error("Final state: No image path extracted.")
             raise RuntimeError("Agent finished but no image path found in response.")

        # Normalize path
        image_path = image_path.replace("\\", "/")
        return image_path

    def _extract_image_path(self, event: Any) -> str | None:
        """Helper to extract image path from various event types."""
        try:
            # Case A: Agent returns JSON text (final answer)
            if path := self._extract_from_response_content(event):
                return self._normalize_path(path)

            # Case B: Tool execution result
            if path := self._extract_from_tool_response(event):
                return self._normalize_path(path)

            # Case C: Inspect Content parts for function_response
            if path := self._extract_from_content_parts(event):
                return self._normalize_path(path)

        except Exception as e:
            logger.warning(f"Error parsing event for image path: {e}")

        return None

    def _extract_from_response_content(self, event: Any) -> str | None:
        if hasattr(event, "response") and event.response and hasattr(event.response, "content") and event.response.content:
             return self._parse_json_or_fallback(event.response.content)
        return None

    def _extract_from_tool_response(self, event: Any) -> str | None:
        if hasattr(event, "tool_response") and event.tool_response:
             for tr in event.tool_response:
                 if tr.name == "generate_image_from_prompt" and tr.response:
                     result = tr.response
                     if isinstance(result, str) and "artifacts" in result:
                           return result
                     elif isinstance(result, dict) and "image_path" in result:
                           return result["image_path"]
        return None

    def _extract_from_content_parts(self, event: Any) -> str | None:
        if not (hasattr(event, "content") and event.content and event.content.parts):
            return None

        for part in event.content.parts:
            if not (hasattr(part, "function_response") and part.function_response):
                continue

            fr = part.function_response
            if fr.name == "generate_image_from_prompt" and fr.response:
                if "result" in fr.response:
                    return fr.response["result"]
                elif "image_path" in fr.response:
                    return fr.response["image_path"]
        return None

    def _normalize_path(self, path: str) -> str:
        """Normalizes path to be relative to artifacts directory if possible."""
        # Replace backslashes
        path = path.replace("\\", "/")

        # Try to find 'artifacts/' segment
        if "artifacts/" in path:
            # Return subpath starting from artifacts/
            # e.g. C:/foo/artifacts/bar.png -> artifacts/bar.png
            idx = path.index("artifacts/")
            return path[idx:]

        return path

    def _parse_json_or_fallback(self, text: str) -> str | None:
        """Parses JSON from text or falls back to regex."""
        try:
            clean_text = self._clean_json_text(text)
            data = json.loads(clean_text)
            if "image_path" in data:
                return data["image_path"]
        except Exception:
            pass

        return self._fallback_regex_search(text)

    def _clean_json_text(self, text: str) -> str:
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text

    def _fallback_regex_search(self, text: str) -> str | None:
        if "artifacts" in text:
            import re
            match = re.search(r"artifacts[\\/][\w\-\.]+\.png", text)
            if match:
                return match.group(0)
        return None
