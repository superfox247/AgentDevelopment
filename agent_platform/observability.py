"""
Observability and Telemetry configuration.

Provides instrumentation for:
- OpenTelemetry (managing Traces/Spans)
- Arize Phoenix (Trace collection)
- Structured JSON logging
- Console alerts for critical errors
"""

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

    # 2. Instrument Logging (Standard 12-Factor)
    try:
        from opentelemetry.instrumentation.logging import LoggingInstrumentor

        # We manually set format, so set_logging_format=False to inject IDs but keep our formatter
        LoggingInstrumentor().instrument(set_logging_format=False)
        logger.info(f"[{agent_name}] Logging instrumentation enabled.")
    except ImportError:
        logger.warning(
            f"[{agent_name}] opentelemetry-instrumentation-logging not found."
        )

    # 3. Instrument Google GenAI (Optional)
    try:
        from opentelemetry.instrumentation.google_genai import (
            GoogleGenAiSdkInstrumentor,
        )

        GoogleGenAiSdkInstrumentor().instrument()
        logger.info(f"[{agent_name}] Google GenAI instrumentation enabled.")
    except ImportError:
        logger.warning(
            f"[{agent_name}] Google GenAI instrumentation NOT found. Token costs may be missing."
        )

    # 4. Register Phoenix Exporter
    # Priority: Env Var > 'phoenix' service > 'host.docker.internal' > 'localhost'
    endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")

    if not endpoint:
        import socket

        try:
            # 1. Try 'phoenix' (Standard Docker Service)
            socket.gethostbyname("phoenix")
            endpoint = "http://phoenix:6006/v1/traces"
        except socket.gaierror:
            try:
                # 2. Try 'host.docker.internal' (Docker Desktop / Gateway)
                socket.gethostbyname("host.docker.internal")
                endpoint = "http://host.docker.internal:6006/v1/traces"
            except socket.gaierror:
                # 3. Fallback to Localhost
                endpoint = "http://localhost:6006/v1/traces"

    register(project_name=agent_name, endpoint=endpoint)
    logger.info(f"[{agent_name}] Telemetry initialized. Endpoint: {endpoint}")

    # 5. Setup Logging Formatters (JSON for machine, Color for dev)
    setup_logging_format()


class JSONFormatter(logging.Formatter):
    """
    Standard 12-Factor JSON Formatter.
    Emits structured logs compatible with Cloud Logging and Phoenix.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record as a JSON string with trace context."""
        import json
        import time

        from opentelemetry import trace

        log_record = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "lineno": record.lineno,
        }

        # Inject Trace Context if available
        span = trace.get_current_span()
        if span != trace.INVALID_SPAN:
            ctx = span.get_span_context()
            log_record["trace_id"] = f"{ctx.trace_id:032x}"
            log_record["span_id"] = f"{ctx.span_id:016x}"

        # Add Exception Info
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Merge "extra" fields (attributes not in standard LogRecord)
        # Standard attributes to ignore
        standard_attrs = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "taskName",
        }

        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_record[key] = value

        return json.dumps(log_record)


def setup_logging_format() -> None:
    """
    Configures root logger to emit JSON to stdout (for container capture)
    and keeps Critical Alerts for dev visibility.
    """
    root_logger = logging.getLogger()

    # Remove default handlers to avoid duplicates/unformatted logs
    # But be careful not to remove the CriticalAlertHandler if it was added early?
    # Actually, we define CriticalAlertHandler below. Let's just add JSON handler.

    # Check environment to decide if we strictly force JSON or allow mixed
    # For ADOS Standard: JSON is primary.

    json_handler = logging.StreamHandler()
    json_handler.setFormatter(JSONFormatter())

    # We might want to replace the default handler
    for h in root_logger.handlers:
        if isinstance(h, logging.StreamHandler) and not isinstance(
            h.formatter, JSONFormatter
        ):
            # Remove default basic config handler
            root_logger.removeHandler(h)

    root_logger.addHandler(json_handler)

    # Re-add Critical Alerts (Dev Friendliness)
    setup_console_alerts()


def setup_console_alerts() -> None:
    """
    Adds a custom logging handler to print high-visibility alerts for critical errors
    (like Quota Exceeded) directly to the console.
    """

    class CriticalAlertHandler(logging.Handler):
        def emit(self, record):  # type: ignore[no-untyped-def]
            msg = self.format(record)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "Quota" in msg:
                # ANSI Escape Codes for Red Background, White Text
                RED_BG = "\033[41m\033[97m"
                RESET = "\033[0m"
                print(
                    f"\n{RED_BG} [CRITICAL ALERT] QUOTA/RESOURCE ERROR DETECTED {RESET}"
                )
                print(f"{RED_BG} {msg} {RESET}\n")

    root_logger = logging.getLogger()
    # Check if already added to avoid duplicates
    if not any(isinstance(h, CriticalAlertHandler) for h in root_logger.handlers):
        root_logger.addHandler(CriticalAlertHandler())
