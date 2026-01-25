# Base Agent Template

Minimal agent template using **YAML config** (`agent.yaml`) plus optional `tools.py`. For the full collocated structure (tools, callbacks, memory, artifacts, planning, evaluations, tests), use [researcher_agent](../researcher_agent/) as the reference and follow the [agent-development workflow](../../.agent/workflows/agent-development.md).

## Structure
- `agent.yaml`: Declarative ADK config (model, tools, instruction). Tools are referenced by module path (e.g. `agents.base_agent.tools.example_tool`).
- `tools.py`: (Optional) Custom tools for this agent.
- `README.md`: This file.

## Usage
1. Copy this folder to `agents/<new_agent_name>`.
2. Rename and update `agent.yaml` (name, model, tools, instruction).
3. Add custom tools in `tools.py` if needed; register them in `agent.yaml`.
4. For the full pattern (callbacks, evals, collocated tests), see researcher_agent and the workflow.
