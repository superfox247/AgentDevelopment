"""
Unit Tests for Content Builder Agent.

Focuses on:
- Internal callback logic (load_research_findings, _save_output)
- Context manipulation
- State persistence
"""

from unittest.mock import MagicMock

import pytest

from domains.course_creator.content_builder.agent import _save_output


@pytest.mark.asyncio
async def test_content_builder_save_output() -> None:
    """Verifies that the _save_output callback correctly parses the event content."""
    # Setup Context
    ctx = MagicMock()
    ctx.session = MagicMock()
    ctx.session.state = {}

    # 1. Mock the Event structure
    from google.adk.events import Event
    from google.genai import types

    # Simulate a Function Call event (standard ADK output_schema behavior)
    mock_args = {
        "title": "Python 101",
        "target_audience": "Beginners",
        "sections": [
            {"heading": "Intro", "content": "Python is great."},
            {"heading": "Syntax", "content": "Indentation matters."},
        ],
    }

    part = types.Part(
        function_call=types.FunctionCall(
            name="ContentArticle",
            args=mock_args
        )
    )

    mock_event = Event(
        author="content_builder",
        content=types.Content(parts=[part])
    )

    # Set the event history
    ctx.session.events = [mock_event]

    # 2. Run the callback
    _save_output(ctx=ctx)

    # 3. Verify state update
    assert "content_article" in ctx.session.state
    saved_content = ctx.session.state["content_article"]
    assert saved_content["title"] == "Python 101"
    assert len(saved_content["sections"]) == 2
    assert saved_content["sections"][0]["heading"] == "Intro"


@pytest.mark.asyncio
async def test_load_research_findings() -> None:
    """Verifies that research findings are correctly injected into the user prompt."""
    # Setup Context
    ctx = MagicMock()
    ctx.session = MagicMock()
    ctx.session.state = {
        "research_findings": {
            "topic": "Python",
            "summary": "A popular language.",
            "sources": ["python.org"],
        }
    }

    from domains.course_creator.content_builder.agent import load_research_findings

    # Run callback
    load_research_findings(ctx)

    # Verify user content injection
    assert ctx.user_content is not None
    assert ctx.user_content.role == "user"
    assert "Here are the Research Findings" in ctx.user_content.parts[0].text
    assert "Python" in ctx.user_content.parts[0].text
