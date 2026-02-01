"""
Researcher Agent FastAPI Server Entry Point.

Creates the FastAPI application using the platform's create_agent_app helper.
"""

from agent_platform.server import create_agent_app
from researcher_agent.agent import root_agent

# Create FastAPI app from root_agent
app = create_agent_app(
    root_agent=root_agent,
    description="Research assistant that browses the web via Google Search to answer questions.",
    enable_a2a=True,
    include_root_route=True,
)
