"""
Agent Registry and Discovery Utility.

Provides dynamic discovery of agents in the agents/ directory.
Extracts metadata from agent.py files and provides a registry interface.
"""

import ast
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AgentMetadata:
    """Metadata extracted from an agent definition."""

    def __init__(
        self,
        name: str,
        path: Path,
        description: str | None = None,
        model: str | None = None,
        has_server: bool = False,
    ):
        self.name = name
        self.path = path
        self.description = description
        self.model = model
        self.has_server = has_server

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "name": self.name,
            "path": str(self.path),
            "description": self.description or "",
            "model": self.model or "",
            "has_server": self.has_server,
        }


def extract_agent_metadata(agent_path: Path) -> AgentMetadata | None:
    """Extract metadata from an agent's agent.py file.

    Args:
        agent_path: Path to the agent directory (e.g., agents/researcher_agent)

    Returns:
        AgentMetadata if agent.py exists and contains root_agent, None otherwise.
    """
    agent_py = agent_path / "agent.py"
    if not agent_py.exists():
        return None

    try:
        with open(agent_py, encoding="utf-8") as f:
            source = f.read()

        # Parse the AST to extract metadata
        tree = ast.parse(source, filename=str(agent_py))

        name = agent_path.name
        description: str | None = None
        model: str | None = None

        # Walk the AST to find root_agent definition
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "root_agent":
                        # Found root_agent assignment
                        if isinstance(node.value, ast.Call):
                            # Extract keyword arguments
                            for keyword in node.value.keywords:
                                if (
                                    keyword.arg == "name"
                                    and isinstance(keyword.value, ast.Constant)
                                    and isinstance(keyword.value.value, str)
                                ):
                                    name = keyword.value.value
                                elif (
                                    keyword.arg == "description"
                                    and isinstance(keyword.value, ast.Constant)
                                    and isinstance(keyword.value.value, str)
                                ):
                                    description = keyword.value.value
                                elif (
                                    keyword.arg == "model"
                                    and isinstance(keyword.value, ast.Constant)
                                    and isinstance(keyword.value.value, str)
                                ):
                                    model = keyword.value.value

        # Check if server.py exists
        has_server = (agent_path / "server.py").exists()

        return AgentMetadata(
            name=name,
            path=agent_path,
            description=description,
            model=model,
            has_server=has_server,
        )

    except Exception as e:
        logger.warning(f"Failed to parse agent metadata from {agent_py}: {e}")
        # Return basic metadata even if parsing fails
        return AgentMetadata(
            name=agent_path.name,
            path=agent_path,
            has_server=(agent_path / "server.py").exists(),
        )


def discover_agents(agents_dir: Path) -> list[AgentMetadata]:
    """Discover all agents in the agents directory.

    Args:
        agents_dir: Path to the agents directory (e.g., agents/)

    Returns:
        List of AgentMetadata for all discovered agents.
    """
    if not agents_dir.exists():
        logger.warning(f"Agents directory does not exist: {agents_dir}")
        return []

    agents: list[AgentMetadata] = []

    for agent_path in agents_dir.iterdir():
        if not agent_path.is_dir():
            continue

        # Skip hidden directories and __pycache__
        if agent_path.name.startswith(".") or agent_path.name == "__pycache__":
            continue

        metadata = extract_agent_metadata(agent_path)
        if metadata:
            agents.append(metadata)

    return sorted(agents, key=lambda a: a.name)


class AgentRegistry:
    """Registry for managing discovered agents."""

    def __init__(self, agents_dir: Path):
        self.agents_dir = agents_dir
        self._agents: list[AgentMetadata] | None = None

    def refresh(self) -> list[AgentMetadata]:
        """Refresh the agent list by re-scanning the directory."""
        self._agents = discover_agents(self.agents_dir)
        return self._agents

    def get_agents(self, refresh: bool = False) -> list[AgentMetadata]:
        """Get the list of agents, optionally refreshing the cache."""
        if self._agents is None or refresh:
            return self.refresh()
        return self._agents

    def get_agent(self, name: str) -> AgentMetadata | None:
        """Get a specific agent by name."""
        agents = self.get_agents()
        return next((a for a in agents if a.name == name), None)

    def agent_exists(self, name: str) -> bool:
        """Check if an agent exists."""
        return self.get_agent(name) is not None
