import json
import os
import subprocess
from typing import Generator
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from google import genai
from agent_platform.config import PlatformConfig

from tools.dashboard.dependencies import (
    ARTIFACTS_DIR,
    ROOT_DIR,
    TEST_SCRIPT,
    get_docker_client,
    get_platform_config,
)
from tools.dashboard.models import (
    ArtifactInfo,
    ArtifactsResponse,
    ModelInfo,
    ModelsResponse,
    SystemFixResponse,
    VerificationRequest,
)

router = APIRouter()


@router.get("/api/status")
async def get_status(client=Depends(get_docker_client)) -> dict:
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


@router.post("/api/verify")
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


@router.get("/api/verify/stream")
async def run_verification_stream() -> StreamingResponse:
    """Stream verification output."""
    cmd = ["uv", "run", str(TEST_SCRIPT)]

    # Add domains/course_creator to PYTHONPATH so 'image_generator' package resolves
    env = os.environ.copy()
    course_creator_path = ROOT_DIR / "domains" / "course_creator"
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}{os.pathsep}{course_creator_path}"

    def process_generator() -> Generator[str, None, None]:
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


@router.get("/api/artifacts")
async def list_artifacts() -> ArtifactsResponse:
    """List generated artifacts."""
    if not ARTIFACTS_DIR.exists():
        return ArtifactsResponse(artifacts=[])

    files = []
    # Recursively find interesting files
    for path in ARTIFACTS_DIR.rglob("*"):
        if path.is_file() and path.suffix in [".md", ".png"]:
            files.append(
                ArtifactInfo(
                    name=path.name,
                    path=str(path.relative_to(ARTIFACTS_DIR)),
                    type="image" if path.suffix == ".png" else "document",
                )
            )
    return ArtifactsResponse(artifacts=files)


@router.get("/api/artifacts/{path:path}")
async def get_artifact(path: str) -> FileResponse:
    """Serve an artifact."""
    file_path = ARTIFACTS_DIR / path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(file_path)


@router.get("/api/benchmark/stream")
async def run_benchmark_stream() -> StreamingResponse:
    """Stream benchmark output."""
    cmd = ["uv", "run", "tools/benchmarks/benchmark_models.py"]

    # Add env if needed, mostly just PYTHONPATH to find agent_platform
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}{os.pathsep}{ROOT_DIR!s}"
    env["PYTHONIOENCODING"] = "utf-8"

    def process_generator() -> Generator[str, None, None]:
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


@router.get("/api/models")
async def list_models(config: PlatformConfig = Depends(get_platform_config)) -> ModelsResponse | dict[str, str]:
    """List available Gemini models."""
    try:
        client = genai.Client(api_key=config.gemini_api_key)
        all_models = list(client.models.list())

        # Filter for recent Gemini models
        models = []
        for m in all_models:
            if (
                m.name
                and "gemini" in m.name
                and "vision" not in m.name
                and "legacy" not in m.name
            ):
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
        model_list = [
            ModelInfo(
                name=str(m.get("name") or ""),
                display_name=str(m.get("display_name") or ""),
                description=str(m.get("description") or ""),
                input_token_limit=int(m.get("input_token_limit") or 0),
                output_token_limit=int(m.get("output_token_limit") or 0),
                top_p=float(m["top_p"]) if m.get("top_p") is not None else None,  # type: ignore
                temperature=float(m["temperature"])  # type: ignore
                if m.get("temperature") is not None
                else None,
            )
            for m in models
        ]
        return ModelsResponse(models=model_list)
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {"error": str(e)}


@router.post("/api/system/fix")
async def run_system_fix(req: dict | None = None) -> SystemFixResponse:
    """Run system auto-fix (debug_system --fix)."""
    cmd = ["uv", "run", ".agent/skills/debug_system/debug_system.py", "--fix"]
    try:
        # Run process
        result = subprocess.run(
            cmd,
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        return SystemFixResponse(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
