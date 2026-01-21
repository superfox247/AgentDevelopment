---
name: SDLC Skills
description: Software Development Lifecycle skills covering plan to operate
---

# SDLC Skills

## Branches

| Branch | When to Use |
|--------|-------------|
| `plan/` | Design, architecture, requirements |
| `develop/` | Build, implement, create |
| `test/` | Write tests, verify, validate |
| `review/` | Code review, security audit |
| `deploy/` | CI/CD, release, infrastructure |
| `operate/` | Debug, monitor, incident response |
| `research/` | Explore, prototype, evaluate |

## Loading

Load the branch matching user intent:
```
User: "Add a new API endpoint"
→ Load: sdlc/develop/SKILL.md
```

## Product Override

If working on a product, also load:
```
products/{product}/skills/{branch}/SKILL.md
```
