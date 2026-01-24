import asyncio

"""
System Router.

Endpoints for checking system health and infrastructure status:
- Health checks (backend, containers)
- Backend Log forwarding (frontend telemetry)
- Verification triggers (e2e tests)
"""

import logging
import os
import time
from collections.abc import AsyncGenerator
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from docker import DockerClient
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from google import genai

from agent_platform.config import PlatformConfig
from tools.dashboard.dependencies import (
    ARTIFACTS_DIR,
    ROOT_DIR,
    TEST_SCRIPT,
    get_docker_client,
    get_genai_client,
    get_platform_config,
)
from tools.dashboard.models import (
    ArtifactInfo,
    ArtifactsResponse,
    ModelInfo,
    ModelsResponse,
    SystemFixResponse,
    TelemetryRequest,
    VerificationRequest,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/telemetry/log")
async def log_frontend_telemetry(req: TelemetryRequest) -> dict:
    """Bridge for frontend errors to backend logs."""
    log_payload = {
        "component": "frontend",
        "ui_component": req.component,
        "url": req.url,
        "stack": req.stack,
        "user_agent": req.user_agent
    }

    if req.level.lower() == "error":
        logger.error(f"[Frontend] {req.message}", extra=log_payload)
    elif req.level.lower() in ["warn", "warning"]:
        logger.warning(f"[Frontend] {req.message}", extra=log_payload)
    else:
        logger.info(f"[Frontend] {req.message}", extra=log_payload)

    return {"status": "ok"}


@router.get("/api/status")
async def get_status(client: DockerClient = Depends(get_docker_client)) -> dict:
    """Checks the status of the infrastructure."""
    status = _get_default_status()
    
    # Update from Docker source if available
    if client:
        _update_from_docker(status, client)
    else:
        # If no client, we default to potentially offline unless found locally
        status["status"] = "offline"

    # Fallback to local ports (Option C)
    _update_from_local_ports(status)

    return status


def _get_default_status() -> dict:
    return {
        "status": "online", # Optimistic default, will be downgraded if critical items miss
        "orchestrator": "offline",
        "content_builder": "offline",
        "image_generator": "offline",
        "customer_service": "offline",
    }


def _update_from_docker(status: dict, client: DockerClient) -> None:
    try:
        containers = client.containers.list()
        for c in containers:
            name = c.name.lower()
            state = "online (docker)" if c.status == "running" else "offline"

            if "orchestrator" in name:
                status["orchestrator"] = state
            elif "content" in name and "builder" in name:
                status["content_builder"] = state
            elif "image" in name or "vision" in name:
                status["image_generator"] = state
            elif "customer" in name:
                status["customer_service"] = state
    except Exception as e:
        logger.warning(f"Error checking containers: {e}")
        status["status"] = "error"


def _update_from_local_ports(status: dict) -> None:
    # Option C: Fallback to local port checks for Dev Mode
    # If orchestrator is still offline, check port 8501
    if status.get("orchestrator") not in ["online", "online (docker)"]:
        if _is_port_open("127.0.0.1", 8501):
            status["orchestrator"] = "online (local)"
            # If we found it locally, update system status to online
            if status["status"] == "offline":
                 status["status"] = "online"


def _is_port_open(host: str, port: int) -> bool:
    """Checks if a local port is open (accepting connections)."""
    import socket
    try:
        with socket.create_connection((host, port), timeout=0.1):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


@router.post("/api/verify")
async def run_verification(req: VerificationRequest) -> dict:
    """Trigger a verification test."""
    if req.test_name != "content_engine":
        raise HTTPException(status_code=400, detail="Unknown test name")

    cmd = ["uv", "run", str(TEST_SCRIPT)]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(ROOT_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
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

    async def process_generator() -> AsyncGenerator[str, None]:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(ROOT_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env
        )

        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode()

        await process.wait()
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

    async def process_generator() -> AsyncGenerator[str, None]:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(ROOT_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env
        )

        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode()

        await process.wait()
        if process.returncode == 0:
            yield "\n[SUCCESS] Benchmark Complete\n"
        else:
            yield f"\n[FAILURE] Process exited with code {process.returncode}\n"

    return StreamingResponse(process_generator(), media_type="text/plain")


@router.get("/api/models")
async def list_models(client: genai.Client = Depends(get_genai_client)) -> ModelsResponse | dict[str, str]:
    """List available Gemini models."""
    try:
        all_models = list(client.models.list())

        model_list = _map_models(all_models)
        return ModelsResponse(models=model_list)
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {"error": str(e)}


def _map_models(all_models: list[Any]) -> list[ModelInfo]:
    """Maps GenAI model objects to Pydantic ModelInfo objects."""
    models_data = []
    for m in all_models:
        if _is_relevant_model(m):
            models_data.append(_create_model_info(m))

    # Sort by name
    models_data.sort(key=lambda x: str(x.name), reverse=True)
    return models_data


def _is_relevant_model(m: Any) -> bool:
    name = m.name or ""
    return (
        "gemini" in name
        and "vision" not in name
        and "legacy" not in name
    )


def _create_model_info(m: Any) -> ModelInfo:
    return ModelInfo(
        name=str(m.name or ""),
        display_name=str(m.display_name or ""),
        description=str(m.description or ""),
        input_token_limit=int(m.input_token_limit or 0),
        output_token_limit=int(m.output_token_limit or 0),
        top_p=float(m.top_p) if m.top_p is not None else None,
        temperature=float(m.temperature) if m.temperature is not None else None,
    )


@router.post("/api/system/fix")
async def run_system_fix(req: dict | None = None) -> SystemFixResponse:
    """Run system auto-fix (debug_system --fix)."""
    cmd = ["uv", "run", ".agent/skills/debug_system/debug_system.py", "--fix"]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(ROOT_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        return SystemFixResponse(
            success=process.returncode == 0,
            stdout=stdout.decode() if stdout else "",
            stderr=stderr.decode() if stderr else "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def _test_single_model(model_name: str, category: str, client: genai.Client) -> dict:
    """Helper to test a single model."""
    result = {
        "model": model_name,
        "category": category,
        "available": False,
        "functional": False,
        "error": None,
        "response_time_ms": None,
    }

    try:
        # First check if model exists
        client.models.get(model=model_name)
        result["available"] = True

        # Then try a simple call
        start = time.time()
        if "image" in model_name.lower() or "imagen" in model_name.lower():
            # For image models, just verify they exist (don't actually generate)
            result["functional"] = True
            result["response_time_ms"] = int((time.time() - start) * 1000)
        else:
            # For text models, do a quick test
            response = client.models.generate_content(
                model=model_name,
                contents="Say 'ok'",
            )
            result["functional"] = bool(response.candidates)
            result["response_time_ms"] = int((time.time() - start) * 1000)

    except Exception as e:
        error_str = str(e)
        result["error"] = error_str[:200]  # Truncate long errors

        # Classify the error
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            result["error_type"] = "rate_limited"
        elif "404" in error_str or "not found" in error_str.lower():
            result["error_type"] = "not_found"
        else:
            result["error_type"] = "unknown"

    return result


@router.get("/api/diagnostics/models")
async def diagnose_models(
    config: PlatformConfig = Depends(get_platform_config),
    client: genai.Client = Depends(get_genai_client),
) -> dict:
    """
    Test each configured model for availability and rate limit status.
    """
    # Models to test - grouped by category
    models_to_test = {
        "orchestration": [
            "models/gemini-2.5-pro",
            "models/gemini-2.0-flash",
            "models/gemini-2.5-flash",
        ],
        "image_generation": [
            "models/gemini-2.5-flash-image",
            "models/gemini-3-pro-image-preview",
            "models/imagen-4.0-generate-001",
            "models/imagen-4.0-fast-generate-001",
        ],
    }

    results: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "api_key_configured": bool(config.gemini_api_key),
        "categories": {},
    }

    if not config.gemini_api_key:
        results["error"] = "No API key configured"
        return results

    # client is already injected
    
    # Test all models in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for category, model_list in models_to_test.items():
            for model_name in model_list:
                future = executor.submit(_test_single_model, model_name, category, client)
                futures[future] = (model_name, category)

        for future in as_completed(futures):
            model_name, category = futures[future]
            try:
                model_result = future.result()
                if category not in results["categories"]:
                    results["categories"][category] = []
                results["categories"][category].append(model_result)
            except Exception as e:
                if category not in results["categories"]:
                    results["categories"][category] = []
                results["categories"][category].append({
                    "model": model_name,
                    "error": str(e),
                })

    # Summary stats
    all_models = []
    for category_results in results["categories"].values():
        all_models.extend(category_results)

    results["summary"] = {
        "total": len(all_models),
        "available": sum(1 for m in all_models if m.get("available")),
        "functional": sum(1 for m in all_models if m.get("functional")),
        "rate_limited": sum(1 for m in all_models if m.get("error_type") == "rate_limited"),
    }

    return results
