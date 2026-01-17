import json
import os
import logging

logger = logging.getLogger(__name__)

from google.adk.agents import InvocationContext
from google.adk.apps.app import App

from agent_platform.yaml_loader import load_agent_from_yaml
from registry.models.protocol import CourseContent


# --- Callbacks ---
def load_research_findings(ctx: InvocationContext):
    """Loads research findings from session state and injects them as user content."""
    findings_data = ctx.session.state.get("research_findings")

    if findings_data:
        import json
        if isinstance(findings_data, dict):
            findings_str = json.dumps(findings_data, indent=2)
        else:
            findings_str = str(findings_data)

        from google.genai import types
        ctx.user_content = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Here are the Research Findings:\n{findings_str}\n\nPlease build the course content.")
            ]
        )

def _parse_course_content(text: str) -> dict | None:
    """Helper to parse CourseContent from text/json."""
    if not text or not text.strip().startswith("{"):
         return None
    try:
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception:
        return None

def _extract_course_content_from_tool_call(event: object) -> dict | None:
    """Helper to check for CourseContent tool call."""
    if not event.content or not event.content.parts:
        return None

    for part in event.content.parts:
        if part.function_call and part.function_call.name == "CourseContent":
            return part.function_call.args
    return None

def _try_parse_fallback(event: object, ctx: InvocationContext):
    """Fallback: Check for JSON in text."""
    if event.content and event.content.parts:
        text = event.content.parts[0].text
        data = _parse_course_content(text)
        if data:
            try:
                 content = CourseContent(**data)
                 ctx.session.state["course_content"] = content.model_dump()
            except Exception:
                 pass

def _save_output(ctx: InvocationContext):
    """Saves the generated course content to the session state."""
    last_event = None
    if ctx.session and ctx.session.events:
        for event in reversed(ctx.session.events):
            if event.author == "content_builder":
                last_event = event
                break

    if not last_event:
        return

    # 1. Try Function Call
    tool_args = _extract_course_content_from_tool_call(last_event)
    if tool_args:
        try:
            content = CourseContent(**tool_args)
            ctx.session.state["course_content"] = content.model_dump()
            return
        except Exception as e:
            logger.error(f"Error parsing CourseContent from tool call: {e}")

    # 2. Fallback
    _try_parse_fallback(last_event, ctx)

# --- Content Builder Agent ---
content_builder = load_agent_from_yaml("agent.yaml", base_dir=os.path.dirname(__file__))

content_builder.before_agent_callback = load_research_findings
content_builder.after_agent_callback = _save_output

app = App(root_agent=content_builder, name="content_builder")
