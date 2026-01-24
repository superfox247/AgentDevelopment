---
name: Python Stack
description: Python-specific patterns and tools
---

# Python Stack

## Package Management
- Tool: `uv`
- Config: `pyproject.toml`
- Install: `uv sync`
- Run: `uv run <command>`

## Formatting & Linting
- Ruff: `uv run ruff check . --fix`
- Format: `uv run ruff format .`

## Type Checking
- MyPy: `uv run mypy .`

## Testing
- pytest: `uv run pytest`

---

## Patterns

### Logging (Mandatory)
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Use structured logging
logger.info("Processing item", extra={"item_id": item.id})

# ❌ Never use print() for logging
```

### Pydantic Models
```python
from pydantic import BaseModel, Field, field_validator

class CreateUserRequest(BaseModel):
    """Request model for creating a user."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: int | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip()

# ✅ Always use model_dump() for serialization
data = user.model_dump(mode="json")

# ✅ Use model_validate() for parsing
user = CreateUserRequest.model_validate(raw_data)
```

### Async Patterns
```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# ✅ Async context manager for resources
@asynccontextmanager
async def get_connection() -> AsyncGenerator[Connection, None]:
    conn = await connect()
    try:
        yield conn
    finally:
        await conn.close()

# Usage
async with get_connection() as conn:
    await conn.execute(query)
```

### Async Testing
```python
from unittest import IsolatedAsyncioTestCase

class TestAsyncService(IsolatedAsyncioTestCase):
    async def test_fetch_data(self):
        result = await fetch_data()
        self.assertEqual(result.status, "ok")
```

---

## Ruff Rules

| Category | Rule | Fix |
|----------|------|-----|
| Imports | `I001` | Sort imports with `ruff check --fix` |
| f-strings | `UP032` | Use f-strings instead of `.format()` |
| Pathlib | `PTH` | Use `pathlib.Path` instead of `os.path` |
| Type hints | `ANN` | Add missing type annotations |

---

## Common Gotchas

| Issue | Solution |
|-------|----------|
| Mutable default args | Use `field(default_factory=list)` or `None` |
| Circular imports | Import inside function or use `TYPE_CHECKING` |
| `await` missing | Always `await` coroutines, use linting |
| Dict key ordering | Python 3.7+ dicts are ordered, but use explicit if needed |

---

## Project Structure

```
agent_platform/
├── agents/            # Agent implementations
├── tools/             # Tool definitions
├── schemas/           # Pydantic models
└── config.py          # Configuration

tests/
├── unit/              # Fast, isolated tests
├── agents/            # ADK evaluations
└── integration/       # Cross-service tests
```
