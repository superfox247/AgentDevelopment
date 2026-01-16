---
description: Build the Agent Factory System
---

# Build Workflow

This workflow builds the Docker containers for the entire system using the Universal Dockerfile pattern.

## 1. Clean Build
To ensure a fresh build and remove old artifacts:

```bash
make clean
```

## 2. Build Containers
Builds `orchestrator`, `researcher`, `judge`, and `content_builder` using `platform/Dockerfile.agent`.

// turbo
```bash
make build
```

## 3. Verify Build
Check if images were created successfully:

```bash
docker images | grep course-creation
```
