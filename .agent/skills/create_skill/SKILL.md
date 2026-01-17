---
name: Create Skill
description: A meta-skill to standardize the creation of new automation skills (SKILL.md + script).
---

# Create Skill

Use this skill to create new skills that follow the "Executable Documentation" pattern.

## 1. Cognitive Heuristics
**When to use:** Use this skill when you need to extend the Agent Factory's capabilities with a new repeatable workflow.
**Validation:** Ensure the new skill has a clear intent (Why?) and success criteria (Did it work?).

## 2. Load Context
- `scripts/create_skill.py`: The automation script.

## 3. Usage (Automated)

Run the script with cognitive parameters:
```bash
uv run python scripts/create_skill.py \
  --name [name] \
  --description "Description" \
  --heuristics "When to use this skill..." \
  --verification "How to verify success..."
```

*Example*:
```bash
uv run python scripts/create_skill.py \
  --name "analyze_logs" \
  --description "Parses error logs" \
  --heuristics "Use when an agent fails with an unknown error." \
  --verification "Check if a root cause summary was generated."
```

## 3. Immediate Follow-up
1.  Navigate to `scripts/[name].py` and implement the logic.
2.  Review `.agent/skills/[name]/SKILL.md`.
