"""Researcher agent: web-capable research assistant.

Uses Google Search for grounding, PlanReActPlanner for multi-step reasoning,
and visibility callbacks for session/state/event inspection. Artifacts are
collocated in agents/researcher_agent/artifacts when run with a Runner
configured with FileArtifactService(root_dir=".../researcher_agent/artifacts").
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from google.adk.tools import google_search

from .callbacks.visibility import (
    after_agent_log,
    after_tool_log,
    before_agent_log,
    before_tool_log,
)

# Google Search requires Gemini 2. One-tool limitation: use only google_search.
# See ADK tools limitations. Use bypass_multi_tools_limit if adding more tools.
root_agent = LlmAgent(
    name="researcher_agent",
    model="gemini-3-flash",
    description="Research assistant that browses the web via Google Search to answer questions.",
    instruction="""You are a careful research assistant. Use the google_search tool to find
up-to-date information. Prefer multiple focused searches over one vague query.
Cite sources when you can. If results are inconclusive, say so. Be concise but thorough.""",
    tools=[google_search],
    before_agent_callback=before_agent_log,
    after_agent_callback=after_agent_log,
    before_tool_callback=before_tool_log,
    after_tool_callback=after_tool_log,
    planner=PlanReActPlanner(),
)
