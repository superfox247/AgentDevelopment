"""
Integration tests for researcher agent discovery and metadata extraction.

These tests verify that the actual researcher_agent in the agents/ directory
can be discovered and its metadata extracted correctly.
"""

from pathlib import Path

import pytest

from dashboard_api.utils.agent_registry import AgentRegistry, extract_agent_metadata


class TestResearcherAgentIntegration:
    """Integration tests using the actual researcher_agent."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def researcher_agent_path(self, project_root: Path) -> Path:
        """Get the path to researcher_agent directory."""
        return project_root / "agents" / "researcher_agent"

    def test_researcher_agent_directory_exists(
        self, researcher_agent_path: Path
    ) -> None:
        """Test that researcher_agent directory exists."""
        assert researcher_agent_path.exists(), f"researcher_agent not found at {researcher_agent_path}"
        assert researcher_agent_path.is_dir()

    def test_researcher_agent_py_exists(self, researcher_agent_path: Path) -> None:
        """Test that agent.py exists in researcher_agent."""
        agent_py = researcher_agent_path / "agent.py"
        assert agent_py.exists(), f"agent.py not found at {agent_py}"

    def test_researcher_agent_server_py_exists(
        self, researcher_agent_path: Path
    ) -> None:
        """Test that server.py exists in researcher_agent."""
        server_py = researcher_agent_path / "server.py"
        assert server_py.exists(), f"server.py not found at {server_py}"

    def test_extract_researcher_agent_metadata(
        self, researcher_agent_path: Path
    ) -> None:
        """Test that metadata can be extracted from researcher_agent."""
        metadata = extract_agent_metadata(researcher_agent_path)

        assert metadata is not None, "Failed to extract metadata from researcher_agent"
        assert metadata.name == "researcher_agent"
        assert metadata.path == researcher_agent_path
        assert metadata.description is not None
        assert "Research assistant" in metadata.description or "research" in metadata.description.lower()
        assert metadata.model == "gemini-2.0-flash"
        assert metadata.has_server is True

    def test_registry_discovers_researcher_agent(self, project_root: Path) -> None:
        """Test that AgentRegistry discovers researcher_agent."""
        agents_dir = project_root / "agents"
        registry = AgentRegistry(agents_dir)
        agents = registry.get_agents(refresh=True)

        assert len(agents) > 0, "No agents discovered"
        researcher = registry.get_agent("researcher_agent")
        assert researcher is not None, "researcher_agent not found in registry"
        assert researcher.name == "researcher_agent"

    def test_researcher_agent_metadata_completeness(
        self, researcher_agent_path: Path
    ) -> None:
        """Test that researcher_agent metadata is complete."""
        metadata = extract_agent_metadata(researcher_agent_path)

        assert metadata is not None
        # All required fields should be present
        assert metadata.name
        assert metadata.path
        # Description should be meaningful
        assert metadata.description
        assert len(metadata.description) > 10
        # Model should be specified
        assert metadata.model
        # Server should be detected
        assert metadata.has_server is True

    def test_researcher_agent_metadata_serialization(
        self, researcher_agent_path: Path
    ) -> None:
        """Test that researcher_agent metadata can be serialized."""
        metadata = extract_agent_metadata(researcher_agent_path)

        assert metadata is not None
        data = metadata.to_dict()

        # Verify all expected keys are present
        assert "name" in data
        assert "path" in data
        assert "description" in data
        assert "model" in data
        assert "has_server" in data

        # Verify values
        assert data["name"] == "researcher_agent"
        assert data["has_server"] is True
        assert data["model"] == "gemini-2.0-flash"
        assert len(data["description"]) > 0
