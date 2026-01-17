---
name: Scaffold Agent Tests
description: A skill to generate pytest unit, integration, and E2E tests for agents, following the Testing Pyramid.
---

# Scaffold Agent Tests

This skill helps you create robust tests for agents.

## 1. Load Context
- `tests/conftest.py`: Fixtures (`test_app`, `mock_llm`).
- `tests/unit/test_yaml_loader.py`: Example unit tests.

## 2. Choose Test Type
1.  **Unit Test**: Isolated logic. Mock ALL external calls.
2.  **Integration Test**: Real DB/Session, Mocked LLM.
3.  **E2E Test**: Full HTTP request.

## 1. Cognitive Heuristics
**When to use:** Use this skill after scaffolding a new agent or feature.
**Validation:** Ensure tests pass using `pytest`.

## 2. Load Context
- `scripts/scaffold_test.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run python scripts/scaffold_test.py \
  --domain [domain_name] \
  --agent [agent_name] \
  --heuristics "Test typical user flows." \
  --verification "Assert output state."
```

*Example*:
```bash
uv run python scripts/scaffold_test.py \
  --domain "course_creator" \
  --agent "writer" \
  --heuristics "Test that it generates valid markdown."
```

This will create `tests/unit/domains/[domain]/[agent]/test_agent.py` with the boilerplate.

## 4. Implementation Steps (Manual)
1.  Read the `test_agent.py` file.
2.  Implement the `test_[agent]_run` function.
3.  Add specific tool mocks.
4. Uncomment the mock setup blocks.
5. Adapt the assertions to match your agent's specific logic.

## 5. Verification
Run the tests:
```bash
uv run pytest tests/unit/domains/[domain]/[agent]/test_agent.py
```
