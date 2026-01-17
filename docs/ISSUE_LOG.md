# 🔴 Issue & Resolution Log

This document serves as the single source of truth for all friction points, errors, and STRICT DEVIATIONS encountered during development.
**Rule:** All items here trigger a mandatory refactor or fix to ensure "Zero Tolerance".

## 📜 Historical Issues (Jan 2026)

| Date | Severity | Description | Status |
| :--- | :--- | :--- | :--- |
| **Jan 16** | 🔴 **High** | `make` command missing on Windows. Replaced with `reset_dev_env.ps1`. | **Resolved** |
| **Jan 16** | 🟡 **Medium** | Linting violations: 91 `ruff` errors + 36 `mypy` errors. Violation of "Zero Tolerance". | **Resolved** |
| **Jan 16** | 🟡 **Medium** | UI/Agent Coupling. Orchestrator was serving HTML. Separated into `apps/web`. | **Resolved** |
| **Jan 16** | 🔴 **High** | Broken Dependency: `google-adk==1.18.0` required non-existent `a2a-sdk`. Upgraded to `1.22.1`. | **Resolved** |

## 🏗️ Infrastructure Refactoring Issues (Jan 17)

### Critical

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **Eval Environment Mismatch** | Running evals on host failed to connect to Docker internal network (DNS resolution failure). | Moved execution *inside* container via `docker compose exec`. |
| **A2A Protocol Strictness** | Ad-hoc dict passing caused validation errors. | Implemented `registry/models/protocol.py` for strict typing. |

### Configuration & Setup

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **Missing Sub-Agent Startup** | Orchestrator failed locally because dependency agents weren't running. | Updated `docker-compose` to boot full stack. |
| **Runner Instantiation** | `Runner` requires explicit dependency injection (`session_service`, etc.). | Updated script to fully instantiate `Runner`. |

### Script Logic Errors

| Error | Cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: google.adk` | Virtual environment not active. | Used `uv run` to enforce lockfile context. |
| `App object has no attribute run` | Misunderstanding of ADK API. | Switched to `google.adk.runners.Runner`. |
| `Runner.run() got unexpected keyword input` | API Mismatch. | Switched to `runner.run_async()` with `genai_types.Content`. |
| `Session not found` | Session not auto-created. | Explicitly called `session_service.create_session`. |
| `1 validation error for Part` | Input was `dict`, expected `str`. | Added parsing logic for `{"message": ...}` input format. |

## 📦 Dependency & Upstream Issues

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **Upstream Deprecation** | `a2a-sdk` uses deprecated `HTTP_413_REQUEST_ENTITY_TOO_LARGE`. | Suppressed warning at import time in `agent_platform/server.py`. |

## 🧪 Test Regressions (Jan 17)
*Issues uncovered during Verification phase.*

| Regression | Root Cause | Fix |
| :--- | :--- | :--- |
| **Integration Test 404** (`test_a2a.py`) | `/api/chat_stream` route was attached to the global `app` instance, but tests use `create_app()` factory which returns a fresh, route-less instance. Endpoint was likely lost during previous UI decoupling. | Restored endpoint and moved registration *inside* `create_app()` to ensure all instances include it. |
| **Unit Test TypeError** (`test_orchestrator.py`) | `MagicMock` auto-creates attributes (like `tool_calls`) as truthy Mocks. The serializer tried to `json.dumps` these Mocks. | Explicitly set `mock_event.tool_calls = []` and `usage_metadata=None` in test fixture to prevent auto-creation. |
| **Eval Test Failure** (`test_course_creator_conversations.py`) | `InvocationContext.model_copy()` returned a fresh `MagicMock` in tests, causing `ctx.plugin_manager` to lose its `AsyncMock` configuration and making `await` fail. | Mocked `ctx.model_copy` to return `ctx` (self) to preserve mock configuration. |

## 🎨 Design & Architecture Patterns
*Detailed breakdown of architectural decisions and friction points.*

### Prompt Registry Location Mismatch
- **Status**: 🟢 **Resolved**
- **Date**: 2026-01-17
- **Description**: `agent_platform/prompts.py` defines `REGISTRY_DIR` as `.agent/prompts`, but docstrings mention `registry/prompts/`.
- **Solution**: Updated docstring in `agent_platform/prompts.py` to match implementation (`.agent/prompts`).

### OpenTelemetry Connection Noise
- **Status**: 🟢 **Resolved**
- **Date**: 2026-01-17
- **Description**: Tests emit repeated `NameResolutionError` for `phoenix` host on port 6006.
- **Solution**:
    1.  Updated `agent_platform/observability.py` to respect `OTEL_SDK_DISABLED` env var.
    2.  Updated `pytest.ini` to set `OTEL_SDK_DISABLED=true`.

### Testing Pattern Friction (ADK Mocking)
- **Status**: 🟢 **Resolved**
- **Date**: 2026-01-17
- **Issue**: `MagicMock` conflicts with Pydantic validation in `BaseAgent` and `InvocationContext`.
- **Solution**:
    1.  Use `MockAgent(BaseAgent)` class instead of `MagicMock`.
    2.  Explicitly set `ctx.end_invocation = False`.
    3.  Mock `model_copy` to return `ctx`.
