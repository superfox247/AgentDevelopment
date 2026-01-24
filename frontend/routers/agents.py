"""
Agent Router.

Endpoints for exploring and interacting with the Agent Ecosystem:
- Listing available agents/domains
- Viewing agent configuration/skills
- Direct chat/interaction with specific agents
"""

import json
import logging
import logging.config
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from google.adk.events import Event
from google.adk.runners import Runner
from google.genai.types import Content, Part

from frontend.dependencies import (
    ROOT_DIR,
    get_customer_service_runner,
    get_image_generator_runner,
)
from frontend.models import (
    AgentInfo,
    AgentsResponse,
    ChatRequest,
    ImageRequest,
    SkillInfo,
    SkillsResponse,
)
from frontend.services import ImageGenerationService

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Helpers ---


def _extract_event_data(event: Event) -> dict | None:
    """Helper to extract event data for frontend."""
    # Start with Tool Calls
    if hasattr(event, "tool_calls") and event.tool_calls:
        tool = event.tool_calls[0]
        return {
            "type": "tool_use",
            "agent": event.author,
            "tool": tool.name or "unknown",
            "text": f"🔧 Calling {tool.name}...",
        }

    # Content (Thoughts / Message)
    if event.content and event.content.parts:
        text = "".join([p.text for p in event.content.parts if p.text])
        if text.strip():
            return {
                "type": "agent_thought" if event.author != "user" else "user_message",
                "agent": event.author,
                "text": text,
            }
    return None


async def _customer_service_event_generator(
    runner: Runner, session_id: str, message: str
) -> AsyncGenerator[str, None]:
    msg = Content(role="user", parts=[Part.from_text(text=message)])
    final_intent = None

    async for event in runner.run_async(
        user_id="dashboard-user", session_id=session_id, new_message=msg
    ):
        data = _extract_event_data(event)
        if data:
            yield json.dumps(data) + "\n"

        if hasattr(event, "content") and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and "intent" in text and "research_request" in text:
                final_intent = "research_request"

    if final_intent == "research_request":
        yield (
            json.dumps(
                {
                    "type": "system_signal",
                    "signal": "research_started",
                    "text": "🚀 Configuration Complete! Starting Research Agent...",
                }
            )
            + "\n"
        )


# --- Endpoints ---


@router.get("/api/agents")
async def list_agents() -> AgentsResponse:
    """List available agents in the domains directory."""
    domains_dir = ROOT_DIR / "domains"
    agents = []

    if not domains_dir.exists():
        return AgentsResponse(agents=[])

    for domain_path in domains_dir.iterdir():
        if domain_path.is_dir():
            for agent_path in domain_path.iterdir():
                if agent_path.is_dir() and (agent_path / "agent.yaml").exists():
                    agents.append(
                        AgentInfo(
                            domain=domain_path.name,
                            name=agent_path.name,
                            path=str(agent_path.relative_to(ROOT_DIR)),
                        )
                    )
    return AgentsResponse(agents=agents)


@router.get("/api/agents/{domain}/{name}")
async def get_agent_config(domain: str, name: str) -> FileResponse:
    """Get the configuration for a specific agent."""
    agent_path = ROOT_DIR / "domains" / domain / name / "agent.yaml"
    if not agent_path.exists():
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    return FileResponse(agent_path)


@router.get("/api/skills")
async def list_skills() -> SkillsResponse:
    """List available skills in the .agent/skills directory."""
    skills_dir = ROOT_DIR / ".agent" / "skills"
    skills = []

    if not skills_dir.exists():
        return SkillsResponse(skills=[])

    for skill_path in skills_dir.iterdir():
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            skills.append(
                SkillInfo(
                    name=skill_path.name, path=str(skill_path.relative_to(ROOT_DIR))
                )
            )
    return SkillsResponse(skills=skills)


@router.get("/api/skills/{name}")
async def get_skill_content(name: str) -> FileResponse:
    """Get the documentation for a specific skill."""
    skill_path = ROOT_DIR / ".agent" / "skills" / name / "SKILL.md"
    if not skill_path.exists():
        raise HTTPException(status_code=404, detail="Skill documentation not found")
    return FileResponse(skill_path)


@router.post("/api/chat/customer_service")
async def chat_customer_service(
    req: ChatRequest, runner: Runner = Depends(get_customer_service_runner)
) -> StreamingResponse:
    """Chat with the Customer Service Agent."""
    # Ensure session exists
    try:
        await runner.session_service.create_session(
            app_name="customer_service",
            user_id="dashboard-user",
            session_id=req.session_id,
        )
    except Exception:
        pass  # Session might already exist

    return StreamingResponse(
        _customer_service_event_generator(runner, req.session_id, req.message),
        media_type="application/x-ndjson",
    )


@router.post("/api/generate/image")
async def generate_image(
    req: ImageRequest, runner: Runner = Depends(get_image_generator_runner)
) -> JSONResponse:
    """Generate an image using the Image Generator Agent."""
    # Instantiate service on the fly or via dependency if complex
    image_service = ImageGenerationService(runner)

    try:
        # Use configured default model if not provided or generic
        model_to_use = req.model
        if not model_to_use or model_to_use == "default":
            # Fallback to a reasonable default from config if available, otherwise hardcoded safe default
            model_to_use = "gemini-1.5-flash"

        image_path = await image_service.generate_image(
            user_id="dashboard-user",
            session_id=req.session_id,
            prompt=req.prompt,
            model=model_to_use,
        )

        if image_path.startswith("artifacts/"):
            serve_path = image_path[len("artifacts/") :]
            return JSONResponse(content={"image_url": f"/api/artifacts/{serve_path}"})

        return JSONResponse(content={"image_url": f"/api/artifacts/{image_path}"})

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
