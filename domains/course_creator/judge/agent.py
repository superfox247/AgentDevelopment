import os

from google.adk.apps.app import App

from agent_platform.yaml_loader import load_agent_from_yaml

# --- Judge Agent ---
yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
judge = load_agent_from_yaml(yaml_path)

app = App(root_agent=judge, name="judge")
