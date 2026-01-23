---
name: Skill Router
description: Entry point that routes user intent to the correct skill branch
---

# Skill Router

## Purpose
Parse user intent and load the appropriate skill branch with smart context.

## Routing Table

| Keywords | Branch | Example |
|----------|--------|---------|
| design, spec, architect, plan | `.agent/skills/sdlc/plan/` | "Design the auth system" |
| build, implement, create, add | `.agent/skills/sdlc/develop/` | "Add a new endpoint" |
| test, verify, validate, check | `.agent/skills/sdlc/test/` | "Write tests for X" |
| review, audit, security | `.agent/skills/sdlc/review/` | "Review this PR" |
| deploy, release, ship, ci/cd | `.agent/skills/sdlc/deploy/` | "Deploy to staging" |
| debug, fix, monitor, logs | `.agent/skills/sdlc/operate/` | "Debug this error" |

## Product Detection

1. Check file path in user context → match against `products/*/manifest.yaml`
2. Check explicit mention → "dashboard", "course creator"
3. Default → platform-level skills only

## Stack Detection

From `manifest.yaml`:
```yaml
stack:
  - typescript  # → load stacks/typescript/
  - react       # → load stacks/react/
```

## Loading Order

1. `_core/` (always)
2. `sdlc/{branch}/` (platform)
3. `products/{name}/skills/{branch}/` (product override)
4. `stacks/{stack}/` (tech-specific)

## Output

After routing, set context:
```
CURRENT_PRODUCT: dashboard | course_creator | null
CURRENT_BRANCH: develop
LOADED_SKILLS: [_core/*, sdlc/develop/*, products/dashboard/skills/develop/*, stacks/typescript/*]
```
