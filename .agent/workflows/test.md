---
description: Standard Testing Workflow
---

# Testing Strategy

Follow this workflow to verify changes before pushing.

## 1. Unit Tests (Fast)
Run isolated unit tests. These mock all external calls.
```bash
make test
```

## 2. Integration Tests (A2A)
Verify agent-to-agent communication using the In-Memory Runner.
```bash
uv run pytest tests/integration
```

## 3. E2E Verification (Full Stack)
Start the server and run end-to-end checks.
```bash
# Terminal 1
uv run uvicorn orchestrator.server:create_app --factory --port 8000

# Terminal 2
uv run pytest tests/e2e
```
