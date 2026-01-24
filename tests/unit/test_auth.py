"""
Unit Tests for Authentication Logic.

Verifies:
- Token format validation
- Header parsing
- Permission logic
- Environment configuration effects
"""


import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from agent_platform.auth.dependencies import get_current_user

# --- Fixtures ---

@pytest.fixture
def app() -> FastAPI:
    """Creates a dummy FastAPI app secured with the auth dependency."""
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(get_current_user)])
    def protected_route() -> dict[str, str]:
        return {"status": "ok"}

    return app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)

# --- Tests ---

def test_auth_missing_header_fails(client: TestClient) -> None:
    """Ensure 401 if Authorization header is missing."""
    # Ensure env is clear (mocking env vars is safer)
    with pytest.MonkeyPatch.context() as m:
        m.delenv("AUTH_DISABLED", raising=False)
        m.setenv("AGENT_API_KEY", "secret")

        response = client.get("/protected")
        assert response.status_code == 401
        assert response.json() == {"detail": "Missing Authorization Header"}

def test_auth_invalid_token_fails(client: TestClient) -> None:
    """Ensure 401 if token is incorrect."""
    with pytest.MonkeyPatch.context() as m:
        m.delenv("AUTH_DISABLED", raising=False)
        m.setenv("AGENT_API_KEY", "secret")

        response = client.get("/protected", headers={"Authorization": "Bearer wrong-key"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid Authentication Token"}

def test_auth_valid_token_succeeds(client: TestClient) -> None:
    """Ensure 200 if token is correct."""
    with pytest.MonkeyPatch.context() as m:
        m.delenv("AUTH_DISABLED", raising=False)
        m.setenv("AGENT_API_KEY", "secret")

        response = client.get("/protected", headers={"Authorization": "Bearer secret"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_auth_disabled_allows_access(client: TestClient) -> None:
    """Ensure access is allowed without token if AUTH_DISABLED=true."""
    with pytest.MonkeyPatch.context() as m:
        m.setenv("AUTH_DISABLED", "true")

        # specific check: missing header should pass
        response = client.get("/protected")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

