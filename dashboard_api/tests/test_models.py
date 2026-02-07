"""
Unit tests for Dashboard API Data Models.

Tests Pydantic models used in API responses.
"""

import pytest
from pydantic import ValidationError

from dashboard_api.models import AgentMetadata


class TestAgentMetadata:
    """Tests for AgentMetadata model."""

    def test_agent_metadata_required_fields(self) -> None:
        """Test that required fields are enforced."""
        metadata = AgentMetadata(
            name="test_agent",
            path="agents/test_agent",
        )
        assert metadata.name == "test_agent"
        assert metadata.path == "agents/test_agent"

    def test_agent_metadata_all_fields(self) -> None:
        """Test AgentMetadata with all fields."""
        metadata = AgentMetadata(
            name="test_agent",
            path="agents/test_agent",
            description="Test description",
            model="gemini-2.0-flash",
            has_server=True,
        )
        assert metadata.name == "test_agent"
        assert metadata.path == "agents/test_agent"
        assert metadata.description == "Test description"
        assert metadata.model == "gemini-2.0-flash"
        assert metadata.has_server is True

    def test_agent_metadata_defaults(self) -> None:
        """Test AgentMetadata default values."""
        metadata = AgentMetadata(
            name="test_agent",
            path="agents/test_agent",
        )
        assert metadata.description == ""
        assert metadata.model == ""
        assert metadata.has_server is False

    def test_agent_metadata_missing_required(self) -> None:
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            AgentMetadata(name=None, path=None)  # type: ignore[arg-type]

    def test_agent_metadata_type_validation(self) -> None:
        """Test that type validation works correctly."""
        # String fields should accept strings
        metadata = AgentMetadata(
            name="test",
            path="agents/test",
            description="desc",
            model="model",
        )
        assert isinstance(metadata.name, str)
        assert isinstance(metadata.path, str)
        assert isinstance(metadata.description, str)
        assert isinstance(metadata.model, str)

        # has_server should be boolean
        metadata = AgentMetadata(
            name="test",
            path="agents/test",
            has_server=True,
        )
        assert isinstance(metadata.has_server, bool)

    def test_agent_metadata_serialization(self) -> None:
        """Test that model can be serialized to dict."""
        metadata = AgentMetadata(
            name="test_agent",
            path="agents/test_agent",
            description="Test",
            model="gemini-2.0-flash",
            has_server=True,
        )

        data = metadata.model_dump()
        assert data == {
            "name": "test_agent",
            "path": "agents/test_agent",
            "description": "Test",
            "model": "gemini-2.0-flash",
            "has_server": True,
        }

    def test_agent_metadata_from_dict(self) -> None:
        """Test creating AgentMetadata from dictionary."""
        data: dict[str, str | bool] = {
            "name": "test_agent",
            "path": "agents/test_agent",
            "description": "Test",
            "model": "gemini-2.0-flash",
            "has_server": True,
        }

        metadata = AgentMetadata.model_validate(data)
        assert metadata.name == "test_agent"
        assert metadata.description == "Test"
        assert metadata.model == "gemini-2.0-flash"
        assert metadata.has_server is True
