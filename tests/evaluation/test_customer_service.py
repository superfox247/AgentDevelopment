import asyncio
import logging
import sys
from pathlib import Path

# Add root to python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from google.adk.artifacts.file_artifact_service import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from domains.course_creator.customer_service.agent import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CSTest")


async def run_test():
    app = create_app()
    runner = Runner(
        app=app,
        session_service=InMemorySessionService(),
        artifact_service=FileArtifactService(root_dir="./eval_artifacts"),
    )

    session = await runner.session_service.create_session(
        app_name="customer_service", user_id="test_user"
    )

    # Conversation Flow
    inputs = [
        "Hello",  # Chat
        "I want to write about Machine Learning",  # Partial -> gathering_info (Topic=ML, Missing: Type, Tone)
        "It should be a fun layout",  # Partial -> gathering_info (Topic=ML, Tone=Fun, Missing: Type)
        "Make it a Social Post",  # Full -> research_request (Topic=ML, Tone=Fun, Type=Social Post)
    ]

    logger.info("Starting Interaction Loop...")

    for text in inputs:
        logger.info(f"USER: {text}")
        adk_msg = types.Content(role="user", parts=[types.Part(text=text)])

        async for event in runner.run_async(
            session_id=session.id, user_id="test_user", new_message=adk_msg
        ):
            if event.content and event.content.parts:
                print(f"AGENT: {event.content.parts[0].text}")

                # Check state update (optional, but good for verification)
                # Note: customer_service_output is updated per turn
                # session_obj = await runner.session_service.load_session(session.id)
                session_obj = session
                last_output = session_obj.state.get("customer_service_output", {})
                print(f"DEBUG STATE: {last_output}")


if __name__ == "__main__":
    asyncio.run(run_test())
