---
description: Process for developing, expanding, and maintaining ADK-based agents
---

# Agent Development Workflow

This workflow defines how we create, extend, and maintain agents in this codebase. All agent work falls under this category. Use the [TDD workflow](tdd_feature.md) when implementing new behavior.

## Agent Structure (Collocated)

Each agent lives in `agents/<agent_name>/` with folders for each concern. See `agents/researcher_agent/` as the reference implementation.

```text
agents/<agent_name>/
├── __init__.py           # Exposes agent module
├── agent.py              # root_agent definition (required for adk web / adk run)
├── .env.example          # API keys, model config (copy to .env)
├── README.md             # Agent purpose, usage, run instructions
├── tools/                # Tool definitions the agent uses
│   ├── __init__.py
│   └── *.py              # e.g. web_tools.py, custom_tools.py
├── callbacks/            # Before/after agent, model, tool hooks
│   ├── __init__.py
│   └── *.py              # e.g. visibility.py, guardrails.py
├── memory/               # Long-term memory setup and docs
│   ├── __init__.py
│   └── README.md         # How memory works, how to view/inspect
├── artifacts/            # Agent-produced outputs (collocated)
│   └── .gitkeep          # Folder tracked; contents often gitignored
├── planning/             # Planner config (e.g. ReAct) if used
│   └── README.md         # Optional
├── evaluations/          # Eval sets, test cases, test_config
│   ├── *.test.json       # Unit-style eval sessions
│   ├── *.evalset.json    # Multi-session evals
│   └── test_config.json  # Criteria thresholds
└── tests/                # Unit tests for tools and support code
    ├── __init__.py
    └── test_*.py
```

## Step 1: Create Agent Skeleton

1. Copy `agents/researcher_agent/` as reference to `agents/<new_agent>/`.
2. Update `agent.py`: set `name`, `description`, `instruction`, `model`.
3. Add `.env.example` with `GOOGLE_API_KEY` (or Vertex) and document in README.

## Step 2: Add Tools (Simply)

- **Built-in**: `from google.adk.tools import google_search` (web), code execution, etc. Add to `tools=[...]`.
- **Custom**: Implement plain Python functions with docstrings (ADK infers schema). Place in `tools/`, import in `agent.py`, add to `tools=[...]`.
- Unit-test tool logic in `tests/test_tools.py` (or per-module).

## Step 3: Add Callbacks (Simply)

- Define functions that accept `CallbackContext` (and `LlmRequest` / `LlmResponse` / tool args as needed).
- Register on the agent: `before_agent_callback=`, `after_agent_callback=`, `before_model_callback=`, `after_model_callback=`, `before_tool_callback=`, `after_tool_callback=`.
- Use for logging, state inspection, guardrails, or modifying requests/results. Return `None` to proceed; return a replacement value to override.

## Step 4: Session, State, and Events (Visibility)

- **Session**: One conversation thread. Managed by `SessionService` (e.g. `InMemorySessionService`).
- **State**: Session scratchpad (`session.state`). Read/write via context in callbacks or tools.
- **Events**: Conversation history (user messages, model replies, tool calls). Visible in **Dev UI** → **Events** tab and **Trace** tab when using `adk web`.

Run `adk web agents/<agent_name>` and use Events/Trace to inspect state and events during development.

## Step 5: Memory (Long-Term)

- **MemoryService**: Searchable store across sessions (e.g. `InMemoryMemoryService`, `VertexAiRagMemoryService`).
- Provide `memory_service` to the **Runner** (not only the agent). The agent uses context methods to search/ingest.
- Document in `memory/README.md`: what we store, how we search, how to view (e.g. programmatic search, admin UI).

## Step 6: Artifact Management (Collocated)

- Use `ArtifactService` (e.g. `FileArtifactService`) with `root_dir` set to `agents/<agent_name>/artifacts/`.
- Agents save/load artifacts via context (`save_artifact`, `load_artifact`, `list_artifacts`). Keep outputs collocated with the agent.

## Step 7: Planning (Optional)

- Add a **planner** (e.g. `PlanReActPlanner`) to the agent: `planner=PlanReActPlanner()`.
- Enables plan-before-act behavior. Document usage in `planning/README.md` if non-obvious.

## Step 8: Evaluations

- **Test files**: `evaluations/*.test.json` — single-session evals (unit-style). Use for fast regression.
- **Evalsets**: `evaluations/*.evalset.json` — multi-session evals. Use for integration-style checks.
- **Config**: `evaluations/test_config.json` — criteria (e.g. `tool_trajectory_avg_score`, `response_match_score`).

