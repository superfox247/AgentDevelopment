# Long-term memory (MemoryService)

The base agent does not configure memory by default. The platform Runner uses `InMemorySessionService` for session state only.

To add memory (e.g. for baseline evals or cross-session recall), configure a `MemoryService` in a custom Runner as described in the researcher agent’s `memory/README.md`.
