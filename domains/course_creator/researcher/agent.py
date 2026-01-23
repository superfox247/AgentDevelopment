import os

from google.adk.apps.app import App

from agent_platform.loader import load_agent

# --- Researcher Agent ---
# Load from adjacent agent.yaml
yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
researcher = load_agent(yaml_path)

app = App(root_agent=researcher, name="researcher")
