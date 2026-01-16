from typing import Literal

from google.adk.agents import Agent
from google.adk.apps.app import App
from pydantic import BaseModel, Field

from agent_platform.config import config
from agent_platform.prompts import load_instruction


# --- Data Models ---
class JudgeFeedback(BaseModel):
    """Structured feedback from the Judge agent."""
    status: Literal["pass", "fail"] = Field(
        description="Whether the research is sufficient ('pass') or needs more work ('fail')."
    )
    feedback: str = Field(
        description="Detailed feedback on what is missing or needs clarification if status is 'fail'. If 'pass', a brief confirmation."
    )

# --- Judge Agent ---
judge = Agent(
    name="judge",
    model=config.default_model,
    description="Evaluates research findings for completeness and accuracy.",
    instruction=load_instruction("judge"),
    output_schema=JudgeFeedback,
    # Disallow transfers as it uses output_schema
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

app = App(root_agent=judge, name="judge")
