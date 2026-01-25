"""
Agent Router.

Endpoints for exploring and interacting with the Agent Ecosystem:
- Listing available agents/domains
- Viewing agent configuration/skills
- Direct chat/interaction with specific agents
"""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from frontend.dependencies import ROOT_DIR
from frontend.models import (
    AgentInfo,
    AgentsResponse,
    SkillInfo,
    SkillsResponse,
)
from frontend.utils.agent_registry import AgentRegistry

router = APIRouter()
logger = logging.getLogger(__name__)

# Agent registry for dynamic discovery
_agent_registry = AgentRegistry(ROOT_DIR / "agents")

# --- Endpoints ---


@router.get("/api/agents")
async def list_agents() -> AgentsResponse:
    """List available agents in the agents directory.

    Dynamically discovers agents by scanning the agents/ directory
    and extracting metadata from agent.py files.
    """
    # Use registry for dynamic discovery
    metadata_list = _agent_registry.get_agents(refresh=True)

    agents = [
        AgentInfo(
            domain="",  # No domain structure currently
            name=metadata.name,
            path=str(metadata.path.relative_to(ROOT_DIR)),
        )
        for metadata in metadata_list
    ]

    return AgentsResponse(agents=agents)


@router.get("/api/agents/{name}/metadata")
async def get_agent_metadata(name: str):
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


