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

from agent_platform.config import PlatformConfig, get_config

# Ensure root is in path prior to imports if needed, though robust imports are better
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# --- Constants ---
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
TEST_SCRIPT = ROOT_DIR / "tests" / "evaluation" / "test_content_engine.py"

# --- Globals (Singleton style for simplicity in this context) ---
_docker_client: docker.DockerClient | None = None


def get_platform_config() -> PlatformConfig:
    """Retrieves the platform configuration singleton.

    Returns:
        PlatformConfig: The active configuration instance.
    """
    return get_config()


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
        except (docker.errors.DockerException, OSError) as e:
            # Docker not available or connection failed
            logging.warning(f"Docker client initialization failed: {e}")
            return None
        except Exception as e:
            # Unexpected error
            logging.error(
                f"Unexpected error initializing Docker client: {e}", exc_info=True
            )
            return None
    return _docker_client


def get_genai_client() -> genai.Client:
    """Returns a new Google GenAI Client using the platform config.

    This function should be overridden in tests to provide a mock client.
    """
    config = get_platform_config()
    # We use the config to get the key. If key is missing, Client might error later
    # or we can handle it here, but usually Client(api_key=None) is valid until a call is made.
    return genai.Client(api_key=config.gemini_api_key)
