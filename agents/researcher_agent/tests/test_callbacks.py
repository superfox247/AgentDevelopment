"""Unit tests for researcher agent callbacks."""

from unittest.mock import MagicMock

import pytest

from agents.researcher_agent.callbacks.visibility import (
    after_agent_log,
    after_tool_log,
    before_agent_log,
    before_tool_log,
)


class TestBeforeAgentLog:
    """Tests for before_agent_log callback."""

    def test_before_agent_log_with_agent_name(self) -> None:
        """Test that callback logs agent name when present."""
        context = MagicMock()
        context.agent_name = "researcher_agent"
        context.invocation_id = "test-inv-123"
        context.state = {"key1": "value1", "key2": "value2"}

        result = before_agent_log(context)
        assert result is None

    def test_before_agent_log_without_agent_name(self) -> None:
        """Test that callback handles missing agent_name gracefully."""
        context = MagicMock()
        del context.agent_name
        context.invocation_id = "test-inv-123"
        context.state = {}

        result = before_agent_log(context)
        assert result is None

    def test_before_agent_log_with_none_state(self) -> None:
        """Test that callback handles None state gracefully."""
        context = MagicMock()
        context.agent_name = "researcher_agent"
        context.invocation_id = "test-inv-123"
        context.state = None

        result = before_agent_log(context)
        assert result is None


class TestAfterAgentLog:
    """Tests for after_agent_log callback."""

    def test_after_agent_log_with_agent_name(self) -> None:
        """Test that callback logs agent name when present."""
        context = MagicMock()
        context.agent_name = "researcher_agent"
        context.invocation_id = "test-inv-123"

        result = after_agent_log(context)
        assert result is None

    def test_after_agent_log_without_agent_name(self) -> None:
        """Test that callback handles missing agent_name gracefully."""
        context = MagicMock()
        del context.agent_name
        context.invocation_id = "test-inv-123"

        result = after_agent_log(context)
        assert result is None


class TestBeforeToolLog:
    """Tests for before_tool_log callback."""

    def test_before_tool_log_with_tool_name(self) -> None:
        """Test that callback logs tool name when present."""
        tool = MagicMock()
        tool.name = "google_search"
        args = {"query": "test query"}
        tool_context = MagicMock()

        result = before_tool_log(tool, args, tool_context)
        assert result is None

    def test_before_tool_log_without_tool_name(self) -> None:
        """Test that callback handles tool without name attribute."""
        tool = MagicMock()
        del tool.name
        args = {"query": "test query"}
        tool_context = MagicMock()

        result = before_tool_log(tool, args, tool_context)
        assert result is None


class TestAfterToolLog:
    """Tests for after_tool_log callback."""

    def test_after_tool_log_with_tool_name(self) -> None:
        """Test that callback logs tool response when present."""
        tool = MagicMock()
        tool.name = "google_search"
        args = {"query": "test query"}
        tool_context = MagicMock()
        tool_response = {"results": ["result1", "result2"]}

        result = after_tool_log(tool, args, tool_context, tool_response)
        assert result is None

    def test_after_tool_log_without_tool_name(self) -> None:
        """Test that callback handles tool without name attribute."""
        tool = MagicMock()
        del tool.name
        args = {"query": "test query"}
        tool_context = MagicMock()
        tool_response = {"results": []}

        result = after_tool_log(tool, args, tool_context, tool_response)
        assert result is None
