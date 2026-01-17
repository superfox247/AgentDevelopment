import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Fix path to allow imports from root
sys.path.append(str(Path(__file__).parent.parent.parent))

from google.adk.artifacts.file_artifact_service import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVAL_DIR = Path(__file__).parent


async def run_evals(agent_name: str, eval_set_name: str) -> None:
    eval_set_path = EVAL_DIR / eval_set_name
    if not eval_set_path.exists():
        logger.error(f"Eval set not found at {eval_set_path}")
        return

    eval_data = json.loads(eval_set_path.read_text(encoding="utf-8"))
    logger.info(f"Loaded {len(eval_data)} eval cases for {agent_name}")

    # Dynamic Agent Loading
    try:
        if agent_name == "orchestrator":
            from domains.course_creator.orchestrator.agent import create_app
        elif agent_name == "image_generator":
            from domains.course_creator.image_generator.agent import create_app
        else:
            logger.error(f"Unknown agent: {agent_name}")
            return

        app = create_app()
    except ImportError as e:
        logger.error(f"Failed to import agent {agent_name}: {e}")
        return

    runner = Runner(
        app=app,
        session_service=InMemorySessionService(),
        artifact_service=FileArtifactService(root_dir="./eval_artifacts"),
    )

    for i, case in enumerate(eval_data):
        input_data = case["input"]
        if isinstance(input_data, dict) and "message" in input_data:
            input_text = input_data["message"]
        else:
            input_text = str(input_data)

        logger.info(f"Running Case {i + 1}: {input_text}")

        try:
            adk_msg = genai_types.Content(
                role="user", parts=[genai_types.Part.from_text(text=input_text)]
            )

            session = await runner.session_service.create_session(
                app_name=app.name,
                user_id="eval_user",
                session_id=f"eval_session_{agent_name}_{i}",
            )

            result_text = ""
            async for event in runner.run_async(
                user_id="eval_user", session_id=session.id, new_message=adk_msg
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            result_text += part.text

            logger.info(f"Result: {result_text}")

            if result_text:
                logger.info(f"Case {i + 1} PASSED")
            else:
                logger.error(f"Case {i + 1} FAILED (No output)")

        except Exception as e:
            logger.error(f"Case {i + 1} FAILED with error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agent",
        default="orchestrator",
        help="Agent to evaluate (orchestrator, image_generator)",
    )
    parser.add_argument(
        "--evalset",
        default="course_creator.evalset.json",
        help="Eval set filename in tests/evaluation/",
    )
    args = parser.parse_args()

    asyncio.run(run_evals(args.agent, args.evalset))
