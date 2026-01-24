"""
Tests for YAML Agent Loading.

Verifies that the `agent_platform.loader.load_agent` function correctly:
- Parses YAML
- Resolves relative paths (instructions/tools)
- Validates schemas
- Handles missing files
"""

from collections.abc import Generator
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
import yaml
from google.adk.agents import LlmAgent
from pydantic import BaseModel

from agent_platform.loader import load_agent


# Dummy Pydantic model for schema testing
class MockSchema(BaseModel):
    pass


@pytest.fixture
def mock_instruction_loader() -> Generator[MagicMock, None, None]:
    # Patch where it is used: AgentConfig in schemas/config.py
    with patch("agent_platform.schemas.config.load_instruction") as mock:
        mock.return_value = "System Instruction"
        yield mock


def test_load_agent_minimal(tmp_path: Path) -> None:
    """Test loading a minimal agent configuration."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {
        "name": "test_agent",
        "model": "test-model-1.0",
        "instruction": "Do things.",
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent(str(agent_yaml))

    assert isinstance(agent, LlmAgent)
    assert agent.name == "test_agent"
    # model is now a Gemini object
    from google.adk.models import Gemini
    assert isinstance(agent.model, Gemini)
    assert agent.model.model == "test-model-1.0"
    if hasattr(agent, "instruction"):
        assert agent.instruction == "Do things."


def test_load_agent_with_instruction_key(
    tmp_path: Path, mock_instruction_loader: MagicMock
) -> None:
    """Test loading agent with instruction_key lookup."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {"name": "key_agent", "instruction_key": "my_agent_key"}
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent(str(agent_yaml))

    mock_instruction_loader.assert_called_once_with("my_agent_key")
    if hasattr(agent, "instruction"):
        assert agent.instruction == "System Instruction"


def test_load_agent_with_instruction_file_relative(tmp_path: Path) -> None:
    """Test loading agent with instruction_file relative to yaml."""
    agent_yaml = tmp_path / "agent.yaml"
    instruction_file = tmp_path / "inst.md"
    instruction_file.write_text("File Instruction", encoding="utf-8")

    config = {"name": "file_agent", "instruction_file": "inst.md"}
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent(str(agent_yaml))
    if hasattr(agent, "instruction"):
        assert agent.instruction == "File Instruction"


def test_load_agent_with_tools_builtin(tmp_path: Path) -> None:
    """Test loading agent with built-in google_search tool."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {"name": "tool_agent", "tools": ["google_search"]}
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    # We need to ensure google.adk.tools is importable or mocked if checking strictly
    # Real import checks if adk is installed. Assuming yes in this env.
    agent = load_agent(str(agent_yaml))
    from typing import cast

    llm_agent = cast(LlmAgent, agent)

    assert len(llm_agent.tools) == 1
    # Check if tool is present
    # The actual tool object structure depends on ADK version.
    # We verify that SOMETHING was added to list.
    assert llm_agent.tools[0] is not None


def test_load_agent_with_schemas(tmp_path: Path) -> None:
    """Test loading agent with input/output schemas."""
    agent_yaml = tmp_path / "agent.yaml"
    # Use a real schema that exists in the project and is a Pydantic model
    config = {
        "name": "schema_agent",
        "instruction": "Test Instruction",
        "input_schema": "schemas.models.protocol.ResearchFindings",
        "output_schema": "schemas.models.protocol.ResearchFindings",
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent(str(agent_yaml))

    llm_agent = cast(LlmAgent, agent)
    # Verify the schemas were actually loaded and assigned
    # We check the name because direct identity might fail if re-imported, but here it should match.
    assert llm_agent.input_schema is not None
    assert llm_agent.input_schema.__name__ == "ResearchFindings"
    assert llm_agent.output_schema is not None
    assert llm_agent.output_schema.__name__ == "ResearchFindings"


def test_load_agent_not_found() -> None:
    """Test FileNotFoundError for missing yaml."""
    with pytest.raises(FileNotFoundError):
        load_agent("/non/existent/path.yaml")


def test_load_agent_missing_instruction_file(tmp_path: Path) -> None:
    """Test FileNotFoundError for missing instruction file."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {"name": "bad_inst_agent", "instruction_file": "missing.md"}
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        load_agent(str(agent_yaml))
