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
| **Layer 5** | **E2E Tests** | `frontend/tests/e2e/` (Playwright) | Full user journeys (Browser → Backend). |
| **Layer 4** | **Component** | `frontend/tests/components/` (Vitest) | Isolated UI components. |
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

### Smart Test Runner (Recommended)

The `run_tests.py` script provides a smart test runner that executes tests in optimal order and exits immediately on first failure. This enables fast fix-retry cycles during development.

#### Quick Start

```bash
# Run all tests (recommended for pre-commit)
python run_tests.py

# Run tests for a specific agent
python run_tests.py --agent researcher_agent

# Run tests without evaluations (faster, no API keys needed)
python run_tests.py --skip-evals

# Verbose output
python run_tests.py --verbose

# Using Makefile
make test                    # Run all tests
make test-agent AGENT=researcher_agent  # Test specific agent
make test-fast              # Skip evaluations
```

#### Test Execution Order

Tests are executed in this order (fastest to slowest, most critical first):

1. **Verification** - Setup checks and agent discovery
   - Verifies researcher agent is discoverable
   - Checks metadata extraction
   - Validates file structure

2. **Unit Tests - Core Utilities**
   - Agent Registry tests
   - Model tests

3. **API Tests**
   - Agent endpoint tests
   - Metadata endpoint tests

4. **Integration Tests**
   - Real agent discovery
   - Metadata extraction from actual files

5. **Agent Tests**
   - Agent-specific unit tests (tools, callbacks, server)

6. **Evaluations** (optional, requires API keys)
   - ADK evaluations
   - Can be skipped with `--skip-evals`

**Early Exit**: The runner stops immediately on first failure, allowing you to fix issues and retry quickly. This enables fast fix-retry cycles during development.

**Commit Readiness**: When all tests pass, you're ready to commit!

#### Command Line Options

```bash
python run_tests.py [OPTIONS]

Options:
  --agent AGENT           Run tests for a specific agent
  --skip-evals            Skip evaluation tests (no API keys needed)
  --skip-verification     Skip verification script
  --verbose, -v           Show verbose output
  --help                  Show help message
```

#### Usage Examples

**Pre-Commit Verification:**
```bash
python run_tests.py
```
If any test fails, the runner stops immediately and shows the error. Fix the issue and run again.

**Testing a Specific Agent:**
```bash
python run_tests.py --agent researcher_agent
```

**Fast Development Cycle:**
```bash
python run_tests.py --skip-evals
```
This runs all tests except evaluations, which require API keys and are slower.

#### Integration with Development Workflow

**Agent Development:**
1. Make your changes
2. Run tests: `python run_tests.py --agent <agent_name>`
3. If tests fail, fix the issue and retry
4. When all tests pass, commit

**Pre-Commit Hook:**
You can integrate this into a pre-commit hook:
```bash
#!/bin/bash
# .git/hooks/pre-commit

python run_tests.py --skip-evals
exit $?
```

#### Benefits

1. **Fast Feedback**: Exits on first failure, no need to wait for all tests
2. **Smart Order**: Runs fastest tests first, slowest last
3. **Easy Retry**: Quick fix-retry cycles during development
4. **Commit Readiness**: When all pass, you're ready to commit
5. **Flexible**: Can skip slow tests or focus on specific agents

#### Troubleshooting

**Tests Fail Immediately:**
This is expected! The runner exits on first failure to help you:
1. See the error immediately
2. Fix the issue
3. Run again quickly

**Evaluation Tests Fail:**
If evaluation tests fail due to missing API keys:
- Use `--skip-evals` to skip them
- Or set up your `.env` file with `GOOGLE_API_KEY`

**Command Not Found:**
Make sure you're in the project root:
```bash
cd /path/to/ai-agent-architecture
python run_tests.py
```

### Backend (Python)
We use `pytest` configured to discover tests in `agent_platform/` and `agents/`.

```bash
# Run all tests (legacy - use run_tests.py for development)
uv run pytest

# Run specific test file
uv run pytest agent_platform/test_config.py
```

### Frontend (TypeScript)
We use `vitest` for component tests and `playwright` for E2E.

```bash
cd frontend
pnpm test          # Vitest (components)
pnpm test:e2e      # Playwright E2E (tests/e2e/)
```

## 📝 Best Practices

- **Naming**: Test files must be named `test_*.py`.
- **Typing**: All test functions must be typed (e.g., `def test_something() -> None:`).
- **Mocking**: Use `unittest.mock` strictly. Avoid making real API calls in Layer 1 tests.
- **Docstrings**: Every test should have a clear docstring explaining *what* it is verifying.
