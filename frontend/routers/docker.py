"""
Docker Router.

Endpoints for managing the underlying container infrastructure:
- Listing active containers
- Lifecycle control (start/stop/restart)
- Log streaming
"""

import json
from collections.abc import Generator

from docker import DockerClient
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse

from frontend.dependencies import get_docker_client
from frontend.models import (
    DockerContainerInfo,
    DockerStatsResponse,
)

router = APIRouter()
DOCKER_ERROR_MSG = "Docker not connected"


@router.get("/api/docker")
async def get_docker_stats(
    client: DockerClient = Depends(get_docker_client),
) -> DockerStatsResponse | dict[str, str]:
    """Get running container stats."""
    if not client:
        return {"error": DOCKER_ERROR_MSG}

    containers = []
    try:
        for c in client.containers.list():
            containers.append(
                DockerContainerInfo(
                    id=c.short_id,
                    name=c.name,
                    status=c.status,
                    image=c.image.tags[0] if c.image.tags else "unknown",
                )
            )
    except Exception as e:
        return {"error": str(e)}

    return DockerStatsResponse(containers=containers)


@router.post("/api/docker/{container_id}/{action}")
async def control_container(
    container_id: str, action: str, client: DockerClient = Depends(get_docker_client)
) -> dict:
    """Control a docker container."""
    if not client:
        raise HTTPException(status_code=503, detail=DOCKER_ERROR_MSG)

    try:
        container = client.containers.get(container_id)
        if action == "start":
            container.start()
        elif action == "stop":
            container.stop()
        elif action == "restart":
            container.restart()
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        return {"status": "success", "action": action, "id": container_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/logs/{container_name}")
async def get_container_logs(
    container_name: str,
    tail: int = 50,
    client: DockerClient = Depends(get_docker_client),
) -> dict:
    """Get a snapshot of container logs."""
    if not client:
        raise HTTPException(status_code=503, detail=DOCKER_ERROR_MSG)

    try:
        container = client.containers.get(container_name)
        # Get logs as bytes
        logs_bytes = container.logs(tail=tail, stdout=True, stderr=True)
        # Decode
        logs_text = logs_bytes.decode("utf-8", errors="replace")
        return {"logs": logs_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/logs/{container_name}/stream")
async def stream_logs_sse(
    container_name: str, client: DockerClient = Depends(get_docker_client)
) -> Response:
    """Stream logs from a container using Server-Sent Events (SSE)."""
    if not client:
        raise HTTPException(status_code=503, detail=DOCKER_ERROR_MSG)

    try:
        container = client.containers.get(container_name)
    except Exception as e:
        return JSONResponse(
            status_code=404, content={"detail": f"Container not found: {e}"}
        )

    def sse_generator() -> Generator[str, None, None]:
        yield f"event: status\ndata: {json.dumps({'status': 'connected', 'container': container_name})}\n\n"

        try:
            # tails=200 for initial context, follow=True for live updates
            log_stream = container.logs(stream=True, tail=200, follow=True)

            for line in log_stream:
                # Docker returns bytes, decode carefully
                text = line.decode("utf-8", errors="replace")
                # SSE format: "data: <payload>\n\n"
                # JSON encode the payload to handle newlines safeley
                payload = json.dumps(
                    {"text": text, "timestamp": "now"}
                )  # timestamp could be real if we parsed it
                yield f"data: {payload}\n\n"

        except Exception as e:
            error_payload = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_payload}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx no-buffer
        },
    )
