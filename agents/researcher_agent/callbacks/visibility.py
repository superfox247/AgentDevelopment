"""Visibility callbacks: log agent/tool lifecycle for session and event inspection.

Use these to observe state and events during development. All callbacks return None
so execution continues normally. View full session/state/events in Dev UI (adk web)
via the Events and Trace tabs.
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


def before_agent_log(callback_context: CallbackContext) -> None:
    """Log before agent runs. Use for session/state visibility."""
    name = getattr(callback_context, "agent_name", "?")
    inv = getattr(callback_context, "invocation_id", None)
    state = getattr(callback_context, "state", None)
    state_keys = list(state.keys()) if state and hasattr(state, "keys") else []
    logger.info(
        "[researcher] before_agent agent=%s invocation=%s state_keys=%s",
        name,
        inv,
        state_keys,
    )


def after_agent_log(callback_context: CallbackContext) -> None:
    """Log after agent runs. Use for session/state visibility."""
    name = getattr(callback_context, "agent_name", "?")
    inv = getattr(callback_context, "invocation_id", None)
    logger.info("[researcher] after_agent agent=%s invocation=%s", name, inv)


def before_tool_log(
    tool: Any,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> None:
    """Log before tool runs. Use for event/trajectory visibility."""
    tool_name = getattr(tool, "name", str(tool))
    logger.info(
        "[researcher] before_tool tool=%s args=%s",
        tool_name,
        {k: str(v)[:80] for k, v in args.items()},
    )


def after_tool_log(
    tool: Any,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> None:
    """Log after tool runs. Use for event/trajectory visibility."""
    tool_name = getattr(tool, "name", str(tool))
    preview = str(tool_response)[:120] + (
        "..." if len(str(tool_response)) > 120 else ""
    )
    logger.info(
        "[researcher] after_tool tool=%s response_preview=%s", tool_name, preview
    )
