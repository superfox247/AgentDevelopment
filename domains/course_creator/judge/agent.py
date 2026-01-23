import os

from google.adk.apps.app import App

from agent_platform.loader import load_agent

# --- Judge Agent ---
yaml_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
judge = load_agent(yaml_path)

app = App(root_agent=judge, name="judge")
