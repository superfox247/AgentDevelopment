"""Tests for Content Creation domain agent configuration.

These tests verify agent YAML loading and configuration.
"""

import os

import pytest
from google.adk.agents import LlmAgent

from agent_platform.server import load_agent_from_yaml


class TestAgentConfiguration:
    """Verify agents load correctly from YAML configuration."""

    @pytest.fixture
    def agent_root(self) -> str:
        return os.path.join(os.getcwd(), "agents/content_creation")

    def test_researcher_loads(self, agent_root: str) -> None:
        """Researcher agent loads with expected configuration."""
        yaml_path = os.path.join(agent_root, "researcher/agent.yaml")
        assert os.path.exists(yaml_path), f"Researcher YAML not found at {yaml_path}"

        agent = load_agent_from_yaml(yaml_path)
        print(f"DEBUG: Loaded agent type: {type(agent)}")
        print(f"DEBUG: Agent config: {agent.model_config}")
        assert isinstance(agent, LlmAgent)
        assert agent.name == "researcher"
        assert agent.output_schema is not None
        # Verify tool loaded
        assert len(agent.tools) > 0
