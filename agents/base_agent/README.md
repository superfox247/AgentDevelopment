# Base Agent

Minimal **baseline agent** for all agent features, testing, and parity. Use it as the reference implementation when adding new agents or validating the platform.

## Purpose

- **Feature parity**: Same structure as researcher (callbacks, tools, planner, server).
- **Testing baseline**: Unit tests for server, callbacks, and tools; run with `python run_tests.py --agent base_agent`.
- **Eval harness**: Minimal eval set (`evaluations/base_baseline.test.json`) and `test_config.json` for `adk eval`.

## Structure

```
base_agent/
├── agent.py           # LlmAgent with echo tool, visibility callbacks, PlanReActPlanner
├── server.py          # FastAPI app via create_platform_app
├── callbacks/         # before/after agent and tool logging ([base] prefix)
├── tools/             # echo(text) — single, dependency-free tool
├── tests/             # test_server, test_callbacks, test_tools
├── evaluations/       # base_baseline.test.json, test_config.json
├── artifacts/         # ADK artifact output
├── memory/            # README (no memory by default)
└── planning/          # README (PlanReActPlanner)
```

## See the agent run

Use **ADK Web** (interactive UI) or **ADK Run** (CLI chat). Both hit the **real LLM** (Gemini).

**Prerequisites**: Copy `agents/base_agent/.env.example` → `agents/base_agent/.env` and set `GOOGLE_API_KEY` (or use Vertex). Same as researcher.

From repo root:

```bash
uv run adk web agents/base_agent --port 8501 --reload_agents
# Open http://localhost:8501, pick base_agent, chat (e.g. "Echo back: hello").
```

```bash
uv run adk run agents/base_agent
# CLI chat; same model calls.
```

Or run `make playground-base` from the repo root.

## Tests

```bash
# Base agent tests only
python run_tests.py --agent base_agent

# Skip evals (no API keys)
python run_tests.py --agent base_agent --skip-evals

# All agents (including base)
python run_tests.py
```

## Evaluations

```bash
uv run adk eval agents/base_agent agents/base_agent/evaluations/base_baseline.test.json \
  --config_file_path agents/base_agent/evaluations/test_config.json \
  --print_detailed_results
```

**Does eval hit the real LLM?** **Yes.** `adk eval` runs the agent live: it sends each eval user message to the agent, the agent calls Gemini (and tools like `echo`), then returns a response. Eval scores that run (e.g. `tool_trajectory_avg_score`, `response_match_score`) against the reference. So you need `GOOGLE_API_KEY` (or Vertex) for evals.