Run evals:

```bash
# Test file (single-session) or evalset (multi-session)
uv run adk eval agents/<agent_name> agents/<agent_name>/evaluations/<set>.test.json
# or .../evaluations/<set>.evalset.json
# Optional: [--config_file_path=.../test_config.json] [--print_detailed_results]
```

Or via **Dev UI** → Eval tab: add session to eval set, run evaluation, inspect results.

## Step 9: Unit Tests (Code the Agent Relies On)

- **Tools**: Test pure logic in `tools/` (e.g. parsing, formatting) in `tests/test_tools.py`.
- **Callbacks**: If callbacks contain non-trivial logic, add `tests/test_callbacks.py`.
- Use `pytest`. Follow [TDD workflow](tdd_feature.md) for new behavior.

```bash
uv run pytest agents/<agent_name>/tests/ -v
```

## Step 10: Pre-Commit Test Verification

Before committing changes, run the smart test runner to verify everything works:

```bash
# Run all tests in smart order (exits on first failure)
python run_tests.py

# Run tests for a specific agent
python run_tests.py --agent researcher_agent

# Run tests without evaluations (faster, no API keys needed)
python run_tests.py --skip-evals

# Using Makefile
make test                    # Run all tests
make test-agent AGENT=researcher_agent  # Test specific agent
make test-fast              # Skip evaluations
```

The test runner executes tests in this order:
1. **Verification** - Checks setup and agent discovery (fastest)
2. **Unit Tests** - Core utilities (agent registry, models)
3. **API Tests** - Endpoint tests
4. **Integration Tests** - Real agent discovery and metadata
5. **Agent Tests** - Agent-specific unit tests
6. **Evaluations** - ADK evaluations (slowest, requires API keys)

**Early Exit**: The runner stops immediately on first failure, allowing you to fix issues and retry quickly. This enables fast fix-retry cycles during development.

**Commit Readiness**: When all tests pass, you're ready to commit!

## Agent Registry & Discovery

The system automatically discovers agents using the **Agent Registry** (`dashboard_api/utils/agent_registry.py`). The registry:

- **Scans** the `agents/` directory for agent folders
- **Extracts metadata** from `agent.py` files using AST parsing:
  - Agent `name` (from `root_agent` definition)
  - `description` (if provided in agent constructor)
  - `model` (if specified)
  - `has_server` (checks for `server.py` entry point)
- **Exposes metadata** via API endpoints:
  - `GET /api/agents` - List all discovered agents
  - `GET /api/agents/{name}/metadata` - Get rich metadata for a specific agent
  - `GET /api/agents/{name}` - Get agent.py source code

### Registry Requirements

For an agent to be discovered by the registry:

1. **Agent folder** must exist in `agents/<agent_name>/`
2. **agent.py** must exist and contain a `root_agent` variable
3. **Metadata extraction** works best when `root_agent` is defined with keyword arguments:
   ```python
   root_agent = LlmAgent(
       name="my_agent",
       description="Agent description",  # Extracted automatically
       model="gemini-2.0-flash",          # Extracted automatically
       # ...
   )
   ```

### Server Entry Point

To enable the agent to run as a FastAPI service (for Docker deployment):

1. Create `agents/<agent_name>/server.py`:
   ```python
   from google.adk.apps import App
   from agent_platform.server import create_platform_app
   from agent import root_agent
   
   adk_app = App(root_agent=root_agent)
   app = create_platform_app(
       adk_app=adk_app,
       description="Agent description",
       enable_a2a=True,
       include_root_route=True,
   )
   ```

2. The registry will detect `has_server=True` and the agent will appear as "Available" in the UI.

## Run and Iterate

- **CLI**: `adk run agents/<agent_name>` (from project root).
- **Dev UI**: `adk web agents/<agent_name>` → select agent, chat, inspect Events/Trace.
- **API**: Use `adk api_server` or the platform's FastAPI runner when integrating with the rest of the system.
- **Dashboard UI**: View agent metadata, description, and model info in the Agents view.

## Checklist for New Agents

- [ ] Agent folder structure (tools, callbacks, memory, artifacts, planning, evaluations, tests).
- [ ] `root_agent` in `agent.py`; tools and callbacks wired.
- [ ] Session/state/events visible via Dev UI.
- [ ] Memory and artifacts documented and configured if used.
- [ ] At least one eval (test file or evalset) and `test_config.json`.
- [ ] Unit tests for tools (and callbacks if applicable).
- [ ] **Pre-commit verification**: Run `python run_tests.py --agent <agent_name>` and all tests pass.
