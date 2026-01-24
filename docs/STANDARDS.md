# Standards & Protocols

## 📜 Code Style

### Python
We strictly follow the **Google Python Style Guide**.
*   **Docstrings**: Mandatory for all modules, classes, and exported functions. Use `"""Google Style"""`.
*   **Typing**: Static typing is required. Use `mypy` strict mode compatibility.
*   **Formatting**: Handled by `ruff` (configuration in `pyproject.toml`).

### TypeScript / frontend
*   **Docstrings**: Use **TSDoc** standard for all exported components and interfaces.
*   **Style**: Functional patterns. No Class components.

## 🔒 The "Zero-Wrapper" Policy

**Status**: Active (Jan 24, 2026)

**Rule**: Do not create custom wrappers around standard SDKs (e.g., Google ADK) unless they provide significant *new* functionality.
*   **Anti-Pattern**: A class `MyAgent` that just calls `LlmAgent(...)`.
*   **Correct**: Instantiate `LlmAgent` directly in your factory/startup code.
*   **Goal**: Reduce "Shadow Infrastructure" and utilize native framework capabilities directly.

## 📡 API Patterns

### Centralized Client
All frontend-to-backend communication MUST go through the centralized `apiClient` in the Dashboard.
*   **Why**: Handles error unwrapping, auth headers, and type safety in one place.
*   **Location**: `frontend/src/api/client.ts`.

### Agent Protocol
Agents communicate via the **Google Agent Development Kit (ADK)** protocol.
*   **Config**: Defined via `agent.yaml` (YAML-First strategy).
*   **Interfaces**: Strict Pydantic models for Input/Output schemas.
