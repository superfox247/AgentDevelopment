---
name: Define Domain Model
description: A skill to define strictly typed Input/Output models in the registry, enforcing the "Schema-First" architecture.
---

# Define Domain Model

Use this skill when a new data contract is needed between agents or for a new agent's interface.

## 1. Load Context
- `registry/models.py`: Centralized models.
- `agent_platform/models.py`: Core shared models.

## 2. Design Principles (Schema-First)
- **Inheritance**: Must inherit from `pydantic.BaseModel`.
- **Field Descriptions**: **MANDATORY**. You must use `Field(..., description="...")`. This description is what the LLM sees.
- **Typing**: Use standard `typing` (`List`, `Optional`, `Dict`).
- **Safety**: Avoid `Any`. Be specific.

## 1. Cognitive Heuristics
**When to use:** Use this skill when you need to define formally typed data structures (Schema-First).
**Validation:** Ensure models inherit from `BaseModel` and have docstrings.

## 2. Load Context
- `.agent/skills/define_domain_model/define_domain_model.py`: The automation script.
- `registry/models/protocol.py`: The target file.

## 3. Usage (Automated)

Run the script:
```bash
uv run .agent/skills/define_domain_model/define_domain_model.py \
  --name "MyModel" \
  --description "Description of the model" \
  --heuristics "Use when exchanging data between Agent A and Agent B" \
  --verification "Must validate X field format"
```

This will append the new model class to `registry/models/protocol.py`.

## 4. Immediate Follow-up
1.  Edit `registry/models/protocol.py` to add the actual fields (name, type, description).
## 4. Verification
Create a snippet to verify serialization:
```python
obj = CourseOutline(title="Test", modules=[], estimated_duration=0)
print(obj.model_dump_json())
```
