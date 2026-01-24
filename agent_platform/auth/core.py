from abc import ABC, abstractmethod

"""
Authentication interfaces and models.

Defines the core abstractions for the abstract authentication layer,
decoupling implementation (Key/OAuth) from consumption.
"""

from pydantic import BaseModel, Field


class User(BaseModel):
    """
    Represents an authenticated entity (user or service).
    """
    id: str = Field(..., description="Unique identifier for the user.")
    username: str = Field(..., description="Human-readable username.")
    scopes: list[str] = Field(default_factory=list, description="List of authorized scopes.")

    class Config:
        frozen = True

class AuthProvider(ABC):
    """
    Abstract Base Class for Authentication Providers.
    Allows for swapping implementations (e.g., Simple Token vs OAuth2).
    """

    @abstractmethod
    def verify_token(self, token: str) -> User | None:
        """
        Verifies the provided token and returns a User object if valid.
        Returns None if invalid.
        """
        pass
