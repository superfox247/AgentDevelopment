import json
import logging
import os
from typing import Any, cast

from google.adk.agents import InvocationContext
from google.adk.apps.app import App
from google.adk.events import Event
from schemas.models.protocol import ContentArticle

from agent_platform.yaml_loader import load_agent_from_yaml

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Callbacks ---
def load_research_findings(*args: Any, **kwargs: Any) -> None:
    """Loads research findings from session state and injects them as user content."""
    # Resolve ctx (usually first arg or 'ctx' kwarg)
    ctx = args[0] if args else kwargs.get("ctx")
    if not ctx:
        return

    findings_data = ctx.session.state.get("research_findings")

    if findings_data:
        import json

        if isinstance(findings_data, dict):
            findings_str = json.dumps(findings_data, indent=2)
        else:
            findings_str = str(findings_data)

        from google.genai import types

        ctx.user_content = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=f"Here are the Research Findings:\n{findings_str}\n\nPlease build the content article."
                )
            ],
        )


def _parse_content_article(text: str) -> dict | None:
    """Helper to parse ContentArticle from text/json."""
    if not text or not text.strip().startswith("{"):
        return None
    try:
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception:
        return None


def _extract_content_from_tool_call(event: object) -> dict | None:
    """Helper to check for ContentArticle tool call."""
    # Cast to Event to safely access attributes
    evt = cast(Event, event)
    if not evt.content or not evt.content.parts:
        return None

    for part in evt.content.parts:
        if part.function_call and part.function_call.name == "ContentArticle":
            return part.function_call.args
    return None


def _try_parse_fallback(event: object, ctx: InvocationContext) -> None:
    """Fallback: Check for JSON in text."""
    evt = cast(Event, event)
    if not (evt.content and evt.content.parts):
        return

    text = evt.content.parts[0].text
    if not text:
        return

    data = _parse_content_article(text)
    if data:
        try:
            content = ContentArticle(**data)
            ctx.session.state["content_article"] = content.model_dump()
        except Exception:
            pass


def _resolve_context(*args: Any, **kwargs: Any) -> InvocationContext | None:
    """Helper to resolve InvocationContext from args/kwargs."""
    ctx = None
    if args and isinstance(args[0], InvocationContext):
        ctx = args[0]
    elif "ctx" in kwargs:
        ctx = kwargs["ctx"]
    elif "context" in kwargs:
        ctx = kwargs["context"]

    if "callback_context" in kwargs:
        cb_ctx = kwargs["callback_context"]
        # Access protected member as revealed by debug
        if hasattr(cb_ctx, "_invocation_context"):
            ctx = cb_ctx._invocation_context
        elif hasattr(cb_ctx, "invocation_context"):
            ctx = cb_ctx.invocation_context
    return ctx


def _get_last_agent_event(ctx: InvocationContext) -> Event | None:
    """Helper to find the last event from content_builder."""
    if ctx.session and ctx.session.events:
        for event in reversed(ctx.session.events):
            if event.author == "content_builder":
                return event
    return None


def _save_output(*args: Any, **kwargs: Any) -> None:
    """Saves the generated content to the session state."""
    logger.info(
        f"DEBUG: _save_output called with args={len(args)}, kwargs={list(kwargs.keys())}"
    )

    ctx = _resolve_context(*args, **kwargs)
    if not ctx:
        logger.error(f"_save_output: No context found. Args: {args}, Kwargs: {kwargs}")
        return

    last_event = _get_last_agent_event(ctx)
    if not last_event:
        logger.error("_save_output: No event from content_builder found.")
        return

    if (
        last_event.content
        and last_event.content.parts
        and last_event.content.parts[0].text
    ):
        logger.info(
            f"DEBUG: Last event content: {last_event.content.parts[0].text[:100]}..."
        )

    # 1. Try Function Call
    tool_args = _extract_content_from_tool_call(last_event)
    if tool_args:
        try:
            content = ContentArticle(**tool_args)
            ctx.session.state["content_article"] = content.model_dump()
            logger.info("DEBUG: content_article saved via tool call.")
            return
        except Exception as e:
            logger.error(f"Error parsing ContentArticle from tool call: {e}")

    # 2. Fallback
    _try_parse_fallback(last_event, ctx)


# --- Content Builder Agent ---
from google.adk.agents import LlmAgent  # noqa: E402


def create_agent() -> LlmAgent:
    agent = load_agent_from_yaml("agent.yaml", base_dir=os.path.dirname(__file__))
    agent.before_agent_callback = load_research_findings
    agent.after_agent_callback = _save_output
    return cast(LlmAgent, agent)


def create_app() -> App:
    return App(root_agent=create_agent(), name="content_builder")


# For backward compatibility or testing if needed, but factories are preferred.
app = create_app()
