from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools import google_search

from agent_platform.config import config
from agent_platform.prompts import load_instruction

# --- Researcher Agent ---
researcher = Agent(
    name="researcher",
    model=config.default_model, # Uses 'gemini-2.5-pro' or env override
    description="Gathers information on a topic using Google Search.",
    instruction=load_instruction("researcher"), # Loaded from registry/prompts/researcher.md
    tools=[google_search],
)

app = App(root_agent=researcher, name="researcher")
