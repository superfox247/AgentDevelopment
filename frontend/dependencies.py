"""
Dashboard Dependency Injection.

Providers for:
- Docker Client
- Agent Runners (lazy loaded)
- Configuration
"""

import logging
import sys
from pathlib import Path

import docker
from google import genai
from google.adk.artifacts import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent_platform.config import PlatformConfig

# Ensure root is in path prior to imports if needed, though robust imports are better
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# --- Constants ---
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
TEST_SCRIPT = ROOT_DIR / "tests" / "evaluation" / "test_content_engine.py"

# --- Globals (Singleton style for simplicity in this context) ---
_docker_client: docker.DockerClient | None = None
_customer_service_runner: Runner | None = None
_image_generator_runner: Runner | None = None


def get_platform_config() -> PlatformConfig:
    """Retrieves the platform configuration singleton.

    Returns:
        PlatformConfig: The active configuration instance.
    """
    return PlatformConfig()


def get_docker_client() -> docker.DockerClient | None:
    """Returns a connected Docker client or None if unavailable.

    Initializes the client from the environment on the first call.

    Returns:
        docker.DockerClient | None: The Docker client if connection succeeds, else None.
    """
    global _docker_client
    if _docker_client is None:
        try:
            _docker_client = docker.from_env()
        except Exception as e:
            logging.warning(f"Docker client initialization failed: {e}")
            return None
    return _docker_client


def get_customer_service_runner() -> Runner:
    """Lazy-load the customer service runner.

    Returns:
        Runner: The initialized Customer Service agent runner.

    Raises:
        ImportError: If the agent code cannot be imported.
    """
    global _customer_service_runner
    if _customer_service_runner is None:
        # Import here to avoid circular dependencies or early load issues
        # Adjust imports to match project structure
        try:
            # Ensure the domain path is available for imports inside the agent code
            content_creation_path = ROOT_DIR / "domains" / "content_creation"
            if str(content_creation_path) not in sys.path:
                sys.path.append(str(content_creation_path))

            from domains.content_creation.customer_service.agent import (
                app as customer_service_app,
            )

            _customer_service_runner = Runner(
                app=customer_service_app,
                artifact_service=FileArtifactService(root_dir=str(ARTIFACTS_DIR)),
                session_service=InMemorySessionService(),
            )
        except ImportError as e:
            logging.error(f"Failed to import Customer Service Agent: {e}")
            raise
    return _customer_service_runner


def get_image_generator_runner() -> Runner:
    """Lazy-load the image generator runner.

    Returns:
        Runner: The initialized Image Generator agent runner.

    Raises:
        ImportError: If the agent code cannot be imported.
    """
    global _image_generator_runner
    if _image_generator_runner is None:
        try:
            # Ensure the domain path is available for imports inside the agent code
            content_creation_path = ROOT_DIR / "domains" / "content_creation"
            if str(content_creation_path) not in sys.path:
                sys.path.append(str(content_creation_path))

            from domains.content_creation.image_generator.agent import (
                app as image_generator_app,
            )

            _image_generator_runner = Runner(
                app=image_generator_app,
                artifact_service=FileArtifactService(root_dir=str(ARTIFACTS_DIR)),
                session_service=InMemorySessionService(),
            )
        except ImportError as e:
            logging.error(f"Failed to import Image Generator Agent: {e}")
            raise

    return _image_generator_runner


def get_genai_client() -> genai.Client:
    """Returns a new Google GenAI Client using the platform config.

    This function should be overridden in tests to provide a mock client.
    """
    config = get_platform_config()
    # We use the config to get the key. If key is missing, Client might error later
    # or we can handle it here, but usually Client(api_key=None) is valid until a call is made.
    return genai.Client(api_key=config.gemini_api_key)
