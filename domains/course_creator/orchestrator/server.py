import json
import os
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google.adk.events import Event
from google.genai import types as genai_types

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
        args_str = json.dumps(tool.args, indent=2) if hasattr(tool, "args") and tool.args else "{}"
        
        return {
            "type": "tool_use", 
            "agent": event.author, 
            "tool": tool.name or "unknown",
            "text": f"🔧 Calling {tool.name}...",
            "args": args_str
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
                "text": text, # Send full text, frontend will handle truncating/markdown
                "tokens": tokens,
                # Simple cost estimation: $0.35 / 1M input (Flash) -> very rough approx
                "cost": (tokens / 1_000_000) * 0.35 
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
        enable_a2a=False, # Orchestrator is the Brain, usually not an A2A worker, but a consumer.
        include_root_route=False # Allow frontend to mount at /
    )

    @app.post("/api/chat_stream")
    async def chat_stream(request: SimpleChatRequest) -> StreamingResponse:

        """Streaming chat endpoint using the runner attached to app state."""
        runner = app.state.runner

        # Simple Session Management
        try:
            session = await runner.session_service.get_session(
                session_id=request.session_id, app_name=adk_app.name, user_id=request.user_id
            )
        except Exception:
            session = None

        if not session:
            session = await runner.session_service.create_session(
                app_name=adk_app.name, user_id=request.user_id, session_id=request.session_id
            )

        user_msg = genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=request.message)]
        )

        async def event_generator() -> AsyncGenerator[str, None]:

            final_text = ""
            async for event in runner.run_async(
                user_id=request.user_id, session_id=session.id, new_message=user_msg
            ):
                # Send Rich Progress
                data = _extract_event_data(event)
                if data:
                    yield json.dumps(data) + "\n"

                # Accumulate
                final_text = _accumulate_text(event, final_text)

            # Send final
            yield json.dumps({"type": "result", "text": final_text.strip()}) + "\n"


        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    @app.post("/feedback")
    def collect_feedback(feedback: Feedback) -> dict[str, str]:
        # logger logic could be added here
        return {"status": "success"}

    return app

app = create_app()




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
