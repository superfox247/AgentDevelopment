from pathlib import Path
from agent_platform.yaml_loader import load_agent_from_yaml

def create_app():
    return load_agent_from_yaml(str(Path(__file__).parent / "agent.yaml"))
