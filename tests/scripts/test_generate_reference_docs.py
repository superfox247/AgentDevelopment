"""Tests for generated docs helpers."""

from __future__ import annotations

from scripts.generate_reference_docs import (
    OpenAPIOperation,
    _domain_id_for_path,
    _render_api_diagram_markdown,
)


def test_domain_id_for_path_classification() -> None:
    """API paths should map to stable product domains."""
    assert _domain_id_for_path("/api/chat/researcher") == "chat"
    assert _domain_id_for_path("/api/agents") == "agent_surface"
    assert _domain_id_for_path("/api/skills/research") == "agent_surface"
    assert _domain_id_for_path("/api/docker") == "runtime_ops"
    assert _domain_id_for_path("/api/logs/container/stream") == "runtime_ops"
    assert _domain_id_for_path("/api/verify") == "diagnostics"
    assert _domain_id_for_path("/api/usage") == "usage"
    assert _domain_id_for_path("/api/telemetry/log") == "telemetry"
    assert _domain_id_for_path("/health") == "health"
    assert _domain_id_for_path("/unknown") == "other"


def test_render_api_diagram_markdown_contains_expected_sections() -> None:
    """Generated API diagrams should include diagram and operation matrix content."""
    operations = [
        OpenAPIOperation(
            method="POST",
            path="/api/chat/{name}",
            operation_id="chat_with_agent",
            tags=(),
        ),
        OpenAPIOperation(
            method="GET",
            path="/api/usage",
            operation_id="get_usage",
            tags=("usage",),
        ),
    ]

    rendered = _render_api_diagram_markdown(operations)

    assert "# Generated API Diagrams" in rendered
    assert "## Domain -> Endpoint Surface" in rendered
    assert "```mermaid" in rendered
    assert '["POST /api/chat/{name}"]' in rendered
    assert '["GET /api/usage"]' in rendered
    assert "| `Chat Experience` | 1 | `POST` |" in rendered
    assert "| `Usage & Quotas` | 1 | `GET` |" in rendered
    assert (
        "| `Chat Experience` | `POST` | `/api/chat/{name}` | `-` | `chat_with_agent` | `-` |"
        in rendered
    )
    assert (
        "| `Usage & Quotas` | `GET` | `/api/usage` | `-` | `get_usage` | `usage` |"
        in rendered
    )
