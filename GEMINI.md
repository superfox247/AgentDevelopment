# GEMINI.md - The Agent Factory Constitution

This document defines the immutable laws and operational rules for the Agent Development Factory. All agents and workflows must adhere to these principles.

## 1. Core Philosophy
-   **Zero Tolerance for Noise**: Warning suppression is forbidden. Fix the root cause (e.g., regex strings, deprecated args).
-   **Structure Over Speed**: Do not create ad-hoc agents in the root. All work belongs to a specific **Domain** or the **Platform**.
-   **Schema-First**: Define Pydantic models in `registry/models/` before writing logic.

## 2. Architecture & Patterns
-   **Domain Isolation**: Agents in `domains/` must be self-contained. Dependencies should point to `platform/` or `registry/`, not cross-domain without explicit contracts.
-   **Factory Pattern**: All agents must use `create_app()` factories for initialization to ensure testability.
-   **Platform Layer**: Use shared services (`platform.auth`, `platform.observability`) instead of reinventing wheels.

## 3. Security & Config
-   **Strict Separation**:
    -   **Secrets** (API Keys) -> `.env` (Never checked in)
    -   **Configuration** -> `domain.yaml` or `config.py` (Checked in)
-   **Typed Config**: Use Pydantic `BaseSettings` for all configuration.

## 4. Observability
-   **No Print**: Use `logging.getLogger(__name__)`.
-   **Trace Everything**: Ensure `trace_id` propagates across A2A calls.

## 5. Testing Pyramid
-   **Unit**: Mock everything. Fast.
-   **Integration**: Test the loop using `InMemorySessionService`.
-   **E2E**: Verify the API contract.

## 6. Context Management
-   **Seek-and-Read**: Use `grep_search` and `view_code_item` to find specific logic. Do not read 5000-line files linearly.
-   **Workflows First**: Check `.agent/workflows/` before asking "How do I...?".
