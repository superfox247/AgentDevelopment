"""
A2A Protocol Bridge - Official ADK Integration

Uses the official google.adk.a2a.executor.A2aAgentExecutor as per framework convention.
"""
import logging

from a2a.types import AgentCapabilities, AgentCard
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.apps.app import App
from google.adk.runners import Runner

logger = logging.getLogger(__name__)


def create_executor(runner: Runner) -> A2aAgentExecutor:
    """
    Factory function to create an A2A executor using the official ADK implementation.
    
    Args:
        runner: The ADK Runner instance wrapping the agent.
        
    Returns:
        An A2aAgentExecutor configured with the runner.
    """
    return A2aAgentExecutor(runner=runner)


def create_agent_card(
    adk_app: App, description: str, host: str, port: int
) -> AgentCard:
    """Helper to generate a standard AgentCard."""
    base_url = f"http://{host}:{port}"

    return AgentCard(
        name=adk_app.name,
        description=description,
        version="0.1.0",
        protocol_version="0.1.0",
        url=f"{base_url}/a2a/{adk_app.name}",
        skills=[],
        capabilities=AgentCapabilities(),
        default_input_modes=["text"],
        default_output_modes=["text"],
        security=[],
    )
