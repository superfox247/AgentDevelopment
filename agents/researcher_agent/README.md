# Researcher Agent

A baseline **web-capable research assistant** built with the [Google ADK](https://google.github.io/adk-docs/get-started/about/). It uses Google Search for grounding, planning (PlanReActPlanner), callbacks for visibility, and follows the [agent-development workflow](../../.agent/workflows/agent-development.md).

## Features

- **Tool use**: `google_search` (Gemini grounding). One-tool limitation: no other tools in the same agent; see [ADK tool limitations](https://google.github.io/adk-docs/tools/limitations/).
- **Callbacks**: `before_agent` / `after_agent` / `before_tool` / `after_tool` logging for session and event visibility.
- **Session / state / events**: Managed by `SessionService`. Inspect in **Dev UI** → Events and Trace tabs.
- **Memory**: Long-term store via `MemoryService`. See [memory/README.md](memory/README.md) for setup and how to view.
- **Artifacts**: Collocated in `artifacts/`. Use `FileArtifactService(root_dir=".../researcher_agent/artifacts")` when running via a custom Runner.
- **Planning**: `PlanReActPlanner` for plan-before-act behavior. See [planning/README.md](planning/README.md).

## Structure

```
researcher_agent/
├── __init__.py
├── agent.py           # root_agent
├── .env.example
├── README.md
├── tools/             # format_search_query (unit-tested; not wired due to one-tool limit)
├── callbacks/         # visibility logging
├── memory/            # MemoryService docs
├── artifacts/         # collocated outputs
├── planning/          # planner docs
├── evaluations/       # evals + test_config
└── tests/             # unit tests for tools
```

## Run

**Prerequisites**: Python 3.10+, `uv` (or `pip`), `google-adk`. Copy `.env.example` → `.env` and set `GOOGLE_API_KEY`.

From project root:

```bash
# Dev UI (recommended): chat, Events tab, Trace tab
uv run adk web agents/researcher_agent

# CLI
uv run adk run agents/researcher_agent
```

Select `researcher_agent` in the Dev UI dropdown, then chat. Use **Events** and **Trace** to inspect tool calls, state, and events.

## Evaluate

```bash
uv run adk eval agents/researcher_agent agents/researcher_agent/evaluations/researcher_basic.test.json \
  --config_file_path agents/researcher_agent/evaluations/test_config.json \
  --print_detailed_results
```

Or use **Dev UI** → Eval tab: add current session to an eval set, run evaluation.

## Unit tests

```bash
uv run pytest agents/researcher_agent/tests/ -v
```

## Custom Runner (memory, artifacts)

When running via your own FastAPI/app Runner, configure `memory_service` and `artifact_service` as in [memory/README.md](memory/README.md). Use `FileArtifactService(root_dir="agents/researcher_agent/artifacts")` so outputs stay collocated.
