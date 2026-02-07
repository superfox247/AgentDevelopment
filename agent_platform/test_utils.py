"""Shared test utilities for agent testing.

Provides common test fixtures and helpers for testing agents and servers.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def get_agent_path(agent_name: str, test_file_path: Path) -> Path:
    """Get the path to an agent directory from a test file.

    Args:
        agent_name: Name of the agent (e.g., "base_agent", "researcher_agent").
        test_file_path: Path to the test file (typically __file__).

    Returns:
        Path to the agent directory.
    """
    project_root = test_file_path.parent.parent.parent.parent
    return project_root / "agents" / agent_name


class TestServerEntryPointBase:
    """Base test class for server.py entry point tests.

    Subclasses should set the agent_name class variable.
    """

    __test__ = False
    agent_name: str = ""

    @pytest.fixture
    def agent_path(self, request: pytest.FixtureRequest) -> Path:
        """Get the path to the agent directory."""
        # Get the test file path from the test request
        test_file_path = Path(request.module.__file__)
        return get_agent_path(self.agent_name, test_file_path)

    def test_server_py_exists(self, agent_path: Path) -> None:
        """Test that server.py file exists."""
        server_py = agent_path / "server.py"
        assert server_py.exists(), f"server.py not found at {server_py}"

    def test_server_py_syntax_valid(self, agent_path: Path) -> None:
        """Test that server.py has valid Python syntax."""
        server_py = agent_path / "server.py"

        with open(server_py, encoding="utf-8") as f:
            code = f.read()

        compile(code, server_py, "exec")

    def test_server_py_imports_agent(self, agent_path: Path) -> None:
        """Test that server.py imports root_agent from agent module."""
        server_py = agent_path / "server.py"

        with open(server_py, encoding="utf-8") as f:
            content = f.read()

        assert (
            "from agent import root_agent" in content or "import root_agent" in content
        )

    def test_server_py_creates_app(self, agent_path: Path) -> None:
        """Test that server.py creates FastAPI app."""
        server_py = agent_path / "server.py"

        with open(server_py, encoding="utf-8") as f:
            content = f.read()

        assert (
            "app" in content
            or "create_agent_app" in content
            or "create_platform_app" in content
        )

    def test_server_py_uses_platform_factory(self, agent_path: Path) -> None:
        """Test that server.py uses create_agent_app or create_platform_app factory."""
        server_py = agent_path / "server.py"

        with open(server_py, encoding="utf-8") as f:
            content = f.read()

        assert "create_agent_app" in content or "create_platform_app" in content
