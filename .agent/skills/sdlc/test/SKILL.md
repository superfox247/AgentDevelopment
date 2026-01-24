---
name: Test Branch
description: Platform-level testing patterns across all layers
---

# Testing Skills

## Testing Pyramid

```
        /\
       /E2E\        ← Playwright (browser)
      /──────\
     /Component\    ← Vitest (React)
    /────────────\
   / Integration  \  ← pytest + httpx
  /────────────────\
 /   Agent Eval     \ ← ADK AgentEvaluator
/────────────────────\
     Unit Tests        ← pytest (fast, no I/O)
```

---

## Commands

| Layer | Command |
|-------|---------|
| All Backend | `uv run pytest` |
| Unit | `uv run pytest tests/unit` |
| Agent | `uv run pytest tests/agents` |
| Integration | `uv run pytest tests/integration` |
| Dashboard API | `uv run pytest tests/dashboard` |
| Component | `cd tools/dashboard && pnpm test` |
| E2E | `cd tools/dashboard && pnpm test:smoke` |

---

## Patterns

### Unit Tests
- **Write BEFORE Implementation** (TDD)
- Mock all I/O
- Use `IsolatedAsyncioTestCase` for async
- Fast: < 100ms per test

### Component Tests
- Use `@testing-library/react`
- Mock API client
- Test user interactions

### E2E Tests
- Use Playwright
- Mock API responses
- Test full user journeys

---

## ADK Agent Evaluation Setup

### Fixture File Format (`.test.json`)
```json
{
  "name": "researcher_test",
  "initial_state": {
    "topic": "machine learning"
  },
  "expected_tool_calls": ["google_search"],
  "rubric": {
    "accuracy": "Did the agent find relevant sources?",
    "completeness": "Were multiple perspectives included?"
  }
}
```

### Evaluation Test Pattern
```python
from google.adk.evaluation import AgentEvaluator

def test_researcher_behavior():
    evaluator = AgentEvaluator(
        agent=researcher_agent,
        fixture_path="tests/agents/fixtures/researcher.test.json"
    )
    result = evaluator.evaluate()

    assert result.tool_trajectory_matches
    assert result.rubric_score >= 0.8
```

---

## Mock Patterns

### API Client Mocking (Vitest)
```typescript
vi.mock('../../src/api/client', () => ({
  apiClient: {
    getDockerStats: vi.fn().mockResolvedValue({
      containers: [
        { name: 'test', status: 'running' }
      ]
    }),
    getAgents: vi.fn().mockResolvedValue({
      agents: []
    }),
  },
}));
```

### Synthetic Library Mocking
```typescript
vi.mock('react-syntax-highlighter', () => ({
  Light: ({ children }: { children: string }) =>
    <pre data-testid="syntax-highlighter">{children}</pre>,
}));
```

### Child Component Suppression
```typescript
vi.mock('../../src/components/LogViewer', () => ({
  default: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="log-viewer">
      <button onClick={onClose}>Close</button>
    </div>
  ),
}));
```

---

## Test Naming Conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| Unit | `test_{function}_{scenario}` | `test_validate_email_invalid_format` |
| Component | `{Component}.test.tsx` | `DockerMonitor.test.tsx` |
| E2E | `{flow}.spec.ts` | `login_flow.spec.ts` |

---

## Product Overrides
Check: `products/{product}/skills/test/`
