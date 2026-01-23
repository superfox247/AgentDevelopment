"""Tests for Course Creator domain agent configuration.

These tests verify agent YAML loading and configuration.
For behavioral testing, see the ADK AgentEvaluator fixtures in fixtures/.

Note: Per the Testing Strategy Overhaul (2026), we do NOT mock LlmAgent internals.
Behavioral verification uses the ADK native evaluation framework with real trajectories.
"""

import os

import pytest
from google.adk.agents import LlmAgent

from agent_platform.loader import load_agent


class TestAgentConfiguration:
    """Verify agents load correctly from YAML configuration."""

    @pytest.fixture
    def agent_root(self) -> str:
        return os.path.join(os.getcwd(), "domains/course_creator")

    def test_researcher_loads(self, agent_root: str) -> None:
        """Researcher agent loads with expected configuration."""
        agent = load_agent(os.path.join(agent_root, "researcher/agent.yaml"))
        assert isinstance(agent, LlmAgent)
        assert agent.name == "researcher"
        assert agent.output_schema is not None
        # Researcher uses google_search (built-in tool)
        assert len(agent.tools) > 0

    def test_judge_loads(self, agent_root: str) -> None:
        """Judge agent loads with expected configuration."""
        agent = load_agent(os.path.join(agent_root, "judge/agent.yaml"))
        assert isinstance(agent, LlmAgent)
        assert agent.name == "judge"
        assert agent.output_schema is not None

    def test_content_builder_loads(self, agent_root: str) -> None:
        """Content builder agent loads with expected configuration."""
        agent = load_agent(os.path.join(agent_root, "content_builder/agent.yaml"))
        assert isinstance(agent, LlmAgent)
        assert agent.name == "content_builder"
        assert agent.input_schema is not None
        assert agent.output_schema is not None

    def test_image_generator_loads(self, agent_root: str) -> None:
        """Image generator agent loads with tools using relative import."""
        agent = load_agent(os.path.join(agent_root, "image_generator/agent.yaml"))
        assert isinstance(agent, LlmAgent)
        assert agent.name == "image_generator"
        assert agent.input_schema is not None
        # Verify the relative tool import worked
        assert len(agent.tools) > 0
        assert any("generate_image" in str(t) for t in agent.tools)

    def test_customer_service_loads(self, agent_root: str) -> None:
        """Customer service agent loads with expected configuration."""
        agent = load_agent(os.path.join(agent_root, "customer_service/agent.yaml"))
        assert isinstance(agent, LlmAgent)
        assert agent.name == "customer_service"
        assert agent.output_schema is not None
