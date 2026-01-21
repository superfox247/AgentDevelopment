---
name: Context Loader
description: Smart context loading based on product and skill branch
---

# Context Loader

## Purpose
Load only the context needed for the current task. Minimize token usage.

## Context Sources (Priority Order)

1. **Product Manifest** → Paths, stack, config
2. **Skill Branch** → Patterns, procedures
3. **Knowledge Items** → Recent learnings
4. **Codebase** → Only files in product scope

## Loading Protocol

### Step 1: Load Manifest
```bash
# If product detected
view_file products/{product}/manifest.yaml
```

### Step 2: Load Branch Skill
```bash
# Platform + product override
view_file sdlc/{branch}/SKILL.md
view_file products/{product}/skills/{branch}/SKILL.md  # if exists
```

### Step 3: Load Stack Skills
```bash
# Based on manifest.stack[]
for stack in manifest.stack:
    view_file stacks/{stack}/SKILL.md
```

### Step 4: Scope Codebase Access
```yaml
# Only access files within product paths
allowed_paths:
  - manifest.paths.root
  - manifest.paths.src
  - manifest.paths.tests
```

## Context Budget

| Phase | Max Files | Max Lines |
|-------|-----------|-----------|
| Planning | 10 | 500 |
| Development | 20 | 1000 |
| Review | 30 | 2000 |

## Anti-Patterns

- ❌ Loading all skills at once
- ❌ Searching entire codebase
- ❌ Reading files outside product scope
- ✅ Load manifest first, then scope everything
