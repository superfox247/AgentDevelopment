import inspect
from collections.abc import AsyncGenerator, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pydantic import PrivateAttr

from domains.course_creator.orchestrator.agent import OrchestratorAgent
from schemas.models.protocol import CustomerServiceResponse


# --- Mock Agent Implementation ---
class MockAgent(BaseAgent):
    """A concrete implementation of BaseAgent for testing purposes."""

    # Store side effect function. We use PrivateAttr to avoid Pydantic trying to serialize/validate it too strictly
    _side_effect: Callable[[InvocationContext], Any] | None = PrivateAttr(default=None)
    _events_to_yield: list[Event] = PrivateAttr(default_factory=list)

    def set_behavior(self, side_effect=None, events: list[Event] | None = None) -> None:
        self._side_effect = side_effect
        self._events_to_yield = events or []

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if self._side_effect:
            if inspect.iscoroutinefunction(self._side_effect):
                await self._side_effect(ctx)
            else:
                self._side_effect(ctx)

        for event in self._events_to_yield:
            yield event


# --- Tests ---


@pytest.fixture
def mock_context():
    session = MagicMock()
    session.state = {}

    ctx = MagicMock()
    ctx.session = session
    ctx.end_invocation = False
    ctx.agent_states = {}
    ctx.end_of_agents = {}

    # Mock plugin manager callbacks to be async no-ops
    ctx.plugin_manager.run_before_agent_callback = AsyncMock(return_value=None)
    ctx.plugin_manager.run_after_agent_callback = AsyncMock(return_value=None)

    # Crucial: invoking an agent creates a NEW context via model_copy.
    # We must ensure the copied context is also usable (or just return self)
    def fake_model_copy(update=None, **kwargs):
        if update:
            for k, v in update.items():
                setattr(ctx, k, v)
        return ctx

    ctx.model_copy.side_effect = fake_model_copy

    return ctx


@pytest.mark.asyncio
async def test_orchestrator_hello_flow(mock_context: Any) -> None:
    """
    Scenario 1: "Hello" Interaction
    Expected: Customer Service replies "chat", Pipeline is NOT called.
    """
    # 1. Setup Mocks using MockAgent
    mock_cs = MockAgent(name="mock_cs")
    mock_pipeline = MockAgent(name="mock_pipeline")

    # Define behavior for CS
    async def cs_side_effect(ctx: InvocationContext) -> None:
        ctx.session.state["customer_service_output"] = CustomerServiceResponse(
            message="Hello there!", intent="chat"
        )

    mock_cs.set_behavior(
        side_effect=cs_side_effect, events=[Event(author="customer_service")]
    )

    # Define behavior for Pipeline (should not be called, but safe default)
    mock_pipeline.set_behavior(events=[Event(author="course_creation_pipeline")])

    # 2. Inject into Orchestrator
    # We use post-init injection because OrchestratorAgent fields are Pydantic fields
    orchestrator = OrchestratorAgent(
        name="test_orchestrator", customer_service=mock_cs, pipeline=mock_pipeline
    )

    # 3. Run
    events = []
    async for event in orchestrator.run_async(mock_context):
        events.append(event)

    # 4. Verify
    # Expect 1 event from CS
    # Expect 2 events: 1 from CS, 1 from Orchestrator (completion)
    assert len(events) == 2
    assert events[0].author == "customer_service"
    assert events[1].content.parts[0].text == "Interaction complete."

    # Verify State
    assert mock_context.session.state["customer_service_output"].intent == "chat"


@pytest.mark.asyncio
async def test_orchestrator_capabilities_flow(mock_context: Any) -> None:
    """
    Scenario 2: "What can you do?"
    Expected: Customer Service replies "chat", Pipeline is NOT called.
    """
    mock_cs = MockAgent(name="mock_cs")
    mock_pipeline = MockAgent(name="mock_pipeline")

    async def cs_side_effect(ctx: InvocationContext) -> None:
        ctx.session.state["customer_service_output"] = CustomerServiceResponse(
            message="I can create courses!", intent="chat"
        )

    mock_cs.set_behavior(
        side_effect=cs_side_effect, events=[Event(author="customer_service")]
    )

    orchestrator = OrchestratorAgent(
        name="test_orchestrator", customer_service=mock_cs, pipeline=mock_pipeline
    )

    events = []
    async for event in orchestrator.run_async(mock_context):
        events.append(event)

    assert len(events) == 2
    assert events[0].author == "customer_service"
    assert events[1].content.parts[0].text == "Interaction complete."


@pytest.mark.asyncio
async def test_orchestrator_full_course_flow(mock_context: Any) -> None:
    """
    Scenario 3: "Create a course"
    Expected: Customer Service replies "research_request", Pipeline IS called.
    """
    mock_cs = MockAgent(name="mock_cs")
    mock_pipeline = MockAgent(name="mock_pipeline")

    async def cs_side_effect(ctx: InvocationContext) -> None:
        ctx.session.state["customer_service_output"] = CustomerServiceResponse(
            message="Starting research...", intent="research_request", topic="Python"
        )

    mock_cs.set_behavior(
        side_effect=cs_side_effect, events=[Event(author="customer_service")]
    )

    # Pipeline should yield an event
    mock_pipeline.set_behavior(events=[Event(author="course_creation_pipeline")])

    orchestrator = OrchestratorAgent(
        name="test_orchestrator", customer_service=mock_cs, pipeline=mock_pipeline
    )

    events = []
    async for event in orchestrator.run_async(mock_context):
        events.append(event)

    # We expect events from both CS and Pipeline
    authors = [e.author for e in events]
    assert "customer_service" in authors
    assert "course_creation_pipeline" in authors
