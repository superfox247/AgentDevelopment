# GEMINI.md - The Agent Factory Constitution

This document defines the immutable laws and operational rules for the Agent Development Factory. All agents and workflows must adhere to these principles.

## 1. Core Philosophy
-   **Zero Tolerance for Noise**: Warning suppression is forbidden. Fix the root cause (e.g., regex strings, deprecated args).
-   **Structure Over Speed**: Do not create ad-hoc agents in the root. All work belongs to a specific **Domain** or the **Platform**.
-   **Schema-First**: Define Pydantic models in `schemas/models/` before writing logic.

## 2. Architecture & Patterns
-   **Domain Isolation**: Agents in `domains/` must be self-contained and decoupled from other domains.
-   **Separation of Concerns**: Domain Agents must remain infrastructure-agnostic. No direct interaction with the container runtime or platform internals.
-   **Factory Pattern**: All agents must use `create_app()` factories for initialization to ensure testability.
-   **Platform Layer**: Use shared services (`platform.auth`, `platform.observability`) instead of reinventing wheels.

## 3. Security & Config
*   **Authority**: See `.agent/skills/audit_security/SKILL.md` for strict enforcement rules.
*   **Principle**: Secrets in `.env`, Config in `domain.yaml`.

## 4. Observability
-   **No Print**: Use `logging.getLogger(__name__)`.
-   **Trace Everything**: Ensure `trace_id` propagates across A2A calls.
-   **Silent Observer**: Debugging is an external act. Agents report errors; they do not investigate them.

## 5. Testing Pyramid
*   **Authority**: See `.agent/skills/scaffold_tests/SKILL.md`.
*   **Principle**: Mock IO in Unit tests. Use `InMemorySession` for Integration.

## 6. Context Management
*   **Authority**: See `.agent/skills/gather_context/SKILL.md`.
*   **Principle**: "Seek-and-Read" (Grep first). Check Workflows first.

## 7. Engineering Standards
*   **Code Style**: See `.agent/skills/smart_lint/SKILL.md`.
*   **Git Workflow**: See `.agent/skills/manage_git/SKILL.md`.
*   **Code Review**: See `.agent/skills/review_code/SKILL.md`.
*   **Development Method**: See `.agent/skills/manage_task/SKILL.md`.

## 8. Sub-Agent Protocol
*   **Authority**: See `.agent/skills/automate_browser/SKILL.md`.
*   **Fail Fast**: Strict retry limit (max 2). If a strategy fails twice, stop and report.
*   **Explicit Scope**: Prompts must define clear "Success Criteria" and "Abort Conditions".
*   **No Autopilot**: Sub-agents must return control for strategic decisions; no infinite loop debugging.
