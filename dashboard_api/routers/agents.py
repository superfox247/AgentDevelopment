"""
Agent Router.

Endpoints for exploring and interacting with the Agent Ecosystem:
- Listing available agents/domains
- Viewing agent configuration/skills
- Direct chat/interaction with specific agents
"""

import importlib
import logging
from typing import Any, cast
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from google.adk.apps import App
from google.adk.artifacts.file_artifact_service import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from dashboard_api.dependencies import ROOT_DIR
from dashboard_api.models import (
    AgentInfo,
    AgentsResponse,
    MessageRequest,
    MessageResponse,
    SkillInfo,
    SkillsResponse,
)
from dashboard_api.utils.agent_registry import AgentRegistry

router = APIRouter()
logger = logging.getLogger(__name__)

# Agent registry for dynamic discovery
_agent_registry = AgentRegistry(ROOT_DIR / "agents")

# --- Endpoints ---


@router.post("/api/chat/{name}")
async def chat_with_agent(name: str, message: MessageRequest) -> MessageResponse:
    """Chat with a specific agent."""
    agent_metadata = _agent_registry.get_agent(name)
    if not agent_metadata:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    # Dynamically import the agent's root_agent from its agent.py
    # Try importing as a module first to support relative imports
    try:
        # Assuming standard structure: agents.<name>.agent
        module_name = f"agents.{name}.agent"
        agent_module = importlib.import_module(module_name)
    except ImportError as err:
        # Fallback to file-based loading (might fail with relative imports)
        logger.warning(f"Could not import {name} as module, falling back to file load")
        spec = importlib.util.spec_from_file_location(
            "agent_module", agent_metadata.path / "agent.py"
        )
        if spec is None or spec.loader is None:
            raise HTTPException(
                status_code=500, detail=f"Could not load agent module for '{name}'"
            ) from err
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)

    # Assuming 'root_agent' is the entry point in agent.py
    root_agent = agent_module.root_agent

    # Create a runner for the agent
    runner = Runner(
        app=App(name=name, root_agent=root_agent),
        artifact_service=FileArtifactService(
            root_dir=agent_metadata.path / "artifacts"
        ),
        session_service=InMemorySessionService(),
    )

    # Process the message stream and return the final text response.
    response_text = ""
    async for event in runner.run_async(
        user_id="dashboard-user",
        session_id=f"{name}-{uuid4()}",
        new_message=cast(Any, message.message),
    ):
        if hasattr(event, "is_final_response") and not event.is_final_response():
            continue
        if (
            hasattr(event, "content")
            and event.content
            and getattr(event.content, "parts", None)
        ):
            first_part = event.content.parts[0]
            if hasattr(first_part, "text") and first_part.text:
                response_text = str(first_part.text)
                continue
        if hasattr(event, "text") and event.text:
            response_text = str(event.text)
            continue
        response_text = str(event)

    return MessageResponse(response=response_text)


@router.get("/api/agents")
async def list_agents() -> AgentsResponse:
    """List available agents in the agents directory.

    Dynamically discovers agents by scanning the agents/ directory
    and extracting metadata from agent.py files.
    """
    # Use registry for dynamic discovery
    metadata_list = _agent_registry.get_agents(refresh=True)

    agents = []
    for metadata in metadata_list:
        try:
            path = str(metadata.path.relative_to(ROOT_DIR))
        except ValueError:
            # Path is not relative to ROOT_DIR (e.g., in tests with temp dirs)
            path = str(metadata.path)
        agents.append(
            AgentInfo(
                domain="",  # No domain structure currently
                name=metadata.name,
                path=path,
            )
        )

    return AgentsResponse(agents=agents)


@router.get("/api/agents/{name}/metadata")
async def get_agent_metadata(name: str) -> dict[str, Any]:
    """Get metadata for a specific agent (description, model, etc.)."""
    agent = _agent_registry.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    return agent.to_dict()


@router.get("/api/agents/{name}")
async def get_agent_config(name: str) -> FileResponse:
    """Get the agent.py file for a specific agent."""
    agent = _agent_registry.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    agent_py = agent.path / "agent.py"
    if not agent_py.exists():
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    return FileResponse(agent_py)


@router.get("/api/agents/{domain}/{name}")
async def get_agent_config_legacy(domain: str, name: str) -> FileResponse:
    """Legacy endpoint for backward compatibility.

    Supports old domain/name pattern but ignores domain.
    """
    return await get_agent_config(name)


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
