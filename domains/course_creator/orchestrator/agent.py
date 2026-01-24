import asyncio

"""
Orchestrator Agent.

The central brain of the Course Creator domain.
- Routes user intent (Customer Service vs Pipeline)
- Manages the entire Content Creation Pipeline (Research -> Draft -> Evaluate -> Refine -> Images -> Finalize).
"""
import logging
import os
import warnings
from collections.abc import AsyncGenerator
from typing import Any

from google.adk.agents import BaseAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.apps.app import App
from google.adk.events import Event
from google.genai import types

from agent_platform.callbacks import create_save_output_callback
from agent_platform.control_flow import StateConditionEscalator
from schemas.models.protocol import ContentArticle, ContentSection

# Import Debug Tools


# Import Local Agents & Tools
try:
    from domains.course_creator.customer_service.agent import (
        create_agent as create_customer_service_agent,
    )
    from domains.course_creator.image_generator.agent import (
        create_agent as create_image_agent,
    )
except ImportError:
    import sys

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    )
    from domains.course_creator.customer_service.agent import (
        create_agent as create_customer_service_agent,
    )
    from domains.course_creator.image_generator.agent import (
        create_agent as create_image_agent,
    )

logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", message=r".*\[EXPERIMENTAL\].*", category=UserWarning)
warnings.filterwarnings(
    "ignore", message=".*save_input_blobs_as_artifacts.*", category=DeprecationWarning
)


def check_judge_feedback(feedback: Any) -> bool:
    """Checks if the judge feedback indicates a pass."""
    if isinstance(feedback, dict):
        return feedback.get("status") == "pass"
    return False


# --- Custom Pipeline Agent ---


class CoursePipelineAgent(BaseAgent):
    """
    Orchestrates the creation of content: Research -> Draft -> Visuals -> Finalize.
    """

    research_loop: BaseAgent
    content_builder: BaseAgent
    image_generator: BaseAgent

    async def _generate_section_image(
        self, section: ContentSection, parent_ctx: InvocationContext
    ) -> None:
        """Generates an image for a specific section in parallel."""
        if not section.image_prompt:
            return

        logger.info(f"Generating image for section '{section.heading}'...")

        msg = types.Content(role="user", parts=[types.Part(text=section.image_prompt)])
        sub_ctx = parent_ctx.model_copy(update={"user_content": msg})

        image_path = await self._execute_image_generation_with_retry(sub_ctx, section.heading)
        if image_path:
            section.image_path = image_path

    async def _execute_image_generation_with_retry(
        self, ctx: InvocationContext, section_name: str
    ) -> str | None:
        """Runs the image generator agent with retry logic for quotas."""
        retries = 3
        backoff = 2

        for attempt in range(retries):
            try:
                final_text = ""
                async for event in self.image_generator.run_async(ctx):
                    if event.content and event.content.parts:
                        final_text += event.content.parts[0].text or ""

                if path := self._validate_image_path(final_text, section_name):
                    return path
                
                # If we got text but it wasn't a path, it's likely a refusal or error message
                logger.warning(f"Image generator returned unexpected text: {final_text}")
                break

            except Exception as e:
                if not await self._handle_generation_error(e, section_name, attempt, retries, backoff):
                    break
        
        return None

    def _validate_image_path(self, text: str, section_name: str) -> str | None:
        """Validates if the returned text looks like a file path."""
        if text and ("/" in text or "\\" in text):
            clean_path = text.strip()
            logger.info(f"Image generated for '{section_name}': {clean_path}")
            return clean_path
        return None

    async def _handle_generation_error(
        self, e: Exception, section_name: str, attempt: int, retries: int, backoff: int
    ) -> bool:
        """Handles exceptions, returning True if retry should be attempted."""
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            wait_time = backoff * (2**attempt)
            logger.warning(
                f"Quota exceeded (429) for '{section_name}'. Retrying in {wait_time}s... (Attempt {attempt + 1}/{retries})"
            )
            await asyncio.sleep(wait_time)
            return True
        
        logger.error(f"Failed to generate image for '{section_name}': {e}")
        return False

    def _compile_markdown(self, article: ContentArticle) -> str:
        """Compiles the article into Markdown with images."""
        md = f"# {article.title}\n\n"
        md += f"*Target Audience: {article.target_audience}*\n\n"

        for section in article.sections:
            md += f"## {section.heading}\n\n"
            md += f"{section.content}\n\n"
            if section.image_path:
                # Use relative path for artifacts or absolute?
                # Standard markdown: ![Alt](path)
                # If path is absolute local, it might not render in web UIs easily without hosting.
                # But for now, we use the path we have.
                os.path.basename(section.image_path)
                # Assuming standard layout where artifacts are served or user opens file.
                md += f"![{section.image_prompt}]({section.image_path})\n\n"
                md += f"> *Visual Directive: {section.image_prompt}*\n\n"

        return md

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Executes the sequential pipeline steps: Research, Draft, Visuals, Finalize."""
        # 1. Research Loop
        logger.info("Step 1: Researching...")
        async for event in self.research_loop.run_async(ctx):
            yield event

        # 2. Content Drafting
        logger.info("Step 2: Drafting Content...")
        async for event in self.content_builder.run_async(ctx):
            yield event

        # 3. Visuals (Parallel)
        logger.info("Step 3: Generating Visuals...")
        data = ctx.session.state.get("content_article")
        if not data:
            logger.error("No content_article in state. Skipping visuals.")
            return

        try:
            article = ContentArticle(**data)
        except Exception as e:
            logger.error(f"Failed to parse ContentArticle: {e}")
            return

        tasks = [
            self._generate_section_image(section, ctx) for section in article.sections
        ]
        if tasks:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="Generating images in parallel...")],
                ),
            )
            await asyncio.gather(*tasks)

        # Update state with image paths
        ctx.session.state["content_article"] = article.model_dump()

        # 4. Finalize
        logger.info("Step 4: Compiling Final Artifact...")
        final_md = self._compile_markdown(article)

        # Save to artifacts
        import uuid

        filename = f"article_{uuid.uuid4()}.md"
        # We need an artifact service. The runner has one, but here we are in the agent.
        # We can write to disk directly as per 'Thin Agent' convention in 'artifacts/' volume.
        artifact_path = os.path.join(os.getcwd(), "artifacts", filename)
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(final_md)

        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=f"Content Creation Complete. Final Article saved to: {artifact_path}\n\nOutput:\n{final_md[:500]}..."
                    )
                ],
            ),
        )


# --- Root Routing Agent ---


class OrchestratorAgent(BaseAgent):
    """
    Routes between Customer Service and the Course Creation Pipeline.
    """

    customer_service: BaseAgent
    pipeline: BaseAgent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Executes the high-level routing logic."""
        # 1. Run Customer Service
        logger.info("Running Customer Service...")
        async for event in self.customer_service.run_async(ctx):
            yield event

        # 2. Check Intent
        cs_output = ctx.session.state.get("customer_service_output")
        if not cs_output:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="Customer Service did not return output.")],
                ),
            )
            return

        if hasattr(cs_output, "model_dump"):
            data = cs_output.model_dump()
        else:
            data = cs_output

        intent = data.get("intent")
        topic = data.get("topic")

        logger.info(f"Intent: {intent}, Topic: {topic}")

        if intent == "research_request":
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(text=f"Starting Content Pipeline for topic: {topic}")
                    ],
                ),
            )
            async for event in self.pipeline.run_async(ctx):
                yield event
        else:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model", parts=[types.Part(text="Interaction complete.")]
                ),
            )


