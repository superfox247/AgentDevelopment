import logging
from pathlib import Path

import yaml
from google.adk.agents import BaseAgent

from agent_platform.schemas.config import AgentConfig

logger = logging.getLogger(__name__)

def load_agent(yaml_path: str | Path) -> BaseAgent:
    """
    Loads an agent using Pydantic-validated configuration.
    Features:
    - Strict Schema Validation
    - Type Safety
    - Relative Import Resolution
    """
    path = Path(yaml_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Agent config not found: {path}")

    logger.info(f"Loading agent config from {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Validate
    config = AgentConfig(**data)
    config.set_base_path(path)

    # Hydrate
    return config.to_agent()
