from pydantic import BaseModel


class DockerContainerInfo(BaseModel):
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


class ModelInfo(BaseModel):
    name: str
    display_name: str
    description: str
    input_token_limit: int
    output_token_limit: int
    top_p: float | None = None
    temperature: float | None = None


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
