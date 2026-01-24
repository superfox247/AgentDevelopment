import asyncio
from collections.abc import AsyncGenerator

"""
Orchestrator Pipeline Integration Tests.

Verifies the full agent workflow (Customer Service -> Research -> Content)
by mocking the leaf nodes (sub-agents) and testing the routing logic.
"""
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.adk.agents import Agent, InvocationContext
from google.adk.events import Event
from google.genai import types

# Extract root_agent from the app for testing
from domains.course_creator.orchestrator.agent import (
    OrchestratorAgent,
    app,
    check_judge_feedback,
)

root_agent = cast(OrchestratorAgent, app.root_agent)
from schemas.models.protocol import CustomerServiceResponse  # noqa: E402


# --- Mock Agent Helper ---
class MockAgent(Agent):
    """A helper agent for testing that yields predefined events and side effects."""
    def __init__(self, name: str, events_to_yield: list[Event] | None = None, side_effect: Any | None = None):
        # Initialize as a proper Pydantic model (BaseAgent)
        super().__init__(
            name=name,
            description="Mock Agent",
            model="mock-model",  # Dummy model to satisfy validation
        )
        self.parent_agent = None
        self._events_to_yield = events_to_yield or []
        self._side_effect = side_effect

    async def run_async(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        print(f"DEBUG: Running MockAgent {self.name}...")
        # Update state if side_effect provided
        if self._side_effect:
            print(f"DEBUG: MockAgent {self.name} executing side_effect")
            await self._side_effect(ctx)

        # Yield events
        for event in self._events_to_yield:
            event.author = self.name
            # Populate context-dependant fields to ensure ADK accepts the event
            event.invocation_id = ctx.invocation_id
            event.branch = ctx.branch

            ctx.session.events.append(event)
            yield event


# --- Fixtures ---


@pytest.fixture
def mock_context() -> MagicMock:
    ctx = MagicMock()
    # Explicitly set string values for IDs to satisfy Pydantic validation of Events
    ctx.invocation_id = "mock-invocation-id"
    ctx.branch = "main"

    ctx.end_invocation = False
    ctx.agent_states = {}
    ctx.end_of_agents = {}
    ctx.session = MagicMock()
    ctx.session.state = {}
    ctx.session.events = []

    # Mock callbacks to avoid errors
    ctx.plugin_manager.run_before_agent_callback = AsyncMock(return_value=None)
    ctx.plugin_manager.run_after_agent_callback = AsyncMock(return_value=None)
    ctx.model_copy.side_effect = lambda **kwargs: ctx
    ctx.should_pause_invocation.return_value = False

    return ctx


@pytest.mark.asyncio
async def test_full_pipeline_happy_path(mock_context: MagicMock) -> None:
    """
    Verifies the happy path:
    User -> Orchestrator -> CustomerService(Research) -> Researcher -> Judge(Pass) -> ContentBuilder -> End
    """

    # 1. Setup Data for Mocks

    # Customer Service: Detects "Research" intent
    async def cs_side_effect(ctx: InvocationContext) -> None:
        ctx.session.state["customer_service_output"] = CustomerServiceResponse(
            message="Starting research...", intent="research_request", topic="Python"
        )
        await asyncio.sleep(0)  # Satisfy async requirement

    mock_cs = MockAgent(
        name="customer_service",
        events_to_yield=[
            Event(
                author="customer_service",
                content=types.Content(
                    parts=[types.Part(text="Sure, researching Python.")]
                ),
            )
        ],
        side_effect=cs_side_effect,
    )

    # Researcher: Returns findings
    async def researcher_side_effect(ctx: InvocationContext) -> None:
        ctx.session.state["research_findings"] = {
            "topic": "Python",
            "summary": "Python is a language.",
            "sources": ["docs.python.org"],
        }
        await asyncio.sleep(0)

    mock_researcher = MockAgent(
        name="researcher",
        events_to_yield=[
            Event(
                author="researcher",
                content=types.Content(parts=[types.Part(text="Found info.")]),
            )
        ],
        side_effect=researcher_side_effect,
    )

    # Judge: Returns "pass"
    async def judge_side_effect(ctx: InvocationContext) -> None:
        ctx.session.state["judge_feedback"] = {"status": "pass", "feedback": "LGTM"}
        await asyncio.sleep(0)

    mock_judge = MockAgent(
        name="judge",
        events_to_yield=[
            Event(
                author="judge", content=types.Content(parts=[types.Part(text="Pass.")])
            )
        ],
        side_effect=judge_side_effect,
    )

    # Content Builder: Transforms findings -> Course
    async def cb_side_effect(ctx: InvocationContext) -> None:
        # Verify it received the input injection (optional, check valid state usage)
        assert "research_findings" in ctx.session.state
        ctx.session.state["course_content"] = {
            "title": "Python Course",
            "modules": [{"title": "Intro", "content": "Welcome"}],
        }
        await asyncio.sleep(0)

    mock_cb = MockAgent(
        name="content_builder",
        events_to_yield=[
            Event(
                author="content_builder",
                content=types.Content(parts=[types.Part(text="Course created.")]),
            )
        ],
        side_effect=cb_side_effect,
    )

    # 2. Inject Mocks via Constructor/Field Injection

    # Create a fresh Research Loop with Mocks
    # We use the real LoopAgent logic to test the loop/escalation
    # We must create a FRESH escalation_checker because the imported one is already bound to a parent
    from google.adk.agents import LoopAgent, SequentialAgent

    from agent_platform.control_flow import StateConditionEscalator

    test_escalation_checker = StateConditionEscalator(
        name="escalation_checker",
        state_key="judge_feedback",
        success_predicate=check_judge_feedback,
        description="Checks the judge's feedback.",
    )

    test_research_loop = LoopAgent(
        name="research_loop",
        sub_agents=[mock_researcher, mock_judge, test_escalation_checker],
        max_iterations=3,
    )

    # Create a fresh Pipeline with Mocks
    test_pipeline = SequentialAgent(
        name="course_creation_pipeline", sub_agents=[test_research_loop, mock_cb]
    )

    # Patch the Root Agent's dependencies
    # Since OrchestratorAgent uses Pydantic fields, we should assign to them.
    # Note: OrchestratorAgent.pipeline is a BaseAgent field.

    root_agent.customer_service = mock_cs
    root_agent.pipeline = test_pipeline

    # 3. Run the Orchestrator
    # We call run_async on the root agent. It should iterate through everything.

    processed_events = []
    async for event in root_agent.run_async(mock_context):
        processed_events.append(event)

    # 4. Verification

    # State Verify
    state = mock_context.session.state

    # Check intermediate states to ensure flow happened
    assert state.get("customer_service_output").intent == "research_request"
    assert "research_findings" in state, "Research Findings not found in state"
    assert state.get("research_findings")["topic"] == "Python"
    assert "judge_feedback" in state, "Judge Feedback not found in state"
    assert state.get("judge_feedback")["status"] == "pass"
    assert "course_content" in state, "Course Content not found in state"
    assert state.get("course_content")["title"] == "Python Course"

    # Flow Verify (by author sequence in events)
    authors = [e.author for e in processed_events]

    # Expected: customer_service -> researcher -> judge -> (escalation stops loop) -> content_builder
    # Note: escalation_checker yields no events effectively, just generic control signals or nothing if internal.
    # Actually, escalation_checker in ADK usually yields nothing if it just sets flags, OR yields EndInvocation.
    # In LoopAgent, if a sub-agent breaks the loop, the loop finishes.

    # Check subsequence
    assert "customer_service" in authors
    assert "researcher" in authors
    assert "judge" in authors
    assert "content_builder" in authors

    # Ensure Content Builder ran AFTER Judge passed
    judge_idx = authors.index("judge")
    cb_idx = authors.index("content_builder")
    assert cb_idx > judge_idx
