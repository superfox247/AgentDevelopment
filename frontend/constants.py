"""
Constants for the frontend application.

Centralizes service names, configuration values, and other constants.
"""

from enum import Enum


class ServiceName(str, Enum):
    """Service names used throughout the application."""

    ORCHESTRATOR = "orchestrator"
    CONTENT_BUILDER = "content_builder"
    IMAGE_GENERATOR = "image_generator"
    CUSTOMER_SERVICE = "customer_service"
    RESEARCHER = "researcher"
    JUDGE = "judge"


# Default values
DEFAULT_TAIL_LOGS = 50
DEFAULT_SESSION_ID = "default-session"
DEFAULT_IMAGE_SESSION_ID = "default-image-session"
