---
name: Deploy Branch
description: CI/CD, infrastructure, release management
---

# Deploy Skills

## Sub-Skills
- `ci_cd/` - GitHub Actions, pipelines
- `infrastructure/` - Docker, cloud resources
- `release/` - Versioning, changelog, deployment

---

## Commands

| Task | Command |
|------|---------|
| Backend deps | `uv sync` |
| Frontend deps | `cd tools/dashboard && pnpm install` |
| Backend build | (not needed - Python) |
| Frontend build | `cd tools/dashboard && pnpm build` |
| Docker build | `docker compose build` |
| Start services | `docker compose up -d` |
| Stop services | `docker compose down` |

---

## Docker Compose Patterns

### Service Definition
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Environment Variables
```yaml
environment:
  # From .env file
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  # Static value
  - LOG_LEVEL=INFO
```

### Volume Mounts
```yaml
volumes:
  # Named volume (persistent)
  - app_data:/app/data
  # Bind mount (development)
  - ./src:/app/src:ro
```

---

## GitHub Actions Patterns

### Basic CI Workflow
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests
        run: uv run pytest

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff
      - run: ruff check .
```

### Matrix Build
```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
```

---

## Release Checklist

### Pre-Release
- [ ] All tests passing
- [ ] Lint clean
- [ ] Type check clean
- [ ] CHANGELOG updated
- [ ] Version bumped

### Release
- [ ] Tag created (`git tag vX.Y.Z`)
- [ ] Tag pushed (`git push --tags`)
- [ ] Release notes written
- [ ] Artifacts published

### Post-Release
- [ ] Production deployment verified
- [ ] Monitoring confirmed
- [ ] Team notified

---

## Version Bumping

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes

```bash
# Update in pyproject.toml
version = "1.2.3"

# Create and push tag
git tag v1.2.3
git push origin v1.2.3
```
