"""
Image Generator Agent.

Responsible for generating visual assets based on prompts using configured
Imagen or Gemini models.
"""

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.apps.app import App

from agent_platform.loader import load_agent


def create_agent() -> LlmAgent:
    """Creates and loads the LlmAgent from the YAML definition.

    Returns:
        LlmAgent: The configured LlmAgent instance.
    """
    from typing import cast

    return cast(
        LlmAgent, load_agent(str(Path(__file__).parent / "agent.yaml"))
    )


def create_app() -> App:
    """Creates the ADK App instance for the Image Generator.

    Returns:
        App: The initialized App containing the agent.
    """
    return App(root_agent=create_agent(), name="image_generator")


app = create_app()
