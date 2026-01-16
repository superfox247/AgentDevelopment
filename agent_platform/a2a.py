import logging
import uuid
from typing import Protocol, cast

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import AgentCapabilities, AgentCard, Message, TextPart
from google.adk.apps.app import App
from google.adk.events import Event
from google.adk.runners import Runner
from google.genai import types as genai_types


class SessionProtocol(Protocol):
    id: str
    events: list[Event]

class TextLike(Protocol):
    text: str



logger = logging.getLogger(__name__)

class AdkToA2aExecutor(AgentExecutor):
    """
    Standard Executor that bridges the A2A Protocol (JSON-RPC) to the Google ADK Runner.
    """
    def __init__(self, runner: Runner, app_name: str):
        self.runner = runner
        self.app_name = app_name

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # 1. User & Session Resolution
        user_id = self._resolve_user_id(context)
        session_id = context.context_id or str(uuid.uuid4())

        logger.info(f"[{self.app_name}] Executing task. User: {user_id}, Session: {session_id}")

        # 2. Extract Text Input
        user_text = self._extract_text(context.message)
        adk_msg = genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=user_text)]
        )

        # 3. Session Management
        session = await self._get_or_create_session(session_id, user_id)

        # 4. Stream Execution
        if session:
            async for event in self.runner.run_async(
                user_id=user_id, session_id=session.id, new_message=adk_msg
            ):
                 await self._handle_event(event, event_queue)


    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass

    def _resolve_user_id(self, context: RequestContext) -> str:
        """Extracts user_id from A2A context headers or state."""
        user_id = "default_user"
        if context.call_context:
            # Try authenticated user object
            if hasattr(context.call_context, "user") and context.call_context.user:
                 if hasattr(context.call_context.user, "id") and context.call_context.user.id:
                     return context.call_context.user.id
            # Try state/metadata
            if context.call_context.state:
                 return context.call_context.state.get("user_id", "default_user")
        return user_id

    def _extract_text(self, message: Message | None) -> str:
        """ Robustly extracts text from an A2A message."""
        if not message or not message.parts:
            return ""

        text = ""
        for part in message.parts:
            # We strictly check for known types first
            if isinstance(part, TextPart):
                text += part.text
            elif hasattr(part, "root") and isinstance(part.root, TextPart):
                text += part.root.text

            # Fallback for loose dicts (runtime safety)
            # Use cast to TextLike to allow dot access safely
            if hasattr(part, 'text'):
                safe_part = cast(TextLike, part)
                val = safe_part.text
                if isinstance(val, str):
                    text += val
            else:
                 # Check if 'text' key exists and is a string (cast to object for runtime dict check)
                 safe_part_obj = cast(object, part)
                 if isinstance(safe_part_obj, dict) and 'text' in safe_part_obj:
                     val = safe_part_obj['text']
                     if isinstance(val, str):
                        text += val




        return text


    async def _get_or_create_session(self, session_id: str, user_id: str) -> SessionProtocol | None:

        try:

            session = await self.runner.session_service.get_session(
                session_id=session_id, app_name=self.app_name, user_id=user_id
            )
        except Exception:
            session = None

        if not session:
            session = await self.runner.session_service.create_session(
                app_name=self.app_name, user_id=user_id, session_id=session_id
            )
        return session

    async def _handle_event(self, event: Event, event_queue: EventQueue) -> None:


        """Translates ADK Events to A2A Messages."""
        if event.content and event.content.parts:
            text_content = ""
            for p in event.content.parts:
                if p.text:
                    text_content += p.text

            if text_content:

                # A2A Message requires stricter typing
                # We use a known working structure
                a2a_msg = Message(
                    message_id=str(uuid.uuid4()), # Corrected snake_case
                    role="agent", # type: ignore # Valid role
                    parts=[TextPart(text=text_content)] # type: ignore # Valid part
                )
                await event_queue.enqueue_event(a2a_msg)


def create_agent_card(adk_app: App, description: str, host: str, port: int) -> AgentCard:

    """Helper to generate a standard AgentCard."""
    # Ensure port and host are valid
    base_url = f"http://{host}:{port}"

    return AgentCard(
        name=adk_app.name,
        description=description,
        version="0.1.0",
        protocol_version="0.1.0",
        url=f"{base_url}/a2a/{adk_app.name}",
        skills=[],
        capabilities=AgentCapabilities(),
        default_input_modes=["text"],
        default_output_modes=["text"],
        security=[]
    )

