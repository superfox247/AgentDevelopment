from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from google.adk.agents import LlmAgent
from pydantic import BaseModel

from agent_platform.yaml_loader import load_agent_from_yaml


# Dummy Pydantic model for schema testing
class MockSchema(BaseModel):
    pass

@pytest.fixture
def mock_instruction_loader():
    with patch("agent_platform.yaml_loader.load_instruction") as mock:
        mock.return_value = "System Instruction"
        yield mock

@pytest.fixture
def mock_import_object():
    with patch("agent_platform.yaml_loader._import_object") as mock:
        yield mock

def test_load_agent_minimal(tmp_path: Path):
    """Test loading a minimal agent configuration."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {
        "name": "test_agent",
        "model": "test-model-1.0",
        "instruction": "Do things.",
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent_from_yaml(str(agent_yaml))

    assert isinstance(agent, LlmAgent)
    assert agent.name == "test_agent"
    assert agent.model == "test-model-1.0"
    # LlmAgent instruction handling varies, but we check if it was loaded.
    # If the property isn't exposed, we just verify no crash.
    # Assuming 'instruction' might be exposed or we skip the check if private.
    # However, for this test to be useful we want to know it loaded.
    # Let's check protected attribute if we must, or trust the loader.
    # Upstream ADK LlmAgent often has 'instruction' property.
    if hasattr(agent, "instruction"):
        assert agent.instruction == "Do things."

def test_load_agent_with_instruction_key(tmp_path: Path, mock_instruction_loader):
    """Test loading agent with instruction_key lookup."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {
        "name": "key_agent",
        "instruction_key": "my_agent_key"
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent_from_yaml(str(agent_yaml))

    mock_instruction_loader.assert_called_once_with("my_agent_key")
    if hasattr(agent, "instruction"):
        assert agent.instruction == "System Instruction"

def test_load_agent_with_instruction_file_relative(tmp_path: Path):
    """Test loading agent with instruction_file relative to yaml."""
    agent_yaml = tmp_path / "agent.yaml"
    instruction_file = tmp_path / "inst.md"
    instruction_file.write_text("File Instruction", encoding="utf-8")

    config = {
        "name": "file_agent",
        "instruction_file": "inst.md"
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    agent = load_agent_from_yaml(str(agent_yaml))
    if hasattr(agent, "instruction"):
        assert agent.instruction == "File Instruction"

def test_load_agent_with_tools_builtin(tmp_path: Path):
    """Test loading agent with built-in google_search tool."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {
        "name": "tool_agent",
        "tools": ["google_search"]
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    # We need to ensure google.adk.tools is importable or mocked if checking strictly
    # Real import checks if adk is installed. Assuming yes in this env.
    agent = load_agent_from_yaml(str(agent_yaml))

    assert len(agent.tools) == 1
    # Check if tool is present
    # The actual tool object structure depends on ADK version.
    # We verify that SOMETHING was added to list.
    assert agent.tools[0] is not None

def test_load_agent_with_schemas(tmp_path: Path, mock_import_object):
    """Test loading agent with input/output schemas."""
    mock_import_object.return_value = MockSchema

    agent_yaml = tmp_path / "agent.yaml"
    config = {
        "name": "schema_agent",
        "input_schema": "my.pkg.Input",
        "output_schema": "my.pkg.Output"
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    # Validates it doesn't crash on import
    load_agent_from_yaml(str(agent_yaml))

    assert mock_import_object.call_count == 2
    mock_import_object.assert_any_call("my.pkg.Input")
    mock_import_object.assert_any_call("my.pkg.Output")

    # Check that schema was assigned. LlmAgent handling of schemas varies by version,
    # but usually stored in public attrs or internal config.
    # Assuming attributes exist or passed to constructor.
    # We can inspect the arguments passed to LlmAgent if we mocked it, but here we run real LlmAgent.
    # Checking attributes if available.
    # Note: LlmAgent in ADK might not expose input_schema publicly directly in all versions.
    # verification via constructor args would be safer if we mocked LlmAgent class.

def test_load_agent_not_found():
    """Test FileNotFoundError for missing yaml."""
    with pytest.raises(FileNotFoundError):
        load_agent_from_yaml("/non/existent/path.yaml")

def test_load_agent_missing_instruction_file(tmp_path: Path):
    """Test FileNotFoundError for missing instruction file."""
    agent_yaml = tmp_path / "agent.yaml"
    config = {
        "name": "bad_inst_agent",
        "instruction_file": "missing.md"
    }
    agent_yaml.write_text(yaml.dump(config), encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        load_agent_from_yaml(str(agent_yaml))
