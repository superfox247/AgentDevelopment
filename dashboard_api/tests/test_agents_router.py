"""
Unit tests for Agent Router endpoints.

Tests the FastAPI router endpoints for agent discovery and metadata.
"""

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from dashboard_api.routers.agents import router
from dashboard_api.utils.agent_registry import AgentMetadata, AgentRegistry


@pytest.fixture
def mock_agents_dir(tmp_path: Path) -> Path:
    """Create a temporary agents directory with test agents."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    # Create researcher_agent
    researcher_dir = agents_dir / "researcher_agent"
    researcher_dir.mkdir()
    researcher_py = researcher_dir / "agent.py"
    researcher_py.write_text(
        """from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="researcher_agent",
    description="Research assistant that browses the web via Google Search to answer questions.",
    model="gemini-2.0-flash",
)
"""
    )
    server_py = researcher_dir / "server.py"
    server_py.write_text("# Server file")

    return agents_dir


@pytest.fixture
def client(mock_agents_dir: Path) -> TestClient:
    """Create a test client with mocked agent registry."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    # Mock the registry to use our test directory
    with patch("dashboard_api.routers.agents._agent_registry") as mock_registry:
        registry = AgentRegistry(mock_agents_dir)
        registry.refresh()
        mock_registry.get_agents.return_value = registry.get_agents()
        mock_registry.get_agent.side_effect = registry.get_agent

        yield TestClient(app)


class TestListAgents:
    """Tests for GET /api/agents endpoint."""

    def test_list_agents_success(
        self, client: TestClient, mock_agents_dir: Path
    ) -> None:
        """Test listing agents returns correct structure."""
        response = client.get("/api/agents")
        assert response.status_code == 200

        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) == 1

        agent = data["agents"][0]
        assert agent["name"] == "researcher_agent"
        assert agent["domain"] == ""
        assert "path" in agent

    def test_list_agents_empty(self, client: TestClient) -> None:
        """Test listing agents when none exist."""
        with patch("dashboard_api.routers.agents._agent_registry") as mock_registry:
            mock_registry.get_agents.return_value = []

            response = client.get("/api/agents")
            assert response.status_code == 200

            data = response.json()
            assert data["agents"] == []


