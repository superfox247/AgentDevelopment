import asyncio
import logging
import os
import sys

# Add root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.artifacts.file_artifact_service import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# We use the agent factory directly for image generator, but for content builder we have create_app.
# We need the AGENT from content builder.
from domains.course_creator.image_generator.agent import create_agent as create_ig_agent
from domains.course_creator.orchestrator.agent import CoursePipelineAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ContentEngineTest")

from collections.abc import AsyncGenerator  # noqa: E402

from google.adk.events import Event  # noqa: E402

# --- Mocks ---


class MockResearchLoop(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info("Mocking Research...")
        yield Event(
            author=self.name,
            content=types.Content(
                role="model", parts=[types.Part(text="Researching...")]
            ),
        )

        # Inject Fake Findings
        ctx.session.state["research_findings"] = {
            "topic": "The History of Espresso",
            "summary": "Espresso originated in Italy. Key elements are pressure, temperature, and grind. The 9-bar rule is famous.",
            "sources": ["fake_url"],
        }
        yield Event(
            author=self.name,
            content=types.Content(
                role="model", parts=[types.Part(text="Research Complete.")]
            ),
        )


async def run_test() -> None:
    # 1. Setup Agents
    logger.info("Setting up agents...")

    mock_research = MockResearchLoop(name="mock_research")

    # Load Content Builder Local
    # We use the factory we just created
    from domains.course_creator.content_builder.agent import (
        create_agent as create_cb_agent,
    )

    real_content_builder = create_cb_agent()

    # Load Image Generator Local
    real_image_gen = create_ig_agent()

    # 2. Assemble Pipeline
    pipeline = CoursePipelineAgent(
        name="test_pipeline",
        research_loop=mock_research,
        content_builder=real_content_builder,
        image_generator=real_image_gen,
    )

    # Wrap in App
    from google.adk.apps.app import App

    test_app = App(root_agent=pipeline, name="test_pipeline")

    # 3. Run
    runner = Runner(
        app=test_app,
        session_service=InMemorySessionService(),
        artifact_service=FileArtifactService(root_dir="./eval_artifacts"),
    )

    logger.info("Starting Run...")
    session = await runner.session_service.create_session(
        app_name="test_pipeline", user_id="test_user"
    )

    # Trigger
    input_text = "Create an article about Espresso."
    adk_msg = types.Content(role="user", parts=[types.Part(text=input_text)])

    # We usually need to inject "intent" logic if using orchestator,
    # but here we run the pipeline directly.
    # The pipeline expects "research_findings" in state?
    # No, Step 1 of pipeline IS research -> it produces finding.
    # Our MockResearchLoop produces findings.

    async for event in runner.run_async(
        session_id=session.id, user_id="test_user", new_message=adk_msg
    ):
        if event.content and event.content.parts:
            print(f"OUTPUT: {event.content.parts[0].text}")

    # 4. Verify Artifacts
    logger.info("Verifying artifacts...")

    try:
        # InMemorySessionService stores sessions in .sessions dict (internal) or we assume session object is still valid?
        # The 'session' variable from create_session holds the state reference!
        # logic: runner updates the session object in place.
        session_obj = session
        content_article = session_obj.state.get("content_article")
    except Exception as e:
        logger.error(f"Failed to check session state: {e}")
        return

    if not content_article:
        logger.error(
            f"TEST FAILED: No content_article in state. State keys: {list(session_obj.state.keys())}"
        )
        if "customer_service_output" in session_obj.state:
            print("DEBUG: Customer Service output found (wrong agent?)")
        return

    import json

    print("DEBUG: Content Article State:")
    print(json.dumps(content_article, indent=2))

    # Check images
    for section in content_article.get("sections", []):
        prompt = section.get("image_prompt")
        path = section.get("image_path")
        print(f"Section '{section['heading']}':")
        print(f"  Prompt: {prompt}")
        print(f"  Path: {path}")

        if prompt and not path:
            logger.error("TEST FAILED: Prompt present but no path generated.")

    logger.info("TEST COMPLETE.")


if __name__ == "__main__":
    asyncio.run(run_test())
