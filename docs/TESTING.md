# Testing Strategy

This document serves as the **Single Source of Truth** for testing standards, strategies, and workflows within the Antigravity Agent Factory.

## 🏆 Core Philosophy

We follow a **Test-Driven Development (TDD)** approach with a preference for **Colocated Unit Tests** for Python code. This ensures tests are discoverable, maintained alongside the code they verify, and serve as live documentation for developers.

### The TDD Workflow (Red-Green-Refactor)

For every new feature or bug fix, follow this strict cycle:

1.  **🔴 Red**: Write a failing test that defines the expected behavior.
2.  **🟢 Green**: Implement the minimal logic required to pass the test.
3.  **🔵 Refactor**: Improve the code structure and performance while ensuring the test stays green.

## 🏗 The 5-Layer Testing Pyramid

We structure verification into five distinct layers to balance speed, fidelity, and cost.

| Layer | Type | Location | Scope |
| :--- | :--- | :--- | :--- |
| **Layer 5** | **E2E Tests** | `frontend/e2e/` (Playwright) | Full user journeys (Browser -> Backend). |
| **Layer 4** | **Component** | `frontend/tests/` (Vitest) | Isolated UI components. |
| **Layer 3** | **Integration** | `tests/integration/` (Optional) | Service boundaries and multiple agents. |
| **Layer 2** | **Agent Structure** | `agents/<agent>/tests/` | Agent configuration, tools, and Docker sanity. |
| **Layer 1** | **Unit Tests** | **Colocated** (`src/foo.py` -> `src/test_foo.py`) | Deterministic function logic and utilities. |

## 📂 Directory Structure & Colocation

We use a **Colocated Strategy** for Python Unit Tests (Layer 1). This means test files live directly next to the source files they test.

### Example Structure

```text
agent_platform/
├── config.py           # Implementation
├── test_config.py      # Unit Test (Layer 1)
├── observability.py    # Implementation
└── test_observability.py # Unit Test (Layer 1)

agents/
└── base_agent/
    ├── tools.py        # Tool Logic
    └── test_tools.py   # Unit Test (Layer 1)
```

### Benefits
- **Discoverability**: You immediately see if a module has tests.
- **Maintenance**: When you move `config.py`, `test_config.py` moves with it.
- **Context**: Tests act as usage examples right next to the code.

## 🧪 Running Tests

### Backend (Python)
We use `pytest` configured to discover tests in `agent_platform/` and `agents/`.

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest agent_platform/test_config.py
```

### Frontend (TypeScript)
We use `vitest` for component tests and `playwright` for E2E.

```bash
cd frontend
npm test
```

## 📝 Best Practices

- **Naming**: Test files must be named `test_*.py`.
- **Typing**: All test functions must be typed (e.g., `def test_something() -> None:`).
- **Mocking**: Use `unittest.mock` strictly. Avoid making real API calls in Layer 1 tests.
- **Docstrings**: Every test should have a clear docstring explaining *what* it is verifying.
