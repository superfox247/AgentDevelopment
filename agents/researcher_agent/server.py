"""
Researcher Agent FastAPI Server Entry Point.

Creates the FastAPI application using the platform's create_platform_app factory.
"""

from google.adk.apps import App

from agent_platform.server import create_platform_app
from agent import root_agent  # agent is the module name when copied to /app/agent

# Create ADK App from root_agent
adk_app = App(root_agent=root_agent)

# Create FastAPI app using platform factory
app = create_platform_app(
    adk_app=adk_app,
    description="Research assistant that browses the web via Google Search to answer questions.",
    enable_a2a=True,
    include_root_route=True,
)
