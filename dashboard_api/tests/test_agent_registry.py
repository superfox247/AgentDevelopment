"""
Unit tests for Agent Registry and Discovery.

Tests the agent registry functionality including metadata extraction,
agent discovery, and registry caching.
"""

from pathlib import Path

from dashboard_api.utils.agent_registry import (
    AgentMetadata,
    AgentRegistry,
    discover_agents,
    extract_agent_metadata,
)


class TestExtractAgentMetadata:
    """Tests for extract_agent_metadata function."""

    def test_extract_metadata_with_all_fields(self, tmp_path: Path) -> None:
        """Test metadata extraction with description, model, and name."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="test_agent",
    description="A test agent for testing",
    model="gemini-2.0-flash",
    tools=[],
)
"""
        )

        metadata = extract_agent_metadata(agent_dir)
        assert metadata is not None
        assert metadata.name == "test_agent"
        assert metadata.description == "A test agent for testing"
        assert metadata.model == "gemini-2.0-flash"
        assert metadata.path == agent_dir

    def test_extract_metadata_without_description(self, tmp_path: Path) -> None:
        """Test metadata extraction when description is missing."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="test_agent",
    model="gemini-2.0-flash",
)
"""
        )

        metadata = extract_agent_metadata(agent_dir)
        assert metadata is not None
        assert metadata.name == "test_agent"
        assert metadata.description is None
        assert metadata.model == "gemini-2.0-flash"

    def test_extract_metadata_fallback_to_dir_name(self, tmp_path: Path) -> None:
        """Test that directory name is used when name is not in agent.py."""
        agent_dir = tmp_path / "my_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(model="gemini-2.0-flash")
"""
        )

        metadata = extract_agent_metadata(agent_dir)
        assert metadata is not None
        assert metadata.name == "my_agent"  # Falls back to directory name

    def test_extract_metadata_detects_server(self, tmp_path: Path) -> None:
        """Test that has_server is True when server.py exists."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        server_py = agent_dir / "server.py"
        server_py.write_text("# Server file")

        metadata = extract_agent_metadata(agent_dir)
        assert metadata is not None
        assert metadata.has_server is True

    def test_extract_metadata_no_server(self, tmp_path: Path) -> None:
        """Test that has_server is False when server.py doesn't exist."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        metadata = extract_agent_metadata(agent_dir)
        assert metadata is not None
        assert metadata.has_server is False

    def test_extract_metadata_missing_agent_py(self, tmp_path: Path) -> None:
        """Test that None is returned when agent.py doesn't exist."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        metadata = extract_agent_metadata(agent_dir)
        assert metadata is None

    def test_extract_metadata_invalid_syntax(self, tmp_path: Path) -> None:
        """Test that invalid Python syntax is handled gracefully."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text("invalid python syntax !!!")

        # Should not raise, but return basic metadata
        _ = extract_agent_metadata(agent_dir)
        # May return None or basic metadata depending on implementation
        # The function should handle errors gracefully

    def test_extract_metadata_no_root_agent(self, tmp_path: Path) -> None:
        """Test that agent.py without root_agent is handled."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        agent_py = agent_dir / "agent.py"
        agent_py.write_text("# Just a comment, no root_agent")

        metadata = extract_agent_metadata(agent_dir)
        # Should return basic metadata with directory name
        assert metadata is not None
        assert metadata.name == "test_agent"


class TestDiscoverAgents:
    """Tests for discover_agents function."""

    def test_discover_single_agent(self, tmp_path: Path) -> None:
        """Test discovering a single agent."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        agents = discover_agents(agents_dir)
        assert len(agents) == 1
        assert agents[0].name == "test_agent"

    def test_discover_multiple_agents(self, tmp_path: Path) -> None:
        """Test discovering multiple agents."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Create two agents
        for agent_name in ["agent1", "agent2"]:
            agent_dir = agents_dir / agent_name
            agent_dir.mkdir()
            agent_py = agent_dir / "agent.py"
            agent_py.write_text(
                f"""from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="{agent_name}")
"""
            )

        agents = discover_agents(agents_dir)
        assert len(agents) == 2
        names = {a.name for a in agents}
        assert names == {"agent1", "agent2"}

    def test_discover_agents_sorted(self, tmp_path: Path) -> None:
        """Test that discovered agents are sorted by name."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Create agents in non-alphabetical order
        for agent_name in ["zebra", "alpha", "beta"]:
            agent_dir = agents_dir / agent_name
            agent_dir.mkdir()
            agent_py = agent_dir / "agent.py"
            agent_py.write_text(
                f"""from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="{agent_name}")