def create_app() -> App:
    """Factory to create the Orchestrator App."""

    # --- Remote Agents ---
    researcher_url = os.environ.get(
        "RESEARCHER_AGENT_CARD_URL", "http://localhost:8001/.well-known/agent.json"
    )
    researcher = RemoteA2aAgent(
        name="researcher",
        agent_card=researcher_url,
        description="Gathers information on a topic using Google Search.",
        after_agent_callback=create_save_output_callback("research_findings"),
    )

    judge_url = os.environ.get(
        "JUDGE_AGENT_CARD_URL", "http://localhost:8002/.well-known/agent.json"
    )
    judge = RemoteA2aAgent(
        name="judge",
        agent_card=judge_url,
        description="Evaluates research findings for completeness and accuracy.",
        after_agent_callback=create_save_output_callback("judge_feedback"),
    )

    content_builder_url = os.environ.get(
        "CONTENT_BUILDER_AGENT_CARD_URL", "http://localhost:8003/.well-known/agent.json"
    )
    content_builder = RemoteA2aAgent(
        name="content_builder",
        agent_card=content_builder_url,
        description="Transforms research findings into a structured course.",
    )

    # --- Local Agents ---
    image_generator = create_image_agent()

    escalation_checker = StateConditionEscalator(
        name="escalation_checker",
        state_key="judge_feedback",
        success_predicate=check_judge_feedback,
    )

    # --- Pipelines ---
    research_loop = LoopAgent(
        name="research_loop",
        description="Iteratively researches and judges until quality standards are met.",
        sub_agents=[researcher, judge, escalation_checker],
        max_iterations=3,
    )

    content_pipeline = CoursePipelineAgent(
        name="content_pipeline",
        research_loop=research_loop,
        content_builder=content_builder,
        image_generator=image_generator,
    )

    # --- Root Agent ---
    root_agent = OrchestratorAgent(
        name="course_creator_orchestrator",
        pipeline=content_pipeline,
        customer_service=create_customer_service_agent(),
    )

    return App(root_agent=root_agent, name="orchestrator")


app = create_app()
