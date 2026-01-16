from collections.abc import AsyncGenerator, Callable
import logging
from typing import Optional

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import PrivateAttr

logger = logging.getLogger(__name__)

class StateConditionEscalator(BaseAgent):
    """
    Checks a condition in the session state and escalates (breaks the loop) if met.
    """
    state_key: str
    # Use PrivateAttr for the predicate to avoid serialization issues/Pydantic validation errors
    # if it's a complex callable. Or just use a field with exclude=True.
    # However, since we initiate it in code, passing it as a field is fine if type is correct.
    success_predicate: Optional[Callable[[object], bool]] = None
    
    description: str = "Checks for exit condition."


    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state_value = ctx.session.state.get(self.state_key)
        
        logger.info(f"[{self.name}] Checking state['{self.state_key}']: {state_value}")

        escalate = False
        if self.success_predicate:
            if self.success_predicate(state_value):
                escalate = True
        else:
            # Default behavior: generic truthiness check
            if state_value:
                escalate = True

        if escalate:
            logger.info(f"[{self.name}] Condition met. Escalating.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)
