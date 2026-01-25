"""Unit tests for researcher agent server.py entry point."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestServerEntryPoint:
    """Tests for server.py entry point."""

    @pytest.fixture
    def researcher_agent_path(self) -> Path:
        """Get the path to researcher_agent directory."""
        project_root = Path(__file__).parent.parent.parent.parent
        return project_root / "agents" / "researcher_agent"

    def test_server_py_exists(self, researcher_agent_path: Path) -> None:
        """Test that server.py file exists."""
        server_py = researcher_agent_path / "server.py"
        assert server_py.exists(), f"server.py not found at {server_py}"

    def test_server_py_syntax_valid(self, researcher_agent_path: Path) -> None:
        """Test that server.py has valid Python syntax."""
        server_py = researcher_agent_path / "server.py"

        # Try to compile the file to check syntax
        with open(server_py, "r", encoding="utf-8") as f:
            code = f.read()

        # Should not raise SyntaxError
        compile(code, server_py, "exec")

    def test_server_py_imports_agent(self, researcher_agent_path: Path) -> None:
        """Test that server.py imports root_agent from agent module."""
        server_py = researcher_agent_path / "server.py"

        with open(server_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Should import root_agent
        assert "from agent import root_agent" in content or "import root_agent" in content

    def test_server_py_creates_app(self, researcher_agent_path: Path) -> None:
        """Test that server.py creates FastAPI app."""
        server_py = researcher_agent_path / "server.py"

        with open(server_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Should create app
        assert "app" in content or "create_platform_app" in content

    def test_server_py_uses_platform_factory(self, researcher_agent_path: Path) -> None:
        """Test that server.py uses create_platform_app factory."""
        server_py = researcher_agent_path / "server.py"

        with open(server_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Should use create_platform_app
        assert "create_platform_app" in content
