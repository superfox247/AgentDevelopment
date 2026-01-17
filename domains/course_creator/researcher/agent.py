import os

from google.adk.apps.app import App

from agent_platform.yaml_loader import load_agent_from_yaml

# --- Researcher Agent ---
# Load from adjacent agent.yaml
yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
researcher = load_agent_from_yaml(yaml_path)

app = App(root_agent=researcher, name="researcher")
