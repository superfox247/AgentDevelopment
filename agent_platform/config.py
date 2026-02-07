"""
Platform configuration and environment management.

Handles:
- Loading environment variables (dotenv)
- Standardizing API keys (GEMINI -> GOOGLE)
- Global Pydantic settings definition
"""

import os
from typing import cast

from dotenv import load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env into os.environ; never override existing vars (e.g. GEMINI_API_KEY from system).
load_dotenv(override=False)

# Standardize: Ensure libraries expecting GOOGLE_API_KEY find it if we only have GEMINI_API_KEY
# Only set GOOGLE_API_KEY if:
# 1. It's not already set (to avoid SDK warning about both being set)
# 2. We're using AI Studio (not Vertex AI)
# 3. GEMINI_API_KEY is available

vertex_ai_setting = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").strip().lower()
use_vertex_ai = vertex_ai_setting in ("true", "1", "yes")
if (
    not use_vertex_ai
    and not os.getenv("GOOGLE_API_KEY")
    and os.getenv("GEMINI_API_KEY")
):
    gemini_api_key = cast(str, os.getenv("GEMINI_API_KEY"))
    os.environ["GOOGLE_API_KEY"] = gemini_api_key

# Avoid repetitive SDK warnings when both keys are set to the same value.
# Keep GOOGLE_API_KEY as the canonical env var expected by Google SDKs.
if (
    not use_vertex_ai
    and os.getenv("GOOGLE_API_KEY")
    and os.getenv("GEMINI_API_KEY") == os.getenv("GOOGLE_API_KEY")
):
    os.environ.pop("GEMINI_API_KEY", None)


class PlatformConfig(BaseSettings):
    """Global Platform Configuration."""

    # Google Gemini (AI Studio)
    gemini_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    )

    # Telemetry
    phoenix_collector_endpoint: str = Field(
        default="http://phoenix:6006/v1/traces", alias="PHOENIX_COLLECTOR_ENDPOINT"
    )
    otel_service_name: str | None = Field(default=None, alias="OTEL_SERVICE_NAME")

    # Agent Defaults - Configurable via environment
    default_model: str = Field(default="models/gemini-2.0-flash", alias="DEFAULT_MODEL")
    default_image_model: str = Field(
        default="models/gemini-2.0-flash", alias="DEFAULT_IMAGE_MODEL"
    )

    # Environment
    env: str = Field(default="development", alias="ENV")

    # Rate Limiting
    rate_limit: str = Field(default="100/minute", alias="RATE_LIMIT")
    rate_limit_storage: str = Field(default="memory://", alias="RATE_LIMIT_STORAGE")
    rate_limit_disabled: bool = Field(default=False, alias="RATE_LIMIT_DISABLED")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:8000", alias="ALLOWED_ORIGINS"
    )

    # Telemetry
    otel_sdk_disabled: bool = Field(default=False, alias="OTEL_SDK_DISABLED")

    # Server Configuration
    agent_host: str = Field(default="localhost", alias="AGENT_HOST")
    port: int = Field(default=8000, alias="PORT")

    # Authentication
    auth_disabled: bool = Field(default=False, alias="AUTH_DISABLED")
    agent_api_key: str | None = Field(default=None, alias="AGENT_API_KEY")

    # Context Engine (Neo4j & Qdrant)
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra env vars
    )

    def validate_required(self) -> None:
        """Validate that required configuration is present."""
        env = self.env.lower()
        if env == "production":
            if not self.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY or GOOGLE_API_KEY is required in production environment"
                )
            if not self.auth_disabled and not self.agent_api_key:
                raise ValueError(
                    "AGENT_API_KEY is required in production when authentication is enabled"
                )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env.lower() == "production"


def get_config() -> PlatformConfig:
    """Returns the global platform configuration singleton."""
    config = PlatformConfig()
    # Validate configuration on initialization
    try:
        config.validate_required()
    except ValueError as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Configuration validation failed: {e}")
        # In development, warn but don't fail
        if config.env.lower() == "production":
            raise
        logger.warning("Continuing with invalid configuration in development mode")
    return config


# Global Instance
config = get_config()
