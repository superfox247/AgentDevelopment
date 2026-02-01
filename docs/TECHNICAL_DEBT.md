# Technical Debt

**Last Updated**: 2026-01-26

Known debt and refactors. Status: Open | In progress | Resolved. Priority: High | Medium | Low.

Planned work → [ROADMAP.md](ROADMAP.md). Active issues → [.agent/issues.md](../.agent/issues.md).

---

## High

### TD-001: Dead agent references

**Status**: Open | **Effort**: Low

References to non-existent agents (customer_service, image_generator, orchestrator, content_builder) in backend.

**Locations**: `dashboard_api/services.py` (if present).

**Fix**: Remove or make dynamic; use registry API. See `.agent/issues.md`.

---

## Medium

### TD-002: Python version alignment

**Status**: Open | **Effort**: Low

Root `pyproject.toml` 3.10–3.14 vs `agent_platform` 3.11–3.13. Align or document.

---

## Low

### TD-003: Code quality

**Status**: Open | **Effort**: Low

Unused imports, type hints, docstrings. Address incrementally.

---

## Resolved (baseline cleanup 2026-01-26)

- **StatusPanel / GeneratorView / schemas**: Removed as part of dashboard baseline. UI is now chat-only (see [DASHBOARD_BASELINE](DASHBOARD_BASELINE.md)).

---

## Metrics (2026-01-26)

| Priority | Count | Resolved |
| :--- | :--- | :--- |
| High | 1 | 0 |
| Medium | 1 | 0 |
| Low | 1 | 0 |

**Review**: Add during reviews; resolve with features or dedicated cleanup.
