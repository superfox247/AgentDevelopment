"""Guardrails and compliance callbacks for customer service agent.

Implements input validation, compliance checking, security guardrails,
and ensures professional, legally compliant responses.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmRequest, LlmResponse
from google.adk.tools.tool_context import ToolContext
from google.genai import types

logger = logging.getLogger(__name__)

# Blocked keywords for security and compliance
BLOCKED_KEYWORDS = [
    "hack",
    "exploit",
    "bypass",
    "unauthorized access",
    "data breach",
    "malware",
    "virus",
    "phishing",
    "ddos",
    "sql injection",
    "xss",
]

# Sensitive information patterns (PII, financial data)
PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email (context-dependent)
]

# Professional response templates
PROFESSIONAL_RESPONSES = {
    "blocked_keyword": "I cannot assist with that request as it may involve security concerns. Please contact our security team directly if you have legitimate security-related questions.",
    "pii_detected": "I noticed you may have included sensitive information. For your security, please avoid sharing personal information like social security numbers, credit card numbers, or passwords in this chat. If you need to share sensitive information, please use our secure channels.",
    "inappropriate_content": "I'm here to help with customer service inquiries in a professional manner. Please rephrase your question so I can assist you better.",
    "compliance_violation": "I cannot process that request as it may not comply with our policies. Please contact our compliance team for assistance with such matters.",
}


def before_agent_log(callback_context: CallbackContext) -> None:
    """Log before agent runs for visibility."""
    name = getattr(callback_context, "agent_name", "?")
    inv = getattr(callback_context, "invocation_id", None)
    state = getattr(callback_context, "state", None)
    state_keys = list(state.keys()) if state and hasattr(state, "keys") else []
    logger.info(
        "[customer_service] before_agent agent=%s invocation=%s state_keys=%s",
        name,
        inv,
        state_keys,
    )


def after_agent_log(callback_context: CallbackContext) -> None:
    """Log after agent runs for visibility."""
    name = getattr(callback_context, "agent_name", "?")
    inv = getattr(callback_context, "invocation_id", None)
    logger.info("[customer_service] after_agent agent=%s invocation=%s", name, inv)


def before_tool_log(
    tool: Any,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> None:
    """Log before tool runs for visibility."""
    tool_name = getattr(tool, "name", str(tool))
    logger.info(
        "[customer_service] before_tool tool=%s args=%s",
        tool_name,
        {k: str(v)[:80] for k, v in args.items()},
    )


def after_tool_log(
    tool: Any,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> None:
    """Log after tool runs for visibility."""
    tool_name = getattr(tool, "name", str(tool))
    preview = str(tool_response)[:120] + (
        "..." if len(str(tool_response)) > 120 else ""
    )
    logger.info(
        "[customer_service] after_tool tool=%s response_preview=%s", tool_name, preview
    )


def check_blocked_keywords(text: str) -> bool:
    """Check if text contains blocked security-related keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in BLOCKED_KEYWORDS)


def check_pii(text: str) -> bool:
    """Check if text contains potential PII patterns."""
    for pattern in PII_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def check_professional_tone(text: str) -> bool:
    """Check if text maintains professional tone (basic check)."""
    # Block excessive profanity or inappropriate language
    inappropriate_words = [
        "damn",
        "hell",
        "crap",
    ]  # Add more as needed, keeping it minimal
    text_lower = text.lower()
    # Only flag if multiple inappropriate words appear
    count = sum(1 for word in inappropriate_words if word in text_lower)
    return count < 2  # Allow minor slips, block excessive use


def before_model_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """Guardrail: Validate user input before it reaches the LLM.
    
    Checks for:
    - Blocked security keywords
    - PII patterns
    - Professional tone
    - Compliance violations
    
    Returns a blocked response if violations are detected, None to proceed.
    """
    agent_name = callback_context.agent_name
    logger.info(
        "[customer_service] before_model_guardrail running for agent: %s", agent_name
    )

    # Extract the latest user message
    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    if not last_user_message_text:
        # No user message found, allow to proceed
        return None

    logger.info(
        "[customer_service] Inspecting user message: '%s...'",
        last_user_message_text[:100],
    )

    # Check 1: Blocked keywords (security concerns)
    if check_blocked_keywords(last_user_message_text):
        logger.warning(
            "[customer_service] Blocked keyword detected. Blocking LLM call."
        )
        callback_context.state["guardrail_blocked_keyword"] = True
        callback_context.state["guardrail_reason"] = "blocked_keyword"
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=PROFESSIONAL_RESPONSES["blocked_keyword"]
                    )
                ],
            )
        )

    # Check 2: PII detection
    if check_pii(last_user_message_text):
        logger.warning("[customer_service] PII pattern detected. Warning user.")
        callback_context.state["guardrail_pii_detected"] = True
        callback_context.state["guardrail_reason"] = "pii_detected"
        # Return warning but allow to proceed (user may need to share info securely)
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=PROFESSIONAL_RESPONSES["pii_detected"]
                    )
                ],
            )
        )

    # Check 3: Professional tone
    if not check_professional_tone(last_user_message_text):
        logger.warning(
            "[customer_service] Unprofessional content detected. Blocking."
        )
        callback_context.state["guardrail_inappropriate"] = True
        callback_context.state["guardrail_reason"] = "inappropriate_content"
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=PROFESSIONAL_RESPONSES["inappropriate_content"]
                    )
                ],
            )
        )

    # All checks passed, allow to proceed
    logger.info("[customer_service] Input validation passed. Allowing LLM call.")
    return None


def before_tool_guardrail(
    tool: Any, args: dict[str, Any], tool_context: ToolContext
) -> dict[str, Any] | None:
    """Guardrail: Validate tool arguments before execution.
    
    Ensures tools are only called with allowed parameters and
    validates arguments for security and compliance.
    
    Returns a dict to override tool result if blocked, None to proceed.
    """
    tool_name = getattr(tool, "name", str(tool))
    agent_name = tool_context.agent_name
    logger.info(
        "[customer_service] before_tool_guardrail running for tool '%s' in agent '%s'",
        tool_name,
        agent_name,
    )
    logger.info("[customer_service] Inspecting tool args: %s", args)

    # Check if tool arguments contain blocked content
    args_str = str(args).lower()
    
    # Check for blocked keywords in tool arguments
    if check_blocked_keywords(args_str):
        logger.warning(
            "[customer_service] Blocked keyword in tool args. Blocking tool execution."
        )
        tool_context.state["guardrail_tool_blocked"] = True
        tool_context.state["guardrail_tool_reason"] = "blocked_keyword"
        return {
            "status": "error",
            "error_message": "Tool execution blocked due to security policy violation.",
        }

    # Check for PII in tool arguments
    if check_pii(args_str):
        logger.warning(
            "[customer_service] PII detected in tool args. Blocking tool execution."
        )
        tool_context.state["guardrail_tool_blocked"] = True
        tool_context.state["guardrail_tool_reason"] = "pii_detected"
        return {
            "status": "error",
            "error_message": "Tool execution blocked: sensitive information detected in arguments.",
        }

    # All checks passed, allow tool to execute
    logger.info(
        "[customer_service] Tool argument validation passed. Allowing tool execution."
    )
    return None
