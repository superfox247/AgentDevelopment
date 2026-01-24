"""
Dashboard Services Layer.

Encapsulates business logic for interacting with Agents and Artifacts
outside of the HTTP/Router context.
"""

import json
import logging
from typing import Any

from google.adk.runners import Runner
from google.genai.types import Content, Part

# Configure logging
logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service to handle image generation via the ADK Runner.

    Encapsulates the interaction with the image generation agent runner, including session management,
    event stream handling, and result extraction.
    """

    def __init__(self, runner: Runner):
        """Initializes the service with a Runner instance.

        Args:
            runner: The ADK Runner to execute agent tasks.
        """
        self.runner = runner

    async def generate_image(
        self, user_id: str, session_id: str, prompt: str, model: str
    ) -> str:
        """Generates an image using the Image Generator Agent.

        Creates an agent session if needed, sends the prompt to the agent, and extracts the path
        of the generated image from the agent's output.

        Args:
            user_id: The unique identifier of the user.
            session_id: The unique identifier for the session.
            prompt: The description of the image to generate.
            model: The specific model ID to use (e.g., 'imagen-3.0-generate-001').

        Returns:
            str: The relative path to the generated image artifact (normalized to forward slashes).

        Raises:
            RuntimeError: If the agent completes without returning an image path.
            Exception: If any underlying error occurs during execution.
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
                user_id=user_id, session_id=session_id, new_message=msg
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
        """Helper to extract image path from various event types.

        Checks response content, tool responses, and function response parts for
        any sign of a generated image path.

        Args:
            event: An event object yielded by the ADK Runner.

        Returns:
            str | None: The normalized image path if found, otherwise None.
        """
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
        if (
            hasattr(event, "response")
            and event.response
            and hasattr(event.response, "content")
            and event.response.content
        ):
            return self._parse_json_or_fallback(event.response.content)
        return None

    def _extract_from_tool_response(self, event: Any) -> str | None:
        if not (hasattr(event, "tool_response") and event.tool_response):
            return None

        for tr in event.tool_response:
            if tr.name == "generate_image_from_prompt":
                return self._extract_path_from_payload(tr.response)
        return None

    def _extract_from_content_parts(self, event: Any) -> str | None:
        if not (hasattr(event, "content") and event.content and event.content.parts):
            return None

        for part in event.content.parts:
            if self._is_image_fn_response(part):
                return self._extract_path_from_payload(part.function_response.response)
        return None

    def _is_image_fn_response(self, part: Any) -> bool:
        return (
            hasattr(part, "function_response")
            and part.function_response
            and part.function_response.name == "generate_image_from_prompt"
        )

    def _extract_path_from_payload(self, payload: Any) -> str | None:
        """Extracts path from a dict/string payload."""
        if not payload:
            return None

        if isinstance(payload, str) and "artifacts" in payload:
            return payload

        if isinstance(payload, dict):
            if "result" in payload:
                return payload["result"]
            if "image_path" in payload:
                return payload["image_path"]

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
