---
name: Scaffold New YAML Agent
description: A skill to scaffold a new AI agent following the Agent Factory "YamlAgent" standards.
---

# Scaffold New YAML Agent

This skill guides you through creating a new agent in the `domains/` directory using the declarative YAML standard.

## 1. Load Context
Before generating any code, you MUST use `view_file` to read these source-of-truth files:
- `agent_platform/yaml_loader.py`: Understand `YamlAgent` arguments.
- `registry/models.py`: Check existing models to avoid duplication.
- `domains/course_creator/root_agent.yaml`: The "Gold Standard" template.
- `domains/[domain]/__init__.py`: Check current registration.

## 2. Requirements Gathering
Ask the user for:
- **Agent Name**: (e.g., `content_writer`)
- **Domain**: (e.g., `course_creator` or a new domain)
- **Role**: What does this agent do?
- **Inputs**: What data does it need? (Schema-First)
- **Outputs**: What data does it produce? (Schema-First)

## 1. Cognitive Heuristics
**When to use:** Use this skill when you need to create a new AI agent component.
**Validation:** Ensure the agent has a clear Role and Domain.

## 2. Load Context
- `.agent/skills/scaffold_agent/scaffold_agent.py`: The automation script.

## 3. Usage (Automated)

Run the script:
```bash
uv run .agent/skills/scaffold_agent/scaffold_agent.py \
  --name [agent_name] \
  --domain [domain_name] \
  --role "Description of what it does" \
  --heuristics "When this agent activates" \
  --verification "Success criteria"
```

*Example*:
```bash
uv run .agent/skills/scaffold_agent/scaffold_agent.py \
  --name "writer" \
  --domain "content_creation" \
  --role "Writes blog posts" \
  --heuristics "Trigger when user asks for a draft." \
  --verification "Check if output is markdown."
```

## 4. Implementation Steps (Manual Fallback)
If the script fails:
1.  Create directory `domains/[domain]/[agent_name]`.
2.  Create `agent.yaml`.
3.  Create `instruction.md`.
4.  Create `agent.py`.
5.  Create necessary `__init__.py` files.

## 5. Immediate Follow-up
1.  Edit `domains/[domain]/[agent_name]/agent.yaml` to customize the prompt and tools.
2.  Run `uv run .agent/skills/define_domain_model/define_domain_model.py` to define your models (see `define_domain_model` skill).
3.  Run `uv run .agent/skills/scaffold_tests/scaffold_tests.py` to generate tests.
4.  Run `uv run adk web [domain]` to verify it loads.
