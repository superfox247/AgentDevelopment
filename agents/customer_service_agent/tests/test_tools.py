"""Unit tests for customer service agent tools."""

from agents.customer_service_agent.tools.input_processor import (
    structure_user_input_impl,
    validate_compliance_impl,
)


def test_structure_user_input_basic() -> None:
    """Test basic input structuring."""
    result = structure_user_input_impl(
        user_message="I need help with billing",
        intent="billing",
        urgency="normal",
        category="billing",
    )

    assert result["original_message"] == "I need help with billing"
    assert result["intent"] == "billing"
    assert result["urgency"] == "normal"
    assert result["category"] == "billing"
    assert "metadata" in result
    assert result["metadata"]["message_length"] > 0


def test_structure_user_input_defaults() -> None:
    """Test input structuring with defaults."""
    result = structure_user_input_impl(user_message="Hello")

    assert result["intent"] == "general_inquiry"
    assert result["urgency"] == "normal"
    assert result["category"] == "general"


def test_validate_compliance_valid() -> None:
    """Test compliance validation with valid input."""
    structured_input = {
        "original_message": "I need help",
        "intent": "general_inquiry",
        "urgency": "normal",
        "category": "general",
    }

    result = validate_compliance_impl(structured_input)

    assert result["is_compliant"] is True
    assert len(result["issues"]) == 0
    assert result["validated_input"] == structured_input


def test_validate_compliance_missing_field() -> None:
    """Test compliance validation with missing required field."""
    structured_input = {
        "original_message": "I need help",
        "intent": "general_inquiry",
        # Missing urgency and category
    }

    result = validate_compliance_impl(structured_input)

    assert result["is_compliant"] is False
    assert len(result["issues"]) > 0
    assert "Missing required field" in str(result["issues"])


def test_validate_compliance_invalid_urgency() -> None:
    """Test compliance validation with invalid urgency."""
    structured_input = {
        "original_message": "I need help",
        "intent": "general_inquiry",
        "urgency": "invalid_urgency",
        "category": "general",
    }

    result = validate_compliance_impl(structured_input)

    assert result["is_compliant"] is False
    assert any("Invalid urgency level" in issue for issue in result["issues"])


def test_validate_compliance_empty_intent() -> None:
    """Test compliance validation with empty intent."""
    structured_input = {
        "original_message": "I need help",
        "intent": "",
        "urgency": "normal",
        "category": "general",
    }

    result = validate_compliance_impl(structured_input)

    assert result["is_compliant"] is False
    assert any("Intent cannot be empty" in issue for issue in result["issues"])
