import json

from fastapi import FastAPI
from google.adk.events import Event

from agent_platform.models import ChatRequest, FeedbackRequest
from agent_platform.server import create_platform_app

from .agent import app as adk_app

# Aliases to maintain backward compatibility if needed, or just replace usages
SimpleChatRequest = ChatRequest
Feedback = FeedbackRequest


def _extract_event_data(event: Event) -> dict | None:
    """Extracts rich data from an event, or None if it's noise."""

    # 1. Tool Calls
    if hasattr(event, "tool_calls") and event.tool_calls:
        tool = event.tool_calls[0]
        # Serialize args to JSON string for display
        args_str = (
            json.dumps(tool.args, indent=2)
            if hasattr(tool, "args") and tool.args
            else "{}"
        )

        return {
            "type": "tool_use",
            "agent": event.author,
            "tool": tool.name or "unknown",
            "text": f"🔧 Calling {tool.name}...",
            "args": args_str,
        }

    # 2. Content (Thoughts / Message)
    if event.content and event.content.parts:
        text = ""
        for part in event.content.parts:
            if part.text:
                text += part.text

        # Check for usage metadata (approximate location based on GenAI types)
        tokens = 0
        if hasattr(event, "usage_metadata") and event.usage_metadata:
            tokens = getattr(event.usage_metadata, "total_token_count", 0)

        if text.strip():
            return {
                "type": "agent_thought",
                "agent": event.author,
                "text": text,  # Send full text, frontend will handle truncating/markdown
                "tokens": tokens,
                # Simple cost estimation: $0.35 / 1M input (Flash) -> very rough approx
                "cost": (tokens / 1_000_000) * 0.35,
            }

    return None


def _accumulate_text(event: Event, current_text: str) -> str:
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text:
                current_text += part.text
    return current_text


def create_app() -> FastAPI:
    # Create Standard App
    app = create_platform_app(
        adk_app=adk_app,
        description="Orchestrates the course creation process.",
        enable_a2a=False,  # Orchestrator is the Brain, usually not an A2A worker, but a consumer.
        include_root_route=False,  # Allow frontend to mount at /
    )

    # Restore missing endpoint for Chat/Integration Tests
    from fastapi.responses import StreamingResponse
    from google.genai.types import Content, Part

    @app.post("/api/chat_stream")
    async def chat_stream(request: ChatRequest) -> object:
        runner = app.state.runner

        # Ensure session
        session_id = request.session_id or "default_session"
        user_id = request.user_id or "default_user"

        try:
            await runner.session_service.create_session(
                app_name=app.title, user_id=user_id, session_id=session_id
            )
        except Exception:
            pass

        prompt = request.message
        msg = Content(role="user", parts=[Part.from_text(text=prompt)])

        from collections.abc import AsyncGenerator

        async def event_generator() -> AsyncGenerator[str, None]:
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=msg
            ):
                data = _extract_event_data(event)
                if data:
                    yield json.dumps(data) + "\n"

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
