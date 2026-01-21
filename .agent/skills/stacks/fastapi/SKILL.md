---
name: FastAPI Stack
description: FastAPI backend patterns
---

# FastAPI Stack

## Router Pattern
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])

class ItemResponse(BaseModel):
    id: str
    name: str

@router.get("/", response_model=list[ItemResponse])
async def list_items(dep=Depends(get_dependency)):
    return [ItemResponse(id="1", name="Item 1")]
```

---

## Patterns

### Response Models (Mandatory)
Always wrap responses in Pydantic models:

```python
from pydantic import BaseModel

# ✅ Wrapped response
class ItemListResponse(BaseModel):
    items: list[Item]
    total: int

# ❌ Never return bare lists
# return [item1, item2]  # Bad!
```

### Dependency Injection
```python
from typing import Annotated
from fastapi import Depends

def get_db() -> Database:
    db = Database()
    try:
        yield db
    finally:
        db.close()

DB = Annotated[Database, Depends(get_db)]

@router.get("/users")
async def get_users(db: DB):
    return db.query(User).all()
```

### Error Handling
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Standard HTTP errors
raise HTTPException(status_code=404, detail="Item not found")

# Custom exception handler
@app.exception_handler(ValidationError)
async def validation_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )
```

### SSE Streaming
```python
from fastapi.responses import StreamingResponse
import asyncio
import json

async def event_generator():
    while True:
        data = await get_latest_event()
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

@router.get("/events")
async def stream_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

### Middleware
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        return response

app.add_middleware(TimingMiddleware)
```

---

## Testing

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.anyio
async def test_list_items(client: AsyncClient):
    response = await client.get("/items/")
    assert response.status_code == 200
    assert "items" in response.json()
```

---

## Project Structure

```
routers/
├── __init__.py
├── agents.py       # /api/agents
├── docker.py       # /api/docker
└── system.py       # /api/system

# main.py
from routers import agents, docker, system

app.include_router(agents.router, prefix="/api")
app.include_router(docker.router, prefix="/api")
```
