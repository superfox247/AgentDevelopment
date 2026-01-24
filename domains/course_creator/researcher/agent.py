"""
Researcher Agent.

Leverages Google Search (Search grounding or Custom Search) to gather information
on course topics.
"""

import os

from google.adk.apps.app import App

from agent_platform.loader import load_agent

# --- Researcher Agent ---
# Load from adjacent agent.yaml

def create_agent():
    """Creates and loads the Researcher LlmAgent from the YAML definition.

    Returns:
        LlmAgent: The configured LlmAgent instance.
    """
    yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
    return load_agent(yaml_path)


def create_app() -> App:
    """Creates the ADK App instance for the Researcher.

    Returns:
        App: The initialized App containing the agent.
    """
    return App(root_agent=create_agent(), name="researcher")


app = create_app()
