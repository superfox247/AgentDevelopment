"""
Dashboard Data Models.

Pydantic schemas used for API Request/Response bodies in the Dashboard Backend.
Covers Docker stats, Agent metadata, and Test/Verification payloads.
"""

from typing import Any

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


class ContainerControlResponse(BaseModel):
    """Response for container control operations."""

    status: str
    action: str
    id: str


class ContainerLogsResponse(BaseModel):
    """Response for container logs."""

    logs: str


class SystemFixResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str


class AgentInfo(BaseModel):
    domain: str
    name: str
    path: str


class AgentMetadata(BaseModel):
    """Rich metadata for an agent including description, model, and server status."""

    name: str
    path: str
    description: str = ""
    model: str = ""
    has_server: bool = False


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


class MessageResponse(BaseModel):
    response: str


# --- Request Models ---


class MessageRequest(BaseModel):
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


class TelemetryResponse(BaseModel):
    """Response for telemetry logging."""

    status: str


class SystemStatus(BaseModel):
    """System status information.

    Note: Only includes the core system status. Agent-specific status
    should be queried via the /api/agents endpoint for dynamic discovery.
    """

    status: str


class VerificationResponse(BaseModel):
    """Response for verification runs."""

    success: bool
    message: str
    details: dict[str, str] | None = None


class QuotaDetailResponse(BaseModel):
    """Response for quota detail information."""

    name: str
    metric: str
    quota_id: str
    refresh_interval: str
    is_precise: bool
    container_type: str
    dimensions: list[dict[str, Any]]


class MetricTimeseriesResponse(BaseModel):
    """Response for metric time series data."""

    metric_name: str
    hours: int
    data_points: list[dict[str, Any]]


# --- Event Models for Streaming ---


class BaseEvent(BaseModel):
    """Base class for streaming events."""

    type: str
    agent: str | None = None
    text: str


class ToolUseEvent(BaseEvent):
    """Event for tool usage."""

    type: str = "tool_use"
    tool: str


class AgentThoughtEvent(BaseEvent):
    """Event for agent thoughts/messages."""

    type: str = "agent_thought"
    agent: str


class UserMessageEvent(BaseEvent):
    """Event for user messages."""

    type: str = "user_message"


class SystemSignalEvent(BaseModel):
    """Event for system signals."""

    type: str = "system_signal"
    signal: str
    text: str
