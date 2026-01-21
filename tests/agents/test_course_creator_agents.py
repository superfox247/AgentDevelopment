"""Tests for Course Creator domain agent configuration.

These tests verify agent YAML loading and configuration. 
For behavioral testing, see the ADK AgentEvaluator fixtures in fixtures/.

Note: Per the Testing Strategy Overhaul (2026), we do NOT mock LlmAgent internals.
Behavioral verification uses the ADK native evaluation framework with real trajectories.
"""

import os

import pytest

from agent_platform.yaml_loader import load_agent_from_yaml


class TestAgentConfiguration:
    """Verify agents load correctly from YAML configuration."""

    @pytest.fixture
    def agent_root(self):
        return os.path.join(os.getcwd(), "domains/course_creator")

    def test_researcher_loads(self, agent_root):
        """Researcher agent loads with expected configuration."""
        agent = load_agent_from_yaml(os.path.join(agent_root, "researcher/agent.yaml"))
        assert agent.name == "researcher"
        assert agent.output_schema is not None
        # Researcher uses google_search (built-in tool)
        assert len(agent.tools) > 0

    def test_judge_loads(self, agent_root):
        """Judge agent loads with expected configuration."""
        agent = load_agent_from_yaml(os.path.join(agent_root, "judge/agent.yaml"))
        assert agent.name == "judge"
        assert agent.output_schema is not None

    def test_content_builder_loads(self, agent_root):
        """Content builder agent loads with expected configuration."""
        agent = load_agent_from_yaml(os.path.join(agent_root, "content_builder/agent.yaml"))
        assert agent.name == "content_builder"
        assert agent.input_schema is not None
        assert agent.output_schema is not None

    def test_image_generator_loads(self, agent_root):
        """Image generator agent loads with tools using relative import."""
        agent = load_agent_from_yaml(os.path.join(agent_root, "image_generator/agent.yaml"))
        assert agent.name == "image_generator"
        assert agent.input_schema is not None
        # Verify the relative tool import worked
        assert len(agent.tools) > 0
        assert any("generate_image" in str(t) for t in agent.tools)

    def test_customer_service_loads(self, agent_root):
        """Customer service agent loads with expected configuration."""
        agent = load_agent_from_yaml(os.path.join(agent_root, "customer_service/agent.yaml"))
        assert agent.name == "customer_service"
        assert agent.output_schema is not None
