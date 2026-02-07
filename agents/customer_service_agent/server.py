"""
Customer Service Agent FastAPI Server Entry Point.

Creates the FastAPI application using the platform's create_agent_app helper.
"""

from customer_service_agent.agent import root_agent

from agent_platform.server import create_agent_app

# Create FastAPI app from root_agent
app = create_agent_app(
    root_agent=root_agent,
    description="Customer service agent that validates user input, ensures compliance, and structures requests for downstream agents. Implements security guardrails and professional response standards.",
    enable_a2a=True,
    include_root_route=True,
)
