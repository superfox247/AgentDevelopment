---
name: Develop Branch
description: Platform-level development patterns and procedures
---

# Development Skills

## Entry Point
This branch covers all implementation work: scaffolding, feature development, refactoring.

## Sub-Skills

| Skill | Use When |
|-------|----------|
| `scaffold/` | Creating new components, agents, modules |
| `implement/` | Building features, adding functionality |
| `refactor/` | Improving existing code structure |

---

## Core Patterns

### TDD Cycle (Mandatory)
1. **Schema**: Define Pydantic/Zod models in `schemas/`
2. **Red**: Write a failing test that defines expected behavior
3. **Green**: Implement the minimal logic to pass the test
4. **Refactor**: Improve code structure while keeping tests green

### Domain Isolation
- No cross-domain imports
- Shared code goes to `platform/` or `shared/`

### Naming Conventions
- Python: `snake_case`
- TypeScript: `camelCase` (functions), `PascalCase` (components)
- Files: Match export name

---

## Agent Scaffolding Protocol

When creating a new agent:

```
domains/{domain}/{agent_name}/
├── agent.yaml          # Agent configuration
├── __init__.py
└── tools/              # Optional custom tools
    └── __init__.py
```

### agent.yaml Template
```yaml
name: "{agent_name}"
description: "What this agent does"
model: "gemini-2.5-flash"
instruction: |
  You are a {role} agent.

  ## Task
  {primary_objective}

  ## Constraints
  - {constraint_1}
  - {constraint_2}
tools:
  - google_search
  - {custom_tool}
```

### Critical Rules

> [!IMPORTANT]
> **Directory Names MUST Match Import Paths**
> If code imports `from schemas.models.protocol`, the directory MUST be `schemas/models/protocol.py`.
> Never create "alias" modules to work around mismatches - fix the source of truth.

> [!IMPORTANT]
> **Agents Use Relative Tool Imports**
> Tools in the same agent directory use relative imports: `.tools.function_name`
> This ensures agents work in both local dev and Docker without path changes.
>
> ```yaml
> # ✅ Correct - relative import
> tools:
>   - .tools.generate_image_from_prompt
>
> # ❌ Wrong - absolute path breaks in Docker
> tools:
>   - domains.course_creator.image_generator.tools.generate_image_from_prompt
> ```

---

## Component Scaffolding Protocol

When creating a new React component:

```
src/components/{ComponentName}/
├── {ComponentName}.tsx    # Main component
├── {ComponentName}.test.tsx
└── index.ts               # Re-export
```

### Component Template
```tsx
interface Props {
  readonly id: string;
}

export function ComponentName({ id }: Props) {
  return <div data-testid="component-name">{id}</div>;
}
```

---

## Refactoring Patterns

### Extract Function
Before:
```python
def process(data):
    # 50 lines of validation
    # 30 lines of transformation
    # 20 lines of saving
```

After:
```python
def process(data):
    validated = validate(data)
    transformed = transform(validated)
    save(transformed)
```

### Replace Conditional with Polymorphism
Before:
```python
if agent_type == "research":
    do_research()
elif agent_type == "judge":
    do_judge()
```

After:
```python
agents = {"research": ResearchAgent, "judge": JudgeAgent}
agents[agent_type]().run()
```

---

## Product Overrides
Check for: `products/{product}/skills/develop/SKILL.md`
If exists, merge with this skill.
