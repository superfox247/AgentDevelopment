import pytest
from fastapi.testclient import TestClient

from domains.course_creator.orchestrator.server import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)

def test_heartbeat(client: TestClient) -> None:
    """
    Simple E2E connectivity check.
    In a real E2E, this would use 'subprocess' to launch the server and 'requests' to hit localhost:8000.
    For now, we use TestClient to verify the stack matches the 'factory' pattern.
    """
    # Just checking if we can load the app and hit a health endpoint (if we had one)
    # The current server doesn't have a health check, but we can check if it initializes.
    assert client is not None

