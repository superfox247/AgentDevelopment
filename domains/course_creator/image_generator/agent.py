from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.apps.app import App

from agent_platform.yaml_loader import load_agent_from_yaml


def create_agent() -> LlmAgent:
    from typing import cast

    return cast(
        LlmAgent, load_agent_from_yaml(str(Path(__file__).parent / "agent.yaml"))
    )


def create_app() -> App:
    return App(root_agent=create_agent(), name="image_generator")


app = create_app()
