import os

from google.adk.agents import LlmAgent
from google.adk.apps.app import App

from agent_platform.callbacks import create_save_output_callback
from agent_platform.yaml_loader import load_agent_from_yaml


# --- Customer Service Agent ---
def create_agent() -> LlmAgent:
    yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
    from typing import cast

    agent = load_agent_from_yaml(yaml_path)
    agent.after_agent_callback = create_save_output_callback("customer_service_output")
    return cast(LlmAgent, agent)


def create_app() -> App:
    return App(root_agent=create_agent(), name="customer_service")


app = create_app()
