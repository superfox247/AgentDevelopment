"""Unit tests for base agent tools."""

from agents.base_agent.tools.echo import echo


def test_echo_basic() -> None:
    """Echo returns input unchanged."""
    assert echo("hello world") == "hello world"


def test_echo_empty() -> None:
    """Echo empty string returns empty string."""
    assert echo("") == ""


def test_echo_none_returns_empty() -> None:
    """Echo None returns empty string (guarded in implementation)."""
    assert echo(None) == ""
