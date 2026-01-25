# Long-term memory (MemoryService)

## What it is

**Memory** is a searchable store of information that can span *many sessions*. It’s separate from **Session** (one conversation) and **State** (that session’s scratchpad). The agent uses it to recall facts, preferences, or past findings across conversations.

## How it works

- **MemoryService** (e.g. `InMemoryMemoryService`, `VertexAiRagMemoryService`) manages the store.
- You pass `memory_service` to the **Runner**, not the agent. The agent uses context methods (e.g. `search_memory`, ingest from session) provided by the framework.
- **InMemoryMemoryService**: fast, for local/dev; data is lost on restart.
- **VertexAiRagMemoryService**: persistent, semantic search over a RAG corpus.

## How to view / inspect

- **In-memory**: Use `memory_service.session_events` (or equivalent) if you hold a reference to the service. You can also add a small admin script or callback that logs summary stats (e.g. number of stored items).
- **Vertex RAG**: Use the Vertex AI console or your RAG corpus tools to inspect indexed content.
- **Programmatic**: Call `memory_service.search_memory(...)` (or the context’s search API) from a test script or admin endpoint to run queries and print results.

## Using memory with the researcher agent

When you run the researcher via a **custom Runner** (e.g. FastAPI app), configure:

```python
from google.adk.memory import InMemoryMemoryService

memory_service = InMemoryMemoryService()
runner = Runner(
    agent=root_agent,
    app_name="researcher_app",
    session_service=...,
    artifact_service=...,
    memory_service=memory_service,
)
```

`adk web` / `adk run` use ADK’s default Runner; they typically don’t expose a configurable MemoryService. For memory-backed runs, use a custom Runner as above.
