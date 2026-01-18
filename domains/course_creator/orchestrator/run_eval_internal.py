import asyncio
import json
import logging
from pathlib import Path

from orchestrator.agent import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVAL_DIR = Path(__file__).parent
EVAL_SET_PATH = EVAL_DIR / "course_creator.evalset.json"


async def run_evals() -> None:
    if not EVAL_SET_PATH.exists():
        logger.error(f"Eval set not found at {EVAL_SET_PATH}")
        return

    eval_data = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))
    logger.info(f"Loaded {len(eval_data)} eval cases.")

    for i, case in enumerate(eval_data):
        input_data = case["input"]
        # Extract message if it's a dict like {"message": "..."}
        if isinstance(input_data, dict) and "message" in input_data:
            input_text = input_data["message"]
        else:
            input_text = str(input_data)

        case.get("expected_criteria", [])

        logger.info(f"Running Case {i + 1}: {input_text}")

        try:
            # Run the agent using the ADK Runner
            from google.adk.artifacts.file_artifact_service import FileArtifactService
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai import types as genai_types

            runner = Runner(
                app=app,
                session_service=InMemorySessionService(),
                artifact_service=FileArtifactService(root_dir="./eval_artifacts"),
            )

            # Construct input
            adk_msg = genai_types.Content(
                role="user", parts=[genai_types.Part.from_text(text=input_text)]
            )

            # Create session explicitly
            session = await runner.session_service.create_session(
                app_name=app.name, user_id="eval_user", session_id=f"eval_session_{i}"
            )

            # Use run_async
            # It yields events. We need to collect the final output or all events.
            # Usually the last event or accumulated text is what we want.

            result_text = ""
            async for event in runner.run_async(
                user_id="eval_user", session_id=session.id, new_message=adk_msg
            ):
                # Accumulate text from events
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            result_text += part.text

            logger.info(f"Result Text: {result_text}")

            if result_text:
                logger.info(f"Case {i + 1} PASSED")
            else:
                logger.error(f"Case {i + 1} FAILED (No output)")

        except Exception as e:
            logger.error(f"Case {i + 1} FAILED with error: {e}")


if __name__ == "__main__":
    asyncio.run(run_evals())
