from pathlib import Path

from agent_platform.yaml_loader import load_agent_from_yaml


def create_app():
    yaml_path = Path(__file__).parent / "agent.yaml"
    return load_agent_from_yaml(str(yaml_path))
