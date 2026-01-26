# Technical Debt

**Last Updated**: 2026-01-25

Known debt and refactors. Status: Open | In progress | Resolved. Priority: High | Medium | Low.

Planned work → [ROADMAP.md](ROADMAP.md). Active issues → [.agent/issues.md](../.agent/issues.md).

---

## High

### TD-001: Dead agent references

**Status**: Open | **Effort**: Low

References to non-existent agents (customer_service, image_generator, orchestrator, content_builder).

**Locations**: `dashboard_api/services.py:58` · `frontend/src/api/schemas.ts` · `StatusPanel.tsx:28-31` · `GeneratorView.tsx:135`

**Fix**: Remove or make dynamic; use registry API. See Issue #1 in `.agent/issues.md`.

---

## Medium

### TD-002: StatusPanel dynamic discovery

**Status**: Open | **Effort**: Medium

StatusPanel uses hardcoded mappings. Refactor to AgentRegistry API like AgentsView.

### TD-003: Python version alignment

**Status**: Open | **Effort**: Low

Root `pyproject.toml` 3.10–3.14 vs `agent_platform` 3.11–3.13. Align or document.

---

## Low

### TD-004: Code quality

**Status**: Open | **Effort**: Low

Unused imports, type hints, docstrings. Address incrementally.

---

## Metrics (2026-01-25)

| Priority | Count | Resolved |
| :--- | :--- | :--- |
| High | 1 | 0 |
| Medium | 2 | 0 |
| Low | 1 | 0 |

**Review**: Add during reviews; resolve with features or dedicated cleanup.
