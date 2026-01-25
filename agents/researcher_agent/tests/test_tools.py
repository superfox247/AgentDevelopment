"""Unit tests for researcher agent tools."""

from agents.researcher_agent.tools.web_tools import format_search_query


def test_format_search_query_basic() -> None:
    """Normalize a simple query."""
    assert format_search_query("  capital of France  ") == "capital of France"


def test_format_search_query_collapse_spaces() -> None:
    """Collapse internal multiple spaces."""
    assert format_search_query("a   b   c") == "a b c"


def test_format_search_query_strip_filler() -> None:
    """Strip common filler phrases from the start."""
    assert format_search_query("Can you tell me the weather?") == "tell me the weather?"
    assert (
        format_search_query("Please find Paris population") == "find Paris population"
    )
    assert (
        format_search_query("I want to know capital of France") == "capital of France"
    )


def test_format_search_query_empty() -> None:
    """Empty or non-string returns empty string."""
    assert format_search_query("") == ""
    assert format_search_query("   ") == ""
