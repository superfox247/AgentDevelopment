from pathlib import Path

from google.adk.apps.app import App

from agent_platform.yaml_loader import load_agent_from_yaml


def create_app() -> App:
    yaml_path = Path(__file__).parent / "agent.yaml"
    # load_agent_from_yaml returns BaseAgent. But create_app should return App.
    # Wait, create_app logic was: return load_agent_from_yaml...
    # BUT App is not Agent.
    # The previous code was: return load_agent_from_yaml...
    # load_agent_from_yaml returns an Agent.
    # If create_app is supposed to return App, it should wrap it.
    # BUT `image_gen/image_generator/agent.py` line 6: def create_app(): ... return load_agent_from_yaml...
    # This implies the function name is wrong or it should return Agent?
    # Actually `google.adk.apps.app.App` wraps an agent.
    # If the function is `create_app`, it should return `App(root_agent=...)`.
    # I'll check the file content again.
    # Step 829 showing:
    # def create_app():
    #    yaml_path = ...
    #    return load_agent_from_yaml(str(yaml_path))
    # This returns an Agent, not an App!
    # So I should fix the logic to wrap it in App.
    agent = load_agent_from_yaml(str(yaml_path))
    return App(root_agent=agent, name="image_generator")
