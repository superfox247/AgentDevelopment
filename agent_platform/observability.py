import logging
import os

from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from phoenix.otel import register

logger = logging.getLogger(__name__)

def setup_telemetry(agent_name: str) -> None:
    """
    Configures OpenTelemetry tracing with Arize Phoenix and Google ADK instrumentation.

    Args:
        agent_name: The name of the agent service (e.g., 'course-creation-researcher')
    """
    if os.environ.get("OTEL_SDK_DISABLED", "false").lower() == "true":
        logger.info(f"[{agent_name}] Telemetry disabled via OTEL_SDK_DISABLED.")
        return

    # 1. Instrument ADK (Automatic)
    GoogleADKInstrumentor().instrument()

    # 2. Instrument Google GenAI (Optional, if installed)
    # This captures token counts and costs from the Gemini SDK
    try:
        from opentelemetry.instrumentation.google_genai import (
            GoogleGenerativeAIInstrumentor,
        )
        GoogleGenerativeAIInstrumentor().instrument()
        logger.info(f"[{agent_name}] Google GenAI instrumentation enabled.")
    except ImportError:
        logger.warning(f"[{agent_name}] Google GenAI instrumentation NOT found. Token costs may be missing.")

    # 3. Register Phoenix Exporter
    # Default: http://localhost:6006/v1/traces (local) or http://phoenix:6006/v1/traces (docker)
    # The PHOENIX_COLLECTOR_ENDPOINT env var takes precedence.
    endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:6006/v1/traces")

    register(
        project_name=agent_name,
        endpoint=endpoint
    )
    logger.info(f"[{agent_name}] Telemetry initialized. Endpoint: {endpoint}")
