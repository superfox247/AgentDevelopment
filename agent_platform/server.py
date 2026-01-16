import logging
import os
import warnings

# A2A Imports
from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPIApplication
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.apps.app import App
from google.adk.artifacts.file_artifact_service import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent_platform.a2a import AdkToA2aExecutor, create_agent_card
from agent_platform.observability import setup_telemetry


# --- Global Hygiene ---
def _configure_logging_and_warnings() -> None:

    logging.basicConfig(level=logging.INFO)
    # Suppress experimental warnings
    warnings.filterwarnings("ignore", message=r".*\[EXPERIMENTAL\].*", category=UserWarning)
    # Suppress ADK internal warnings
    logging.getLogger("google_adk.google.adk.runners").setLevel(logging.ERROR)
    logging.getLogger("google.adk.runners").setLevel(logging.ERROR)
    # Suppress Auth warnings
    warnings.filterwarnings("ignore", message=".*Your application has authenticated using end user credentials.*")

_configure_logging_and_warnings()
logger = logging.getLogger(__name__)

def create_platform_app(
    adk_app: App,
    description: str = "",
    enable_a2a: bool = True,
    include_root_route: bool = True
) -> FastAPI:

    """
    Factory to create a standard Agent FastAPI application.

    Args:

        adk_app: The Google ADK App instance (from agent.py).
        description: Description of the agent for the Agent Card.
        enable_a2a: Whether to expose A2A endpoints (default: True).
    """
    app_name = adk_app.name

    # 1. Telemetry
    setup_telemetry(agent_name=f"course-creation-{app_name}")

    # 2. ADK Runner
    runner = Runner(
        app=adk_app,
        artifact_service=FileArtifactService(base_path="./artifacts"),
        session_service=InMemorySessionService(),
    )

    # 3. FastAPI App
    app = FastAPI(title=app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach runner to state for local use (e.g. wrapper endpoints)
    app.state.runner = runner

    # 4. A2A Configuration
    if enable_a2a:
        host = os.environ.get("AGENT_HOST", "localhost")
        port = int(os.environ.get("PORT", "8000")) # Default, overridden by uvicorn usually

        # Executor & Handler
        task_store = InMemoryTaskStore()
        executor = AdkToA2aExecutor(runner, app_name)
        request_handler = DefaultRequestHandler(agent_executor=executor, task_store=task_store)

        # Agent Card
        card = create_agent_card(adk_app, description, host, port)

        # A2A App Wrapper
        a2a_app = A2AFastAPIApplication(agent_card=card, http_handler=request_handler)
        a2a_app.add_routes_to_app(
            app=app,
            rpc_url=f"/a2a/{app_name}",
            agent_card_url="/.well-known/agent.json"
        )

        logger.info(f"[{app_name}] A2A enabled at http://{host}:{port}/a2a/{app_name}")

    if include_root_route:
        @app.get("/")
        def root() -> dict[str, str]:
            info = {
                "status": "ok",
                "service": app_name,
            }
            if enable_a2a:
               info["a2a_card"] = "/.well-known/agent.json"
            return info

    return app

