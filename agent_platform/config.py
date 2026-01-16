import os

from pydantic import Field
from pydantic_settings import BaseSettings


class PlatformConfig(BaseSettings):
    """Global Platform Configuration."""

    # Google Cloud
    google_cloud_project: str | None = Field(default=None, alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION")
    google_genai_use_vertexai: bool = Field(default=True, alias="GOOGLE_GENAI_USE_VERTEXAI")

    # Telemetry
    phoenix_collector_endpoint: str = Field(default="http://phoenix:6006/v1/traces", alias="PHOENIX_COLLECTOR_ENDPOINT")
    otel_service_name: str | None = Field(default=None, alias="OTEL_SERVICE_NAME")

    # Agent Defaults
    default_model: str = "gemini-2.5-pro"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" # Allow extra env vars

def get_config() -> PlatformConfig:
    return PlatformConfig()

# Global Instance
config = get_config()

# Helper to ensure project_id is set (supports existing logic)
if not config.google_cloud_project:
    try:
        import google.auth
        _, project_id = google.auth.default()
        if project_id:
             os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        pass
