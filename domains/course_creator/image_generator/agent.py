from pathlib import Path

from google.adk.apps.app import App

from agent_platform.yaml_loader import load_agent_from_yaml


def create_agent():
    return load_agent_from_yaml(str(Path(__file__).parent / "agent.yaml"))


def create_app():
    return App(root_agent=create_agent(), name="image_generator")


app = create_app()
