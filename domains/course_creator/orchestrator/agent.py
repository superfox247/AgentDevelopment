import logging
import os
import warnings
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.apps.app import App
from google.adk.events import Event
from pydantic import Field

from agent_platform.callbacks import create_save_output_callback
from agent_platform.control_flow import StateConditionEscalator
from registry.models.protocol import (
    JudgeFeedback,
)

# Import Local Agents
# Import Local Agents
# Use absolute imports assuming the monorepo root is in PYTHONPATH
# OR relative imports if running as a package
try:
    from domains.course_creator.customer_service.agent import customer_service
except ImportError:
    # Fallback for when running from within the domains directory
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    from domains.course_creator.customer_service.agent import customer_service

logger = logging.getLogger(__name__)

# Suppress experimental warnings for A2A components
warnings.filterwarnings("ignore", message=r".*\[EXPERIMENTAL\].*", category=UserWarning)
# Upstream bug: google.adk.runners accesses deprecated 'save_input_blobs_as_artifacts' internally
warnings.filterwarnings("ignore", message=".*save_input_blobs_as_artifacts.*", category=DeprecationWarning)


# --- Root Routing Agent ---

class OrchestratorAgent(BaseAgent):
    """
    Routes between Customer Service and the Course Creation Pipeline.
    """
    customer_service: BaseAgent = Field(default=customer_service)
    pipeline: BaseAgent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:

        # 1. Run Customer Service
        logger.info("Running Customer Service...")
        async for event in self.customer_service.run_async(ctx):
            yield event

        # 2. Check Intent
        # stored by after_agent_callback=create_save_output_callback("customer_service_output")
        cs_output = ctx.session.state.get("customer_service_output")

        if not cs_output:
            logger.warning("No output from Customer Service. Stopping.")
            return

        # Handle Dict vs Pydantic model
        if hasattr(cs_output, "model_dump"):
            data = cs_output.model_dump()
        elif isinstance(cs_output, dict):
            data = cs_output
        else:
            logger.warning(f"Unexpected output format from Customer Service: {type(cs_output)}")
            return

        intent = data.get("intent")
        topic = data.get("topic")

        logger.info(f"Customer Service Intent: {intent}, Topic: {topic}")

        if intent == "research_request":
            logger.info("Intent is 'research_request'. Starting Course Creation Pipeline...")
            # Optionally, we could inject the topic into the prompt/state for the researcher
            # For now, we rely on the conversation history which contains the user's request
            # and the customer service confirmation "Starting research on [topic]..."

            async for event in self.pipeline.run_async(ctx):
                yield event
        else:
            logger.info("Intent is 'chat'. Interaction complete.")


def create_app() -> App:
    """Factory to create the Orchestrator App."""
    
    # --- Remote Agents ---
    researcher_url = os.environ.get("RESEARCHER_AGENT_CARD_URL", "http://localhost:8001/.well-known/agent.json")
    researcher = RemoteA2aAgent(
        name="researcher",
        agent_card=researcher_url,
        description="Gathers information on a topic using Google Search.",
        after_agent_callback=create_save_output_callback("research_findings")
    )

    judge_url = os.environ.get("JUDGE_AGENT_CARD_URL", "http://localhost:8002/.well-known/agent.json")
    judge = RemoteA2aAgent(
        name="judge",
        agent_card=judge_url,
        description="Evaluates research findings for completeness and accuracy.",
        after_agent_callback=create_save_output_callback("judge_feedback")
    )

    content_builder_url = os.environ.get("CONTENT_BUILDER_AGENT_CARD_URL", "http://localhost:8003/.well-known/agent.json")
    content_builder = RemoteA2aAgent(
        name="content_builder",
        agent_card=content_builder_url,
        description="Transforms research findings into a structured course."
    )

    # --- Pipelines ---
    research_loop = LoopAgent(
        name="research_loop",
        description="Iteratively researches and judges until quality standards are met.",
        sub_agents=[researcher, judge, escalation_checker],
        max_iterations=3,
    )

    course_creation_pipeline = SequentialAgent(
        name="course_creation_pipeline",
        description="A pipeline that researches a topic and then builds a course from it.",
        sub_agents=[research_loop, content_builder],
    )

    # --- Root Agent ---
    root_agent = OrchestratorAgent(
        name="course_creator_orchestrator",
        pipeline=course_creation_pipeline
    )

    return App(root_agent=root_agent, name="orchestrator")
