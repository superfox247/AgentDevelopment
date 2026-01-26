"""Base agent: minimal baseline for all agent features, testing, and parity.

Uses a single echo tool (no external APIs), PlanReActPlanner, and visibility
callbacks. Use as the reference implementation for agent structure, tests,
and eval harness.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner

from .callbacks.visibility import (
    after_agent_log,
    after_tool_log,
    before_agent_log,
    before_tool_log,
)
from .tools.echo import echo

root_agent = LlmAgent(
    name="base_agent",
    model="gemini-2.0-flash",
    description="Baseline agent for testing and feature parity. Minimal tools and callbacks.",
    instruction="""You are a minimal baseline agent. Use the echo tool when asked to repeat or echo text.
Otherwise respond concisely. You exist to validate agent structure, callbacks, and tests.""",
    tools=[echo],
    before_agent_callback=before_agent_log,
    after_agent_callback=after_agent_log,
    before_tool_callback=before_tool_log,
    after_tool_callback=after_tool_log,
    planner=PlanReActPlanner(),
)
