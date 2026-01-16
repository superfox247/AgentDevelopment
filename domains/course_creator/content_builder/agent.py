from google.adk.agents import Agent
from google.adk.apps.app import App

from agent_platform.config import config
from agent_platform.prompts import load_instruction

# --- Content Builder Agent ---
content_builder = Agent(
    name="content_builder",
    model=config.default_model,
    description="Transforms research findings into a structured course.",
    instruction=load_instruction("content_builder"),
)

app = App(root_agent=content_builder, name="content_builder")
