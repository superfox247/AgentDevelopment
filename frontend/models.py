"""
Dashboard Data Models.

Pydantic schemas used for API Request/Response bodies in the Dashboard Backend.
Covers Docker stats, Agent metadata, and Test/Verification payloads.
"""

from pydantic import BaseModel
class ModelInfo(BaseModel):
    name: str
    display_name: str
    description: str
    input_token_limit: int
    output_token_limit: int
    top_p: float | None = None
    temperature: float | None = None


class DockerContainerInfo(BaseModel):
    """Schema for a running Docker container."""

    id: str
    name: str
    status: str
    image: str


class DockerStatsResponse(BaseModel):
    containers: list[DockerContainerInfo]


class SystemFixResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str


class AgentInfo(BaseModel):
    domain: str
    name: str
    path: str


class SkillInfo(BaseModel):
    name: str
    path: str


class AgentsResponse(BaseModel):
    agents: list[AgentInfo]


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class SkillsResponse(BaseModel):
    skills: list[SkillInfo]


class ArtifactInfo(BaseModel):
    name: str
    path: str
    type: str


class ArtifactsResponse(BaseModel):
    artifacts: list[ArtifactInfo]


# --- Request Models ---


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default-session"


class ImageRequest(BaseModel):
    prompt: str
    model: str = "models/gemini-1.5-flash"
    session_id: str = "default-image-session"


class VerificationRequest(BaseModel):
    test_name: str = "content_engine"


class ContainerAction(BaseModel):
    action: str = "restart"  # start, stop, restart


class TelemetryRequest(BaseModel):
    """Frontend telemetry log."""

    level: str = "error"
    message: str
    component: str | None = None
    stack: str | None = None
    url: str | None = None
    user_agent: str | None = None
