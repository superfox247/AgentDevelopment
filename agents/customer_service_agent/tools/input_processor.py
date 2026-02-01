"""Tools for processing and structuring user input for downstream agents."""

from __future__ import annotations

import json
from typing import Any


def structure_user_input(
    user_message: str,
    intent: str | None = None,
    urgency: str = "normal",
    category: str | None = None,
) -> dict[str, Any]:
    """Process and structure raw user input into a format suitable for downstream agents.
    
    This tool processes raw user input and structures it into a format
    that downstream agents can use effectively. It extracts intent, urgency,
    category, and other metadata.
    
    Args:
        user_message: The raw user input message
        intent: Detected or inferred intent (e.g., "billing", "technical_support", "general_inquiry")
        urgency: Urgency level ("low", "normal", "high", "critical")
        category: Request category (e.g., "account", "product", "billing", "technical")
    
    Returns:
        A structured dictionary with processed input and metadata
    """
    structured = {
        "original_message": user_message,
        "intent": intent or "general_inquiry",
        "urgency": urgency,
        "category": category or "general",
        "structured_message": user_message,  # Can be enhanced with NLU processing
        "metadata": {
            "message_length": len(user_message),
            "word_count": len(user_message.split()),
            "has_question": "?" in user_message,
        },
    }
    
    return structured


def validate_compliance(
    structured_input: dict[str, Any],
    compliance_rules: list[str] | None = None,
) -> dict[str, Any]:
    """Validate that structured input complies with policies and rules before passing to downstream agents.
    
    Checks the structured input against compliance rules and policies
    to ensure it's safe to pass to downstream agents. Returns compliance status and any issues found.
    
    Args:
        structured_input: The structured input dictionary from structure_user_input
        compliance_rules: List of compliance rule names to check (e.g., ["gdpr", "hipaa"])
    
    Returns:
        Validation result with compliance status and any issues found
    """
    if compliance_rules is None:
        compliance_rules = ["default"]
    
    issues = []
    is_compliant = True
    
    # Check 1: Ensure structured input has required fields
    required_fields = ["original_message", "intent", "urgency", "category"]
    for field in required_fields:
        if field not in structured_input:
            issues.append(f"Missing required field: {field}")
            is_compliant = False
    
    # Check 2: Validate urgency level
    valid_urgency = ["low", "normal", "high", "critical"]
    if structured_input.get("urgency") not in valid_urgency:
        issues.append(f"Invalid urgency level: {structured_input.get('urgency')}")
        is_compliant = False
    
    # Check 3: Validate intent is not empty
    if not structured_input.get("intent") or structured_input.get("intent").strip() == "":
        issues.append("Intent cannot be empty")
        is_compliant = False
    
    result = {
        "is_compliant": is_compliant,
        "compliance_rules_checked": compliance_rules,
        "issues": issues,
        "validated_input": structured_input if is_compliant else None,
    }
    
    return result
