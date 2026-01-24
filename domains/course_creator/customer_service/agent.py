import os

"""
Customer Service Agent.

Frontline agent for user interaction. Collects requirements and initial user intent.
"""

from google.adk.agents import LlmAgent
from google.adk.apps.app import App

from agent_platform.callbacks import create_save_output_callback
from agent_platform.loader import load_agent


# --- Customer Service Agent ---
def create_agent() -> LlmAgent:
    """Creates the Customer Service agent with output callback configuration."""
    yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
    from typing import cast

    agent = load_agent(yaml_path)
    agent.after_agent_callback = create_save_output_callback("customer_service_output")
    return cast(LlmAgent, agent)


def create_app() -> App:
    """Creates the ADK App serving the Customer Service agent."""
    return App(root_agent=create_agent(), name="customer_service")


app = create_app()