class TestGetAgentMetadata:
    """Tests for GET /api/agents/{name}/metadata endpoint."""

    def test_get_metadata_success(self, client: TestClient) -> None:
        """Test getting agent metadata returns correct structure."""
        response = client.get("/api/agents/researcher_agent/metadata")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "researcher_agent"
        assert (
            data["description"]
            == "Research assistant that browses the web via Google Search to answer questions."
        )
        assert data["model"] == "gemini-2.0-flash"
        assert data["has_server"] is True
        assert "path" in data

    def test_get_metadata_not_found(self, client: TestClient) -> None:
        """Test getting metadata for non-existent agent returns 404."""
        with patch("dashboard_api.routers.agents._agent_registry") as mock_registry:
            mock_registry.get_agent.return_value = None

            response = client.get("/api/agents/nonexistent/metadata")
            assert response.status_code == 404

            data = response.json()
            assert "detail" in data
            assert "nonexistent" in data["detail"].lower()

    def test_get_metadata_schema_validation(self, client: TestClient) -> None:
        """Test that metadata response matches expected schema."""
        response = client.get("/api/agents/researcher_agent/metadata")
        assert response.status_code == 200

        data = response.json()
        # Validate all required fields are present
        required_fields = ["name", "path", "description", "model", "has_server"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Validate types
        assert isinstance(data["name"], str)
        assert isinstance(data["path"], str)
        assert isinstance(data["description"], str)
        assert isinstance(data["model"], str)
        assert isinstance(data["has_server"], bool)


class TestGetAgentConfig:
    """Tests for GET /api/agents/{name} endpoint."""

    def test_get_config_success(
        self, client: TestClient, mock_agents_dir: Path
    ) -> None:
        """Test getting agent.py file returns file content."""
        response = client.get("/api/agents/researcher_agent")
        assert response.status_code == 200

        # Should return file content
        content = response.text
        assert "researcher_agent" in content
        assert "LlmAgent" in content

    def test_get_config_not_found(self, client: TestClient) -> None:
        """Test getting config for non-existent agent returns 404."""
        with patch("dashboard_api.routers.agents._agent_registry") as mock_registry:
            mock_registry.get_agent.return_value = None

            response = client.get("/api/agents/nonexistent")
            assert response.status_code == 404

    def test_get_config_legacy_endpoint(self, client: TestClient) -> None:
        """Test legacy domain/name endpoint still works."""
        response = client.get("/api/agents/domain/researcher_agent")
        # Should work (domain is ignored)
        assert response.status_code == 200


class TestGetAgentConfigMissingFile:
    """Tests for edge cases when agent.py is missing."""

    def test_get_config_missing_agent_py(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test getting config when agent.py doesn't exist."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir(exist_ok=True)

        agent_dir = agents_dir / "broken_agent"
        agent_dir.mkdir()
        # No agent.py file

        with patch("dashboard_api.routers.agents._agent_registry") as mock_registry:
            metadata = AgentMetadata(
                name="broken_agent",
                path=agent_dir,
            )
            mock_registry.get_agent.return_value = metadata

            response = client.get("/api/agents/broken_agent")
            assert response.status_code == 404


class TestSkillsEndpoints:
    """Tests for skills endpoints (bonus coverage)."""

    def test_list_skills_empty(self, client: TestClient) -> None:
        """Test listing skills when none exist."""
        with patch("dashboard_api.routers.agents.ROOT_DIR") as mock_root:
            skills_dir = Path("/nonexistent")
            mock_root.__truediv__ = (
                lambda self, other: skills_dir / other
                if other == ".agent"
                else Path(str(self) + "/" + str(other))
            )

            response = client.get("/api/skills")
            assert response.status_code == 200

            data = response.json()
            assert data["skills"] == []


class TestChatWithAgent:
    """Tests for POST /api/chat/{name} endpoint."""

    def test_chat_uses_runner_async_generator(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test chat endpoint iterates Runner.run_async events and returns final text."""

        class FakeEvent:
            def __init__(self, text: str, author: str = "researcher_agent") -> None:
                self.content = type(
                    "Content", (), {"parts": [type("Part", (), {"text": text})()]}
                )()
                self.author = author

        class FakeRunner:
            last_kwargs: ClassVar[dict[str, object]] = {}

            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

            async def run_async(
                self, **kwargs: object
            ) -> AsyncGenerator[FakeEvent, None]:
                FakeRunner.last_kwargs = kwargs
                yield FakeEvent("intermediate")
                yield FakeEvent("final answer")

        agent_dir = tmp_path / "agents" / "researcher_agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        metadata = AgentMetadata(name="researcher_agent", path=agent_dir)

        class FakeApp:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

        class FakeSessionService:
            async def create_session(self, **kwargs: object) -> None:
                return None

        with (
            patch(
                "dashboard_api.routers.agents._agent_registry.get_agent",
                return_value=metadata,
            ),
            patch("dashboard_api.routers.agents.App", FakeApp),
            patch("dashboard_api.routers.agents.Runner", FakeRunner),
            patch(
                "dashboard_api.routers.agents.InMemorySessionService",
                FakeSessionService,
            ),
            patch(
                "dashboard_api.routers.agents.importlib.import_module",
                return_value=type("AgentModule", (), {"root_agent": object()})(),
            ),
        ):
            response = client.post(
                "/api/chat/researcher_agent",
                json={"message": "hello", "session_id": "s1"},
            )

        assert response.status_code == 200
        lines = [line for line in response.text.splitlines() if line]
        assert len(lines) == 2
        assert '"type":"agent_thought"' in lines[0]
        assert '"text":"intermediate"' in lines[0]
        assert '"text":"final answer"' in lines[1]
        assert FakeRunner.last_kwargs["session_id"] == "s1"

    def test_chat_legacy_json_response(self, client: TestClient, tmp_path: Path) -> None:
        """Test chat endpoint supports legacy non-streaming JSON mode."""

        class FakeEvent:
            def __init__(self, text: str) -> None:
                self.content = type(
                    "Content", (), {"parts": [type("Part", (), {"text": text})()]}
                )()

        class FakeRunner:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

            async def run_async(self, **kwargs: object) -> AsyncGenerator[FakeEvent, None]:
                yield FakeEvent("intermediate")
                yield FakeEvent("final answer")

        agent_dir = tmp_path / "agents" / "researcher_agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        metadata = AgentMetadata(name="researcher_agent", path=agent_dir)

        class FakeApp:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

        class FakeSessionService:
            async def create_session(self, **kwargs: object) -> None:
                return None

        with (
            patch(
                "dashboard_api.routers.agents._agent_registry.get_agent",
                return_value=metadata,
            ),
            patch("dashboard_api.routers.agents.App", FakeApp),
            patch("dashboard_api.routers.agents.Runner", FakeRunner),
            patch(
                "dashboard_api.routers.agents.InMemorySessionService",
                FakeSessionService,
            ),
            patch(
                "dashboard_api.routers.agents.importlib.import_module",
                return_value=type("AgentModule", (), {"root_agent": object()})(),
            ),
        ):
            response = client.post(
                "/api/chat/researcher_agent?stream=false",
                json={"message": "hello", "session_id": "s1"},
            )

        assert response.status_code == 200
        assert response.json() == {"response": "final answer"}
