import logging
import sys
from pathlib import Path

import docker
from google.adk.artifacts import FileArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent_platform.config import PlatformConfig

# Ensure root is in path prior to imports if needed, though robust imports are better
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

# --- Constants ---
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
TEST_SCRIPT = ROOT_DIR / "tests" / "evaluation" / "test_content_engine.py"

# --- Globals (Singleton style for simplicity in this context) ---
_docker_client = None
_customer_service_runner = None
_image_generator_runner = None

def get_platform_config() -> PlatformConfig:
    return PlatformConfig()

def get_docker_client():
    """Returns a connected Docker client or None if unavailable."""
    global _docker_client
    if _docker_client is None:
        try:
            _docker_client = docker.from_env()
        except Exception as e:
            logging.warning(f"Docker client initialization failed: {e}")
            return None
    return _docker_client

def get_customer_service_runner() -> Runner:
    """Lazy-load the customer service runner."""
    global _customer_service_runner
    if _customer_service_runner is None:
        # Import here to avoid circular dependencies or early load issues
        # Adjust imports to match project structure
        try:
             # Ensure the domain path is available for imports inside the agent code
            course_creator_path = ROOT_DIR / "domains" / "course_creator"
            if str(course_creator_path) not in sys.path:
                 sys.path.append(str(course_creator_path))

            from domains.course_creator.customer_service.agent import (
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
    """Lazy-load the image generator runner."""
    global _image_generator_runner
    if _image_generator_runner is None:
        try:
            # Ensure the domain path is available for imports inside the agent code
            course_creator_path = ROOT_DIR / "domains" / "course_creator"
            if str(course_creator_path) not in sys.path:
                 sys.path.append(str(course_creator_path))

            from domains.course_creator.image_generator.agent import (
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
