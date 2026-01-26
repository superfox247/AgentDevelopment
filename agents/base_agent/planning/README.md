# Planning (PlanReActPlanner)

The base agent uses **PlanReActPlanner**, same as the researcher agent, for feature parity and baseline testing.

Configured in `agent.py`:

```python
from google.adk.planners import PlanReActPlanner

root_agent = LlmAgent(
    ...
    planner=PlanReActPlanner(),
)
```
