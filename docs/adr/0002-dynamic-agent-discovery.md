# ADR-0002: Dynamic agent discovery

**Status**: Accepted | **Date**: 2026-01-25

## Context

Agents were hardcoded in frontend, API, and config. Adding agents required edits in many places.

## Decision

**AgentRegistry**: scan `agents/`, extract metadata from `agent.py` via AST. API and UI discover agents dynamically.

## Consequences

- **Positive**: New agents auto-discovered; no manual list updates; scales with fleet size.
- **Negative**: Depends on consistent `agent.py` structure; AST parsing adds a small layer.

## Alternatives

- **Static config**: Rejected—doesn’t scale.
- **Convention-only (no registry)**: Rejected—no metadata for UI without parsing.
