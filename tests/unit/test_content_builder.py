from unittest.mock import MagicMock

import pytest

from domains.course_creator.content_builder.agent import _save_output


@pytest.mark.asyncio
async def test_content_builder_save_output():
    # Setup Context
    ctx = MagicMock()
    ctx.session = MagicMock()
    ctx.session.state = {}

    # 1. Mock the Event structure
    from google.adk.events import Event

    # Simulate a Function Call event (standard ADK output_schema behavior)
    mock_args = {
        "title": "Python 101",
        "modules": [
            {"title": "Intro", "content": "Python is great."},
            {"title": "Syntax", "content": "Indentation matters."}
        ]
    }

    mock_event = MagicMock(spec=Event)
    mock_event.author = "content_builder"
    mock_event.content = MagicMock()

    # Mock the FunctionCall part
    part = MagicMock()
    part.function_call = MagicMock()
    part.function_call.name = "CourseContent"
    part.function_call.args = mock_args
    mock_event.content.parts = [part]

    # Set the event history
    ctx.session.events = [mock_event]

    # 2. Run the callback
    await _save_output(ctx)

    # 3. Verify state update
    assert "course_content" in ctx.session.state
    saved_content = ctx.session.state["course_content"]
    assert saved_content["title"] == "Python 101"
    assert len(saved_content["modules"]) == 2
    assert saved_content["modules"][0]["title"] == "Intro"

@pytest.mark.asyncio
async def test_load_research_findings():
    # Setup Context
    ctx = MagicMock()
    ctx.session = MagicMock()
    ctx.session.state = {
        "research_findings": {
            "topic": "Python",
            "summary": "A popular language.",
            "sources": ["python.org"]
        }
    }

    from domains.course_creator.content_builder.agent import load_research_findings

    # Run callback
    await load_research_findings(ctx)

    # Verify user content injection
    assert ctx.user_content is not None
    assert ctx.user_content.role == "user"
    assert "Here are the Research Findings" in ctx.user_content.parts[0].text
    assert "Python" in ctx.user_content.parts[0].text
