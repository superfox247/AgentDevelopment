---
description: Build the Agent Factory System
---

# Build Workflow

> **Skill**: See `sdlc/deploy/SKILL.md` for deployment patterns

## Backend Build

// turbo
```bash
uv sync
```

## Dashboard Build

// turbo
```bash
cd tools/dashboard && pnpm install && pnpm build
```

## Docker Build

```bash
docker compose build
```

## Verify

```bash
docker images | Select-String "course"
```
