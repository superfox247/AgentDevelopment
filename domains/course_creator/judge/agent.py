"""
Judge Agent.

Evaluates research findings for quality and completeness.
"""

import os

from google.adk.apps.app import App

from agent_platform.loader import load_agent


# --- Judge Agent ---
def create_agent():
    """Creates and loads the Judge LlmAgent from the YAML definition.

    Returns:
        LlmAgent: The configured LlmAgent instance.
    """
    yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
    return load_agent(yaml_path)


def create_app() -> App:
    """Creates the ADK App instance for the Judge.

    Returns:
        App: The initialized App containing the agent.
    """
    return App(root_agent=create_agent(), name="judge")


app = create_app()
