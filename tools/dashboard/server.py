import json
import os
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).parent.parent.parent
# Ensure root is in path for imports
import sys

sys.path.append(str(ROOT_DIR))  # noqa: E402

ARTIFACTS_DIR = ROOT_DIR / "artifacts"
TEST_SCRIPT = ROOT_DIR / "tests" / "evaluation" / "test_content_engine.py"

from google import genai
from google.adk.artifacts import FileArtifactService
from google.adk.events import Event

# --- Customer Service Agent Setup ---
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent_platform.config import PlatformConfig  # noqa: E402
from domains.course_creator.customer_service.agent import app as customer_service_app  # noqa: E402

customer_service_runner = Runner(
    app=customer_service_app,
    artifact_service=FileArtifactService(root_dir=str(ARTIFACTS_DIR)),
    session_service=InMemorySessionService(),
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default-session"


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


import docker

client = None
try:
    client = docker.from_env()
except Exception as e:
    print(f"Warning: Docker client invalid: {e}")


class VerificationRequest(BaseModel):
    test_name: str = "content_engine"


@app.get("/api/docker")
async def get_docker_stats() -> list[dict] | dict:
    """Get running container stats."""
    if not client:
        return {"error": "Docker not connected"}

    containers = []
    try:
        for c in client.containers.list():
            containers.append(
                {
                    "id": c.short_id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                }
            )
    except Exception as e:
        return {"error": str(e)}

    return containers


@app.get("/api/status")
async def get_status() -> dict:
    """Checks the status of the infrastructure."""
    if not client:
        return {
            "status": "offline",
            "orchestrator": "unknown",
            "content_builder": "unknown",
            "image_generator": "unknown",
            "customer_service": "unknown",
        }

    status = {
        "status": "online",
        "orchestrator": "offline",
        "content_builder": "offline",
        "image_generator": "offline",
        "customer_service": "offline",
    }

    try:
        containers = client.containers.list()
        for c in containers:
            name = c.name.lower()
            state = "online" if c.status == "running" else "offline"

            # Match course_creator-orchestrator
            if "orchestrator" in name:
                status["orchestrator"] = state
            elif "content" in name and "builder" in name:
                status["content_builder"] = state
            elif "image" in name or "vision" in name:
                status["image_generator"] = state
            elif "customer" in name:
                status["customer_service"] = state

    except Exception as e:
        print(f"Error checking containers: {e}")
        status["status"] = "error"

    return status


@app.post("/api/verify")
async def run_verification(req: VerificationRequest) -> dict:
    """Trigger a verification test."""
    if req.test_name != "content_engine":
        raise HTTPException(status_code=400, detail="Unknown test name")

    cmd = ["uv", "run", str(TEST_SCRIPT)]

    try:
        # Run process
        # For simplicity, we wait for completion. Streaming is better but harder to implement quickly.
        result = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/logs/{container_name}")
async def stream_logs(container_name: str) -> StreamingResponse | JSONResponse:
    """Stream logs from a container."""
    if not client:
        raise HTTPException(status_code=503, detail="Docker not connected")

    try:
        # Check if container exists first to give better error
        container = client.containers.get(container_name)

        def log_generator():
            # Get logs. stream=True returns a generator.
            try:
                # Docker SDK for python's logs() with stream=True returns bytes generator
                yield from container.logs(stream=True, tail=100, follow=True)
            except Exception as e:
                yield f"Error reading logs: {e}\n".encode()

        return StreamingResponse(log_generator(), media_type="text/plain")
    except Exception as e:
        print(f"Error streaming logs: {e}")
        # If container not found or other error
        return JSONResponse(status_code=404, content={"detail": str(e)})


@app.get("/api/verify/stream")
async def run_verification_stream() -> StreamingResponse:
    """Stream verification output."""
    cmd = ["uv", "run", str(TEST_SCRIPT)]

    # Add domains/course_creator to PYTHONPATH so 'image_generator' package resolves
    env = os.environ.copy()
    course_creator_path = ROOT_DIR / "domains" / "course_creator"
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}{os.pathsep}{course_creator_path}"

    def process_generator():
        process = subprocess.Popen(
            cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            env=env,
        )

        if process.stdout:
            yield from process.stdout

        process.wait()
        if process.returncode == 0:
            yield "\n[SUCCESS] Verification Complete\n"
        else:
            yield f"\n[FAILURE] Process exited with code {process.returncode}\n"

    return StreamingResponse(process_generator(), media_type="text/plain")


@app.get("/api/artifacts")
async def list_artifacts() -> list[dict]:
    """List generated artifacts."""
    if not ARTIFACTS_DIR.exists():
        return []

    files = []
    # Recursively find interesting files
    for path in ARTIFACTS_DIR.rglob("*"):
        if path.is_file() and path.suffix in [".md", ".png"]:
            files.append(
                {
                    "name": path.name,
                    "path": str(path.relative_to(ARTIFACTS_DIR)),
                    "type": "image" if path.suffix == ".png" else "document",
                }
            )
    return files


@app.get("/api/artifacts/{path:path}")
async def get_artifact(path: str) -> FileResponse:
    """Serve an artifact."""
    file_path = ARTIFACTS_DIR / path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(file_path)


@app.get("/api/benchmark/stream")
async def run_benchmark_stream() -> StreamingResponse:
    """Stream benchmark output."""
    cmd = ["uv", "run", "benchmark_models.py"]

    # Add env if needed, mostly just PYTHONPATH to find agent_platform
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}{os.pathsep}{ROOT_DIR!s}"
    env["PYTHONIOENCODING"] = "utf-8"

    def process_generator():
        process = subprocess.Popen(
            cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,  # Line buffered
            env=env,
        )

        if process.stdout:
            yield from process.stdout

        process.wait()
        if process.returncode == 0:
            yield "\n[SUCCESS] Benchmark Complete\n"
        else:
            yield f"\n[FAILURE] Process exited with code {process.returncode}\n"

    return StreamingResponse(process_generator(), media_type="text/plain")


@app.get("/api/models")
async def list_models() -> list[dict] | dict:
    """List available Gemini models."""
    try:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)
        all_models = list(client.models.list())

        # Filter for recent Gemini models
        models = []
        for m in all_models:
            if m.name and "gemini" in m.name and "vision" not in m.name and "legacy" not in m.name:
                models.append(
                    {
                        "name": m.name,
                        "display_name": m.display_name,
                        "description": m.description,
                        "input_token_limit": m.input_token_limit,
                        "output_token_limit": m.output_token_limit,
                        "top_p": m.top_p,
                        "temperature": m.temperature,
                    }
                )

        # Sort by name
        models.sort(key=lambda x: str(x.get("name", "")), reverse=True)
        return models
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {"error": str(e)}


@app.post("/api/chat/customer_service")
async def chat_customer_service(req: ChatRequest) -> StreamingResponse:
    """Chat with the Customer Service Agent."""
    from google.genai.types import Content, Part

    # Ensure session exists
    try:
        await customer_service_runner.session_service.create_session(
            app_name="customer_service",
            user_id="dashboard-user",
            session_id=req.session_id,
        )
    except Exception:
        pass  # Session might already exist

    msg = Content(role="user", parts=[Part.from_text(text=req.message)])

    async def event_generator():
        final_intent = None

        async for event in customer_service_runner.run_async(
            user_id="dashboard-user", session_id=req.session_id, new_message=msg
        ):
            data = _extract_event_data(event)
            if data:
                yield json.dumps(data) + "\n"

            # Check for intent in the final response (CustomerServiceResponse)
            # This logic mimics the `_save_output` callback check but strictly for the UI signal
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

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010)
