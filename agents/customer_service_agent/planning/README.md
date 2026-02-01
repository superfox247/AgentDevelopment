# Planning (PlanReActPlanner)

The customer service agent uses **PlanReActPlanner**, which makes the model produce a **plan** before taking actions (e.g. tool calls). That improves multi-step processing: the agent reasons about input validation, structuring, and compliance checking first, then executes.

## Configuration

The planner is wired in `agent.py`:

```python
from google.adk.planners import PlanReActPlanner

root_agent = LlmAgent(
    ...
    planner=PlanReActPlanner(),
)
```

No extra config is required. `PlanReActPlanner` does not need built-in "thinking" support from the model.

## Optional

- **BuiltInPlanner** (with `thinking_config`): Uses the model's native thinking mode. Only for models that support it.
- **Custom planner**: Implement `BasePlanner` and use it in place of `PlanReActPlanner` if you need different planning behavior.
