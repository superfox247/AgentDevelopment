"""
Docker Router.

Endpoints for managing the underlying container infrastructure:
- Listing active containers
- Lifecycle control (start/stop/restart)
- Log streaming
"""

import json
import logging
from collections.abc import Generator

from docker import DockerClient
from docker.errors import APIError
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from dashboard_api.dependencies import get_docker_client
from dashboard_api.models import (
    ContainerControlResponse,
    ContainerLogsResponse,
    DockerContainerInfo,
    DockerStatsResponse,
)
from dashboard_api.utils.docker_utils import (
    ContainerAction,
    execute_container_action,
    get_container_safe,
    validate_docker_client,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/docker")
async def get_docker_stats(
    client: DockerClient = Depends(get_docker_client),
) -> DockerStatsResponse:
    """Get running container stats."""
    validate_docker_client(client)

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
    except APIError as e:
        logger.error(f"Docker API error listing containers: {e}")
        raise HTTPException(
            status_code=503, detail=f"Docker API error: {e.explanation}"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error listing containers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to list containers: {e!s}"
        ) from e

    return DockerStatsResponse(containers=containers)


@router.post("/api/docker/{container_id}/{action}")
async def control_container(
    container_id: str,
    action: ContainerAction,
    client: DockerClient = Depends(get_docker_client),
) -> ContainerControlResponse:
    """Control a docker container."""
    validate_docker_client(client)

    container = get_container_safe(client, container_id)
    execute_container_action(container, action)

    return ContainerControlResponse(
        status="success", action=action.value, id=container_id
    )


@router.get("/api/logs/{container_name}")
async def get_container_logs(
    container_name: str,
    tail: int = Query(default=50, ge=1, le=10000, description="Number of log lines to retrieve"),
    client: DockerClient = Depends(get_docker_client),
) -> ContainerLogsResponse:
    """Get a snapshot of container logs."""
    validate_docker_client(client)
    container = get_container_safe(client, container_name)

    try:
        # Get logs as bytes
        logs_bytes = container.logs(tail=tail, stdout=True, stderr=True)
        # Decode
        logs_text = logs_bytes.decode("utf-8", errors="replace")
        return ContainerLogsResponse(logs=logs_text)
    except APIError as e:
        logger.error(f"Docker API error reading logs: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to read logs: {e.explanation}"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error reading logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}") from e


@router.get("/api/logs/{container_name}/stream")
async def stream_logs_sse(
    container_name: str, client: DockerClient = Depends(get_docker_client)
) -> Response:
    """Stream logs from a container using Server-Sent Events (SSE)."""
    validate_docker_client(client)

    try:
        container = get_container_safe(client, container_name)
    except HTTPException:
        # Re-raise HTTPException as JSONResponse for SSE endpoint
        raise

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
