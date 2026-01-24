"""
Platform configuration and environment management.

Handles:
- Loading environment variables (dotenv)
- Standardizing API keys (GEMINI -> GOOGLE)
- Global Pydantic settings definition
"""


from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load env vars from .env file into os.environ
load_dotenv()

# Standardize: Ensure libraries expecting GOOGLE_API_KEY find it if we only have GEMINI_API_KEY
# (Removed to avoid SDK warning: "Both GOOGLE_API_KEY and GEMINI_API_KEY are set")
# We rely on GEMINI_API_KEY explicitly in our PlatformConfig.

class PlatformConfig(BaseSettings):
    """Global Platform Configuration."""

    # Google Gemini (AI Studio)
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")

    # Telemetry
    phoenix_collector_endpoint: str = Field(
        default="http://phoenix:6006/v1/traces", alias="PHOENIX_COLLECTOR_ENDPOINT"
    )
    otel_service_name: str | None = Field(default=None, alias="OTEL_SERVICE_NAME")

    # Agent Defaults - use Flash models for high usage limits
    default_model: str = "models/gemini-2.0-flash"
    default_image_model: str = "models/gemini-2.0-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra env vars
    )


def get_config() -> PlatformConfig:
    """Returns the global platform configuration singleton."""
    return PlatformConfig()


# Global Instance
config = get_config()
