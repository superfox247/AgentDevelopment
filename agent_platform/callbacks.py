"""
Callback utilities for the Agent Platform.

Provides standard callbacks for:
- State persistence (saving outputs to context)
- Chain of Thought handling
- Inter-agent communication support
"""
import json
import logging
from collections.abc import Callable

from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)


def _extract_and_save_content(ctx: CallbackContext, key: str, text: str) -> None:
    """Helper to parse and save content to state.

    If the text looks like JSON, it attempts to parse it.

    Args:
        ctx: The callback context containing session state.
        key: The state key to save the content under.
        text: The text content to save (parsed as JSON if possible).
    """
    # Try to parse as JSON if it looks like it, for judge_feedback etc
    if text.strip().startswith("{"):
        try:
            ctx.state[key] = json.loads(text)
        except json.JSONDecodeError:
            ctx.state[key] = text
    else:
        ctx.state[key] = text

    logger.info(f"[{ctx.agent_name}] Saved output to state['{key}']")


def create_save_output_callback(key: str) -> Callable[[CallbackContext], None]:
    """Creates a callback to save the agent's final response to session state.

    This is useful for 'Chain of Thought' or 'Pipeline' agents where you want
    to persist the output of one agent for the next agent to use.

    Args:
        key: The state key to save the output under.

    Returns:
        Callable[[CallbackContext], None]: The configured callback function.
    """

    def callback(callback_context: CallbackContext, **kwargs: object) -> None:
        ctx = callback_context
        # Find the last event from this agent that has content
        if not ctx.session or not ctx.session.events:
            return

        for event in reversed(ctx.session.events):
            if event.author == ctx.agent_name and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    _extract_and_save_content(ctx, key, text)
                    return

    return callback
