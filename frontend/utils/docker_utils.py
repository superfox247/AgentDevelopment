"""
Docker utility functions for error handling and container operations.

Provides reusable functions for common Docker operations with consistent error handling.
"""

import logging
from enum import Enum

from docker import DockerClient
from docker.errors import APIError, ContainerError, NotFound
from docker.models.containers import Container
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ContainerAction(str, Enum):
    """Valid container actions."""

    START = "start"
    STOP = "stop"
    RESTART = "restart"


def get_container_safe(client: DockerClient, container_id: str) -> Container:
    """
    Safely retrieve a Docker container, handling common errors.

    Args:
        client: The Docker client instance.
        container_id: The container ID or name.

    Returns:
        The Docker container object.

    Raises:
        HTTPException: If the container is not found or Docker API error occurs.
    """
    try:
        return client.containers.get(container_id)
    except NotFound:
        raise HTTPException(
            status_code=404, detail=f"Container '{container_id}' not found"
        ) from None
    except APIError as e:
        logger.error(f"Docker API error getting container '{container_id}': {e}")
        raise HTTPException(
            status_code=503, detail=f"Docker API error: {e.explanation}"
        ) from e


def execute_container_action(container: Container, action: ContainerAction) -> None:
    """
    Execute a container action (start, stop, restart) with error handling.

    Args:
        container: The Docker container object.
        action: The action to perform.

    Raises:
        HTTPException: If the action fails or is invalid.
    """
    try:
        if action == ContainerAction.START:
            container.start()
        elif action == ContainerAction.STOP:
            container.stop()
        elif action == ContainerAction.RESTART:
            container.restart()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action '{action}'. Valid actions: start, stop, restart",
            )
    except ContainerError as e:
        logger.error(f"Container error during {action}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Container operation failed: {e.stderr}"
        ) from e
    except APIError as e:
        logger.error(f"Docker API error during {action}: {e}")
        raise HTTPException(
            status_code=503, detail=f"Docker API error: {e.explanation}"
        ) from e


def validate_docker_client(client: DockerClient | None) -> None:
    """
    Validate that a Docker client is available.

    Args:
        client: The Docker client instance or None.

    Raises:
        HTTPException: If the client is None (Docker not connected).
    """
    if not client:
        raise HTTPException(status_code=503, detail="Docker not connected")
