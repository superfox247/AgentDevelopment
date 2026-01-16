import os
import warnings

from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.apps.app import App

from agent_platform.callbacks import create_save_output_callback
from agent_platform.control_flow import StateConditionEscalator

# Suppress experimental warnings for A2A components
warnings.filterwarnings("ignore", message=r".*\[EXPERIMENTAL\].*", category=UserWarning)
# Upstream bug: google.adk.runners accesses deprecated 'save_input_blobs_as_artifacts' internally
warnings.filterwarnings("ignore", message=".*save_input_blobs_as_artifacts.*", category=DeprecationWarning)


# --- Remote Agents ---
# These agents are running in their own containers. We connect to them via A2A.

# Default URLs assume local running on different ports if env vars are not set.
# Note: We use the agent card URL (e.g., http://localhost:8001/.well-known/agent.json) for discovery.
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

# --- Local Orchestration Agents ---

def check_judge_feedback(feedback: object) -> bool:
    if feedback and isinstance(feedback, dict) and feedback.get("status") == "pass":
        return True
    if isinstance(feedback, str) and '"status": "pass"' in feedback:
        return True
    return False

escalation_checker = StateConditionEscalator(
    name="escalation_checker",
    state_key="judge_feedback",
    success_predicate=check_judge_feedback,
    description="Checks the judge's feedback and escalates if it passed."
)

# --- Orchestration ---

research_loop = LoopAgent(
    name="research_loop",
    description="Iteratively researches and judges until quality standards are met.",
    sub_agents=[researcher, judge, escalation_checker],
    max_iterations=3,
)

root_agent = SequentialAgent(
    name="course_creation_pipeline",
    description="A pipeline that researches a topic and then builds a course from it.",
    sub_agents=[research_loop, content_builder],
)

app = App(root_agent=root_agent, name="orchestrator")
