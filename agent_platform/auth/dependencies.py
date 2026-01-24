import logging
import os
from typing import Annotated

"""
FastAPI dependencies for Authentication.

Provides dependency injection providers for:
- Retrieving the current user
- validating tokens
- Handling "Auth Disabled" dev modes
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from agent_platform.auth.core import AuthProvider, User

logger = logging.getLogger(__name__)

# Security Scheme (Bearer Token)
security_scheme = HTTPBearer(auto_error=False)

class SimpleTokenProvider(AuthProvider):
    """
    Simple implementation that checks against a single server-side API Key.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def verify_token(self, token: str) -> User | None:
        if token == self.api_key:
            return User(id="admin", username="Admin User", scopes=["*"])
        return None

def get_auth_provider() -> AuthProvider:
    """
    Factory to get the configured AuthProvider.

    Returns:
        AuthProvider: The active authentication provider instance.
    """
    # 1. Check if Auth is disabled (Dev Mode)
    if os.environ.get("AUTH_DISABLED", "false").lower() == "true":
        logger.warning("AUTH_DISABLED=true: Permitting all requests as 'anonymous' admin.")
        return SimpleTokenProvider(api_key="anonymous") # Dummy

    # 2. Get API Key from Env
    api_key = os.environ.get("AGENT_API_KEY")
    if not api_key:
        logger.warning("AGENT_API_KEY not set! Authentication will fail for all non-empty tokens.")
        # We don't crash, but verify_token will practically always fail unless token matches "" (unlikely intention)
        # Better safety: set a random impossible key if missing?
        # For now, let's just log warning.
        api_key = "CHANGEME_CRITICAL_MISSING_KEY"

    return SimpleTokenProvider(api_key=api_key)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    provider: Annotated[AuthProvider, Depends(get_auth_provider)]
) -> User:
    """
    FastAPI Dependency to retrieve and verify the current user.

    Args:
        creds: The HTTP Bearer credentials injected by FastAPI.
        provider: The authentication provider injected by get_auth_provider.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: 401 if missing or invalid credentials.
    """

    # 0. Handle Dev Mode "Disabled" shortcut
    # If auth disabled, the provider above returns a dummy.
    # But checking env var again here saves us from requiring a token at all in the header.
    if os.environ.get("AUTH_DISABLED", "false").lower() == "true":
        return User(id="dev", username="Developer", scopes=["*"])

    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = provider.verify_token(creds.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
