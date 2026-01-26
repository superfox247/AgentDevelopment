# ADR-0001: Use Python for agents

**Status**: Accepted | **Date**: 2026-01-25

## Context

Two patterns existed: YAML-based agents (`agent.yaml`) and Python-based (`agent.py`). Only Python was used; YAML and `load_agent_from_yaml()` were dead.

## Decision

Standardize on **Python only**. Each agent: `agent.py` with `root_agent`, collocated `tools/`, `callbacks/`, etc.

## Consequences

- **Positive**: Single pattern, full ADK features, easier testing and versioning.
- **Negative**: No declarative config; new agents require Python.

## Alternatives

- **YAML**: Rejected—missing features, unused, extra maintenance.
- **Hybrid**: Rejected—complexity without benefit.
