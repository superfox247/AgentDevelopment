from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PlatformConfig(BaseSettings):
    """Global Platform Configuration."""

    # Google Gemini (AI Studio)
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")

    # Telemetry
    phoenix_collector_endpoint: str = Field(
        default="http://phoenix:6006/v1/traces", alias="PHOENIX_COLLECTOR_ENDPOINT"
    )
    otel_service_name: str | None = Field(default=None, alias="OTEL_SERVICE_NAME")

    # Agent Defaults
    default_model: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra env vars
    )


def get_config() -> PlatformConfig:
    return PlatformConfig()


# Global Instance
config = get_config()
