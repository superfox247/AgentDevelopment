
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass, field
from typing import Any

# --- Docker Fakes ---

class FakeImage:
    def __init__(self, tags: list[str] = ["image:latest"]):
        self.tags = tags

class FakeContainer:
    def __init__(self, id: str, name: str, status: str = "running"):
        self.short_id = id
        self.name = name
        self.status = status
        self.image = FakeImage()
        self._logs: bytes = b"fake logs\n"

    def start(self) -> None:
        self.status = "running"

    def stop(self) -> None:
        self.status = "exited"

    def restart(self) -> None:
        self.status = "running"

    def logs(self, stream: bool = False, tail: str | int = "all", follow: bool = False, stdout: bool = True, stderr: bool = True) -> bytes | Iterator[bytes]:
        if stream:
            # Return an iterator for streaming
            return iter([self._logs])
        return self._logs

class FakeContainerCollection:
    def __init__(self, containers: list[FakeContainer]):
        self._containers = {c.short_id: c for c in containers}
        # Also index by name for convenience in tests (simulating Docker's loose get)
        self._by_name = {c.name: c for c in containers}

    def list(self) -> list[FakeContainer]:
        return list(self._containers.values())

    def get(self, container_id: str) -> FakeContainer:
        # Docker client .get() can often work with name or ID
        if container_id in self._containers:
            return self._containers[container_id]
        if container_id in self._by_name:
            return self._by_name[container_id]
        raise Exception(f"Container {container_id} not found")

class FakeDockerClient:
    def __init__(self) -> None:
        self._containers = [
            FakeContainer(id="12345678", name="course_creator-orchestrator", status="running")
        ]
        self.containers = FakeContainerCollection(self._containers)

# --- ADK Fakes ---

@dataclass
class FakeResponse:
    content: str | None = None

@dataclass
class FakeFunctionResponse:
    name: str
    response: dict[str, Any]

@dataclass
class FakePart:
    function_response: FakeFunctionResponse | None = None

@dataclass
class FakeContent:
    parts: list[FakePart] = field(default_factory=list)

@dataclass
class FakeToolResponse:
    name: str
    response: dict[str, Any] | str

@dataclass
class FakeEvent:
    """Simulates a Google GenAI Event."""
    response: FakeResponse | None = None
    tool_response: list[FakeToolResponse] | None = None
    content: FakeContent | None = None

class FakeSessionService:
    async def create_session(self, app_name: str, user_id: str, session_id: str) -> None:
        pass

class FakeRunner:
    def __init__(self) -> None:
        self.session_service = FakeSessionService()
        self.events: list[FakeEvent] = []

    def set_mock_events(self, events: list[FakeEvent]) -> None:
        """Helper to set up the sequence of events the runner 'generates'."""
        self.events = events

    async def run_async(self, user_id: str, session_id: str, new_message: Any) -> AsyncIterator[FakeEvent]:
        # Consume the generator to simulate async work if needed, mostly just yield
        for event in self.events:
            yield event