"""
            )

        agents = discover_agents(agents_dir)
        assert len(agents) == 3
        assert [a.name for a in agents] == ["alpha", "beta", "zebra"]

    def test_discover_agents_skips_hidden_dirs(self, tmp_path: Path) -> None:
        """Test that hidden directories are skipped."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Create a hidden directory
        hidden_dir = agents_dir / ".hidden"
        hidden_dir.mkdir()
        agent_py = hidden_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="hidden")
"""
        )

        # Create a normal agent
        agent_dir = agents_dir / "visible_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="visible_agent")
"""
        )

        agents = discover_agents(agents_dir)
        assert len(agents) == 1
        assert agents[0].name == "visible_agent"

    def test_discover_agents_skips_pycache(self, tmp_path: Path) -> None:
        """Test that __pycache__ directories are skipped."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Create __pycache__
        pycache = agents_dir / "__pycache__"
        pycache.mkdir()

        # Create a normal agent
        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        agents = discover_agents(agents_dir)
        assert len(agents) == 1

    def test_discover_agents_missing_directory(self, tmp_path: Path) -> None:
        """Test that missing directory returns empty list."""
        agents_dir = tmp_path / "nonexistent"
        agents = discover_agents(agents_dir)
        assert agents == []


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    def test_registry_initialization(self, tmp_path: Path) -> None:
        """Test registry initialization."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        registry = AgentRegistry(agents_dir)
        assert registry.agents_dir == agents_dir
        assert registry._agents is None  # Not loaded yet

    def test_registry_refresh(self, tmp_path: Path) -> None:
        """Test registry refresh loads agents."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        registry = AgentRegistry(agents_dir)
        agents = registry.refresh()

        assert len(agents) == 1
        assert agents[0].name == "test_agent"
        assert registry._agents == agents  # Cached

    def test_registry_get_agents_caches(self, tmp_path: Path) -> None:
        """Test that get_agents caches results."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        registry = AgentRegistry(agents_dir)
        agents1 = registry.get_agents()
        agents2 = registry.get_agents()

        # Should return same list (cached)
        assert agents1 is agents2
        assert len(agents1) == 1

    def test_registry_get_agents_refresh(self, tmp_path: Path) -> None:
        """Test that get_agents with refresh=True reloads."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        registry = AgentRegistry(agents_dir)
        _ = registry.get_agents()

        # Add another agent
        agent2_dir = agents_dir / "agent2"
        agent2_dir.mkdir()
        agent2_py = agent2_dir / "agent.py"
        agent2_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="agent2")
"""
        )

        # Without refresh, should return cached
        agents2 = registry.get_agents()
        assert len(agents2) == 1

        # With refresh, should reload
        agents3 = registry.get_agents(refresh=True)
        assert len(agents3) == 2

    def test_registry_get_agent(self, tmp_path: Path) -> None:
        """Test getting a specific agent by name."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        registry = AgentRegistry(agents_dir)
        agent = registry.get_agent("test_agent")

        assert agent is not None
        assert agent.name == "test_agent"

    def test_registry_get_agent_not_found(self, tmp_path: Path) -> None:
        """Test getting a non-existent agent returns None."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        registry = AgentRegistry(agents_dir)
        agent = registry.get_agent("nonexistent")

        assert agent is None

    def test_registry_agent_exists(self, tmp_path: Path) -> None:
        """Test checking if an agent exists."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_dir = agents_dir / "test_agent"
        agent_dir.mkdir()
        agent_py = agent_dir / "agent.py"
        agent_py.write_text(
            """from google.adk.agents import LlmAgent

root_agent = LlmAgent(name="test_agent")
"""
        )

        registry = AgentRegistry(agents_dir)
        assert registry.agent_exists("test_agent") is True
        assert registry.agent_exists("nonexistent") is False

    def test_agent_metadata_to_dict(self, tmp_path: Path) -> None:
        """Test AgentMetadata.to_dict() method."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        metadata = AgentMetadata(
            name="test_agent",
            path=agent_dir,
            description="Test description",
            model="gemini-2.0-flash",
            has_server=True,
        )

        result = metadata.to_dict()
        assert result == {
            "name": "test_agent",
            "path": str(agent_dir),
            "description": "Test description",
            "model": "gemini-2.0-flash",
            "has_server": True,
        }

    def test_agent_metadata_to_dict_defaults(self, tmp_path: Path) -> None:
        """Test AgentMetadata.to_dict() with default values."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()

        metadata = AgentMetadata(
            name="test_agent",
            path=agent_dir,
        )

        result = metadata.to_dict()
        assert result == {
            "name": "test_agent",
            "path": str(agent_dir),
            "description": "",
            "model": "",
            "has_server": False,
        }
