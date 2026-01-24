"""
Unit tests for Base Agent tools.
"""
from agents.base_agent.tools import example_tool

def test_example_tool() -> None:
    """Verify the example tool returns the expected greeting."""
    result = example_tool("World")
    assert result == "Hello, World!"

def test_example_tool_empty() -> None:
    """Verify behavior with empty string if relevant (simple check)."""
    result = example_tool("")
    assert result == "Hello, !"
